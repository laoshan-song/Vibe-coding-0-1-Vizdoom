import argparse
from importlib.util import find_spec
from pathlib import Path

import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor

from scenario_catalog import (
    default_bc_path,
    default_checkpoint_dir,
    default_log_dir,
    default_ppo_path,
    get_default_timesteps,
    get_scenario_spec,
    list_scenarios,
)
from scenario_env import make_env


def make_single_env(scenario, visible=False):
    def _factory():
        return make_env(scenario=scenario, visible=visible)
    return _factory


def load_bc_payload(model_path, device):
    payload = torch.load(model_path, map_location=device)
    state_dict = payload['state_dict']
    return {
        'obs_dim': int(payload['obs_dim']),
        'action_dim': int(payload['action_dim']),
        'state_dict': state_dict,
        'hidden_sizes': [
            int(state_dict['net.0.weight'].shape[0]),
            int(state_dict['net.2.weight'].shape[0]),
        ],
    }


def build_policy_kwargs(spec, bc_payload=None):
    if spec.observation_mode == 'visual':
        return {}
    if bc_payload is None:
        return {}
    hidden_sizes = bc_payload['hidden_sizes']
    return {'net_arch': dict(pi=hidden_sizes, vf=hidden_sizes), 'activation_fn': nn.ReLU, 'ortho_init': False}


def initialize_actor_from_bc(model, bc_payload):
    actor_layers = [module for module in model.policy.mlp_extractor.policy_net if isinstance(module, nn.Linear)]
    bc_state = bc_payload['state_dict']
    bc_layers = [('net.0.weight', 'net.0.bias'), ('net.2.weight', 'net.2.bias')]
    for actor_layer, (weight_key, bias_key) in zip(actor_layers, bc_layers):
        actor_layer.weight.data.copy_(bc_state[weight_key].to(actor_layer.weight.device))
        actor_layer.bias.data.copy_(bc_state[bias_key].to(actor_layer.bias.device))
    model.policy.action_net.weight.data.copy_(bc_state['net.4.weight'].to(model.policy.action_net.weight.device))
    model.policy.action_net.bias.data.copy_(bc_state['net.4.bias'].to(model.policy.action_net.bias.device))


def parse_args():
    parser = argparse.ArgumentParser(description='Train PPO for a built-in ViZDoom scenario.')
    parser.add_argument('--scenario', choices=list_scenarios(), required=True)
    parser.add_argument('--timesteps', type=int, default=None)
    parser.add_argument('--num-envs', type=int, default=4)
    parser.add_argument('--model-path', default=None)
    parser.add_argument('--log-dir', default=None)
    parser.add_argument('--checkpoint-dir', default=None)
    parser.add_argument('--checkpoint-freq', type=int, default=50000)
    parser.add_argument('--bc-init', default=None)
    parser.add_argument('--resume', default=None, help='Resume training from a PPO model zip file')
    parser.add_argument('--visible', action='store_true')
    parser.add_argument('--cpu', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    spec = get_scenario_spec(args.scenario)
    timesteps = args.timesteps if args.timesteps is not None else get_default_timesteps(args.scenario)
    if args.visible and args.num_envs != 1:
        print('visible training requires --num-envs 1, overriding')
        args.num_envs = 1

    model_path = Path(args.model_path or default_ppo_path(args.scenario))
    log_dir = Path(args.log_dir or default_log_dir(args.scenario))
    checkpoint_dir = Path(args.checkpoint_dir or default_checkpoint_dir(args.scenario))
    model_path.parent.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    vec_env = DummyVecEnv([make_single_env(args.scenario, visible=args.visible) for _ in range(args.num_envs)])
    vec_env = VecMonitor(vec_env)

    tensorboard_log = str(log_dir) if find_spec('tensorboard') is not None else None
    progress_bar = find_spec('tqdm') is not None and find_spec('rich') is not None
    device = 'cpu' if args.cpu else 'auto'

    bc_init_path = args.bc_init
    if bc_init_path == 'auto':
        bc_init_path = str(default_bc_path(args.scenario))
    if spec.pipeline != 'teacher_bc_ppo':
        bc_init_path = None

    bc_payload = load_bc_payload(bc_init_path, torch.device('cpu')) if bc_init_path else None
    policy_name = 'MlpPolicy' if spec.observation_mode == 'structured' else 'CnnPolicy'

    if args.resume:
        print(f'resuming PPO from checkpoint: {args.resume}')
        model = PPO.load(
            args.resume,
            env=vec_env,
            device=device,
            tensorboard_log=tensorboard_log,
        )
    else:
        model = PPO(
            policy=policy_name,
            env=vec_env,
            learning_rate=3e-4,
            n_steps=512 if spec.observation_mode == 'structured' else 256,
            batch_size=512 if spec.observation_mode == 'structured' else 256,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,
            verbose=1,
            device=device,
            tensorboard_log=tensorboard_log,
            policy_kwargs=build_policy_kwargs(spec, bc_payload),
        )

        if bc_payload is not None:
            initialize_actor_from_bc(model, bc_payload)
            print(f'initialized PPO actor from BC: {bc_init_path}')

    checkpoint_callback = CheckpointCallback(
        save_freq=max(1, args.checkpoint_freq // args.num_envs),
        save_path=str(checkpoint_dir),
        name_prefix=f'{args.scenario}_ppo',
    )
    print(
        f'starting PPO scenario={args.scenario} title={spec.title} mode={spec.observation_mode} '
        f'timesteps={timesteps} bc_init={bc_init_path is not None} resume={args.resume is not None}'
    )
    model.learn(total_timesteps=timesteps, callback=checkpoint_callback, progress_bar=progress_bar, reset_num_timesteps=args.resume is None)
    model.save(str(model_path))
    print(f'saved PPO model to {model_path}')
    vec_env.close()


if __name__ == '__main__':
    main()

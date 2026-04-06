import argparse
from pathlib import Path

import torch
from stable_baselines3 import PPO

from scenario_model import load_bc_model
from scenario_catalog import default_bc_path, default_ppo_path, get_scenario_spec, list_scenarios
from scenario_env import make_env
from scenario_teacher import ScenarioTeacherPolicy


def parse_args():
    parser = argparse.ArgumentParser(description='Play a model for a built-in scenario.')
    parser.add_argument('--scenario', choices=list_scenarios(), required=True)
    parser.add_argument('--agent', choices=['teacher', 'bc', 'ppo'], default='ppo')
    parser.add_argument('--episodes', type=int, default=5)
    parser.add_argument('--bc-model', default=None)
    parser.add_argument('--ppo-model', default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    spec = get_scenario_spec(args.scenario)
    env = make_env(args.scenario, visible=True)
    teacher = None
    bc_model = None
    ppo_model = None

    if args.agent == 'teacher':
        if spec.pipeline != 'teacher_bc_ppo':
            raise ValueError(f'scenario={args.scenario} uses {spec.pipeline}, teacher playback is not available')
        teacher = ScenarioTeacherPolicy(args.scenario)
        teacher.bind_action_names(env.action_names)
    elif args.agent == 'bc':
        if spec.pipeline != 'teacher_bc_ppo':
            raise ValueError(f'scenario={args.scenario} uses {spec.pipeline}, BC playback is not available')
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        bc_model = load_bc_model(Path(args.bc_model or default_bc_path(args.scenario)), device)
    else:
        ppo_model = PPO.load(Path(args.ppo_model or default_ppo_path(args.scenario)))

    try:
        for episode in range(1, args.episodes + 1):
            if teacher is not None:
                teacher.reset()
            obs, _ = env.reset()
            done = False
            total_reward = 0.0
            steps = 0
            last_action = 0
            while not done:
                if teacher is not None:
                    action = teacher.predict(obs)
                elif bc_model is not None:
                    with torch.no_grad():
                        logits = bc_model(torch.tensor(obs, dtype=torch.float32).unsqueeze(0).to(next(bc_model.parameters()).device))
                        action = int(torch.argmax(logits, dim=1).item())
                else:
                    action, _ = ppo_model.predict(obs, deterministic=True)
                    action = int(action)
                obs, reward, terminated, truncated, _ = env.step(action)
                total_reward += reward
                done = terminated or truncated
                steps += 1
                last_action = action
                env.render()
            print(f'episode={episode} steps={steps} reward={total_reward:.2f} last_action={env.action_names[last_action]}')
    finally:
        env.close()


if __name__ == '__main__':
    main()

import argparse
from pathlib import Path

import numpy as np

from scenario_catalog import default_demo_path, get_scenario_spec, list_scenarios
from scenario_env import make_env
from scenario_teacher import ScenarioTeacherPolicy


def parse_args():
    parser = argparse.ArgumentParser(description='Collect teacher demonstrations for a built-in scenario.')
    parser.add_argument('--scenario', choices=list_scenarios(), required=True)
    parser.add_argument('--episodes', type=int, default=200)
    parser.add_argument('--output', default=None)
    parser.add_argument('--visible', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    spec = get_scenario_spec(args.scenario)
    if spec.pipeline != 'teacher_bc_ppo':
        raise ValueError(f'scenario={args.scenario} uses {spec.pipeline}, demo collection is not the primary path')

    output_path = Path(args.output or default_demo_path(args.scenario))
    env = make_env(args.scenario, visible=args.visible)
    teacher = ScenarioTeacherPolicy(args.scenario)
    teacher.bind_action_names(env.action_names)

    observations = []
    actions = []
    episode_rewards = []
    try:
        for episode in range(1, args.episodes + 1):
            teacher.reset()
            obs, _ = env.reset()
            done = False
            total_reward = 0.0
            while not done:
                action = teacher.predict(obs)
                observations.append(obs.copy())
                actions.append(action)
                obs, reward, terminated, truncated, _ = env.step(action)
                total_reward += reward
                done = terminated or truncated
                if args.visible:
                    env.render()
            episode_rewards.append(total_reward)
            print(f'episode={episode} reward={total_reward:.2f}')
    finally:
        env.close()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        observations=np.asarray(observations, dtype=np.float32),
        actions=np.asarray(actions, dtype=np.int64),
        episode_rewards=np.asarray(episode_rewards, dtype=np.float32),
    )
    print(f'saved demos to {output_path} mean_reward={float(np.mean(episode_rewards)):.2f}')


if __name__ == '__main__':
    main()

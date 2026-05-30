import argparse
import subprocess
import sys

from scenario_catalog import get_scenario_spec, list_scenarios


def run_command(command):
    print('running:', ' '.join(command))
    subprocess.run(command, check=True)


def parse_args():
    parser = argparse.ArgumentParser(description='Run the workflow for a built-in ViZDoom scenario.')
    parser.add_argument('--scenario', choices=list_scenarios(), required=True)
    parser.add_argument('--stage', choices=['teacher', 'collect', 'bc', 'train', 'play', 'all'], default='all')
    parser.add_argument('--episodes', type=int, default=None)
    parser.add_argument('--epochs', type=int, default=None)
    parser.add_argument('--timesteps', type=int, default=None)
    parser.add_argument('--agent', choices=['teacher', 'bc', 'ppo'], default='ppo')
    parser.add_argument('--visible', action='store_true')
    parser.add_argument('--cpu', action='store_true')
    parser.add_argument('--val-split', type=float, default=None)
    parser.add_argument('--patience', type=int, default=None)
    parser.add_argument('--resume', default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    spec = get_scenario_spec(args.scenario)
    python = sys.executable

    if args.stage == 'teacher':
        run_command([python, 'scenario_teacher.py', '--scenario', args.scenario, '--episodes', str(args.episodes or 5)] + (['--visible'] if args.visible else []))
        return

    if args.stage in {'collect', 'all'} and spec.pipeline == 'teacher_bc_ppo':
        command = [python, 'scenario_collect.py', '--scenario', args.scenario]
        if args.episodes is not None:
            command.extend(['--episodes', str(args.episodes)])
        if args.visible:
            command.append('--visible')
        run_command(command)

    if args.stage in {'bc', 'all'} and spec.pipeline == 'teacher_bc_ppo':
        command = [python, 'scenario_bc.py', '--scenario', args.scenario]
        if args.epochs is not None:
            command.extend(['--epochs', str(args.epochs)])
        if args.val_split is not None:
            command.extend(['--val-split', str(args.val_split)])
        if args.patience is not None:
            command.extend(['--patience', str(args.patience)])
        if args.cpu:
            command.append('--cpu')
        run_command(command)

    if args.stage in {'train', 'all'}:
        command = [python, 'scenario_train.py', '--scenario', args.scenario]
        if spec.pipeline == 'teacher_bc_ppo':
            command.extend(['--bc-init', 'auto'])
        if args.timesteps is not None:
            command.extend(['--timesteps', str(args.timesteps)])
        if args.resume is not None:
            command.extend(['--resume', str(args.resume)])
        if args.cpu:
            command.append('--cpu')
        if args.visible:
            command.append('--visible')
            command.extend(['--num-envs', '1'])
        run_command(command)

    if args.stage == 'play':
        run_command([python, 'scenario_play.py', '--scenario', args.scenario, '--agent', args.agent])


if __name__ == '__main__':
    main()

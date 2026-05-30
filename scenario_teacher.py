import argparse

from scenario_catalog import get_scenario_spec, list_scenarios
from scenario_env import make_env


class ScenarioTeacherPolicy:
    def __init__(self, scenario: str, center_threshold: float = 0.08, search_hold: int = 6):
        self.spec = get_scenario_spec(scenario)
        self.scenario = scenario
        self.center_threshold = center_threshold
        self.search_hold = max(1, int(search_hold))
        self.action_names = []
        self.reset()

    def bind_action_names(self, action_names):
        self.action_names = list(action_names)

    def reset(self):
        self.search_direction = -1
        self.missing_steps = 0

    def _action_index(self, keyword: str, fallback: int = 0):
        for index, name in enumerate(self.action_names):
            if keyword in name:
                return index
        return fallback

    def _search_action(self):
        self.missing_steps += 1
        if self.missing_steps % self.search_hold == 0:
            self.search_direction *= -1
        if self.search_direction < 0:
            return self._action_index('TURN_LEFT', self._action_index('MOVE_LEFT', 0))
        return self._action_index('TURN_RIGHT', self._action_index('MOVE_RIGHT', 0))

    def predict(self, obs):
        if self.spec.observation_mode != 'structured':
            raise ValueError(f'teacher policy is only supported for structured scenarios, got {self.scenario}')
        visible = obs[-6]
        x_offset = obs[-5]
        centered = obs[-1]
        health = obs[-3]

        if self.spec.family == 'dodge':
            if visible < 0.5:
                return self._action_index('MOVE_LEFT', 0)
            return self._action_index('MOVE_RIGHT', 0) if x_offset < 0 else self._action_index('MOVE_LEFT', 0)

        if visible < 0.5:
            return self._search_action()

        self.missing_steps = 0
        self.search_direction = -1 if x_offset < 0 else 1

        threshold = self.center_threshold
        if self.spec.family == 'collect' and health < 0.3:
            threshold = self.center_threshold * 3.0

        if 'ATTACK' in ' '.join(self.action_names):
            if centered > 0.5 or abs(x_offset) < threshold:
                return self._action_index('ATTACK', 0)
            if 'TURN_LEFT' in ' '.join(self.action_names) or 'TURN_RIGHT' in ' '.join(self.action_names):
                return self._action_index('TURN_LEFT', 0) if x_offset < 0 else self._action_index('TURN_RIGHT', 1)
            return self._action_index('MOVE_LEFT', 0) if x_offset < 0 else self._action_index('MOVE_RIGHT', 1)

        if 'MOVE_FORWARD' in ' '.join(self.action_names):
            if centered > 0.5 or abs(x_offset) < threshold:
                return self._action_index('MOVE_FORWARD', 0)
            return self._action_index('TURN_LEFT', 0) if x_offset < 0 else self._action_index('TURN_RIGHT', 1)

        return self._search_action()


def parse_args():
    parser = argparse.ArgumentParser(description='Run a scenario-specific heuristic teacher policy.')
    parser.add_argument('--scenario', choices=list_scenarios(), required=True)
    parser.add_argument('--episodes', type=int, default=5)
    parser.add_argument('--visible', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    spec = get_scenario_spec(args.scenario)
    if spec.pipeline != 'teacher_bc_ppo':
        raise ValueError(f'scenario={args.scenario} uses {spec.pipeline}, teacher is not the recommended entrypoint')

    env = make_env(args.scenario, visible=args.visible)
    teacher = ScenarioTeacherPolicy(args.scenario)
    teacher.bind_action_names(env.action_names)
    print(f'running teacher for scenario={spec.name} title={spec.title} strategy={spec.training_strategy}')
    try:
        for episode in range(args.episodes):
            teacher.reset()
            obs, _ = env.reset()
            done = False
            total_reward = 0.0
            steps = 0
            last_action = 0
            while not done:
                action = teacher.predict(obs)
                obs, reward, terminated, truncated, _ = env.step(action)
                total_reward += reward
                done = terminated or truncated
                steps += 1
                last_action = action
                if args.visible:
                    env.render()
            print(f'episode={episode + 1} steps={steps} reward={total_reward:.2f} last_action={env.action_names[last_action]}')
    finally:
        env.close()


if __name__ == '__main__':
    main()

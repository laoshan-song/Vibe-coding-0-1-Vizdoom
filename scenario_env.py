import argparse
from collections import deque

import cv2
import gymnasium as gym
import numpy as np
import vizdoom as zd
from gymnasium import spaces

from scenario_catalog import get_scenario_spec, list_scenarios


ACTION_PROFILES = {
    'strafe_attack_3': [
        ('MOVE_LEFT',),
        ('MOVE_RIGHT',),
        ('ATTACK',),
    ],
    'turn_attack_3': [
        ('TURN_LEFT',),
        ('TURN_RIGHT',),
        ('ATTACK',),
    ],
    'dodge_2': [
        ('MOVE_LEFT',),
        ('MOVE_RIGHT',),
    ],
    'turn_move_3': [
        ('TURN_LEFT',),
        ('TURN_RIGHT',),
        ('MOVE_FORWARD',),
    ],
    'nav_5': [
        ('TURN_LEFT',),
        ('TURN_RIGHT',),
        ('MOVE_FORWARD',),
        ('MOVE_LEFT',),
        ('MOVE_RIGHT',),
    ],
    'arena_7': [
        ('TURN_LEFT',),
        ('TURN_RIGHT',),
        ('MOVE_FORWARD',),
        ('MOVE_BACKWARD',),
        ('MOVE_LEFT',),
        ('MOVE_RIGHT',),
        ('ATTACK',),
    ],
}

PICKUP_LABELS = {
    'ArmorBonus', 'Stimpack', 'Medikit', 'ClipBox', 'Clip', 'RocketBox', 'RocketAmmo',
    'CellPack', 'Cell', 'ShellBox', 'Shell', 'Backpack', 'GreenArmor', 'BlueArmor'
}
IGNORED_LABELS = {'DoomPlayer', 'MarineChainsawVzd'}


class ScenarioVizDoomEnv(gym.Env):
    metadata = {'render_modes': ['human'], 'render_fps': 35}

    def __init__(
        self,
        scenario: str,
        visible: bool = False,
        frame_skip: int = 4,
        history: int = 4,
        frame_size: tuple[int, int] = (84, 84),
        living_bonus: float = 0.01,
        aim_bonus: float = 0.2,
        center_threshold: float = 0.1,
        attack_align_bonus: float = 0.5,
        attack_miss_penalty: float = 0.1,
        move_align_bonus: float = 0.2,
        health_loss_penalty: float = 0.2,
    ):
        super().__init__()
        self.spec = get_scenario_spec(scenario)
        self.scenario = scenario
        self.visible = visible
        self.frame_skip = frame_skip
        self.history = history
        self.frame_size = frame_size
        self.living_bonus = living_bonus
        self.aim_bonus = aim_bonus
        self.center_threshold = center_threshold
        self.attack_align_bonus = attack_align_bonus
        self.attack_miss_penalty = attack_miss_penalty
        self.move_align_bonus = move_align_bonus
        self.health_loss_penalty = health_loss_penalty
        self.window_name = f'ViZDoom {scenario}'

        self.action_definitions = ACTION_PROFILES[self.spec.action_profile]
        self.action_names = ['+'.join(combo) for combo in self.action_definitions]
        self.action_space = spaces.Discrete(len(self.action_definitions))

        self.single_obs_size = 6
        if self.spec.observation_mode == 'structured':
            self.observation_space = spaces.Box(
                low=-1.0,
                high=1.0,
                shape=(self.single_obs_size * history,),
                dtype=np.float32,
            )
        else:
            self.observation_space = spaces.Box(
                low=0,
                high=255,
                shape=(history, frame_size[0], frame_size[1]),
                dtype=np.uint8,
            )

        self.game = None
        self.action_vectors = None
        self.state_history = deque(maxlen=history)
        self.last_health = 100.0
        self.last_ammo = 0.0

    def _init_game(self):
        if self.game is not None:
            return
        game = zd.DoomGame()
        game.load_config(zd.scenarios_path + f'/{self.scenario}.cfg')
        game.set_window_visible(self.visible)
        game.set_sound_enabled(False)
        game.set_labels_buffer_enabled(True)
        game.init()
        self.game = game
        self.action_vectors = self._build_action_vectors()

    def _build_action_vectors(self):
        available = [button.name for button in self.game.get_available_buttons()]
        vectors = []
        for combo in self.action_definitions:
            vector = [0] * len(available)
            for button_name in combo:
                if button_name in available:
                    vector[available.index(button_name)] = 1
            vectors.append(vector)
        return vectors

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._init_game()
        self.game.new_episode()
        obs = self._extract_observation()
        self.state_history.clear()
        for _ in range(self.history):
            self.state_history.append(obs.copy())
        self.last_health = self._normalized_var(self.spec.health_var, 100.0, 100.0)
        self.last_ammo = self._normalized_var(self.spec.ammo_var, 0.0, 50.0)
        return self._stacked_obs(), self._info(obs)

    def step(self, action):
        raw_reward = float(self.game.make_action(self.action_vectors[int(action)], self.frame_skip))
        done = self.game.is_episode_finished()
        if done:
            obs = self._zero_obs()
            self.state_history.append(obs)
            return self._stacked_obs(), float(raw_reward - 1.0), True, False, self._info(obs, raw_reward)

        obs = self._extract_observation()
        self.state_history.append(obs)
        reward = self._shape_reward(obs, int(action), raw_reward)
        self.last_health = self._normalized_var(self.spec.health_var, self.last_health, 100.0)
        self.last_ammo = self._normalized_var(self.spec.ammo_var, self.last_ammo, 50.0)
        return self._stacked_obs(), float(reward), False, False, self._info(obs, raw_reward)

    def _zero_obs(self):
        if self.spec.observation_mode == 'structured':
            return np.zeros(self.single_obs_size, dtype=np.float32)
        return np.zeros(self.frame_size, dtype=np.uint8)

    def _stacked_obs(self):
        if self.spec.observation_mode == 'structured':
            return np.concatenate(list(self.state_history), dtype=np.float32)
        return np.stack(list(self.state_history), axis=0).astype(np.uint8)

    def _extract_observation(self):
        if self.spec.observation_mode == 'structured':
            return self._extract_structured_features()
        return self._extract_frame()

    def _extract_frame(self):
        state = self.game.get_state()
        if state is None:
            return self._zero_obs()
        frame = np.transpose(state.screen_buffer, (1, 2, 0))
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        resized = cv2.resize(gray, self.frame_size, interpolation=cv2.INTER_AREA)
        return resized.astype(np.uint8)

    def _normalized_var(self, name, default, scale):
        if name is None:
            return 0.0
        state = self.game.get_state()
        if state is None:
            return default
        values = state.game_variables
        for variable, value in zip(self.game.get_available_game_variables(), values):
            if variable.name == name:
                return float(np.clip(float(value) / scale, 0.0, 1.0))
        return default

    def _extract_structured_features(self):
        state = self.game.get_state()
        if state is None:
            return np.zeros(self.single_obs_size, dtype=np.float32)

        target = self._find_target(state)
        screen_w = state.screen_buffer.shape[2]
        visible = 1.0 if target is not None else 0.0
        if target is not None:
            center_x = target.x + target.width / 2.0
            x_offset = (center_x / screen_w) * 2.0 - 1.0
            width_ratio = target.width / screen_w
        else:
            x_offset = 0.0
            width_ratio = 0.0

        ammo = self._normalized_var(self.spec.ammo_var, 0.0, 50.0)
        health = self._normalized_var(self.spec.health_var, 1.0, 100.0)
        centered = 1.0 if visible > 0.5 and abs(x_offset) < self.center_threshold else 0.0
        return np.array([visible, x_offset, width_ratio, ammo, health, centered], dtype=np.float32)

    def _find_target(self, state):
        labels = getattr(state, 'labels', None)
        if not labels:
            return None
        if self.spec.target_labels:
            candidates = [lab for lab in labels if lab.object_name in self.spec.target_labels]
        elif self.spec.family in {'combat', 'dodge'}:
            candidates = [
                lab for lab in labels
                if lab.object_name not in IGNORED_LABELS and lab.object_name not in PICKUP_LABELS
            ]
        elif self.spec.family == 'collect':
            candidates = [lab for lab in labels if lab.object_name == 'Medikit']
        else:
            candidates = []
        if not candidates:
            return None
        return max(candidates, key=lambda lab: lab.width * lab.height)

    def _shape_reward(self, obs, action, raw_reward):
        if self.spec.observation_mode != 'structured':
            health = self._normalized_var(self.spec.health_var, self.last_health, 100.0)
            reward = raw_reward + self.living_bonus
            if health < self.last_health:
                reward += (health - self.last_health) * self.health_loss_penalty
            return reward

        visible, x_offset, width_ratio, ammo, health, centered = obs.tolist()
        reward = raw_reward + self.living_bonus
        action_name = self.action_names[action]
        if visible > 0.5:
            reward += self.aim_bonus * max(0.0, 1.0 - abs(x_offset))
        if 'ATTACK' in action_name:
            if centered > 0.5:
                reward += self.attack_align_bonus
            elif ammo < self.last_ammo:
                reward -= self.attack_miss_penalty
        if 'MOVE_FORWARD' in action_name and centered > 0.5:
            reward += self.move_align_bonus
        if health < self.last_health:
            reward += (health - self.last_health) * self.health_loss_penalty
        return reward

    def _info(self, obs, raw_reward=0.0):
        if self.spec.observation_mode == 'structured':
            return {
                'raw_reward': float(raw_reward),
                'visible': float(obs[0]),
                'x_offset': float(obs[1]),
                'target_width': float(obs[2]),
                'ammo_norm': float(obs[3]),
                'health_norm': float(obs[4]),
                'centered': float(obs[5]),
            }
        return {'raw_reward': float(raw_reward)}

    def render(self):
        if self.game is None or self.game.get_state() is None:
            return
        frame = np.transpose(self.game.get_state().screen_buffer, (1, 2, 0))
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_resized = cv2.resize(frame_bgr, (960, 720), interpolation=cv2.INTER_NEAREST)
        cv2.imshow(self.window_name, frame_resized)
        cv2.waitKey(1)

    def close(self):
        if self.game is not None:
            self.game.close()
            self.game = None
        cv2.destroyAllWindows()


def make_env(scenario: str, **kwargs):
    return ScenarioVizDoomEnv(scenario=scenario, **kwargs)


def parse_args():
    parser = argparse.ArgumentParser(description='Smoke test a scenario-specific ViZDoom environment.')
    parser.add_argument('--scenario', choices=list_scenarios(), required=True)
    parser.add_argument('--episodes', type=int, default=3)
    parser.add_argument('--visible', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    env = make_env(args.scenario, visible=args.visible)
    print(f'smoke testing scenario={args.scenario} obs_mode={env.spec.observation_mode} actions={env.action_names}')
    try:
        for episode in range(args.episodes):
            obs, _ = env.reset()
            done = False
            total_reward = 0.0
            while not done:
                action = env.action_space.sample()
                obs, reward, terminated, truncated, _ = env.step(action)
                total_reward += reward
                done = terminated or truncated
                if args.visible:
                    env.render()
            print(f'episode={episode + 1} total_reward={total_reward:.2f}')
    finally:
        env.close()


if __name__ == '__main__':
    main()

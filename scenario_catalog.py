from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ScenarioSpec:
    name: str
    title: str
    family: str
    difficulty: str
    observation_mode: str
    pipeline: str
    action_profile: str
    description: str
    training_strategy: str
    target_labels: tuple[str, ...] = ()
    ammo_var: str | None = None
    health_var: str | None = 'HEALTH'


DEFAULT_TIMESTEPS = {
    'simpler_basic': 200000,
    'basic': 300000,
    'basic_audio': 300000,
    'basic_notifications': 300000,
    'rocket_basic': 300000,
    'learning': 300000,
    'defend_the_center': 300000,
    'defend_the_line': 300000,
    'predict_position': 300000,
    'take_cover': 200000,
    'health_gathering': 300000,
    'health_gathering_supreme': 500000,
    'my_way_home': 500000,
    'deadly_corridor': 500000,
    'cig': 1000000,
    'deathmatch': 1000000,
    'multi': 1000000,
    'multi_duel': 300000,
    'doom': 1000000,
    'doom2': 1000000,
    'freedoom1': 1000000,
    'freedoom2': 1000000,
    'oblige': 1000000,
}


SCENARIOS = {
    'basic': ScenarioSpec('basic', '基础左右移动射击', 'combat', 'starter', 'structured', 'teacher_bc_ppo', 'strafe_attack_3', '最经典入门场景，左右移动并开火。', '先学左右对齐和开火，再用 PPO 微调。', ('Cacodemon', 'DoomPlayer'), 'AMMO2', None),
    'basic_audio': ScenarioSpec('basic_audio', '带音频提示的基础射击', 'combat', 'starter', 'structured', 'teacher_bc_ppo', 'strafe_attack_3', '基础射击的音频版本。', '沿用 basic 的左右移动射击路线。', ('Cacodemon', 'DoomPlayer'), 'AMMO2', None),
    'basic_notifications': ScenarioSpec('basic_notifications', '带通知的基础射击', 'combat', 'starter', 'structured', 'teacher_bc_ppo', 'strafe_attack_3', '基础射击的通知版本。', '沿用 basic 的左右移动射击路线。', ('Cacodemon', 'DoomPlayer'), 'AMMO2', None),
    'simpler_basic': ScenarioSpec('simpler_basic', '更简单的基础射击', 'combat', 'starter', 'structured', 'teacher_bc_ppo', 'strafe_attack_3', '比 basic 更简单的射击入门场景。', '作为最轻量的射击热身场景。', ('Cacodemon', 'DoomPlayer'), 'AMMO2', None),
    'rocket_basic': ScenarioSpec('rocket_basic', '火箭版基础射击', 'combat', 'intermediate', 'structured', 'teacher_bc_ppo', 'strafe_attack_3', '仍是左右移动开火，但武器反馈不同。', '先学对齐，再处理更强武器反馈。', (), 'AMMO2', None),
    'learning': ScenarioSpec('learning', '学习版基础射击', 'combat', 'starter', 'structured', 'teacher_bc_ppo', 'strafe_attack_3', '与 basic 同类的学习场景。', '和 basic 共用入门射击策略。', ('Cacodemon', 'DoomPlayer'), 'AMMO2', None),
    'defend_the_center': ScenarioSpec('defend_the_center', '中心防守', 'combat', 'starter', 'structured', 'teacher_bc_ppo', 'turn_attack_3', '站桩防守，转向并开火。', '当前主线场景，先 BC 再 PPO。', ('DoomPlayer',), 'AMMO2', 'HEALTH'),
    'defend_the_line': ScenarioSpec('defend_the_line', '防守一条线', 'combat', 'intermediate', 'structured', 'teacher_bc_ppo', 'turn_attack_3', '比 defend_the_center 更强调正面持续防守。', '复用中心防守打法，但需要更稳。', ('DoomPlayer',), 'AMMO2', 'HEALTH'),
    'predict_position': ScenarioSpec('predict_position', '位置预测射击', 'combat', 'intermediate', 'structured', 'teacher_bc_ppo', 'turn_attack_3', '转向并预判目标位置。', '用结构化瞄准特征先学稳定开火。', ('DoomPlayer',), 'AMMO2', 'HEALTH'),
    'take_cover': ScenarioSpec('take_cover', '左右躲避', 'dodge', 'starter', 'structured', 'teacher_bc_ppo', 'dodge_2', '只有左右移动，目标是躲避攻击。', '先学看到敌人后反向躲避。', ('DoomImp',), None, 'HEALTH'),
    'health_gathering': ScenarioSpec('health_gathering', '捡血包生存', 'collect', 'intermediate', 'structured', 'teacher_bc_ppo', 'turn_move_3', '转向并向血包移动维持生命。', '把 Medikit 当作目标，先找再冲过去。', ('Medikit',), None, 'HEALTH'),
    'health_gathering_supreme': ScenarioSpec('health_gathering_supreme', '高强度捡血包生存', 'collect', 'advanced', 'structured', 'teacher_bc_ppo', 'turn_move_3', '更难的捡血包生存环境。', '在 health_gathering 基础上拉长训练。', ('Medikit',), None, 'HEALTH'),
    'my_way_home': ScenarioSpec('my_way_home', '回家导航', 'navigation', 'intermediate', 'visual', 'ppo_only', 'nav_5', '经典导航场景，没有现成标签目标。', '使用视觉 PPO，先学朝路口前进。', (), None, None),
    'deadly_corridor': ScenarioSpec('deadly_corridor', '致命走廊', 'combat', 'advanced', 'visual', 'ppo_only', 'arena_7', '需要移动、转向、开火和承受压力。', '建议直接用视觉 PPO 长时间训练。', (), None, 'HEALTH'),
    'cig': ScenarioSpec('cig', '竞赛战斗场景', 'combat', 'expert', 'visual', 'ppo_only', 'arena_7', '复杂战斗和导航混合。', '先用 PPO 打基础，不建议新手首发。', (), None, None),
    'deathmatch': ScenarioSpec('deathmatch', '死亡竞赛', 'combat', 'expert', 'visual', 'ppo_only', 'arena_7', '多目标高复杂战斗。', '先建立可运行 PPO baseline，再谈扩展武器策略。', (), 'SELECTED_WEAPON_AMMO', 'HEALTH'),
    'multi': ScenarioSpec('multi', '多人战斗', 'combat', 'expert', 'visual', 'ppo_only', 'arena_7', '多人版本战斗场景。', '先用单策略 PPO 跑通，再扩展。', (), 'AMMO3', 'HEALTH'),
    'multi_duel': ScenarioSpec('multi_duel', '多人决斗', 'combat', 'intermediate', 'structured', 'teacher_bc_ppo', 'strafe_attack_3', '小动作空间的对战场景。', '作为 basic 向对战扩展的过渡。', (), None, None),
    'doom': ScenarioSpec('doom', 'Doom 完整游戏', 'full_game', 'expert', 'visual', 'ppo_only', 'arena_7', '完整 Doom 游戏基线配置。', '建议只做 PPO baseline，不要一开始追求通关。', (), None, None),
    'doom2': ScenarioSpec('doom2', 'Doom II 完整游戏', 'full_game', 'expert', 'visual', 'ppo_only', 'arena_7', '完整 Doom II 游戏基线配置。', '和 doom 一样，先做可运行 baseline。', (), None, None),
    'freedoom1': ScenarioSpec('freedoom1', 'Freedoom Phase 1', 'full_game', 'expert', 'visual', 'ppo_only', 'arena_7', 'Freedoom 版本完整游戏。', '适合作为开源完整战役 PPO baseline。', (), None, None),
    'freedoom2': ScenarioSpec('freedoom2', 'Freedoom Phase 2', 'full_game', 'expert', 'visual', 'ppo_only', 'arena_7', 'Freedoom 第二阶段完整游戏。', '和 freedoom1 类似，先做可运行基线。', (), None, None),
    'oblige': ScenarioSpec('oblige', 'Oblige 随机关卡', 'full_game', 'expert', 'visual', 'ppo_only', 'arena_7', '更偏随机和泛化的完整地图。', '用视觉 PPO 做泛化实验。', (), None, 'HEALTH'),
}


LEARNING_PATH = [
    'simpler_basic',
    'basic',
    'defend_the_center',
    'defend_the_line',
    'health_gathering',
    'health_gathering_supreme',
    'my_way_home',
    'deadly_corridor',
    'cig',
    'deathmatch',
]


def get_default_timesteps(name: str) -> int:
    return DEFAULT_TIMESTEPS.get(name, 300000)


def get_scenario_spec(name: str) -> ScenarioSpec:
    if name not in SCENARIOS:
        valid = ', '.join(sorted(SCENARIOS))
        raise ValueError(f'unknown scenario={name!r}, expected one of: {valid}')
    return SCENARIOS[name]


def list_scenarios() -> list[str]:
    return list(SCENARIOS)


def scenario_artifact_dir(name: str) -> Path:
    return PROJECT_ROOT / 'artifacts' / 'scenarios' / name


def default_demo_path(name: str) -> Path:
    return scenario_artifact_dir(name) / 'demos_teacher.npz'


def default_bc_path(name: str) -> Path:
    return scenario_artifact_dir(name) / 'bc_agent.pt'


def default_ppo_path(name: str) -> Path:
    return scenario_artifact_dir(name) / 'ppo_model.zip'


def default_checkpoint_dir(name: str) -> Path:
    return scenario_artifact_dir(name) / 'checkpoints'


def default_log_dir(name: str) -> Path:
    return scenario_artifact_dir(name) / 'ppo_logs'

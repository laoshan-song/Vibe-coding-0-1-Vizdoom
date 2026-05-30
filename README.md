# ViZDoom Scenarios Project

这是一个按 ViZDoom 自带场景拆开的教学项目，面向刚接触 ViZDoom、强化学习、模仿学习的初学者。项目核心目标不是先讲大量理论，而是让你尽快跑通训练、看懂行为，并逐步做出自己的 Doom AI。

当前主入口只有一套：`scenarios/`。你平时最常见的使用方式就是进入某个场景目录，直接运行里面的 `train.py` 和 `play.py`。

## 快速开始

```bash
cd /home/laoshansong/vizdoom_project
source venv/bin/activate
cd scenarios/basic
python train.py
python play.py --agent ppo
```

如果你还没有虚拟环境，可以先执行：

```bash
cd /home/laoshansong/vizdoom_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 项目结构

```text
/home/laoshansong/vizdoom_project
├── venv/                    # Python 虚拟环境
├── scenarios/               # 你平时真正进入的地方
│   ├── basic/
│   │   ├── train.py
│   │   ├── play.py
│   │   ├── model_path.txt
│   │   └── README.md
│   └── ...
├── artifacts/scenarios/     # 训练后生成的模型、日志、演示数据
└── scenario_*.py            # 公共底层
```

根目录公共脚本包括：

- [scenario_catalog.py](./scenario_catalog.py)
- [scenario_env.py](./scenario_env.py)
- [scenario_teacher.py](./scenario_teacher.py)
- [scenario_collect.py](./scenario_collect.py)
- [scenario_bc.py](./scenario_bc.py)
- [scenario_train.py](./scenario_train.py)
- [scenario_play.py](./scenario_play.py)
- [scenario_pipeline.py](./scenario_pipeline.py)
- [scenario_model.py](./scenario_model.py)
- [scenarios/README.md](./scenarios/README.md)

## 你应该怎么使用这个项目

建议按下面顺序：

1. 先读这份根目录 `README.md`
2. 再看 [scenarios/README.md](./scenarios/README.md)
3. 然后进入某个场景目录，只和以下四个文件打交道：
   - `train.py`
   - `play.py`
   - `model_path.txt`
   - `README.md`

这个项目刻意采用“每个场景一个文件夹”的方式，目的是让初学者不需要先理解全部公共脚本，就能开始训练和回放。

## 这个项目在做什么

项目目标是在 ViZDoom 自带场景中训练出自己的 Doom AI，并按教学难度逐步推进：

- 先从动作简单的场景开始
- 先学最基础的能力，比如左右移动、对准、开火
- 再学搜索、跟踪、生存
- 最后进入更复杂的视觉导航和复杂战斗

ViZDoom 本质上是 Doom 游戏的 AI 实验环境。它允许程序反复执行这样一个循环：

```text
看到状态 -> 选择动作 -> 执行动作 -> 得到奖励 -> 进入下一步
```

## 两条训练路线

### 1. 结构化场景路线

适合：`simpler_basic`、`basic`、`defend_the_center`、`defend_the_line`、`health_gathering`、`take_cover`

特点：

- 动作空间较小
- 目标清楚
- 可以手写教师策略
- 适合先模仿再强化学习

完整流程：

```text
教师策略 -> 演示采集 -> BC -> PPO
```

### 2. 视觉 PPO 路线

适合：`my_way_home`、`deadly_corridor`、`cig`、`deathmatch`、`doom`

特点：

- 目标难以手写规则
- 动作更复杂
- 更依赖视觉和时序能力

完整流程：

```text
视觉输入 -> PPO
```

## 核心算法怎么理解

### Q-Learning

核心问题是：在状态 `s` 下，动作 `a` 值不值得做。它学习的是 `Q(s, a)`，也就是某动作的长期价值。

### DQN

可以理解为：

```text
Q-Learning + 神经网络
```

它是很经典的入门方法，但在复杂 Doom 纯视觉任务里通常偏慢、偏难调。

### BC

`Behavior Cloning`，行为克隆。本质是监督学习：

- 输入状态
- 标签是教师动作
- 输出预测动作

在这个项目里，BC 的主要价值是给 PPO 做热启动。

### PPO

`Proximal Policy Optimization`，这个项目真正承担主训练任务的算法。最直观的理解是：

```text
每次更新策略时，不要改得太猛，稳定一点，慢慢变好
```

### 教师策略和演示采集

教师策略不是神经网络，而是手写规则。比如在 `basic` 里：

```text
目标在左边 -> 向左移动
目标在右边 -> 向右移动
基本对准 -> 开火
```

教师运行时留下 `(状态, 动作)` 数据，后续会被用于 BC 训练。

## 为什么这个项目不把 DQN 作为主线

因为项目目标不是方法纯度，而是尽快让新手做出一个真的会行动的 Doom 模型。

对这个目标来说，纯视觉 DQN 常见问题是：

- 学得慢
- 难调
- 难 debug
- 新手长时间看不到正反馈

所以这里采用：

- 简单场景先走结构化路线
- 更复杂场景再走视觉 PPO

## 推荐学习路线

建议按下面顺序推进：

1. `simpler_basic`
2. `basic`
3. `defend_the_center`
4. `defend_the_line`
5. `health_gathering`
6. `my_way_home`
7. `deadly_corridor`
8. `deathmatch`

压缩成一句话就是：先学瞄准和开火，再学搜索和防守，再学生存和找路，最后再学复杂战斗。

### 场景通关标准

- `simpler_basic`：不再随机乱动，开始明显朝目标修正
- `basic`：能左右修正并在对准后开火
- `defend_the_center`：会搜索、转向，并在中心区域稳定攻击
- `defend_the_line`：比 `defend_the_center` 更稳，不容易乱晃
- `health_gathering`：会朝资源移动，而不是在危险中原地耗死
- `my_way_home`：不再只是撞墙和打转，而是出现连续探索路径
- `deadly_corridor`：行为已经有连续战斗和移动意图
- `deathmatch`：至少形成基本可持续行动，而不是彻底随机

## 第一次真正上手该怎么做

### 1. 先跑 `basic`

```bash
cd /home/laoshansong/vizdoom_project/scenarios/basic
python train.py
```

这一步通常会触发：

```text
Teacher -> Demo Collection -> BC -> PPO
```

训练完成后回放：

```bash
python play.py --agent ppo
```

### 2. 回放时观察什么

第一次回放，不要只盯着分数，更重要的是看行为：

- 会不会朝目标方向修正
- 会不会在正确时机开火
- 会不会比随机动作更像有意图地行动

如果是导航场景，重点看：

- 会不会一直撞墙
- 会不会持续朝某个方向探索
- 会不会比随机走路更像在找路

## 训练流程图

### 结构化场景

```text
进入场景目录
   |
   v
python train.py
   |
   +--> 教师策略跑场景
   +--> 保存演示数据
   +--> BC 学老师
   +--> PPO 继续强化学习
   `--> 保存最终模型
```

### 视觉场景

```text
进入场景目录
   |
   v
python train.py --timesteps 500000
   |
   +--> 直接创建视觉 PPO
   +--> 与环境交互训练
   `--> 保存最终模型
```

## `play.py` 和 `model_path.txt` 的作用

最常见的回放命令：

```bash
python play.py --agent ppo
```

对于支持教师和 BC 的结构化场景，也可以：

```bash
python play.py --agent teacher
python play.py --agent bc
```

你可以这样理解：

```text
teacher = 规则老师
bc      = 学老师的学生
ppo     = 继续自己练过的学生
```

`model_path.txt` 不是模型本体，而是说明默认模型路径的文件。`play.py` 会根据它去找模型；第一次训练前，这个路径对应的模型文件可能还不存在。

## 常见调参入口

如果你只想调参，不想碰公共底层，通常只需要在场景目录里工作。最常见的杠杆是：

- `timesteps`
- 结构化场景里的奖励设计
- 结构化场景里的教师规则
- PPO 的学习率
- PPO 的探索强度，例如 `ent_coef`

常见命令：

```bash
python train.py --timesteps 500000
python ../../scenario_pipeline.py --scenario basic --val-split 0.1 --patience 3
python ../../scenario_pipeline.py --scenario basic --stage train --resume ../../artifacts/scenarios/basic/checkpoints/basic_ppo_50000_steps.zip
python play.py --agent ppo
```

根目录的 `scenario_pipeline.py` 支持完整流程参数透传：`--val-split` 和 `--patience` 会传给 BC 训练，`--resume` 会传给 PPO 继续训练。未显式设置 `--timesteps` 时，项目会按场景难度使用默认训练步数。

## Vibe Coding：怎么让 AI 帮你写 RL 代码

在这个项目里，你最该投入精力的是：

- 设计规则
- 设计奖励
- 设计目标
- 调参和观察行为

最适合让 AI 帮你的，不是“把整个 RL 项目重写一遍”，而是这些局部任务：

### 1. 写 Teacher 策略

示例 Prompt：

> 我正在用 ViZDoom 做 `health_gathering` 场景。游戏状态包含玩家血量和周围物品的相对坐标。请帮我写一段 Python 规则代码（Teacher Policy），逻辑是：优先向距离最近的急救包移动，如果血量低于 20 则全速前进。只输出动作选择逻辑即可。

### 2. 设计 Reward Shaping

示例 Prompt：

> 我的 PPO 模型在 `my_way_home` 场景里总是原地转圈。目前奖励只有找到终点给 `+100`，其余是 `0`。请帮我设计一个密集奖励函数，比如根据距离终点远近给小奖励，并提供具体的数学映射逻辑。

### 3. 解释报错

遇到 `train.py` 崩溃、环境初始化失败、shape 对不上时，把完整 traceback 和你刚改的那几行代码一起发给 AI，并要求它优先判断是路径问题、shape 问题还是逻辑问题。

### 4. 正确的协作姿势

不要说：

```text
帮我做一个最强 Doom AI
```

更有效的说法是：

```text
帮我改这一小段规则
帮我设计这一小段奖励
帮我解释这个具体报错
帮我分析这个模型为什么原地打转
```

一句话原则：让 AI 解决局部问题，不要让 AI 接管整个项目方向。

### 5. 可直接复用的 Prompt 模板

```text
我在做 ViZDoom 的 <场景名> 场景。
当前文件是 <train.py / play.py / 教师规则文件 / 奖励函数位置>。
我现在的输入状态有：<列出状态变量>。
动作空间有：<列出动作>。
当前问题是：<原地打转 / 撞墙 / 乱开火 / 奖励不涨 / shape 报错>。
请你只帮我修改：<教师动作逻辑 / reward shaping / 某个报错定位 / 某一段参数建议>。
不要重写整个项目，只给出可以直接粘贴的 Python 逻辑和修改原因。
```

## Vibe Debug：模型变傻时怎么排查

### 症状 1：原地转圈或一直撞墙

可能原因：

- 探索不够
- 陷入局部最优
- 重复某种暂时不会受罚的无意义动作

排查方向：适当调大探索强度，例如 `ent_coef`。

### 症状 2：对着空气疯狂开火

可能原因：奖励函数被钻空子了。

排查方向：

- 检查是否奖励了“开火”却没有惩罚“乱开火”
- 增加“开火但未命中”的惩罚

### 症状 3：BC 回放很好，一进 PPO 就崩

可能原因：

- PPO 学习率过大
- 更新太猛，忘掉了老师动作

排查方向：

- 先把学习率从例如 `3e-4` 降到 `1e-4`
- 缩短 PPO 总训练步数，观察是不是后期崩盘

### 症状 4：reward 在涨，但回放看起来还是很蠢

可能原因：reward 奖励的不是你真正想要的行为，而是某个可被钻空子的近似指标。

一句话原则：先怀疑奖励设计和调参，再怀疑算法本身。

推荐排查顺序：

```text
先看回放行为
   ->
再查奖励是不是在奖励错误动作
   ->
再查探索强度够不够
   ->
再查学习率是不是太大
   ->
最后才考虑要不要换算法
```

## 设计原则

- 每个场景一个文件夹
- 每个场景文件夹只暴露最少入口
- 初学者不需要先理解公共脚本再开始训练
- 结构化场景走 `teacher -> demos -> BC -> PPO`
- 更复杂或无标签场景直接走视觉 `PPO`

## 常见误区

- 不要一上来就练 `deathmatch`
- 不要一上来就要求像人一样打 Doom
- 不要模型一蠢就立刻换算法
- 先跑通一个简单场景，再升级

## 最后只记这一句也可以

```bash
cd /home/laoshansong/vizdoom_project/scenarios/<某个场景>
python train.py
python play.py --agent ppo
```

先从 `basic` 开始，不要跳级。

# Doom 完整游戏

场景名：`doom`

- 难度：`expert`
- 类型：`full_game`
- 观测方式：`visual`
- 推荐路线：`ppo_only`
- 默认动作抽象：`arena_7`

## 这是什么场景

完整 Doom 游戏基线配置。

## 这个场景主要在练什么

这个场景主要训练：长时序探索、战斗、生存和泛化能力。

建议只做 PPO baseline，不要一开始追求通关。

这个场景主要靠视觉 PPO 自己试错，训练时间通常要更长。

## 这个文件夹里有什么

- `train.py`：训练入口，尽量让你只跑一个命令就开始训练
- `play.py`：回放入口，用来观察 teacher / bc / ppo 的行为
- `model_path.txt`：默认模型保存位置说明
- `README.md`：这个场景的教学说明

## 你应该怎么跑

### 1. 训练

```bash
python train.py --timesteps 500000
```

这条命令背后默认走的是：

```text
Visual Observation -> PPO
```

### 2. 回放

```bash
python play.py --agent ppo
```

这个场景可用的回放模式：

```bash
python play.py --agent ppo
```

## 新手先看这三件事

- 先跑 `python train.py`，不要先改底层公共脚本。
- 再跑 `python play.py --agent ppo`，先看行为是不是有明确意图。
- 最后才开始调 `timesteps`、奖励、teacher 逻辑或 PPO 参数。

## 训练流程图

```text
进入 doom/
   |
   v
运行 train.py
   |
   v
保存模型到 artifacts/scenarios/doom/ppo_model.zip
   |
   v
运行 play.py 观察行为
```

## 你在这个场景里应该重点观察什么

这个场景更多依赖整体视觉或生存目标，不一定有单一标签目标。

建议重点看：

- 会不会维持连续行动，而不是频繁卡死
- 会不会在探索、战斗和生存之间出现基本切换
- 是否至少形成可重复的 baseline 行为

## 什么时候算“过关”

Vibe Check：已经形成可重复的完整流程 baseline，而不是开局就乱走乱撞。

如果你连续回放几局都能看到类似倾向，就说明这个场景已经开始学对了。

## 模型变笨时先改什么

- 先不要追求通关，先追求稳定可运行 baseline。
- 如果长时间训练仍完全随机，先缩小目标，只看能否形成持续移动和基本战斗。
- 这类场景优先加大 timesteps，而不是一开始频繁改模型结构。

## 推荐调参方向

- 先优先调整 `--timesteps`，这是最通用也最不容易改坏的杠杆。
- 视觉场景先追求形成连续探索或战斗行为，再追求更高分。
- 如果回放明显退化，优先先缩小改动范围，一次只改一个因素。

## 下一步去哪

如果你已经打到这里，下一步更适合开始做你自己的 reward shaping、teacher 规则或 PPO 长训练实验。

## 模型文件说明

默认模型路径见 [`model_path.txt`](/home/laoshansong/vizdoom_project/scenarios/doom/model_path.txt)。
如果当前还没有模型文件，先运行 `train.py`。

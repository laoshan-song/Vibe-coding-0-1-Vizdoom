# 回家导航

场景名：`my_way_home`

- 难度：`intermediate`
- 类型：`navigation`
- 观测方式：`visual`
- 推荐路线：`ppo_only`
- 默认动作抽象：`nav_5`

## 这是什么场景

经典导航场景，没有现成标签目标。

## 这个场景主要在练什么

这个场景主要训练：连续探索、避墙和路径保持。

使用视觉 PPO，先学朝路口前进。

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
进入 my_way_home/
   |
   v
运行 train.py
   |
   v
保存模型到 artifacts/scenarios/my_way_home/ppo_model.zip
   |
   v
运行 play.py 观察行为
```

## 你在这个场景里应该重点观察什么

这个场景更多依赖整体视觉或生存目标，不一定有单一标签目标。

建议重点看：

- 会不会长期撞墙或原地打转
- 会不会形成连续的探索方向，而不是每步都乱变
- 是否出现像“找出口”而不是“随机游走”的路径

## 什么时候算“过关”

Vibe Check：不再只是撞墙和打转，开始出现连续探索路径。

如果你连续回放几局都能看到类似倾向，就说明这个场景已经开始学对了。

## 模型变笨时先改什么

- 如果原地打转，先增加探索强度或延长训练步数。
- 如果 reward 在涨但行为很蠢，优先怀疑 reward shaping 被钻空子了。
- 如果一直撞墙，先把“远离墙面”或“朝目标区域前进”的密集奖励设计得更清楚。

## 推荐调参方向

- 先优先调整 `--timesteps`，这是最通用也最不容易改坏的杠杆。
- 视觉场景先追求形成连续探索或战斗行为，再追求更高分。
- 如果回放明显退化，优先先缩小改动范围，一次只改一个因素。

## 下一步去哪

推荐下一站：[`deadly_corridor`](/home/laoshansong/vizdoom_project/scenarios/deadly_corridor/README.md)

## 模型文件说明

默认模型路径见 [`model_path.txt`](/home/laoshansong/vizdoom_project/scenarios/my_way_home/model_path.txt)。
如果当前还没有模型文件，先运行 `train.py`。

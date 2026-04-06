# 多人决斗

场景名：`multi_duel`

- 难度：`intermediate`
- 类型：`combat`
- 观测方式：`structured`
- 推荐路线：`teacher_bc_ppo`
- 默认动作抽象：`strafe_attack_3`

## 这是什么场景

小动作空间的对战场景。

## 这个场景主要在练什么

这个场景主要训练：瞄准、转向、射击节奏和持续战斗意图。

作为 basic 向对战扩展的过渡。

这个场景适合先用规则老师把方向带出来，再让 PPO 微调。

## 这个文件夹里有什么

- `train.py`：训练入口，尽量让你只跑一个命令就开始训练
- `play.py`：回放入口，用来观察 teacher / bc / ppo 的行为
- `model_path.txt`：默认模型保存位置说明
- `README.md`：这个场景的教学说明

## 你应该怎么跑

### 1. 训练

```bash
python train.py
```

这条命令背后默认走的是：

```text
Teacher -> Demo Collection -> BC -> PPO
```

### 2. 回放

```bash
python play.py --agent ppo
```

这个场景可用的回放模式：

```bash
python play.py --agent teacher
python play.py --agent bc
python play.py --agent ppo
```

## 新手先看这三件事

- 先跑 `python train.py`，不要先改底层公共脚本。
- 再跑 `python play.py --agent ppo`，先看行为是不是有明确意图。
- 最后才开始调 `timesteps`、奖励、teacher 逻辑或 PPO 参数。

## 训练流程图

```text
进入 multi_duel/
   |
   v
运行 train.py
   |
   v
保存模型到 artifacts/scenarios/multi_duel/ppo_model.zip
   |
   v
运行 play.py 观察行为
```

## 你在这个场景里应该重点观察什么

这个场景更多依赖整体视觉或生存目标，不一定有单一标签目标。

建议重点看：

- 会不会先转向目标，再出手，而不是乱打
- 会不会出现连续几步都朝着同一个战斗目标修正
- 攻击时机是否比随机策略更像“看到了再打”

## 什么时候算“过关”

Vibe Check：会在对战环境里做基础瞄准和出手，不再像纯随机策略。

如果你连续回放几局都能看到类似倾向，就说明这个场景已经开始学对了。

## 模型变笨时先改什么

- 如果乱开火，先检查奖励里有没有“未命中扣分”或“浪费子弹扣分”。
- 如果只是来回晃，先增加训练时长，再看探索强度是不是太低。
- 如果 BC 很好但 PPO 一接手就崩，先减小 PPO 学习率。

## 推荐调参方向

- 先优先调整 `--timesteps`，这是最通用也最不容易改坏的杠杆。
- 结构化场景先保证 teacher 和 BC 路线能跑顺，再谈 PPO 微调。
- 如果回放明显退化，优先先缩小改动范围，一次只改一个因素。

## 下一步去哪

如果你已经打到这里，下一步更适合开始做你自己的 reward shaping、teacher 规则或 PPO 长训练实验。

## 模型文件说明

默认模型路径见 [`model_path.txt`](/home/laoshansong/vizdoom_project/scenarios/multi_duel/model_path.txt)。
如果当前还没有模型文件，先运行 `train.py`。

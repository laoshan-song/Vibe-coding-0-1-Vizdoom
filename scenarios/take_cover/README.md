# 左右躲避

场景名：`take_cover`

- 难度：`starter`
- 类型：`dodge`
- 观测方式：`structured`
- 推荐路线：`teacher_bc_ppo`
- 默认动作抽象：`dodge_2`

## 这是什么场景

只有左右移动，目标是躲避攻击。

## 这个场景主要在练什么

这个场景主要训练：危险感知和及时躲避。

先学看到敌人后反向躲避。

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
进入 take_cover/
   |
   v
运行 train.py
   |
   v
保存模型到 artifacts/scenarios/take_cover/ppo_model.zip
   |
   v
运行 play.py 观察行为
```

## 你在这个场景里应该重点观察什么

教师或奖励里经常会围绕这些目标对象做设计：`DoomImp`。

建议重点看：

- 看到危险后会不会及时横向移动
- 会不会为了躲避而持续保持位移
- 行为是否比静止挨打更像主动保命

## 什么时候算“过关”

Vibe Check：看到危险后会明显侧移，减少站桩挨打。

如果你连续回放几局都能看到类似倾向，就说明这个场景已经开始学对了。

## 模型变笨时先改什么

- 如果经常不躲，先确认奖励是否真的鼓励“减少受伤”。
- 如果左右横跳但没生存提升，说明策略只学到了动作，不知道什么时候该躲。
- 优先先把 teacher 规则训顺，再延长 PPO。

## 推荐调参方向

- 先优先调整 `--timesteps`，这是最通用也最不容易改坏的杠杆。
- 结构化场景先保证 teacher 和 BC 路线能跑顺，再谈 PPO 微调。
- 如果回放明显退化，优先先缩小改动范围，一次只改一个因素。

## 下一步去哪

如果你已经打到这里，下一步更适合开始做你自己的 reward shaping、teacher 规则或 PPO 长训练实验。

## 模型文件说明

默认模型路径见 [`model_path.txt`](/home/laoshansong/vizdoom_project/scenarios/take_cover/model_path.txt)。
如果当前还没有模型文件，先运行 `train.py`。

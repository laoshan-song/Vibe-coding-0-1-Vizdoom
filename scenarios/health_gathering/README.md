# 捡血包生存

场景名：`health_gathering`

- 难度：`intermediate`
- 类型：`collect`
- 观测方式：`structured`
- 推荐路线：`teacher_bc_ppo`
- 默认动作抽象：`turn_move_3`

## 这是什么场景

转向并向血包移动维持生命。

## 这个场景主要在练什么

这个场景主要训练：资源搜索、目标靠近和生存决策。

把 Medikit 当作目标，先找再冲过去。

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
进入 health_gathering/
   |
   v
运行 train.py
   |
   v
保存模型到 artifacts/scenarios/health_gathering/ppo_model.zip
   |
   v
运行 play.py 观察行为
```

## 你在这个场景里应该重点观察什么

教师或奖励里经常会围绕这些目标对象做设计：`Medikit`。

建议重点看：

- 会不会主动朝资源方向靠近，而不是瞎逛
- 丢失目标后会不会继续搜索，而不是卡住
- 在压力下是否还能持续移动并维持生存

## 什么时候算“过关”

Vibe Check：会主动找血包，并在压力下继续靠近资源。

如果你连续回放几局都能看到类似倾向，就说明这个场景已经开始学对了。

## 模型变笨时先改什么

- 如果只会乱跑，先看奖励是不是把“活着”奖励过大而把“接近资源”奖励做得太弱。
- 如果站着不动，先提高探索强度，再检查目标方向特征是否真的输入进去了。
- 如果会看见资源却不靠近，优先重写 teacher 规则或距离奖励。

## 推荐调参方向

- 先优先调整 `--timesteps`，这是最通用也最不容易改坏的杠杆。
- 结构化场景先保证 teacher 和 BC 路线能跑顺，再谈 PPO 微调。
- 如果回放明显退化，优先先缩小改动范围，一次只改一个因素。

## 下一步去哪

推荐下一站：[`health_gathering_supreme`](/home/laoshansong/vizdoom_project/scenarios/health_gathering_supreme/README.md)

## 模型文件说明

默认模型路径见 [`model_path.txt`](/home/laoshansong/vizdoom_project/scenarios/health_gathering/model_path.txt)。
如果当前还没有模型文件，先运行 `train.py`。

# ViZDoom 场景化教学总教程

这份教程面向完全不懂 ViZDoom、强化学习、模仿学习的人。目标不是让你先读很多理论，而是让你先能跑、能看懂、能调参、能逐步做出自己的 Doom AI。

现在这个项目已经完全改成“每个场景一个文件夹”的形式。你以后最常见的工作方式就是：

```bash
cd /home/laoshansong/vizdoom_project/scenarios/<场景名>
python train.py
python play.py --agent ppo
```

如果你是第一次接触这个项目，建议先完整读完这份文档，再去跑 `basic`。

## 1. 这个项目到底在做什么

这个项目的目标，是让你在 ViZDoom 自带场景中训练出自己的 Doom AI 模型。

但这里不会一开始就让你挑战最复杂场景，而是按教学思路来：

- 先从动作简单的场景开始
- 先学会最基础的能力，比如左右移动、对准、开火
- 再学搜索、跟踪、生存
- 最后再进入更复杂的视觉导航和复杂战斗

## 2. 你现在到底在哪个环境里运行

这个项目默认工作目录是：

```text
/home/laoshansong/vizdoom_project
```

最常用的几个位置：

```text
项目根目录:
/home/laoshansong/vizdoom_project

虚拟环境:
/home/laoshansong/vizdoom_project/venv

场景目录:
/home/laoshansong/vizdoom_project/scenarios

训练产物目录:
/home/laoshansong/vizdoom_project/artifacts/scenarios
```

可以把它想象成下面这棵树：

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
└── scenario_*.py            # 公共底层，不建议新手一开始就改
```

建议的运行方式：

```bash
cd /home/laoshansong/vizdoom_project
source venv/bin/activate
cd scenarios/basic
python train.py
```

也就是说：先在项目根目录激活环境，再进入具体场景目录，只和这个目录里的 `train.py` / `play.py` 打交道。

## 3. ViZDoom 是什么

ViZDoom 是 Doom 游戏的 AI 实验环境。它允许程序：

- 读到游戏状态
- 输出动作
- 获得奖励
- 在固定场景中反复训练

最核心的循环就是：

```text
看到状态 -> 选择动作 -> 执行动作 -> 得到奖励 -> 进入下一步
```

## 4. 这个项目为什么分成两条路线

### 4.1 结构化场景路线

适合：`simpler_basic`、`basic`、`defend_the_center`、`defend_the_line`、`health_gathering`、`take_cover` 这类场景。

特点：

- 动作空间较小
- 目标清楚
- 能写启发式教师策略
- 适合先模仿再强化学习

路线是：

```text
教师策略 -> 演示采集 -> BC -> PPO
```

### 4.2 视觉 PPO 路线

适合：`my_way_home`、`deadly_corridor`、`cig`、`deathmatch`、`doom` 这类更复杂场景。

特点：

- 目标难以手写规则
- 动作更复杂
- 更依赖视觉和时序能力

路线是：

```text
视觉输入 -> PPO
```

## 5. 你需要知道的核心算法

### 5.1 Q-Learning 是什么

Q-Learning 的核心问题是：

```text
在状态 s 下，动作 a 到底值不值得做？
```

它学习的是：

```text
Q(s, a)
```

也就是“在这个状态下，这个动作的长期价值分数”。

优点：

- 思路直观
- 很适合教学入门

问题：

- 状态空间一大就很难做
- 图像输入时几乎无法直接用表格法

### 5.2 DQN 是什么

DQN 就是：

```text
Q-Learning + 神经网络
```

它不再直接存 Q 表，而是让神经网络输入状态、输出每个动作的 Q 值。

典型组件：

- `Experience Replay`
- `Target Network`
- `Epsilon-Greedy`

优点：

- 非常经典
- 离散动作问题里概念很清晰

问题：

- 样本效率不高
- 训练容易不稳
- 在复杂 Doom 纯视觉任务里通常很慢

### 5.3 为什么这个项目不把 DQN 作为主线

因为这个项目的目标不是方法纯度，而是：

```text
尽快让新手做出一个真的会做事的 Doom 模型
```

对这个目标来说，纯视觉 DQN 的主要问题是：

- 学得慢
- 难调
- 难 debug
- 新手很长时间看不到正反馈

所以这里选择：

- 简单场景先走结构化路线
- 更复杂场景再走视觉 PPO

### 5.4 BC 是什么

BC 是 `Behavior Cloning`，行为克隆。

它本质上是监督学习：

- 输入：状态
- 标签：教师动作
- 输出：预测动作

你可以把它理解成：

```text
学老师怎么做
```

在这个项目里，BC 的价值主要是作为 PPO 的热启动。

### 5.5 PPO 是什么

PPO 是 `Proximal Policy Optimization`。

最直观的理解是：

```text
每次更新策略时，不要改得太猛，稳定一点，慢慢变好
```

这也是它在工程上很常用的原因：

- 比较稳
- 泛用性强
- 适合从简单到复杂逐步扩展

### 5.6 教师策略和演示采集是什么

教师策略不是神经网络，而是手写规则。

例如在 `basic` 场景里，它可能会做这种事：

```text
目标在左边 -> 向左移动
目标在右边 -> 向右移动
基本对准 -> 开火
```

教师跑游戏时留下 `(状态, 动作)` 数据，这些数据会被保存下来，供 BC 训练。

### 5.7 这几个算法在本项目里分别扮演什么角色

```text
Q-Learning  = 帮你理解“动作价值”这个思想
DQN         = 帮你理解“神经网络怎么学动作价值”
BC          = 先把学生训练得像老师
PPO         = 再让学生自己通过试错变强
```

如果你是零基础，最实用的记忆方式不是死背公式，而是记住：

- `Q-Learning` 和 `DQN` 更适合拿来建立概念
- `BC` 适合做热启动
- `PPO` 是这个项目真正承担主训练任务的算法

## 6. Vibe Coding 秘籍：如何让 AI 帮你写 RL 代码

这个项目里，你不需要手写所有神经网络结构和 PPO 细节。底层框架已经有了。你真正最该投入精力的，是：

- 设计规则
- 设计奖励
- 设计目标
- 调参和观察行为

也就是俗称的“炼丹”。

当你开发一个新场景，或者想把某个场景训得更好时，最适合让 AI 帮你的，不是“把整个 RL 项目重写一遍”，而是下面这几类明确任务。

### 6.1 让 AI 帮你写 Teacher 策略

适用场景：结构化场景，或者你已经能定义清楚目标和动作时。

Prompt 示例：

> 我正在用 ViZDoom 做 `health_gathering` 场景。游戏状态包含玩家血量和周围物品的相对坐标。请帮我写一段 Python 规则代码（Teacher Policy），逻辑是：优先向距离最近的急救包移动，如果血量低于 20 则全速前进。只输出动作选择逻辑即可。

使用技巧：

- 先说清楚场景名
- 再说清楚你手上有哪些状态变量
- 再说清楚动作空间
- 最后限制 AI 只输出某一小段逻辑，不要让它改整个项目

### 6.2 让 AI 帮你设计 Reward Shaping

适用场景：PPO 能跑，但行为很蠢，或者 reward 太稀疏时。

Prompt 示例：

> 我的 PPO 模型在 `my_way_home` 场景里总是原地转圈。目前奖励只有找到终点给 `+100`，其余是 `0`。请帮我设计一个密集奖励（Dense Reward）函数，比如根据距离终点远近给小奖励，并提供具体的数学映射逻辑。

使用技巧：

- 说清楚当前 reward 是什么
- 说清楚当前模型表现出了什么坏行为
- 让 AI 输出“可执行的 reward 逻辑”，不要只输出空泛建议

### 6.3 让 AI 帮你解释报错

适用场景：`train.py` 崩掉、环境初始化失败、shape 对不上等。

做法很直接：

- 把完整 traceback 贴给 AI
- 再贴你刚刚改动的那几行代码
- 最后补一句“请优先判断是路径问题、shape 问题还是逻辑问题”

这样 AI 才更容易给出有用定位，而不是泛泛而谈。

### 6.4 Vibe Coding 的正确姿势

最有效的协作方式不是：

```text
“帮我做一个最强 Doom AI。”
```

而是：

```text
“帮我改这一小段规则。”
“帮我设计这一小段奖励。”
“帮我解释这个具体报错。”
“帮我分析这个模型为什么原地打转。”
```

一句话原则：

```text
让 AI 解决局部问题，不要让 AI 接管整个项目方向。
```

### 6.5 可以直接复制的 Vibe Prompt 模板

当你不知道怎么开口问 AI 时，直接套这个模板：

```text
我在做 ViZDoom 的 <场景名> 场景。
当前文件是 <train.py / play.py / 教师规则文件 / 奖励函数位置>。
我现在的输入状态有：<列出状态变量>。
动作空间有：<列出动作>。
当前问题是：<原地打转 / 撞墙 / 乱开火 / 奖励不涨 / shape 报错>。
请你只帮我修改：<教师动作逻辑 / reward shaping / 某个报错定位 / 某一段参数建议>。
不要重写整个项目，只给出可以直接粘贴的 Python 逻辑和修改原因。
```

这样问的好处是：

- AI 不容易发散
- 输出更接近可直接运行的代码
- 你更容易知道自己到底改了哪一层

## 7. 推荐学习路线

建议先按这条主线走，不要一开始分太多支线：

1. `simpler_basic`
2. `basic`
3. `defend_the_center`
4. `defend_the_line`
5. `health_gathering`
6. `my_way_home`
7. `deadly_corridor`
8. `deathmatch`

原因很简单：

- 前面先学基础动作
- 中间学跟踪和生存
- 后面再碰复杂视觉和复杂战斗

如果你只想记一版最短路线，就记这一句：

```text
先学“瞄准和开火”，再学“搜索和防守”，再学“生存和找路”，最后再学“复杂战斗”。
```

### 场景通关的 Vibe Check

- `simpler_basic`
  过关标准：模型不再随机乱动，已经有明显朝目标修正的倾向。
- `basic`
  过关标准：能明显左右修正并在对准后开火。
- `defend_the_center`
  过关标准：会搜索、会转向、会在中心区域稳定攻击。
- `defend_the_line`
  过关标准：比 `defend_the_center` 更稳，不容易乱晃。
- `health_gathering`
  过关标准：会朝资源移动，而不是在危险中原地耗死。
- `my_way_home`
  过关标准：不再只是撞墙和打转，而是出现连续探索路径。
- `deadly_corridor`
  过关标准：行为看起来已经有连续战斗和移动意图。
- `deathmatch`
  过关标准：至少形成基本的可持续行动，不是彻底随机。

你可以把这条路线压缩理解成四个关卡：

```text
第 1 关：simpler_basic / basic
学会瞄准、修正方向、正确开火

第 2 关：defend_the_center / defend_the_line
学会搜索目标、连续攻击、保持相对稳定

第 3 关：health_gathering / my_way_home
学会资源导向、生存、导航探索

第 4 关：deadly_corridor / deathmatch
学会在复杂视觉和战斗压力下持续行动
```

## 8. 第一次真正上手，你应该怎么做

### 8.1 安装环境

```bash
cd /home/laoshansong/vizdoom_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

如果你已经有现成 `venv/`，就不用重复创建。

### 8.2 跑 `basic`

```bash
cd /home/laoshansong/vizdoom_project/scenarios/basic
python train.py
```

这一步你实际触发的是：

```text
Teacher -> Demo Collection -> BC -> PPO
```

训练完成后回放：

```bash
python play.py --agent ppo
```

### 8.3 你应该观察什么

第一次回放模型时，不要只盯着“分数高不高”。更重要的是看行为：

- 会不会朝目标方向修正
- 会不会在正确时机开火
- 会不会比随机动作更像有意图地行动

## 9. 给新手的视觉辅助：训练流程图

### 9.1 结构化场景

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

### 9.2 视觉场景

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

## 10. 给新手的视觉辅助：你在看什么

### 10.1 训练时

你看到的通常是：

```text
iterations / timesteps / fps / reward
```

含义是：

- `timesteps`：模型已经和环境交互了多少步
- `reward`：当前表现大致怎么样
- `fps`：训练速度

### 10.2 回放时

你应该问自己：

```text
这个模型是随机乱动，还是有明显目标地行动？
```

如果是结构化射击场景，重点看：

- 看到敌人了吗
- 对准了吗
- 开火时机对吗

如果是导航场景，重点看：

- 会不会一直撞墙
- 会不会持续朝某个方向探索
- 会不会比随机走路更像在找路

## 11. 遇到模型变智障怎么办？Vibe Debug 指南

在运行 `python play.py --agent ppo` 时，如果你的模型表现得像个傻子，不要马上怀疑 PPO 算法错了。先按症状判断。

### 症状 1：模型只会原地转圈，或者一直往墙上撞

直觉诊断：

- 探索不够
- 陷入局部最优
- 模型偶然发现某种无意义动作不会立刻受罚，于是一直重复

Vibe 疗法：

- 去训练脚本里找熵相关参数，比如 `ent_coef` 或你自己定义的探索强度
- 稍微调大一点，比如从 `0.01` 调到 `0.05`
- 让它被迫多做一些随机探索

### 症状 2：在结构化场景里，对着空气疯狂开火

直觉诊断：

- 奖励函数被钻空子了
- 你奖励了“开火”，但没惩罚“乱开火”

Vibe 疗法：

- 重看奖励设计
- 增加惩罚项，例如：开火且未命中 `-1`
- 重新检查是否有“打偏扣分”或“浪费子弹扣分”

### 症状 3：BC 阶段回放很好，一进 PPO 阶段就崩盘

直觉诊断：

- PPO 学习率太大
- 更新太猛，忘掉了老师动作

Vibe 疗法：

- 把学习率调小，比如从 `3e-4` 降到 `1e-4`
- 先缩短 PPO 总训练步数，看看前期是不是正常
- 如果前期正常、后期崩，通常就是更新过头了

### 症状 4：reward 在涨，但回放看起来还是很蠢

直觉诊断：

- reward 不等于你真正想要的行为
- 模型可能在刷 reward 漏洞

Vibe 疗法：

- 回到环境奖励定义
- 问自己：这个 reward 到底奖励的是“真正的目标”，还是某个可被钻空子的近似指标？

一句话原则：

```text
先怀疑奖励设计和调参，再怀疑算法本身。
```

### 11.1 Vibe Debug 的排查顺序

新手最容易犯的错，是一看到模型表现差，就同时乱改 10 个参数。更好的顺序是：

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

换句话说：

- 先看行为
- 再看奖励
- 再看参数
- 最后才看算法

## 12. 每个场景目录里的 train.py 实际上帮你省了什么

很多项目会让新手自己记一堆命令：

- 先跑教师
- 再采样
- 再训练 BC
- 再训练 PPO
- 再回放

这个项目故意不让你记这么多。

对于结构化场景：

```text
python train.py
```

背后就自动帮你串起来了。

## 13. play.py 怎么用

最常见的是：

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

## 14. model_path.txt 是什么

这个文件不是模型本体，而是说明文件。

它会告诉你：

- 默认模型存在哪里
- 当前目录里的 `play.py` 默认会去哪读模型
- 如果你第一次训练，这个位置一开始可能还没有文件

## 15. 如果你只想调参，不想碰公共底层

你可以只在每个场景目录里工作，常见做法是：

```bash
python train.py --timesteps 500000
python play.py --agent ppo
```

最常见的调参杠杆：

- `timesteps`
- 结构化场景里的奖励设计
- 结构化场景里的教师规则
- PPO 的学习率和探索强度

## 16. 常见误区

- 不要一上来就练 `deathmatch`
- 不要一上来就要求像人一样打 Doom
- 不要模型一蠢就立刻换算法
- 先跑通一个简单场景，再升级

## 17. 一张总结图

```text
零基础上手
   |
   v
读总教程
   |
   v
进入 simpler_basic / basic
   |
   v
python train.py
   |
   v
python play.py --agent ppo
   |
   v
看懂模型在做什么
   |
   v
进入 defend_the_center / health_gathering
   |
   v
再进入 my_way_home / deadly_corridor
   |
   v
最后再碰 deathmatch / doom
```

## 18. 你只记住这一句也可以

```bash
cd /home/laoshansong/vizdoom_project/scenarios/<某个场景>
python train.py
python play.py --agent ppo
```

先从 `basic` 开始，不要跳级。

# Built-in Scenarios

这个目录按 ViZDoom 自带场景一一拆分。现在每个场景文件夹都尽量收敛成同一种结构：

- `train.py`
- `play.py`
- `model_path.txt`
- `README.md`

也就是说，你进入某个场景目录后，不需要再去猜这个场景应该调用哪个公共脚本。

## 推荐学习路径

1. `simpler_basic`：更简单的基础射击
2. `basic`：基础左右移动射击
3. `defend_the_center`：中心防守
4. `defend_the_line`：防守一条线
5. `health_gathering`：捡血包生存
6. `health_gathering_supreme`：高强度捡血包生存
7. `my_way_home`：回家导航
8. `deadly_corridor`：致命走廊
9. `cig`：竞赛战斗场景
10. `deathmatch`：死亡竞赛

## 使用方式

例如：

```bash
cd scenarios/basic
python train.py
python play.py --agent ppo
```

视觉导航场景：

```bash
cd scenarios/my_way_home
python train.py --timesteps 500000
python play.py --agent ppo
```

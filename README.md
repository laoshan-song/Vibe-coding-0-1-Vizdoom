# ViZDoom Scenarios Project

这是一个按 ViZDoom 自带场景拆开的教学项目。现在主入口只有一套：`scenarios/`。

## 你应该怎么用

1. 先看总教程：
   [VIZDOOM_PROJECT_GUIDE_ZH.md](/home/laoshansong/vizdoom_project/VIZDOOM_PROJECT_GUIDE_ZH.md)
2. 再看场景总览：
   [scenarios/README.md](/home/laoshansong/vizdoom_project/scenarios/README.md)
3. 然后进入某个场景目录，直接使用里面的四个文件：
   - `train.py`
   - `play.py`
   - `model_path.txt`
   - `README.md`

## 最短上手

```bash
cd /home/laoshansong/vizdoom_project
source venv/bin/activate
cd scenarios/basic
python train.py
python play.py --agent ppo
```

## 项目结构

当前项目只保留两层核心结构：

- 场景公共底层
  - [scenario_catalog.py](/home/laoshansong/vizdoom_project/scenario_catalog.py)
  - [scenario_env.py](/home/laoshansong/vizdoom_project/scenario_env.py)
  - [scenario_teacher.py](/home/laoshansong/vizdoom_project/scenario_teacher.py)
  - [scenario_collect.py](/home/laoshansong/vizdoom_project/scenario_collect.py)
  - [scenario_bc.py](/home/laoshansong/vizdoom_project/scenario_bc.py)
  - [scenario_train.py](/home/laoshansong/vizdoom_project/scenario_train.py)
  - [scenario_play.py](/home/laoshansong/vizdoom_project/scenario_play.py)
  - [scenario_pipeline.py](/home/laoshansong/vizdoom_project/scenario_pipeline.py)
  - [scenario_model.py](/home/laoshansong/vizdoom_project/scenario_model.py)
- 场景目录
  - [scenarios/README.md](/home/laoshansong/vizdoom_project/scenarios/README.md)
  - `scenarios/<scenario_name>/`

## 设计原则

- 每个场景一个文件夹
- 每个场景文件夹都只暴露最少入口
- 初学者不需要先理解公共脚本再开始训练
- 结构化场景走 `teacher -> demos -> BC -> PPO`
- 更复杂或无标签场景直接走视觉 `PPO`

# Raspberry Pi Robot Control

这是一个运行在树莓派机器人场景下的 Python 控制项目，主流程包括语音唤醒、离线语音识别、姿态识别、节奏识别和串口动作下发。

## 快速入口

- 项目说明：[docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)
- 全新树莓派环境配置教程：[docs/RASPBERRY_PI_SETUP.md](docs/RASPBERRY_PI_SETUP.md)
- 不同机器人适配清单：[docs/ROBOT_PORTING_CHECKLIST.md](docs/ROBOT_PORTING_CHECKLIST.md)
- 清理记录：[docs/CLEANUP_REPORT.md](docs/CLEANUP_REPORT.md)
- 主程序：[main.py](main.py)
- 动作分发：[action_neo.py](action_neo.py)

## 常用命令

```bash
python3 main.py
python3 speech_recog.py
python3 speech_train.py
python3 posture_recognition/static_recognition.py
python3 rhythm_train/rhythm_train.py
python3 scripts/capture_to_image_folder.py
```

旧版 README 已归档到 `archive/legacy/README_legacy.md`。

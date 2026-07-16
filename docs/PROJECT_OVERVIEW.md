# 项目说明文档

## 项目概览

本项目是运行在树莓派机器人场景下的 Python 控制程序，负责语音交互、姿态识别、节奏识别和动作下发。

核心流程是：程序监听唤醒词，录制用户语音，将语音转成文本，再根据配置匹配动作指令；部分指令会进入姿态识别或节奏识别模式，最终通过串口把动作命令发送给下位机。

## 当前目录结构

```text
.
├── main.py                         # 主入口，启动 Snowboy 热词监听
├── action_neo.py                   # 动作分发、串口通信、音频反馈
├── speech_recog.py                 # Vosk 离线语音识别
├── speech_train.py                 # 语音指令词维护脚本
├── speech_train.json               # 语音关键词到动作名的映射配置
├── rhythm_recog1.py                # 当前节奏识别实现
├── datapackage.py                  # 动作文件名到串口数据包的转换
├── config.py                       # 姿态识别器全局初始化
├── docs/                           # 项目说明、清理记录等文档
├── deployment/                     # 树莓派部署/自启动相关文件
├── archive/legacy/                 # 旧实验脚本、旧配置、旧节奏数据和备用 TFLite 姿态实现归档
├── scripts/                        # 辅助工具脚本
├── rhythm_train/                   # 节奏训练音频和训练脚本
├── posture_recognition/            # 姿态识别模块、模型和分类器输出
├── pipelines/                      # 异步推理管线
├── model/                          # Snowboy 热词模型和 Vosk 模型目录
├── resources/                      # 提示音、动作反馈音、歌曲资源
├── image/                          # 姿态图片采集/训练数据
├── include/ lib/ swig/             # Snowboy 头文件、库和 Python 绑定
└── temp_record/                    # 运行时临时录音目录，由代码自动创建
```

根目录保留了主程序直接引用的文件。文档、部署文件、旧脚本和工具脚本已经分离，避免入口目录继续膨胀。

## 运行流程

```text
main.py
  -> 初始化姿态识别器 config.initialize_pose_identifier()
  -> 加载 Snowboy 热词模型 model/YiFeng2025.pmdl
  -> snowboydecoder.HotwordDetector.start()
  -> 检测到唤醒词后录音
  -> speech_recog.py 使用 Vosk 做离线语音识别
  -> action_neo.py 根据 speech_train.json 匹配指令
  -> 执行姿态识别 / 节奏识别 / 连续语音动作控制
  -> datapackage.py 生成串口数据包
  -> /dev/ttyAMA0 以 115200 波特率下发给下位机
```

主入口是 [main.py](../main.py)。动作分发集中在 [action_neo.py](../action_neo.py)。

## 核心模块

| 文件/目录 | 作用 |
| --- | --- |
| [main.py](../main.py) | 程序入口，启动热词监听 |
| [snowboydecoder.py](../snowboydecoder.py) | Snowboy 热词检测和唤醒回调 |
| [speech_recog.py](../speech_recog.py) | 录音并使用 Vosk 做离线语音识别 |
| [action_neo.py](../action_neo.py) | 根据语音文本分发动作，播放提示音，发送串口命令 |
| [speech_train.json](../speech_train.json) | 语音关键词和动作名映射配置 |
| [speech_train.py](../speech_train.py) | 交互式维护语音指令词 |
| [posture_recognition/static_recognition.py](../posture_recognition/static_recognition.py) | 摄像头姿态识别 |
| [rhythm_recog1.py](../rhythm_recog1.py) | 录制音乐片段并识别节奏匹配结果 |
| [rhythm_train/rhythm_train.py](../rhythm_train/rhythm_train.py) | 根据训练音频生成节奏数据库 |
| [datapackage.py](../datapackage.py) | 将动作文件名转换为串口数据包 |
| [scripts/capture_to_image_folder.py](../scripts/capture_to_image_folder.py) | 姿态图片采集工具 |
| [deployment/killjoy.desktop](../deployment/killjoy.desktop) | 树莓派桌面自启动配置示例 |

## 功能说明

### 语音唤醒和识别

[main.py](../main.py) 使用 `model/YiFeng2025.pmdl` 作为 Snowboy 热词模型。唤醒后，程序调用 [speech_recog.py](../speech_recog.py) 录制音频，并使用 `vosk.Model("model")` 做离线识别。

识别过程会临时写入 `temp_record/temp.wav` 和 `result.txt`。这些都是运行产物，已经加入 `.gitignore`。

### 动作分发

[action_neo.py](../action_neo.py) 读取 [speech_train.json](../speech_train.json)，用识别文本匹配各动作的关键词列表。

匹配成功后按 `name` 字段进入对应流程：

- `pose_recognition`：进入姿态识别。
- `rhythm_recognition`：进入节奏识别。
- `speech_recognition`：进入连续语音动作控制。
- 其他动作：生成串口数据并下发。

### 姿态识别

[posture_recognition/static_recognition.py](../posture_recognition/static_recognition.py) 使用 MediaPipe Pose Landmarker 提取人体关键点，再用本地分类器识别姿态。

主要模型文件：

- `posture_recognition/models/pose_landmarker_heavy.task`
- `posture_recognition/output/YiFeng_pose_recognizer.pickle`

识别结果图会保存为 `last_result.jpg`，该文件属于运行产物。

### 节奏识别

[rhythm_recog1.py](../rhythm_recog1.py) 会录制一段音乐，使用 `librosa` 提取节拍，再和 `beatDatabase1.npy` 做 DTW 匹配，返回最接近的曲目。

[rhythm_train/rhythm_train.py](../rhythm_train/rhythm_train.py) 从 `rhythm_train/` 下的音频生成 `beatDatabase1.npy`，与识别脚本读取路径保持一致。

### 串口通信

动作最终通过 `/dev/ttyAMA0` 以 `115200` 波特率发送给下位机。[datapackage.py](../datapackage.py) 负责把 `.bin` 或 `.odr` 动作文件名转换为发送数据。

## 依赖环境

项目目前没有提供 `requirements.txt`。从源码看，主要依赖包括：

- `opencv-python`
- `numpy`
- `pandas`
- `mediapipe`
- `vosk`
- `pyaudio`
- `librosa`
- `dtw`
- `pyserial`
- Snowboy Python 绑定
- 系统音频播放工具：`mplayer`，部分代码会尝试 `ffplay`

树莓派运行时还需要摄像头、麦克风/USB 声卡、可用串口和下位机动作文件。

## 常用命令

启动主程序：

```bash
python3 main.py
```

测试语音识别：

```bash
python3 speech_recog.py
```

维护语音指令：

```bash
python3 speech_train.py
```

测试姿态识别：

```bash
python3 posture_recognition/static_recognition.py
```

重新生成节奏数据库：

```bash
python3 rhythm_train/rhythm_train.py
```

采集姿态训练图片：

```bash
python3 scripts/capture_to_image_folder.py
```

## 维护注意事项

- 当前 README 和部分源码注释存在中文编码显示异常，建议后续统一为 UTF-8。
- 全新树莓派系统部署时，先按 [RASPBERRY_PI_SETUP.md](./RASPBERRY_PI_SETUP.md) 配置环境。
- 换不同机器人时，先按 [ROBOT_PORTING_CHECKLIST.md](./ROBOT_PORTING_CHECKLIST.md) 检查热词模型、动作文件、姿态分类器、节奏数据库和部署路径；硬件连接不做调整。
- `speech_train.json` 是语音指令匹配的核心配置，新增动作时要同步准备音频资源和下位机动作文件。
- `rhythm_train/rhythm_train.py` 和 `rhythm_recog1.py` 已统一使用 `beatDatabase1.npy`。
- 临时录音、识别结果图、缓存文件和 IDE 文件已加入 `.gitignore`。
- 旧实验脚本已放入 `archive/legacy/`，不要作为主流程入口使用。
- `archive/legacy/tflite_pose/` 中的 `ml/` 和 `tracker/` 是旧的 TFLite MoveNet/PoseNet 姿态估计备用实现，当前主流程不依赖它们。

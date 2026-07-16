# 全新树莓派系统环境配置教程

本文用于在一台全新的树莓派系统中部署本项目。硬件连接方式保持现有项目默认方案，不在这里修改串口、摄像头、麦克风或下位机通信方案。

## 1. 系统准备

建议使用 Raspberry Pi OS 64-bit，首次启动后先完成系统更新：

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

重启后安装基础工具：

```bash
sudo apt install -y \
  git \
  vim \
  python3 \
  python3-venv \
  python3-pip \
  python3-dev \
  build-essential \
  cmake \
  pkg-config
```

## 2. 安装系统依赖

安装音频、OpenCV、PyAudio、MediaPipe/Vosk 常用底层依赖：

```bash
sudo apt install -y \
  mplayer \
  ffmpeg \
  portaudio19-dev \
  libasound2-dev \
  libatlas-base-dev \
  libopenblas-dev \
  liblapack-dev \
  libhdf5-dev \
  libffi-dev \
  libssl-dev \
  libjpeg-dev \
  libpng-dev \
  libtiff-dev \
  libavcodec-dev \
  libavformat-dev \
  libswscale-dev \
  libgtk-3-dev \
  python3-opencv
```

如果需要蓝牙音箱，并继续使用 `scripts/start.sh` 中的蓝牙连接逻辑，再安装：

```bash
sudo apt install -y bluetooth bluez pulseaudio-module-bluetooth
```

## 3. 获取项目代码

把项目放到树莓派桌面目录，示例路径：

```bash
cd /home/pi/Desktop
git clone <你的仓库地址> dancing_robot
cd dancing_robot
```

如果不是通过 git 获取，也可以直接把整理后的项目文件夹复制到：

```text
/home/pi/Desktop/dancing_robot
```

## 4. 创建 Python 虚拟环境

项目脚本默认虚拟环境路径是 `/home/pi/myenv`：

```bash
python3 -m venv /home/pi/myenv
source /home/pi/myenv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

## 5. 安装 Python 依赖

当前项目还没有 `requirements.txt`，先手动安装源码中用到的主要包：

```bash
pip install \
  numpy \
  pandas \
  opencv-python \
  mediapipe \
  vosk \
  pyaudio \
  librosa \
  dtw \
  pyserial
```

如果 `opencv-python` 在树莓派上安装慢或失败，优先使用系统包 `python3-opencv`，并跳过 pip 里的 `opencv-python`。

## 6. 确认模型和资源文件

以下文件/目录必须存在：

```text
model/YiFeng2025.pmdl
model/                         # Vosk 模型目录
posture_recognition/models/pose_landmarker_heavy.task
posture_recognition/output/YiFeng_pose_recognizer.pickle
beatDatabase1.npy
resources/
rhythm_train/
```

检查命令：

```bash
ls model/YiFeng2025.pmdl
ls posture_recognition/models/pose_landmarker_heavy.task
ls posture_recognition/output/YiFeng_pose_recognizer.pickle
ls beatDatabase1.npy
ls resources
```

## 7. Snowboy 运行文件

项目根目录需要 Snowboy 的 Python 扩展文件：

```text
_snowboydetect.so
snowboydecoder.py
```

检查：

```bash
ls _snowboydetect.so snowboydecoder.py
```

如果 `_snowboydetect.so` 与当前树莓派 Python 版本或系统架构不匹配，需要重新编译 Snowboy Python 绑定。项目中保留了 `include/`、`lib/`、`swig/` 和 `scripts/install_swig.sh`，但这一步通常比普通依赖安装更容易出问题，建议优先使用已验证可运行的 `.so`。

## 8. 音频播放检查

确认 `mplayer` 能播放提示音：

```bash
mplayer resources/ding.wav
mplayer resources/sorry.MP3
```

如果没有声音，先在系统音频设置中确认默认输出设备。使用蓝牙音箱时，先完成蓝牙配对和连接。

## 9. 摄像头检查

项目提供了摄像头测试脚本：

```bash
python3 scripts/test_cam.py
```

也可以运行姿态识别脚本：

```bash
python3 posture_recognition/static_recognition.py
```

如果没有图形界面或远程运行，`static_recognition.py` 默认会保存最后一帧结果到 `last_result.jpg`。

## 10. 语音识别检查

激活虚拟环境后运行：

```bash
source /home/pi/myenv/bin/activate
cd /home/pi/Desktop/dancing_robot
python3 speech_recog.py
```

它会录音并调用 Vosk 模型识别。失败时优先检查：

- 麦克风是否被系统识别。
- `pyaudio` 是否安装成功。
- `model/` 是否是有效 Vosk 模型目录。

## 11. 节奏数据库检查

重新生成节奏库：

```bash
source /home/pi/myenv/bin/activate
cd /home/pi/Desktop/dancing_robot
python3 rhythm_train/rhythm_train.py
```

成功后应生成或更新：

```text
beatDatabase1.npy
```

## 12. 启动主程序

```bash
source /home/pi/myenv/bin/activate
cd /home/pi/Desktop/dancing_robot
python3 main.py
```

主程序会播放启动提示音，初始化姿态识别器，然后进入 Snowboy 热词监听。

## 13. 配置开机自启动

项目已有示例：

```text
deployment/killjoy.desktop
scripts/start.sh
```

如果项目路径使用 `/home/pi/Desktop/dancing_robot`，虚拟环境使用 `/home/pi/myenv`，可以把 desktop 文件复制到自启动目录：

```bash
mkdir -p /home/pi/.config/autostart
cp deployment/killjoy.desktop /home/pi/.config/autostart/killjoy.desktop
```

然后检查 `deployment/killjoy.desktop` 里的启动脚本路径是否正确：

```text
Exec=lxterminal -e bash -c 'sudo bash /home/pi/Desktop/start.sh;$SHELL'
```

如果使用当前项目内的脚本，建议改为：

```text
Exec=lxterminal -e bash -c 'bash /home/pi/Desktop/dancing_robot/scripts/start.sh;$SHELL'
```

同时确认 `scripts/start.sh` 中项目路径和虚拟环境路径正确：

```bash
cd /home/pi/Desktop/dancing_robot
source /home/pi/myenv/bin/activate
python /home/pi/Desktop/dancing_robot/main.py
```

## 14. 最小验收清单

部署完成后按顺序跑：

```bash
source /home/pi/myenv/bin/activate
cd /home/pi/Desktop/dancing_robot
python3 speech_recog.py
python3 posture_recognition/static_recognition.py
python3 rhythm_train/rhythm_train.py
python3 main.py
```

四项都能运行，才算环境配置完成。

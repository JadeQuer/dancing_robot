import snowboydecoder
import signal
import os
import tensorflow as tf
import warnings
import sys

# 导入静态姿势识别器
from posture_recognition.static_recognition import StaticPostureIdentifier

path = "resources/ding.wav"
os.system('mplayer %s' % path)

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


warnings.filterwarnings("ignore")

# 初始化静态姿势识别器（全局变量）
try:
    print("初始化静态姿势识别器...")
    pose_identifier = StaticPostureIdentifier()
    print("静态姿势识别器初始化完成")
except Exception as e:
    print(f"初始化静态姿势识别器失败: {e}")
    pose_identifier = None
    
model = "model/killjoy.pmdl"

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.40)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=snowboydecoder.play_audio_file,
                interrupt_check=interrupt_callback,
                sleep_time=0.03)

detector.terminate()

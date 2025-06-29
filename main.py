import snowboydecoder
import signal
import os
import warnings
import sys
import config
import time

path = "resources/ding.wav"
os.system('mplayer %s' % path)

interrupted = False
first_time = True

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

warnings.filterwarnings("ignore")

config.initialize_pose_identifier()
    
model = "model/lansiluote.pmdl"

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.45)
detector.first_time = True
print('Listening... Press Ctrl+C to exit')

# main loop

detector.start(detected_callback=snowboydecoder.play_audio_file,
                interrupt_check=interrupt_callback,
                sleep_time=0.03)

detector.terminate()

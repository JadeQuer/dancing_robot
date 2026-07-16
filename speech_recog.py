import json
import os
import wave
import vosk
import pyaudio

model = vosk.Model("model")

rec = vosk.KaldiRecognizer(model, 16000)
rec.SetWords(True)
rec.SetPartialWords(True)

framerate = 16000
NUM_SAMPLES = 2000
TIME = 10
channels = 1
sampwidth = 2


# 录自己的音保存成wav文件,并保存到对应的文件夹下
# 注意rate=16K,录制时间可以自行调整
def save_wave_file(filename, data):
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()


def record(f, time=5):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=framerate,
        input=True,
        frames_per_buffer=NUM_SAMPLES,
    )
    my_buf = []
    count = 0
    os.system('mplayer %s' % './resources/ding.wav')
    print("开始录音")
    print("录音中({}s)".format(str(time)))
    while count < TIME * time:
        string_audio_data = stream.read(NUM_SAMPLES)
        my_buf.append(string_audio_data)
        count += 1
        print(".", end="", flush=True)
    os.system('mplayer %s' % './resources/dong.wav')
    print("录音结束")
    save_wave_file(f, my_buf)
    stream.close()


def speech_recog():
    record('./temp_record/temp.wav', time=3)
    vosk.SetLogLevel(-1)
    wf = wave.open("./temp_record/temp.wav", "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        exit(1)

    file = open("result.txt", "w+")
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            file.write(json.loads(rec.Result())['text'] + "\n\n")
    file.write(json.loads(rec.Result())['text'])
    file.close()
    f = open("result.txt")
    text = f.read().replace(' ', '')
    return text


if __name__ == '__main__':
    with open('speech.txt', 'a') as f:
    # 测试代码
        l = []
        text = speech_recog()
        while 1:
            l.append(text)
            print(l)
            text = speech_recog()
            f.write(text + '\n')
        

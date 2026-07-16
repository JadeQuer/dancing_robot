# rhythm_recog.py
import wave
from numpy.linalg import norm
from numpy import array
import librosa
import pyaudio
import numpy as np
import os
from dtw import dtw

framerate = 16000
NUM_SAMPLES = 2000
channels = 1
sampwidth = 2
TIME = 10  # 每次读取 NUM_SAMPLES 的次数上限（总时长 ≈ TIME * NUM_SAMPLES / framerate）

def save_wave_file(filename, data):
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()

def record_music(f, time=5):
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
    total_chunks = int(time * framerate / NUM_SAMPLES) + 1
    print("开始录音")
    print("录音中({}s)".format(str(time)))
    while count < total_chunks:
        string_audio_data = stream.read(NUM_SAMPLES)
        my_buf.append(string_audio_data)
        count += 1
        print(".", end="", flush=True)
    print("\n录音结束")
    save_wave_file(f, my_buf)
    stream.close()

def play_audio(audio_file):
    # 使用 ffplay（更可靠）或 mplayer
    if os.system('ffplay -nodisp -autoexit "%s" > /dev/null 2>&1' % audio_file) != 0:
        os.system('mplayer "%s" > /dev/null 2>&1' % audio_file)

def rhythm_recog():
    play_audio('resources/rhythm.MP3')
    record_music('./temp_record/song_temp.wav', time=13)
    play_audio('resources/finish.MP3')
    
    # 加载数据库
    all_data = np.load('beatDatabase1.npy', allow_pickle=True)
    beat_database = all_data.item()

    # 处理用户录音
    testAudio = "./temp_record/song_temp.wav"
    y, sr = librosa.load(testAudio, sr=framerate)
    tempo, beat_times = librosa.beat.beat_track(y=y, sr=sr, units='time')
    beat_times = np.array(beat_times)
    
    if len(beat_times) < 2:
        print("⚠️ 未检测到足够节拍，无法识别")
        return "未知", {}
        
    intervals = np.diff(beat_times)
    # 如果训练时做了归一化，这里也要做：
    # intervals = intervals / np.mean(intervals)
    
    x = intervals.reshape(-1, 1)

    compare_result = {}
    for songID in beat_database.keys():
        y_db = np.array(beat_database[songID])
        if len(y_db) < 2:
            continue
        # 如果训练时归一化了，这里不需要再除（因为已经存的是归一化后的）
        y_db = y_db.reshape(-1, 1)
        
        # DTW 比较
        dist, _, _, path = dtw(x, y_db, dist=lambda a, b: norm(a - b, ord=1))
        # 归一化距离（可选但推荐）
        dist_norm = dist / len(path[0])
        compare_result[songID] = dist_norm

    if not compare_result:
        return "未知", {}
        
    matched_song = min(compare_result, key=compare_result.get)
    print("识别结果为: " + matched_song)
    return matched_song, compare_result

if __name__ == '__main__':
    result, scores = rhythm_recog()
    play_audio("resources/index"+result) # 歌曲名称

    print("最终结果:", result)

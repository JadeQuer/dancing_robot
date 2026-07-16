import librosa
import os
import numpy as np

# 音乐文件夹路径
music_dir = 'rhythm_train/'  # 可改为 'songs/' 等
output_path = 'beatDatabase1.npy'

beat_database = {}

# 获取所有音频文件
for filename in os.listdir(music_dir):
    if filename.lower().endswith(('.wav', '.mp3', '.MP3')):
        filepath = os.path.join(music_dir, filename)
        print(f"处理: {filepath}")
        
        try:
            # 加载音频
            y, sr = librosa.load(filepath, sr=16000)  # 统一采样率
            
            # 提取节拍时间戳（单位：秒）—— 推荐！
            tempo, beat_times = librosa.beat.beat_track(y=y, sr=sr, units='time')
            
            # 保存节拍时间序列（单位：秒）
            beat_database[filename] = beat_times.tolist()  # 转为 list 更兼容
            
            print(f"  节拍数: {len(beat_times)}, 前5个: {beat_times[:5]}")
            
        except Exception as e:
            print(f"  ❌ 跳过 {filename}: {e}")

# 检查是否真的有数据
if not beat_database:
    raise ValueError("没有成功加载任何音频文件！请检查路径和格式。")

print(f"\n✅ 成功处理 {len(beat_database)} 首歌曲")
np.save(output_path, beat_database)
print(f"数据库已保存至: {output_path}")

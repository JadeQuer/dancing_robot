import os
import time
import json
import serial
from rhythm_recog import rhythm_recog
from speech_recog import speech_recog
from datapackage import DataPackageConverter
from posture_recognition.static_recognition import StaticPostureIdentifier
import config

pose_identifier = config.pose_identifier


# 初始化串口
def initialize_serial():
    try:
        ser = serial.Serial('/dev/ttyAMA0', 115200)
        if not ser.isOpen():
            ser.open()
        return ser
    except serial.SerialException:
        raise Exception("Failed to initialize serial connection.")


def play_audio(audio_file):
    os.system('mplayer -volume 200 %s' % audio_file)
    
# 保存局部变量到文件
def save_variable_to_file(value):
    with open('temp.txt', 'w') as file:
        file.write(str(value))


def action_neo(text):
    # 读取 speech_train.json 文件
    try:
        with open('speech_train.json', 'r', encoding='utf-8') as f:
            speech_data = json.load(f)
    except Exception as e:
        print(f"Error loading speech_train.json: {e}")
        return

    ser = initialize_serial()
    keyword = "" # 存储指令的name字段
    
    # 遍历 speech_train.json 检查是否有匹配的关键词
    for action, action_data in speech_data.items():
        # 跳过黑名单
        if action == "黑名单":
            continue
        
        # 检查 text 是否包含列表中的任一关键词
        for keyword_text in action_data["list"]:
            if keyword_text in text:
                # 找到匹配的关键词，使用对应的 name 值
                keyword = action_data["name"]
                print(f"找到关键词 '{keyword_text}'，对应动作 '{action}'，指令名称 '{keyword}'")
                break
        
        if keyword:  # 如果找到了关键词，退出外层循环
            break

    if not keyword:
        play_audio('resources/sorry.wav')
        
    else:
        # 姿态识别
        if keyword == "pose_recognition":            
            play_audio('resources/begin_pose.wav')
            play_audio('resources/dong.wav')
            
            while True:
                
                # 检查姿势识别器是否已成功初始化
                global pose_identifier
                if pose_identifier is None:
                    print("姿势识别器未初始化，尝试重新初始化...")
                    try:
                        pose_identifier = StaticPostureIdentifier()
                    except Exception as e:
                        print(f"初始化姿势识别器失败: {e}")
                        play_audio('resources/sorry.wav')
                        return
                
                # 使用初始化好的识别器实例
                print("请在摄像头前保持姿势...")
                # 调用静态姿势识别函数
                pose = pose_identifier.recognize_posture(camera_index=0, timeout=15, stable_duration=2.0, display=True)
                
                
                if pose is None:
                    play_audio('resources/timeout.wav')
                    break
                
                if pose == "stop":
                    play_audio('resources/stop.wav')
                    break
            
                play_audio(pose + ".wav")
                send_bytes = DataPackageConverter(pose + ".bin").hex_output
                send_serial_data(ser, send_bytes)

        # 韵律识别
        elif keyword == "rhythm_recognition":
            play_audio("resources/yunlv.wav")
            matched_song, compare_result = rhythm_recog()
            play_audio("index/"+matched_song) # 歌曲名称
            if matched_song == "choice.MP3":
                movements = DataPackageConverter("choice.odr").hex_output
            else:
                movements = DataPackageConverter("dance.odr").hex_output
            ser.write(bytearray(movements)) # 执行动作
            play_audio(matched_song) # 播放歌曲
        
        # 自选动作
        else:
            audio_file = keyword + ".wav"
            send_bytes = DataPackageConverter(keyword + ".bin").hex_output
            play_audio(audio_file)
            send_serial_data(ser, send_bytes)

        if ser and ser.isOpen():
            ser.close()
            



def send_serial_data(ser, data):
    ser.write(bytearray(data))
    while True:
        size = ser.inWaiting()  # 获得缓冲区字符
        if size != 0:
            res = ser.read(size)  # 读取内容并显示
            print(res)
            ser.flushInput()  # 情况接收缓存区
            if res == b'\xff\x00\x05\x05\x00\x00\x18"' or res == b'\xff\x00\x05\x05\x00\x00\x19"':
                break
            time.sleep(0.5)  # 软件延时
            


if __name__ == '__main__':
    # 测试代码
    while True:
        order = int(input("请输入指令:0:退出 1:voice 2:keyboard"))
        if order == 0:
            break
        elif order == 1:
            print("请说出指令...")
            text = speech_recog()
            action_neo(text)
        elif order == 2:
            text = input()
            action_neo(text)

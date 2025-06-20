import os
import time
import json
import serial
from speech_recog import speech_recog
from datapackage import DataPackageConverter
import cv2


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
        play_audio('resources/sorry.MP3')
        
    else:
        if keyword == "检测机体状态":            
            play_audio("resources/0.MP3")
            for i in range(1,8):
                if i >=1 and i <= 4:
                    movements = DataPackageConverter(f"{i}.bin").hex_output
                    send_serial_data(ser, movements)
                #play_audio(f"resources/music{i}.wav") #音效
                play_audio(f"resources/{i}.MP3") #解说
        
        elif keyword == "检测环境":
            cap = cv2.VideoCapture(0)
            time.sleep(3)  
            play_audio("resources/stone.MP3")
            time.sleep(3)
            play_audio("resources/sand.MP3")
            cap.release()
            play_audio("resources/plan.MP3")
        # 自选动作
        else:
            if keyword == "fenli1":
                send_bytes = DataPackageConverter(keyword + ".bin").hex_output
            else:
                send_bytes = DataPackageConverter(keyword + ".odr").hex_output
            send_serial_data(ser, send_bytes)
            #play_audio("resources/music" + keyword + ".wav") #音效
            if keyword != "plan":
                play_audio("resources/" + keyword + ".MP3") #解说

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

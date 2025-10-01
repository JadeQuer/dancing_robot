import os
import time
import json
import serial
from speech_recog import speech_recog
from datapackage import DataPackageConverter
import cv2
from test_cam import find_camera
import sys


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
    if "关机" in text:
        os.system("sudo shutdown -h now")
        return
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
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open("word.txt", "a", encoding="utf-8") as f:
            f.write(f"[{current_time}] 识别失败的词汇: {text}\n")
            f.flush()  # 强制刷新缓冲区
        
    else:
        if keyword == "评估机体状态":            
            play_audio("resources/0.WAV")
            time_sleep_list = [0,0,4,2,0]
            for i in range(1,6):
                time_sleep = time_sleep_list[i]
                if i == 2:
                    time.sleep(8) 
                    play_audio("resources/10.WAV") #解说
                movements = DataPackageConverter(f"{i}.bin").hex_output
                ser.write(bytearray(movements))
                play_audio(f"resources/music{i}.WAV") #音效
                time.sleep(time_sleep) #等待动作完成
                play_audio(f"resources/{i}.WAV") #解说
        
        elif keyword == "检测环境":
            max_index = 5
            cap, idx = find_camera(max_index=max_index)
            if cap is None:
                print("错误：未找到可用的摄像头（尝试索引 0..%d）。" % max_index)
                sys.exit(1)
            play_audio("resources/0.WAV")
            time.sleep(3)
            play_audio("resources/6.WAV")
            time.sleep(3)
            play_audio("resources/7.WAV")
            time.sleep(3)
            play_audio("resources/8.WAV")
            cap.release()
            
        elif keyword == "开始探测":
            movements = DataPackageConverter("plan.odr").hex_output
            ser.write(bytearray(movements))
            play_audio("resources/planmusic.WAV") # 音效

        elif keyword == "报告电池余量":
            play_audio("resources/9.WAV") # 解说

        elif keyword == "继续任务":
            play_audio("resources/0.WAV")
            movements = DataPackageConverter("detect.odr").hex_output
            ser.write(bytearray(movements))
            play_audio("resources/detectmusic.WAV") # 音效
            movements = DataPackageConverter("baojing.odr").hex_output
            ser.write(bytearray(movements))
            play_audio("resources/baojing.WAV") # 解说

        elif keyword == "分离机体":
            send_bytes = DataPackageConverter("fenli1.bin").hex_output
            send_serial_data(ser, send_bytes)
            play_audio("resources/fenli1.WAV")
            time.sleep(3) # 独立行动
            movements = DataPackageConverter("task.odr").hex_output
            ser.write(bytearray(movements))
            play_audio("resources/task.WAV")
            movements = DataPackageConverter("empty.odr").hex_output
            ser.write(bytearray(movements))
            play_audio("resources/empty.WAV")
            movements = DataPackageConverter("wudao.odr").hex_output
            ser.write(bytearray(movements))
            play_audio("resources/wudao.WAV")


        if ser and ser.isOpen():
            ser.close()
            



def send_serial_data(ser, data):
    ser.write(bytearray(data))
    start_time = time.time()  # 记录开始时间
    timeout = 60  # 设置60秒超时
    
    while True:
        # 检查是否超时
        if time.time() - start_time > timeout:
            print("串口通信超时，自动退出循环")
            break
            
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
        order = int(input("请输入指令:0:退出 1:检测机体状态 2:开始探测 3:检测环境 4:报告电池余量 5:继续任务 6:分离机体 7:独立行动 8:voice"))
        order_list = ["0", "检测机体状态", "开始探测", "检测环境", "报告电池余量", "继续任务", "分离机体", "独立行动"]
        if order == 0:
            break
        elif order == 8:
            print("请说出指令...")
            text = speech_recog()
            action_neo(text)
        else:
            text = order_list[order]
            action_neo(text)
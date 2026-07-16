#!/usr/bin/env python3
"""
树莓派 USB 摄像头采集脚本（纯终端模式，适用于 VS Code Remote / SSH）
操作方式：
  - 启动后选择类别
  - 输入 'p' 拍照，'n' 切换类别，'q' 退出当前类，'exit' 全局退出
"""

import cv2
import os
import sys
import time
import serial

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from datapackage import DataPackageConverter


def initialize_serial():
    try:
        ser = serial.Serial('/dev/ttyAMA0', 115200)
        if not ser.isOpen():
            ser.open()
        return ser
    except serial.SerialException:
        raise Exception("Failed to initialize serial connection.")

def send_serial_data(ser, data,timeout=10):
    ser.write(bytearray(data))
    start_time = time.time()  # 记录开始时间

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
            

            

# ========== 配置 ==========
CLASSES = ["BigStand", "lunge", "crouch", "handsup", "stop", "ShiJueBaoTou", "ShiJueHuiShou"]
BASE_DIR = "image"
CAMERA_ID = 0
ROTATE_ANGLE = int(os.getenv('ROTATE', '180'))
# =========================
ser = initialize_serial()
send_bytes = DataPackageConverter("scwadapt.bin").hex_output
#send_serial_data(ser, send_bytes)
if ROTATE_ANGLE not in [0, 90, 180, 270]:
    raise ValueError("ROTATE 必须是 0/90/180/270")

os.makedirs(BASE_DIR, exist_ok=True)

# 打开摄像头（Linux 兼容）
cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)
if not cap.isOpened():
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        print("❌ 无法打开摄像头，请检查连接或权限", file=sys.stderr)
        exit(1)

def rotate_image(frame, angle):
    if angle == 0:
        return frame
    (h, w) = frame.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    return cv2.warpAffine(frame, M, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT)

def menu():
    print("\n" + "="*40)
    print("📸 数据采集系统（终端模式）")
    for i, name in enumerate(CLASSES, 1):
        print(f"{i}. {name}")
    print("0. 退出程序")
    print("="*40)
    if ROTATE_ANGLE:
        print(f"🔄 图片将旋转 {ROTATE_ANGLE}°")

def collect_one(cls):
    folder = os.path.join(BASE_DIR, cls)
    os.makedirs(folder, exist_ok=True)
    exists = [f for f in os.listdir(folder) if f.endswith('.jpg')]
    idx = max([int(f.split('.')[0]) for f in exists], default=-1) + 1

    print(f'\n🟢 开始采集类别: "{cls}"，起始编号: {idx:04d}')
    print("指令: p=拍照, n=结束当前类并返回菜单, q=退出当前类, exit=全局退出")

    while True:
        cmd = input("▶ 输入指令: ").strip().lower()
        if cmd == 'exit':
            cap.release()
            print("👋 全局退出")
            exit(0)
        elif cmd == 'q' or cmd == 'n':
            break
        elif cmd == 'p':
            ret, frame = cap.read()
            if not ret:
                print("⚠️ 读取帧失败！")
                continue
            frame_rot = rotate_image(frame, ROTATE_ANGLE)
            path = os.path.join(folder, f"{idx:04d}.jpg")
            cv2.imwrite(path, frame_rot)
            print(f"✅ 已保存: {path}")
            idx += 1
        else:
            print("❓ 未知指令（p/n/q/exit）")

    return True

def main():
    try:
        while True:
            menu()
            try:
                choice = input("请选择类别编号（0 退出）: ").strip()
                if choice == '0':
                    break
                choice = int(choice)
                if 1 <= choice <= len(CLASSES):
                    collect_one(CLASSES[choice - 1])
                else:
                    print("❌ 编号超出范围！")
            except KeyboardInterrupt:
                print("\n🛑 用户中断")
                break
            except ValueError:
                print("❌ 请输入数字！")
    finally:
        cap.release()
    print("🔚 采集结束")

if __name__ == '__main__':
    main()

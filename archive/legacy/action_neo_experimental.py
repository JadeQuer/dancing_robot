import os
import time
import json
import serial
import cv2
from rhythm_recog import rhythm_recog
from speech_recog import speech_recog
from datapackage import DataPackageConverter
from posture_recognition.static_recognition import StaticPostureIdentifier
import config

pose_identifier = config.pose_identifier


# 初始化串口
def initialize_serial():
    try:
        ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
        # 不需要手动 open()，Serial() 构造时已打开
        print("✅ 串口初始化成功")
        return ser
    except serial.SerialException as e:
        print(f"❌ 串口初始化失败: {e}")
        raise Exception("Failed to initialize serial connection.")


def play_audio(audio_file):
    if os.path.exists(audio_file):
        os.system('mplayer -volume 100 "{}"'.format(audio_file))
    else:
        print(f"⚠️ 音频文件不存在: {audio_file}")


def save_variable_to_file(value):
    with open('temp.txt', 'w') as file:
        file.write(str(value))


def send_serial_data(ser, data):
    """
    安全发送串口数据，并等待特定响应。
    返回 True 表示成功收到确认，False 表示失败或超时。
    """
    if not ser or not ser.is_open:
        print("❌ 串口未打开，无法发送数据")
        return False

    try:
        ser.write(bytearray(data))
        print(f"📤 已发送 {len(data)} 字节数据")
    except (serial.SerialException, OSError) as e:
        print(f"❌ 串口写入失败: {e}")
        return False

    start_time = time.time()
    timeout = 5  # 秒

    while time.time() - start_time < timeout:
        size = ser.inWaiting()
        if size > 0:
            res = ser.read(size)
            print("📥 收到设备响应:", res)
            ser.flushInput()
            # 检查是否为有效结束帧
            if res in (b'\xff\x00\x05\x05\x00\x00\x18"', b'\xff\x00\x05\x05\x00\x00\x19"'):
                return True
        time.sleep(0.1)

    print("⚠️ 串口通信超时，未收到有效响应")
    return False


def action_neo(text):
    global pose_identifier

    # 加载语音指令配置
    try:
        with open('speech_train.json', 'r', encoding='utf-8') as f:
            speech_data = json.load(f)
    except Exception as e:
        print(f"❌ 加载 speech_train.json 失败: {e}")
        play_audio('resources/sorry.MP3')
        return

    ser = None
    keyword = ""

    # 查找匹配关键词
    for action, action_data in speech_data.items():
        if action == "黑名单":
            continue
        for keyword_text in action_data["list"]:
            if keyword_text in text:
                keyword = action_data["name"]
                print(f"🔍 找到关键词 '{keyword_text}'，对应动作 '{action}'，指令名称 '{keyword}'")
                break
        if keyword:
            break

    if not keyword:
        play_audio('resources/sorry.MP3')
        return

    # === 安全执行动作（带串口管理）===
    try:
        ser = initialize_serial()

        # 姿态识别模式
        if keyword == "pose_recognition":
            while True:
                play_audio('resources/pose.MP3')
                send_bytes = DataPackageConverter("0deer_see.bin").hex_output
                if not send_serial_data(ser, send_bytes):
                    play_audio('resources/connection_error.MP3')
                    break

                play_audio('resources/dong.wav')

                # 确保姿势识别器已初始化
                if pose_identifier is None:
                    print("🔄 姿势识别器未初始化，尝试重新初始化...")
                    try:
                        pose_identifier = StaticPostureIdentifier()
                        print("✅ 姿势识别器初始化成功")
                    except FileNotFoundError as e:
                        print(f"❌ 模型文件缺失: {e}")
                        play_audio('resources/sorry.MP3')
                        break
                    except Exception as e:
                        print(f"❌ 姿势识别器初始化失败: {e}")
                        play_audio('resources/sorry.MP3')
                        break

                print("📸 请在摄像头前保持姿势...")
                pose = pose_identifier.recognize_posture(
                    camera_index=0,
                    timeout=15,
                    stable_duration=2.0,
                    display=True,
                    camera_rotation=180
                )

                send_bytes = DataPackageConverter("0deer_reset.bin").hex_output
                send_serial_data(ser, send_bytes)  # 即使失败也继续

                if pose is None:
                    play_audio('resources/timeout.MP3')
                    break
                if pose == "stop":
                    play_audio('resources/stop.MP3')
                    break

                audio_path = f'resources/{pose}.MP3'
                play_audio(audio_path)
                send_bytes = DataPackageConverter(pose + ".bin").hex_output
                send_serial_data(ser, send_bytes)

        # 韵律识别模式
        elif keyword == "rhythm_recognition":
            play_audio("resources/rhythm.MP3")
            matched_song, compare_result = rhythm_recog()
            play_audio("resources/index" + matched_song)

            if matched_song == "TryEverything.MP3":
                movements = DataPackageConverter("0deer_dance2.odr").hex_output
            else:
                movements = DataPackageConverter("0deer_dance1.odr").hex_output

            if not send_serial_data(ser, movements):
                play_audio('resources/connection_error.MP3')
            else:
                play_audio("resources/" + matched_song)

        # 语音自选动作模式
        elif keyword == "speech_recognition":
            print("🎤 进入语音识别模式，请说出动作指令...")
            play_audio('resources/please_speak.MP3')
            failed_count = 0
            max_failed_attempts = 5

            while True:
                word = speech_recog()
                print(f"🗣️ 识别到的指令: {word}")

                # 退出关键词（可优化为正则或更鲁棒匹配）
                exit_keywords = ["结束", "仅剩", "既然说", "家住", "引述", "别墅", "野兽"]
                if any(kw in word for kw in exit_keywords):
                    print("⏹️ 识别到退出指令")
                    play_audio('resources/exit.MP3')
                    break

                action_found = False
                for action, action_data in speech_data.items():
                    if action == "黑名单":
                        continue
                    for keyword_text in action_data["list"]:
                        if keyword_text in word:
                            action_keyword = action_data["name"]
                            print(f"🎯 找到匹配动作: {action} -> {action_keyword}")
                            play_audio(f'resources/{action_keyword}.MP3')

                            if action in ["左移", "右移", "向左转", "向右转", "前进", "后退"]:
                                send_bytes = DataPackageConverter('scw' + action_keyword + ".odr").hex_output
                            else:
                                send_bytes = DataPackageConverter('scw' + action_keyword + ".bin").hex_output

                            if not send_serial_data(ser, send_bytes):
                                play_audio('resources/connection_error.MP3')
                            action_found = True
                            failed_count = 0
                            play_audio('resources/please_speak.MP3')
                            break
                    if action_found:
                        break

                if not action_found:
                    failed_count += 1
                    print(f"❓ 未找到匹配动作 (失败 {failed_count}/{max_failed_attempts})")
                    play_audio('resources/sorry.MP3')
                    if failed_count >= max_failed_attempts:
                        print("🚫 达到最大失败次数，退出语音模式")
                        play_audio('resources/exit.MP3')
                        break
                    else:
                        play_audio('resources/please_speak.MP3')

        # 普通动作
        else:
            play_audio(f'resources/{keyword}.MP3')
            if keyword in ["QianJin", "HouTui", "ZuoYi", "YouYi", "XiangZuoZhuan", "XiangYouZhuan"]:
                send_bytes = DataPackageConverter(keyword + ".odr").hex_output
            else:
                send_bytes = DataPackageConverter(keyword + ".bin").hex_output

            if not send_serial_data(ser, send_bytes):
                play_audio('resources/connection_error.MP3')

    except Exception as e:
        print(f"💥 动作执行过程中发生异常: {e}")
        play_audio('resources/sorry.MP3')
    finally:
        # 确保串口总是被关闭
        if ser and ser.is_open:
            try:
                ser.close()
                print("🔌 串口已安全关闭")
            except Exception as close_err:
                print(f"⚠️ 关闭串口时出错: {close_err}")


if __name__ == '__main__':
    # 测试代码
    action_neo("举左手")
    while True:
        try:
            order = int(input("请输入指令: 0:退出 1:语音 2:键盘\n"))
            if order == 0:
                break
            elif order == 1:
                print("请说出指令...")
                text = speech_recog()
                print("识别结果:", text)
                action_neo(text)
            elif order == 2:
                choice = int(input("1:姿态识别 2:韵律识别 3:语音识别\n"))
                if choice == 1:
                    action_neo("姿态识别")
                elif choice == 2:
                    action_neo("韵律识别")
                else:
                    action_neo("语音识别")
        except KeyboardInterrupt:
            print("\n👋 程序被用户中断")
            break
        except Exception as e:
            print(f"主循环异常: {e}")
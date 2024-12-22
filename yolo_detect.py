import cv2
from yolov5_killjoy.detect import run
# 获取摄像头内容，参数 0 表示使用默认的摄像头
def detect_character():
    cap = cv2.VideoCapture(0)
    flag = 0

    success, frame = cap.read()  # 读取摄像头的一帧图像

    if success:
        c, r, h, w = run()

    cap.release()  # 释放摄像头资源
    cv2.destroyAllWindows()  # 关闭OpenCV窗口
    return c, r, h, w

if __name__ == "__main__":
    detect_character()

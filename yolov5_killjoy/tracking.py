import cv2 as cv
import cv2
import os

from detect import run, parse_opt


def detect_character():
    global c, r, h, w
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
    success, frame = cap.read()  # 读取摄像头的一帧图像
    if success:
        if not os.path.exists('temp_img'):
            os.makedirs('temp_img')
        # 保存当前帧到临时文件
        temp_image_path = 'temp_img/temp_frame.jpg'
        cv2.imwrite(temp_image_path, frame)
        opt = parse_opt()
        c, r, h, w = run(**vars(opt))
        print(c, r, h, w)

    cap.release()  # 释放摄像头资源
    cv2.destroyAllWindows()  # 关闭OpenCV窗口
    return c, r, h, w


def tracking():
    # 创建读取视频的对象
    c, r, h, w = detect_character()
    cap = cv.VideoCapture(0)

    # 获取第一帧位置，并指定目标位置
    ret, frame = cap.read()
    track_window = (c, r, h, w)
    # 指定感兴趣区域
    roi = frame[r:r + h, c:c + w]

    # 计算直方图
    # 转换色彩空间
    hsv_roi = cv.cvtColor(roi, cv.COLOR_BGR2HSV)
    # 计算直方图
    roi_hist = cv.calcHist([hsv_roi], [0], None, [180], [0, 180])
    # 归一化
    cv.normalize(roi_hist, roi_hist, 0, 255, cv.NORM_MINMAX)

    # 目标追踪
    # 设置窗口搜索终止条件：最大迭代次数，窗口中心漂移最小值
    term_crit = (cv.TermCriteria_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)

    while True:
        ret, frame = cap.read()
        if ret:
            # 计算直方图的反向投影
            hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
            dst = cv.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)

            # 进行meanshift追踪
            ret, track_window = cv.meanShift(dst, track_window, term_crit)

            # 将追踪的位置绘制在视频上，并进行显示
            x, y, w, h = track_window
            img = cv.rectangle(frame, (x, y), (x + w, y + h), 255, 2)
            cv.imshow("frame", img)

            if cv.waitKey(20) & 0xFF == ord('q'):
                break

        else:
            break

    # 资源释放
    cap.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    tracking()

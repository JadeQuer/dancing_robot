import cv2
import sys


def find_camera(max_index=5):
    """遍历摄像头索引，返回第一个能打开并能读取到帧的 VideoCapture 对象和索引。

    Args:
        max_index (int): 尝试的最大索引（包含）。会从 0 开始尝试到 max_index。

    Returns:
        (cap, idx) 或 (None, None)
    """
    for idx in range(0, max_index + 1):
        print(f"尝试打开摄像头索引 {idx} ...")
        cap = cv2.VideoCapture(idx)
        if not cap.isOpened():
            cap.release()
            print(f"索引 {idx} 无法打开")
            continue

        # 尝试读取一帧以确认摄像头可用
        ret, _ = cap.read()
        if not ret:
            cap.release()
            print(f"索引 {idx} 打开但无法读取帧，跳过")
            continue

        print(f"成功：使用摄像头索引 {idx}")
        return cap, idx

    return None, None


def open_camera():
    # 可根据需要调整最大索引
    max_index = 5
    cap, idx = find_camera(max_index=max_index)

    if cap is None:
        print("错误：未找到可用的摄像头（尝试索引 0..%d）。" % max_index)
        sys.exit(1)

    print("摄像头已开启 - 按 'q' 键退出")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("错误：无法获取画面")
                break

            cv2.imshow('Camera Feed', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # 确保释放资源
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    open_camera()
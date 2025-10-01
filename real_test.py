import cv2
import numpy as np

# 打开摄像头
cap = cv2.VideoCapture(0)

# 定义三张图片的RGB平均值范围（假设已知）
# 这些范围需要根据你的图片进行调整
color_ranges = {
    "image1": {"min": (0, 0, 0), "max": (80, 80, 80)},
    "image2": {"min": (120, 120, 130), "max": (140, 140, 160)},
    "image3": {"min": (200, 50, 50), "max": (255, 100, 100)}
}

def get_average_rgb(image):
    """
    计算图像的RGB平均值
    """
    avg_color_per_row = np.average(image, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    return avg_color

def match_color(avg_rgb):
    """
    根据RGB平均值匹配图片
    """
    for name, range in color_ranges.items():
        if (range["min"][0] <= avg_rgb[2] <= range["max"][0] and
            range["min"][1] <= avg_rgb[1] <= range["max"][1] and
            range["min"][2] <= avg_rgb[0] <= range["max"][2]):
            return name
    return "Unknown"

while True:
    # 读取摄像头帧
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # 计算RGB平均值
    avg_rgb = get_average_rgb(frame)

    # 匹配颜色
    matched_image = match_color(avg_rgb)

    # 显示结果
    cv2.putText(frame, f"RGB: {avg_rgb}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Matched: {matched_image}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow("Camera", frame)

    # 按下'q'键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头并关闭窗口
cap.release()
cv2.destroyAllWindows()
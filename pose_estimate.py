import cv2
import numpy as np

# 打开摄像头
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 高斯模糊
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 边缘检测
    edged = cv2.Canny(blurred, 50, 150)

    # 形态学操作去除噪点
    kernel = np.ones((3, 3), np.uint8)
    closing = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 查找轮廓
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 初始化最大轮廓和最大面积
    max_contour = None
    max_area = 0

    for contour in contours:
        # 近似多边形
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # 如果轮廓是一个四边形
        if len(approx) == 4:
            area = cv2.contourArea(approx)
            if area > max_area:
                max_contour = approx
                max_area = area

    # 如果找到了最大轮廓
    if max_contour is not None:
        # 创建掩码
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [max_contour], -1, (255), thickness=cv2.FILLED)

        # 提取目标区域
        target = cv2.bitwise_and(frame, frame, mask=mask)

        # 创建黑色背景
        black_background = np.zeros_like(frame)

        # 反转掩码
        mask_inv = cv2.bitwise_not(mask)

        # 将反转的掩码应用于黑色背景
        background_with_mask = cv2.bitwise_and(black_background, black_background, mask=mask_inv)

        # 合并目标区域和黑色背景
        result = cv2.add(target, background_with_mask)

        # 显示结果
        cv2.imshow('Frame', result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()

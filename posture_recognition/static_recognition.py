"""
识别静态图片/摄像头中的姿势
远程无桌面环境友好版：仅保留最后一张结果图，保存在当前路径
"""
import os
import cv2
import glob
import time
import numpy as np
import pickle
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

SHOW_GUI = os.getenv('SHOW_GUI') == '1'  # True 则弹窗
SAVE_IMG = True                    # 是否保存结果图（仅最后一张）


class StaticPostureIdentifier:
    def __init__(self, model_path="models/pose_landmarker_heavy.task", camera_rotation=0):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.recognizer_path = os.path.join(self.current_dir, "output", "YiFeng_pose_recognizer.pickle")

        if camera_rotation not in [0, 90, 180, 270]:
            raise ValueError("摄像头旋转角度必须是 0, 90, 180, 270 中的一个")
        self.camera_rotation = camera_rotation

        # MediaPipe 初始化
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=os.path.join(self.current_dir, model_path)),
            running_mode=VisionRunningMode.IMAGE
        )
        self.landmarker = PoseLandmarker.create_from_options(options)

        # 加载分类器
        print(f"从 {self.recognizer_path} 加载识别器...")
        if not os.path.exists(self.recognizer_path):
            raise FileNotFoundError(f"找不到模型文件: {self.recognizer_path}")
        with open(self.recognizer_path, "rb") as f:
            data = pickle.load(f)
        self.recognizer = data["model"]
        self.label_encoder = data["le"]
        print(f"已加载包含 {len(self.label_encoder.classes_)} 个类别的模型: "
              f"{', '.join(self.label_encoder.classes_)}")

        # 固定输出路径（当前目录）
        self.result_img_path = os.path.join(os.getcwd(), "last_result.jpg")

    # ----------------  以下方法无改动  ----------------
    def _rotate_image(self, image, angle):
        if angle == 0:
            return image
        elif angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        raise ValueError(f"不支持的旋转角度: {angle}")

    def _draw_landmarks(self, annotated_frame, pose_landmarks):
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=l.x, y=l.y, z=l.z)
            for l in pose_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_frame,
            pose_landmarks_proto,
            solutions.pose.POSE_CONNECTIONS,
            solutions.drawing_styles.get_default_pose_landmarks_style()
        )

    def _predict_posture(self, flat_landmarks):
        probs = self.recognizer.predict_proba([flat_landmarks])[0]
        idx = np.argmax(probs)
        return self.label_encoder.classes_[idx], probs[idx]

    # ---------------  核心识别接口  ---------------
    def use(self, frame):
        rotated = self._rotate_image(frame, self.camera_rotation)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                            data=cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB))
        result = self.landmarker.detect(mp_image)
        landmarks_list = result.pose_landmarks
        annotated = cv2.cvtColor(np.copy(mp_image.numpy_view()), cv2.COLOR_RGB2BGR)

        label = None
        has_pose = bool(landmarks_list)

        for landmarks in landmarks_list:
            self._draw_landmarks(annotated, landmarks)
            flat = np.array([[l.x, l.y] for l in landmarks]).flatten()
            label, prob = self._predict_posture(flat)
            text = f"{label}: {prob*100:.2f}%"
            cv2.putText(annotated, text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        # 仅保留最后一张结果图（覆盖写）
        if SAVE_IMG:
            cv2.imwrite(self.result_img_path, annotated)
        return annotated, has_pose, label

    # ---------------  摄像头实时版（可选） ---------------
    def recognize_posture(self, camera_index=0, timeout=30, stable_duration=2.0,
                          display=True, camera_rotation=None):
        if camera_rotation is not None:
            if camera_rotation not in [0, 90, 180, 270]:
                raise ValueError("摄像头旋转角度必须是 0, 90, 180, 270 中的一个")
            original_rotation = self.camera_rotation
            self.camera_rotation = camera_rotation
        else:
            original_rotation = None

        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("无法打开摄像头")
            return None

        current_posture = None
        start_time = time.time()
        last_detection_time = 0

        print("请在摄像头前保持稳定姿势...")
        if self.camera_rotation != 0:
            print(f"摄像头已设置为旋转 {self.camera_rotation} 度")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("无法获取图像")
                    break
                annotated, has_pose, detected = self.use(frame)
                now = time.time()
                if now - start_time > timeout:
                    print("识别超时")
                    break

                # 以下逻辑与原文件相同，仅把 imshow 包进 SHOW_GUI
                if has_pose and detected is not None:
                    if current_posture is None or current_posture == detected:
                        current_posture = detected
                        if last_detection_time == 0:
                            last_detection_time = now
                        stable_time = now - last_detection_time
                        progress = min(stable_time / stable_duration * 100, 100)
                        cv2.putText(annotated, f"保持姿势: {progress:.0f}%", (10, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                        if stable_time >= stable_duration:
                            result_text = f"识别结果: {current_posture}"
                            cv2.putText(annotated, result_text, (10, 120),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2, cv2.LINE_AA)
                            if display and SHOW_GUI:
                                cv2.imshow('pose', annotated)
                                cv2.waitKey(1000)
                            print(f"成功识别姿势: {current_posture}")
                            return current_posture
                    else:
                        current_posture = detected
                        last_detection_time = now
                        print(f"姿势变化为: {detected}，重新计时")
                else:
                    if last_detection_time != 0:
                        last_detection_time = 0
                        print("姿势丢失，请回到摄像头范围内")
                    cv2.putText(annotated, "请保持稳定姿势", (10, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

                if display and SHOW_GUI:
                    cv2.imshow('frame', annotated)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("用户中断识别")
                        return None
        finally:
            cap.release()
            if display and SHOW_GUI:
                cv2.destroyAllWindows()
            if original_rotation is not None:
                self.camera_rotation = original_rotation
        return None


# ----------------  直接跑  ----------------
if __name__ == "__main__":
    print("=== 静态姿势识别 - 仅保留最后一张结果图（当前目录）===")
    identifier = StaticPostureIdentifier(camera_rotation=0)

    test_imgs = glob.glob("test_dataset/*.jpg")
    if test_imgs:
        for img_path in test_imgs:
            frame = cv2.imread(img_path)
            if frame is None:
                print("读图失败:", img_path)
                continue
            annotated, has_pose, label = identifier.use(frame)
            print("图片:", img_path, "识别结果:", label)
        print("最后结果图:", identifier.result_img_path)
    else:
        print("未找到 test_dataset/*.jpg，自动进入摄像头实时模式")
        pose = identifier.recognize_posture(camera_index=0, timeout=30,
                                            stable_duration=2.0, display=True)
        if pose:
            print("最终姿势:", pose)
        else:
            print("未识别到姿势或用户中断")
        print("最后结果图:", identifier.result_img_path)
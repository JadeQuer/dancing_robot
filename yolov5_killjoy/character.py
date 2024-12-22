import cv2 as cv
import os
# import onnxruntime
# from ultralytics.utils.checks import is_ascii
import sys
from ultralytics.utils.ops import scale_coords
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..yolov5_killjoy')))
import torch
import pathlib
from pathlib import Path
pathlib.WindowsPath = pathlib.PosixPath


#这里的路径需要注意，这部分代码的意思就是将当前目录设置为代码的根目录，以免代码环境冲突
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
from models.common import DetectMultiBackend
from models.experimental import attempt_load
from ultralytics.utils.plotting import Annotator, colors
from utils.general import (
    cv2,
    non_max_suppression, set_logging,
)
from utils.torch_utils import select_device

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../yolov5_killjoy')))

def detect_character(weights='best.pt',  # model.pt path(s)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='cpu',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        line_thickness=3,  # bounding box thickness (pixels)
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        data=ROOT / "data/dataset.yaml",  # dataset.yaml path
        ):
    sys.path.append('/home/pi/Desktop/killjoy/yolov5_killjoy')

    # Initialize
    global character, confidence
    character = ''
    confidence = 0
    set_logging()
    device = select_device(device)
    print(device)
    half &= device.type != 'cpu'  # half precision only supported on CUDA

    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
    names = model.module.names if hasattr(model, 'module') else model.names  # get class names
    # ascii = is_ascii(names)  # names are ascii (use PIL for UTF-8)
    capture = cv2.VideoCapture(0)

    while True:
        # 获取一帧
        ret, frame = capture.read()

        img = torch.from_numpy(frame).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img = img / 255.0  # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None]  # expand for batch dim
        img = img.transpose(2, 3)
        img = img.transpose(1, 2)

        # Inference
        pred = model(img, augment=False, visualize=False)[0]

        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

        # Process predictions
        for i, det in enumerate(pred):  # detections per image
            annotator = Annotator(frame, line_width=line_thickness, pil=not ascii)
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    num = str(n.item())
                    character = str(names[int(c)]) # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    c = int(cls)  # integer class
                    confidence = float(conf)
                    label = f'{names[c]} {conf:.2f}'
                    annotator.box_label(xyxy, label, color=colors(c, True))
                    # print(xyxy)

                print('result:' + character + ":" + str(confidence))

        cv2.imshow('frame', frame)
        if confidence >= 0.5:
            break

    return character


if __name__ == '__main__':
    #tracking()
    print(sys.path)
    detect_character()

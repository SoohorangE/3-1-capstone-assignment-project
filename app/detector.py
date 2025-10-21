# app/detector.py

import cv2
import torch
import numpy as np
from ultralytics import YOLO
from typing import List, Dict


class FireDetector:
    """
    YOLO 모델의 트래킹 기능을 사용하여 객체를 추적하고 시각화하는 클래스.
    """

    def __init__(self, model_path: str, conf_threshold: float = 0.5):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"'{self.device}' 장치를 사용하여 모델을 실행합니다.")

        # YOLO 모델을 직접 로드합니다.
        try:
            self.model = YOLO(model_path)
            self.model.to(self.device)
            print(f"성공적으로 YOLO 모델을 로드했습니다: {model_path}")
            # 클래스 이름은 모델 파일에서 직접 가져옵니다.
            self.class_names = self.model.names
            print(f"라벨 정보: {self.class_names}")
        except Exception as e:
            print(f"모델 로딩 실패: {e}")
            raise

        self.conf_threshold = conf_threshold

    def track_and_draw(self, frame: np.ndarray) -> (np.ndarray, List[Dict]):
        """
        한 프레임에 대해 객체 추적 및 시각화를 수행합니다.

        Returns:
            - 시각화된 프레임 (np.ndarray)
            - 탐지된 객체 정보 리스트 (List[Dict])
        """
        # model.track() 메소드를 사용하여 추적을 수행합니다.
        # persist=True 옵션은 프레임 간의 추적 정보를 유지시킵니다.
        results = self.model.track(frame, persist=True, conf=self.conf_threshold, verbose=False)

        # 결과가 없으면 원본 프레임을 반환합니다.
        if results[0].boxes is None:
            return frame, []

        annotated_frame = results[0].plot()  # Ultralytics의 내장 시각화 기능을 사용합니다.

        detections = []
        # 결과에서 추적 ID, 박스 좌표, 클래스 정보를 추출합니다.
        # .id가 None이 아닌 경우에만 처리하여 추적이 시작된 객체만 다룹니다.
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            confs = results[0].boxes.conf.cpu().numpy()

            for box, track_id, cls_id, conf in zip(boxes, track_ids, class_ids, confs):
                detections.append({
                    "box": box.tolist(),
                    "track_id": track_id,
                    "class_id": cls_id,
                    "class_name": self.class_names[cls_id],
                    "conf": conf
                })

        return annotated_frame, detections
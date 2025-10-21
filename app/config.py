# config.py

import os

# --- 기본 경로 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DEBUG_DIR = os.path.join(BASE_DIR, "debug_frames")

# --- 모델 및 데이터 경로 ---
# ⭐️ 사용할 모델을 .pt 파일로 설정
MODEL_PATH = os.path.join(BASE_DIR, "models/best.pt")

# --- 탐지 설정 ---
# 모델 학습 시 사용했던 이미지 크기 (참고용)
IMG_SIZE = 640
# 탐지할 최소 신뢰도(confidence) 임계값
CONF_THRESHOLD = 0.3

# --- 디버그 설정 ---
# True로 설정하면 처음 탐지되는 N개의 프레임을 이미지로 저장
DEBUG_MODE = False
MAX_DEBUG_IMAGES = 10

# 파일 크기 제한 설정 (100MB)
MAX_FILE_SIZE = 200 * 1024 * 1024

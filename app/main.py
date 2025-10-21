# main.py

import uvicorn
import asyncio
import os
import uuid
import logging
import shutil

from fastapi import FastAPI, Request, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask
import cv2

# 설정 파일에서 모든 설정값 가져오기
import config
from app.detector import FireDetector

# --- 기본 설정 ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
app = FastAPI()
templates = Jinja2Templates(directory="front")
app.mount("/front", StaticFiles(directory="front"), name="front")

# --- 디렉토리 생성 ---
os.makedirs(config.UPLOADS_DIR, exist_ok=True)
os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
os.makedirs(config.DEBUG_DIR, exist_ok=True)

# --- 모델 로딩 ---
try:
    # detector 초기화 방식 변경
    detector = FireDetector(
        model_path=config.MODEL_PATH,
        conf_threshold=config.CONF_THRESHOLD
    )
except Exception as e:
    logging.error(f"모델 로딩 중 심각한 오류 발생: {e}")
    raise RuntimeError("Failed to load model") from e


# --- 동기 영상 처리 함수 ---
def process_video_sync(input_path: str, output_path: str) -> bool:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        logging.error(f"비디오 파일을 열 수 없습니다: {input_path}")
        return False

    writer = None
    frame_idx = 0
    debug_count = 0
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if fps == 0: fps = 30

        # 코덱 avc1
        codecs = ['avc1']
        for codec in codecs:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            if writer.isOpened():
                logging.info(f"VideoWriter 초기화 성공. 사용할 코덱: {codec}")
                break
        else:  # for-else 구문: break 없이 루프가 끝나면 실행
            logging.error("사용 가능한 코덱을 찾지 못해 VideoWriter 초기화에 최종 실패했습니다.")
            return False

        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_idx += 1

            processed_frame, detections = detector.track_and_draw(frame)
            writer.write(processed_frame)

            if config.DEBUG_MODE and detections and debug_count < config.MAX_DEBUG_IMAGES:
                debug_path = os.path.join(config.DEBUG_DIR, f"frame_{frame_idx}.jpg")
                cv2.imwrite(debug_path, processed_frame)
                debug_count += 1

    except Exception as e:
        logging.error(f"영상 처리 중 예외 발생 (프레임 #{frame_idx}): {e}", exc_info=True)
        return False
    finally:
        if cap.isOpened(): cap.release()
        if writer and writer.isOpened(): writer.release()

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        logging.error(f"결과 파일이 생성되지 않았거나 비어있습니다: {output_path}")
        return False

    logging.info(f"영상 처리 완료: {output_path}")
    return True


def cleanup_files(paths: list[str]):
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                logging.info(f"임시 파일 삭제: {path}")
        except OSError as e:
            logging.error(f"임시 파일 삭제 실패: {path}, 오류: {e}")


# --- API 엔드포인트 ---
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/detect-fire/")
async def detect_fire_in_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # 1. 파일 크기 검사 로직 추가
    file.file.seek(0, 2)
    size = file.file.tell()
    if size > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"파일 크기가 100MB를 초과했습니다."
        )
    file.file.seek(0)

    # --- 기존 파일 경로 설정 로직 ---
    unique_id = uuid.uuid4().hex
    ext = os.path.splitext(file.filename)[1].lower()
    if not ext: ext = ".mp4"
    input_path = os.path.join(config.UPLOADS_DIR, f"{unique_id}{ext}")
    output_path = os.path.join(config.OUTPUTS_DIR, f"{unique_id}_processed.mp4")

    # 2. 메모리 효율적인 파일 저장 방식으로 변경
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logging.error(f"파일 저장 실패: {e}")
        raise HTTPException(status_code=500, detail="파일 저장에 실패했습니다.")
    finally:
        file.file.close()

    success = await asyncio.to_thread(process_video_sync, input_path, output_path)

    if not success:
        background_tasks.add_task(cleanup_files, [input_path])
        raise HTTPException(status_code=500, detail="비디오 처리 실패")

    background_tasks.add_task(cleanup_files, [input_path])
    cleanup_task = BackgroundTask(cleanup_files, paths=[input_path, output_path])

    return FileResponse(
        path=output_path,
        media_type='video/mp4',
        filename=f"result_{file.filename}",
        background=cleanup_task
    )

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
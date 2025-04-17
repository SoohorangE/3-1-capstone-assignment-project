from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import uvicorn

from app.generator import Generator


# 입력 모델 정의
class PromptRequest(BaseModel):
    history : list
# FastAPI 앱 초기화
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="front")
app.mount("/front", StaticFiles(directory="front"), name="front")

# 모델 초기화
generator = Generator()

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/answer")
async def answer(request: PromptRequest):
    response, summary = generator.generate_model(request)

    return {"result": response, "summary":summary}

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)




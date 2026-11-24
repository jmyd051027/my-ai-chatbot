
import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers.data_router import router as data_router
from routers.chat_router import router as chat_router
from security.auth import verify_access

# 환경변수 불러오기
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="Sleep AI",
    description="수면 데이터 기반 AI 분석 챗봇",
    version="1.0.0"
)

# 프론트엔드 접속 허용 주소
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500"
    ).split(",")
    if origin.strip()
]

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 수면 데이터 API 연결 및 접근 권한 검사
app.include_router(
    data_router,
    dependencies=[Depends(verify_access)]
)

# AI 챗봇 API 연결 및 접근 권한 검사
app.include_router(
    chat_router,
    dependencies=[Depends(verify_access)]
)


# 서버 상태 확인
@app.get("/")
def root():
    return {
        "message": "Sleep AI 서버가 실행 중입니다.",
        "status": "ok"
    }

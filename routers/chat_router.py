
import logging
import time

from collections import deque
from threading import Lock

from fastapi import APIRouter, HTTPException
from schemas.chat import ChatRequest, ChatResponse
from services import chat_service, conversation_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["AI 챗봇"]
)


# 1. AI API 요청 횟수 제한 설정
MINUTE_LIMIT = 5
DAILY_LIMIT = 30

request_times = deque()
request_lock = Lock()


def check_request_limit():
    now = time.monotonic()

    with request_lock:

        # 24시간이 지난 요청 기록 제거
        while request_times and now - request_times[0] >= 86400:
            request_times.popleft()

        # 최근 1분 동안의 요청 횟수 계산
        recent_count = sum(
            1 for timestamp in request_times
            if now - timestamp < 60
        )

        # 24시간 요청 제한
        if len(request_times) >= DAILY_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="24시간 AI 질문 한도인 30회를 초과했습니다."
            )

        # 1분 요청 제한
        if recent_count >= MINUTE_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="1분당 AI 질문은 최대 5회입니다. 잠시 후 다시 시도해 주세요."
            )

        # 허용된 요청 기록
        request_times.append(now)


# 2. AI 질문 및 답변 자동 저장
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    # AI 호출 전 요청 횟수 확인
    check_request_limit()

    try:
        answer = chat_service.generate_answer(
            request.question
        )

        if not answer or not answer.strip():
            raise ValueError("AI 답변이 비어 있습니다.")

        result = conversation_service.save_conversation(
            request.question,
            answer
        )

        return result

    except Exception:
        logger.exception("챗봇 처리 오류")

        raise HTTPException(
            status_code=500,
            detail="AI 답변 처리 중 오류가 발생했습니다."
        )


# 3. 전체 대화 기록 조회
@router.get(
    "/conversations",
    response_model=list[ChatResponse]
)
def get_conversations():
    return conversation_service.get_conversations()


# 4. 특정 대화 기록 조회
@router.get(
    "/conversations/{conversation_id}",
    response_model=ChatResponse
)
def get_conversation(conversation_id: str):
    result = conversation_service.get_conversation(
        conversation_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="대화 기록을 찾을 수 없습니다."
        )

    return result

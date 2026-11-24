
import logging

from fastapi import APIRouter, HTTPException
from schemas.chat import ChatRequest, ChatResponse
from services import chat_service, conversation_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["AI 챗봇"]
)


# 1. AI 질문 및 답변 자동 저장
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
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


# 2. 전체 대화 기록 조회
@router.get(
    "/conversations",
    response_model=list[ChatResponse]
)
def get_conversations():
    return conversation_service.get_conversations()


# 3. 특정 대화 기록 조회
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


from pydantic import BaseModel, Field, field_validator


# 사용자 질문 검증
class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("질문을 입력해 주세요.")

        return value


# AI 답변 및 대화 기록 형식
class ChatResponse(BaseModel):
    id: str
    question: str
    answer: str
    created_at: str

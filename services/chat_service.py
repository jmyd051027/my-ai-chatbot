import os
import json
import logging

from openai import OpenAI
from dotenv import load_dotenv
from services.summary_service import get_summary

load_dotenv()

logger = logging.getLogger(__name__)


def generate_answer(question: str):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OpenAI API 키가 없습니다.")

    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv(
            "OPENAI_BASE_URL",
            "https://copa.codyssey.kr/v1"
        ),
        timeout=60.0
    )

    # Firebase 수면 데이터 분석 결과 가져오기
    summary = get_summary()

    context = json.dumps(
        summary,
        ensure_ascii=False,
        indent=2
    )

    # AI에게 전달할 지시사항
    instructions = """
당신은 수면 데이터 분석 AI 챗봇입니다.

제공된 수면 통계 데이터를 근거로 답변하세요.
데이터에 없는 수치를 만들어 내지 마세요.
데이터가 부족하면 부족하다고 설명하세요.
의학적인 진단은 하지 마세요.
친절하고 이해하기 쉬운 한국어로 답변하세요.
현재 수면 기록은 가상의 테스트 데이터입니다.
핵심 내용을 중심으로 간결하게 답변하세요.
"""

    # 교육장 전용 API 서버에 질문 전달
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        messages=[
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": f"""
수면 데이터 분석 결과:
{context}

사용자 질문:
{question}
"""
            }
        ],
        max_completion_tokens=4000
    )

    if not response.choices:
        raise ValueError("AI 응답 목록이 비어 있습니다.")

    choice = response.choices[0]
    answer = choice.message.content

    # 빈 답변 발생 시 종료 원인 기록
    if not answer or not answer.strip():
        logger.error(
            "AI 빈 답변 발생: finish_reason=%s, usage=%s",
            choice.finish_reason,
            response.usage
        )

        raise ValueError(
            f"AI 답변이 비어 있습니다. "
            f"종료 원인: {choice.finish_reason}"
        )

    return answer.strip()
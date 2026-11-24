
import os
import json

from openai import OpenAI
from dotenv import load_dotenv
from services.summary_service import get_summary

load_dotenv()


def generate_answer(question: str):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OpenAI API 키가 없습니다.")

    client = OpenAI(api_key=api_key)

    # Firebase 수면 데이터 분석 결과 가져오기
    summary = get_summary()

    # 분석 결과를 문자열로 변환
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
"""

    # 수면 분석 결과와 사용자 질문 전달
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        instructions=instructions,
        input=f"""
수면 데이터 분석 결과:
{context}

사용자 질문:
{question}
""",
        max_output_tokens=1000
    )

    return response.output_text

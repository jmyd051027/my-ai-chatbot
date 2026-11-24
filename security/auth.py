
import os
import secrets

from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()


def verify_access(
    x_access_key: str | None = Header(default=None)
):
    # 서버 환경변수에서 접근 비밀번호 불러오기
    access_key = os.getenv("APP_ACCESS_KEY")

    # 서버에 비밀번호가 설정되지 않은 경우
    if not access_key:
        raise HTTPException(
            status_code=503,
            detail="서버 접근 설정이 완료되지 않았습니다."
        )

    # 비밀번호가 없거나 일치하지 않는 경우
    if not x_access_key or not secrets.compare_digest(
        x_access_key.encode("utf-8"),
        access_key.encode("utf-8")
    ):
        raise HTTPException(
            status_code=401,
            detail="접근 비밀번호가 올바르지 않습니다."
        )

    return True

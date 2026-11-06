from sqlalchemy import Column, Integer, String, Float
from database import Base

# 데이터베이스에 만들어질 '표(테이블)'의 설계도입니다.
class SleepRecord(Base):
    __tablename__ = "sleep_records" # 표의 이름

    # 표의 기둥(컬럼)들을 정의합니다.
    id = Column(Integer, primary_key=True, index=True) # 고유 번호 (1, 2, 3...)
    date = Column(String, index=True)                  # 날짜 (예: "2023-10-27")
    sleep_hours = Column(Float)                        # 수면 시간 (예: 7.5)
    condition = Column(String)                         # 자고 일어난 상태 (예: "개운함")
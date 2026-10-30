from fastapi import FastAPI
from pydantic import BaseModel # 데이터 틀을 만들기 위한 도구 추가!

app = FastAPI()

# 1. 수면 기록 데이터의 '틀' 만들기 (붕어빵 틀)
class SleepRecord(BaseModel):
    date: str       # 날짜 (예: "2023-10-27")
    hours: float    # 수면 시간 (예: 7.5)
    memo: str       # 메모 (예: "꿀잠 잤다!")

# 2. 임시 데이터베이스 (기록을 차곡차곡 저장할 빈 리스트)
sleep_db = []

@app.get("/")
def read_root():
    return {"message": "수면시간 분석 AI 챗봇에 오신 것을 환영합니다!"}

# 3. [Create] 수면 기록 저장하기 (POST 방식)
@app.post("/sleeps")
def create_sleep_record(record: SleepRecord):
    sleep_db.append(record) # 리스트에 데이터 추가
    return {"message": "수면 기록이 성공적으로 저장되었습니다!", "data": record}

# 4. [Read] 저장된 모든 수면 기록 보기 (GET 방식)
@app.get("/sleeps")
def get_sleep_records():
    return {"total_records": len(sleep_db), "records": sleep_db}

# 5. [Update] 데이터 수정하기 (PUT 방식)
@app.put("/sleeps/{date}")
def update_sleep(date: str, hours: float, memo: str):
    for record in sleep_db:
        if record.date == date:       # 대괄호 대신 점(.) 사용!
            record.hours = hours      # 대괄호 대신 점(.) 사용!
            record.memo = memo        # 대괄호 대신 점(.) 사용!
            return {"message": f"{date}의 수면 기록이 수정되었습니다!"}
    return {"message": "해당 날짜의 기록을 찾을 수 없습니다."}

# 6. [Delete] 데이터 삭제하기 (DELETE 방식)
@app.delete("/sleeps/{date}")
def delete_sleep(date: str):
    for i, record in enumerate(sleep_db):
        if record.date == date:       # 대괄호 대신 점(.) 사용!
            del sleep_db[i]
            return {"message": f"{date}의 수면 기록이 삭제되었습니다!"}
    return {"message": "해당 날짜의 기록을 찾을 수 없습니다."}

@app.get("/sleeps/analysis")
def analyze_sleep():
    # 1. 데이터가 하나도 없는 경우 방어
    if not sleep_db:
        return {"message": "분석할 수면 데이터가 없습니다. 먼저 데이터를 추가해주세요!"}
    
    # 2. 총 수면 시간 계산
    total_hours = 0
    for record in sleep_db:
        total_hours += record.hours
        
    # 3. 평균 수면 시간 계산 (총 시간 / 데이터 개수)
    average_hours = total_hours / len(sleep_db)
    average_hours = round(average_hours, 1) # 소수점 첫째 자리까지만 표시
    
    # 4. 평균 수면 시간에 따른 맞춤형 피드백
    if average_hours >= 7.0:
        feedback = "훌륭합니다! 평균 7시간 이상 충분한 수면을 취하고 계시네요. 🌟"
    else:
        feedback = "수면 시간이 조금 부족합니다. 건강을 위해 오늘은 일찍 주무시는 건 어떨까요? 🛌"
        
    # 5. 최종 분석 결과 반환
    return {
        "데이터_개수": len(sleep_db),
        "평균_수면시간": average_hours,
        "AI_피드백": feedback
    }
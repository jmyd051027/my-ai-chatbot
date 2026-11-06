from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal

# 1. 앱이 실행될 때 DB 파일과 테이블을 자동으로 만듭니다.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2. DB에 접속하기 위한 도우미 함수 (창구 역할)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. 수면 기록 데이터의 '틀' 만들기 (DB 이름표에 맞춤!)
class SleepEntry(BaseModel):
    date: str           # 날짜 (예: "2023-10-27")
    sleep_hours: float  # 수면 시간 (기존 hours -> sleep_hours로 변경)
    condition: str      # 메모/상태 (기존 memo -> condition으로 변경)

@app.get("/")
def read_root():
    return {"message": "수면시간 분석 AI 챗봇에 오신 것을 환영합니다!"}

# 4. [Create] 수면 기록 DB에 저장하기 (POST 방식)
@app.post("/sleeps")
def create_sleep_record(record: SleepEntry, db: Session = Depends(get_db)):
    # DB에 넣을 형태로 포장
    new_record = models.SleepRecord(
        date=record.date,
        sleep_hours=record.sleep_hours,
        condition=record.condition
    )
    db.add(new_record) # DB에 추가
    db.commit()        # 도장 쾅! (영구 저장)
    db.refresh(new_record)
    return {"message": "수면 기록이 성공적으로 저장되었습니다!", "data": new_record}

# 5. [Read] DB에 저장된 모든 수면 기록 보기 (GET 방식)
@app.get("/sleeps")
def get_sleep_records(db: Session = Depends(get_db)):
    # DB에서 SleepRecord 데이터를 전부 가져옴
    records = db.query(models.SleepRecord).all()
    return {"total_records": len(records), "records": records}

# 6. [분석] 수면 데이터 분석 기능 
# (💡주의: 고정된 주소(/analysis)는 변하는 주소(/{sleep_id})보다 위에 있어야 에러가 안 납니다!)
@app.get("/sleeps/analysis")
def analyze_sleep(db: Session = Depends(get_db)):
    # DB에서 모든 기록 가져오기
    records = db.query(models.SleepRecord).all()
    
    # 데이터가 하나도 없는 경우 방어
    if not records:
        return {"message": "분석할 수면 데이터가 없습니다. 먼저 데이터를 추가해주세요!"}
    
    # 총 수면 시간 계산
    total_hours = 0
    for record in records:
        total_hours += record.sleep_hours
        
    # 평균 수면 시간 계산
    average_hours = total_hours / len(records)
    average_hours = round(average_hours, 1)
    
    # 평균 수면 시간에 따른 맞춤형 피드백
    if average_hours >= 7.0:
        feedback = "훌륭합니다! 평균 7시간 이상 충분한 수면을 취하고 계시네요. 🌟"
    else:
        feedback = "수면 시간이 조금 부족합니다. 건강을 위해 오늘은 일찍 주무시는 건 어떨까요? 🛌"
        
    return {
        "데이터_개수": len(records),
        "평균_수면시간": average_hours,
        "AI_피드백": feedback
    }

# 7. [Read] 특정 수면 기록 하나만 보기 (GET 방식)
@app.get("/sleeps/{sleep_id}")
def get_sleep(sleep_id: int, db: Session = Depends(get_db)):
    # DB에서 id가 일치하는 데이터 딱 1개만 찾아오기
    record = db.query(models.SleepRecord).filter(models.SleepRecord.id == sleep_id).first()
    
    # 만약 데이터가 없다면 404 에러 보내기
    if record is None:
        raise HTTPException(status_code=404, detail="해당 ID의 수면 기록을 찾을 수 없습니다.")
    
    return record

# 8. [Update] DB 데이터 수정하기 (PUT 방식) - ✨ id 기준으로 업그레이드!
@app.put("/sleeps/{sleep_id}")
def update_sleep(sleep_id: int, sleep_hours: float, condition: str, db: Session = Depends(get_db)):
    # DB에서 해당 ID의 기록을 하나 찾음
    record = db.query(models.SleepRecord).filter(models.SleepRecord.id == sleep_id).first()
    
    if record:
        record.sleep_hours = sleep_hours
        record.condition = condition
        db.commit() # 수정된 내용 저장
        return {"message": f"{sleep_id}번 수면 기록이 수정되었습니다!", "data": record}
    
    raise HTTPException(status_code=404, detail="해당 ID의 기록을 찾을 수 없습니다.")

# 9. [Delete] DB 데이터 삭제하기 (DELETE 방식) - ✨ id 기준으로 업그레이드!
@app.delete("/sleeps/{sleep_id}")
def delete_sleep(sleep_id: int, db: Session = Depends(get_db)):
    # DB에서 해당 ID의 기록을 하나 찾음
    record = db.query(models.SleepRecord).filter(models.SleepRecord.id == sleep_id).first()
    
    if record:
        db.delete(record) # DB에서 삭제
        db.commit()       # 삭제 내용 반영
        return {"message": f"{sleep_id}번 수면 기록이 삭제되었습니다!"}
    
    raise HTTPException(status_code=404, detail="해당 ID의 기록을 찾을 수 없습니다.")
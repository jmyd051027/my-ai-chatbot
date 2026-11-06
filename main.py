from fastapi import FastAPI, HTTPException  # <-- 에러 해결: HTTPException 추가됨!
from pydantic import BaseModel
from database import db  # Firebase 연동 파일 불러오기

app = FastAPI()

# --- 데이터 모델 정의 ---
class SleepData(BaseModel):
    date: str
    sleep_hours: float
    condition: str
    mood: str

# --- 1. 환영 메시지 (GET) ---
@app.get("/")
def read_root():
    return {"message": "수면 시간 분석 AI 챗봇에 오신 것을 환영합니다!"}

# --- 2. 수면 데이터 생성 (POST) ---
@app.post("/sleep/")
def create_sleep_data(sleep: SleepData):
    # Firebase Firestore에 데이터 저장 (자동 ID 생성)
    doc_ref = db.collection('sleep_data').document() 
    doc_ref.set(sleep.dict())
    return {"message": "성공적으로 저장되었습니다!", "id": doc_ref.id}

# --- 3. 수면 데이터 전체 조회 (GET) ---
@app.get("/sleep/")
def read_sleep_data():
    docs = db.collection('sleep_data').stream()
    sleep_list = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id  # 조회할 때 문서 ID도 함께 보여줌
        sleep_list.append(data)
    return sleep_list

# --- 4. 특정 수면 데이터 수정 (PUT) ---
@app.put("/sleep/{sleep_id}")
def update_sleep_data(sleep_id: str, sleep: SleepData):
    doc_ref = db.collection('sleep_data').document(sleep_id)
    doc = doc_ref.get()
    
    # 데이터가 없으면 404 에러 발생
    if not doc.exists:
        raise HTTPException(status_code=404, detail="수정할 데이터를 찾을 수 없습니다.")
    
    # 데이터가 있으면 업데이트
    doc_ref.update(sleep.dict())
    return {"message": f"ID {sleep_id} 데이터가 성공적으로 수정되었습니다!"}

# --- 5. 특정 수면 데이터 삭제 (DELETE) ---
@app.delete("/sleep/{sleep_id}")
def delete_sleep_data(sleep_id: str):
    doc_ref = db.collection('sleep_data').document(sleep_id)
    doc = doc_ref.get()
    
    # 데이터가 없으면 404 에러 발생
    if not doc.exists:
        raise HTTPException(status_code=404, detail="삭제할 데이터를 찾을 수 없습니다.")
    
    # 데이터가 있으면 삭제
    doc_ref.delete()
    return {"message": f"ID {sleep_id} 데이터가 성공적으로 삭제되었습니다!"}

@app.get("/sleep/analyze")
def analyze_sleep():
    # 1. Firebase에서 모든 수면 데이터 가져오기
    docs = db.collection('sleep_records').stream()
    
    total_hours = 0
    count = 0
    
    # 2. 데이터 하나씩 읽으면서 시간 더하기
    for doc in docs:
        data = doc.to_dict()
        total_hours += data.get('sleep_hours', 0)
        count += 1
        
    # 3. 데이터가 하나도 없는 경우 예외 처리
    if count == 0:
        return {"message": "분석할 수면 데이터가 없습니다. 먼저 데이터를 추가해주세요!"}
        
    # 4. 평균 수면 시간 계산 (소수점 첫째 자리까지)
    avg_hours = round(total_hours / count, 1)
    
    # 5. 평균 시간에 따른 맞춤형 피드백 생성
    if avg_hours < 7:
        feedback = "수면이 부족해 보여요! 오늘은 조금 더 일찍 잠자리에 들어보세요. 🌙"
    elif avg_hours <= 9:
        feedback = "아주 훌륭합니다! 적절한 수면 시간을 잘 유지하고 계시네요. 👍"
    else:
        feedback = "수면 시간이 꽤 기네요! 너무 오래 자면 오히려 무기력해질 수 있으니 주의하세요. ☀️"
        
    # 6. 최종 결과 반환
    return {
        "총_기록_수": count,
        "평균_수면시간": avg_hours,
        "AI_피드백": feedback
    }
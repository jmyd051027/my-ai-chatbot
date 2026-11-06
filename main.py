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
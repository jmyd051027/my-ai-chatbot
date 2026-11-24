
from database import db

# Firestore 컬렉션 지정
collection = db.collection("data")


# 1. 수면 데이터 추가
def create_data(data: dict):
    doc_ref = collection.document()
    doc_ref.set(data)

    return {"id": doc_ref.id, **data}


# 2. 전체 수면 데이터 조회
def get_all_data():
    docs = collection.order_by("date").stream()

    return [
        {"id": doc.id, **doc.to_dict()}
        for doc in docs
    ]


# 3. 수면 데이터 수정
def update_data(data_id: str, data: dict):
    doc_ref = collection.document(data_id)

    if not doc_ref.get().exists:
        return None

    doc_ref.update(data)

    return {"id": data_id, **data}


# 4. 수면 데이터 삭제
def delete_data(data_id: str):
    doc_ref = collection.document(data_id)

    if not doc_ref.get().exists:
        return False

    doc_ref.delete()

    return True

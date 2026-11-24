
from datetime import datetime, timezone
from database import db

collection = db.collection("conversations")


# 대화 기록 저장
def save_conversation(question: str, answer: str):
    data = {
        "question": question,
        "answer": answer,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    doc_ref = collection.document()
    doc_ref.set(data)

    return {
        "id": doc_ref.id,
        **data
    }


# 전체 대화 기록 조회
def get_conversations():
    docs = collection.order_by(
        "created_at",
        direction="DESCENDING"
    ).stream()

    return [
        {"id": doc.id, **doc.to_dict()}
        for doc in docs
    ]


# 특정 대화 기록 조회
def get_conversation(conversation_id: str):
    doc = collection.document(conversation_id).get()

    if not doc.exists:
        return None

    return {
        "id": doc.id,
        **doc.to_dict()
    }

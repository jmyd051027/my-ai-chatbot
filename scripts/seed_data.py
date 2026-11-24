
import random
from datetime import date, timedelta
from database import db


def seed_data():
    collection = db.collection("data")

    random.seed(42)
    today = date.today()

    batch = db.batch()
    count = 0

    for i in range(100):
        record_date = today - timedelta(days=99 - i)

        # 평일과 주말 수면 시간 구분
        if record_date.weekday() >= 5:
            hours = random.uniform(7, 10)
        else:
            hours = random.uniform(4, 8)

        hours = round(hours, 1)

        # 수면 시간에 따른 메모 생성
        if hours < 6:
            memo = "수면 부족으로 피곤했음"
        elif hours < 7:
            memo = "조금 피곤했음"
        elif hours < 9:
            memo = "충분히 자고 개운했음"
        else:
            memo = "평소보다 오래 잠"

        data = {
            "date": record_date.isoformat(),
            "value": hours,
            "memo": memo
        }

        # 중복 생성을 방지하기 위한 고유 ID
        doc_id = f"sample_{record_date.isoformat()}"
        doc_ref = collection.document(doc_id)

        batch.set(doc_ref, data)
        count += 1

    batch.commit()

    print(f"수면 테스트 데이터 {count}개 저장 완료!")


if __name__ == "__main__":
    seed_data()

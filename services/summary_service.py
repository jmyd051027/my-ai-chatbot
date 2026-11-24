
from statistics import mean
from services.data_service import get_all_data


def get_summary():
    records = get_all_data()

    # 데이터가 없는 경우
    if not records:
        return {
            "count": 0,
            "start_date": None,
            "end_date": None,
            "mean": None,
            "min": None,
            "max": None,
            "recent_mean": None,
            "previous_mean": None,
            "trend": "데이터 부족"
        }

    # 날짜순 정렬
    records = sorted(records, key=lambda x: x["date"])

    # 수면 시간만 추출
    values = [record["value"] for record in records]

    # 최근 기록 평균
    recent_mean = mean(values[-7:])

    previous_mean = None
    trend = "데이터 부족"

    # 최근 7개와 이전 7개 기록 비교
    if len(values) >= 14:
        previous_mean = mean(values[-14:-7])

        difference = recent_mean - previous_mean

        if difference > 0.1:
            trend = "증가"
        elif difference < -0.1:
            trend = "감소"
        else:
            trend = "유지"

    # 분석 결과 반환
    return {
        "count": len(records),
        "start_date": records[0]["date"],
        "end_date": records[-1]["date"],
        "mean": round(mean(values), 2),
        "min": min(values),
        "max": max(values),
        "recent_mean": round(recent_mean, 2),
        "previous_mean": (
            round(previous_mean, 2)
            if previous_mean is not None
            else None
        ),
        "trend": trend
    }

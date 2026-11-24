
from fastapi import APIRouter, HTTPException
from schemas.data import DataCreate, DataUpdate, DataResponse
from services import data_service, summary_service

router = APIRouter(
    prefix="/api/data",
    tags=["수면 데이터"]
)


# 1. 수면 기록 추가
@router.post("", response_model=DataResponse, status_code=201)
def create_data(data: DataCreate):
    return data_service.create_data(
        data.model_dump(mode="json")
    )


# 2. 전체 수면 기록 조회
@router.get("", response_model=list[DataResponse])
def get_all_data():
    return data_service.get_all_data()


# 3. 수면 기록 수정
@router.put("/{data_id}", response_model=DataResponse)
def update_data(data_id: str, data: DataUpdate):
    result = data_service.update_data(
        data_id,
        data.model_dump(mode="json")
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="수면 기록을 찾을 수 없습니다."
        )

    return result


# 4. 수면 기록 삭제
@router.delete("/{data_id}")
def delete_data(data_id: str):
    success = data_service.delete_data(data_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="수면 기록을 찾을 수 없습니다."
        )

    return {"message": "수면 기록이 삭제되었습니다."}

# 5. 수면 데이터 요약
@router.get("/summary")
def get_summary():
    return summary_service.get_summary()

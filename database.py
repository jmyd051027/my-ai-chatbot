from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. DB 파일 이름 설정 (이름은 sleep_data.db로 만들어집니다)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sleep_data.db"

# 2. DB 엔진 생성 (파이썬과 SQLite를 연결해주는 심장 역할)
# connect_args={"check_same_thread": False}는 SQLite를 쓸 때 꼭 필요한 설정입니다.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. DB 세션 생성기 (DB에 데이터를 넣거나 뺄 때 사용하는 '접속 창구' 역할)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 베이스 클래스 (앞으로 만들 데이터 표(테이블)의 뼈대가 됩니다)
Base = declarative_base()
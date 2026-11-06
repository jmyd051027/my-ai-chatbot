import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# 1. 우리가 방금 업로드한 비밀키 파일 연결
cred = credentials.Certificate("firebase-key.json")

# 2. Firebase 앱 초기화 (서버가 재시작될 때 중복 실행되는 것을 방지)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# 3. Firestore 데이터베이스 조종기(클라이언트) 생성
db = firestore.client()
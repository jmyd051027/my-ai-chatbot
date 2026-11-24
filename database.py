
import os
import json
import firebase_admin

from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# 환경변수 불러오기
load_dotenv()

# Firebase 인증 정보 불러오기
firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
firebase_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

if not firebase_admin._apps:
    if firebase_json:
        cred = credentials.Certificate(json.loads(firebase_json))
    elif firebase_path:
        cred = credentials.Certificate(firebase_path)
    else:
        raise ValueError("Firebase 인증 정보가 없습니다.")

    firebase_admin.initialize_app(cred)

# Firestore 데이터베이스 연결
db = firestore.client()

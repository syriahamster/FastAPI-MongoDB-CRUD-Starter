import os
import json
import pymongo
import schedule
import time
from datetime import datetime
from bson.json_util import dumps

# 환경변수로부터 설정값 읽기
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "testdb")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/backup")

client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

def backup_database():
    backup_data = {}
    for collection_name in db.list_collection_names():
        # BSON 타입을 JSON으로 변환하여 저장
        backup_data[collection_name] = json.loads(dumps(db[collection_name].find({})))
    return backup_data

def perform_backup():
    # 타임스탬프를 포함한 파일명 생성 (예: backup_20250319_040000.json)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"backup_{timestamp}.json")
    print(f"백업 시작: {output_file}")
    
    backup_data = backup_database()
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, indent=4, ensure_ascii=False)
    print(f"백업 완료: {output_file}")
    
    # 백업 디렉토리 내 파일 수 제한 (최대 3개)
    files = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR)
             if f.startswith("backup_") and f.endswith(".json")]
    files.sort()  # 파일명에 포함된 타임스탬프를 기준으로 정렬됨
    if len(files) > 3:
        for file_to_remove in files[:-3]:
            os.remove(file_to_remove)
            print(f"오래된 백업 파일 삭제: {file_to_remove}")

def main():
    # 매일 04:00에 perform_backup 함수를 실행하도록 스케줄링
    schedule.every().day.at("04:00").do(perform_backup)
    print("매일 04:00 백업 스케줄이 등록되었습니다.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 스케줄 확인

if __name__ == '__main__':
    main()

import os
import json
import pymongo
import schedule
import time
from datetime import datetime
from bson.json_util import dumps

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "testdb")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/backup")

client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

def backup_database():
    backup_data = {}
    for collection_name in db.list_collection_names():
        backup_data[collection_name] = json.loads(dumps(db[collection_name].find({})))
    return backup_data

def perform_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"backup_{timestamp}.json")
    print(f"Backup started: {output_file}")
    
    backup_data = backup_database()
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, indent=4, ensure_ascii=False)
    print(f"백업 완료: {output_file}")
    
    # Limit the number of files in the backup directory (maximum 3)
    files = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR)
             if f.startswith("backup_") and f.endswith(".json")]
    files.sort()  # sort by timestamp
    if len(files) > 3:
        for file_to_remove in files[:-3]:
            os.remove(file_to_remove)
            print(f"Old backup file removed: {file_to_remove}")

def main():
    schedule.every().day.at("04:00").do(perform_backup)
    print("Daily 04:00 backup schedule has been set.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # check every minute

if __name__ == '__main__':
    main()

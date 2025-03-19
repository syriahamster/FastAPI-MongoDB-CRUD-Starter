from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Optional
import os

app = FastAPI()

# MongoDB 연결 정보 (docker-compose로 띄운 컨테이너에 연결)
MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.testdb
item_collection = database.get_collection("items")

# ObjectId를 위한 Pydantic 커스텀 타입
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class Item(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Item name",
                "description": "Item description"
            }
        }

# 업데이트 시 사용할 모델 (PUT 시 사용)
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True

def item_helper(item) -> dict:
    return {
        "_id": str(item["_id"]),
        "name": item["name"],
        "description": item.get("description", "")
    }

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    item = item.dict(by_alias=True)
    new_item = await item_collection.insert_one(item)
    created_item = await item_collection.find_one({"_id": new_item.inserted_id})
    return item_helper(created_item)

@app.get("/items/", response_model=list[Item])
async def get_items():
    items = []
    async for item in item_collection.find():
        items.append(item_helper(item))
    return items

@app.get("/items/{id}", response_model=Item)
async def get_item(id: str):
    if (item := await item_collection.find_one({"_id": ObjectId(id)})) is not None:
        return item_helper(item)
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{id}")
async def update_item(id: str, item: ItemUpdate):
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id format")
    
    # 업데이트할 데이터만 추출 (제공되지 않은 필드는 제외)
    update_data = item.dict(exclude_unset=True)
    
    # _id 또는 id 필드가 포함되어 있다면 제거 (immutable 필드)
    update_data.pop("id", None)
    update_data.pop("_id", None)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")
    
    # 비동기 update_one 호출: await를 사용하여 Future 객체가 아닌 실제 결과에 접근합니다.
    result = await item_collection.update_one({"_id": oid}, {"$set": update_data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    updated_item = await item_collection.find_one({"_id": oid})
    if updated_item:
        return item_helper(updated_item)
    else:
        raise HTTPException(status_code=404, detail="Item not found after update")

@app.delete("/items/{id}")
async def delete_item(id: str):
    delete_result = await item_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

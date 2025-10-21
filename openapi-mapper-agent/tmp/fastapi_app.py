# tmp/fastapi_app.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
async def read_items():
    return {"message": "Read items"}

@app.post("/items/")
async def create_item(item: dict):
    return {"message": "Item created", "item": item}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"message": f"Read item {item_id}"}

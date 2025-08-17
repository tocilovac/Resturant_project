from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import  Optional

from Database import init_db, seed_burgers_if_empty
from Auth import register_user, login_user, get_user_id_by_username
from orders import validate_and_place_order, list_menu, list_user_orders


app = FastAPI(title="Restaurant API", version="0.1.0")

class registerrequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=3)

class loginrequest(BaseModel):
    username: str
    password: str

class OrderRequest(BaseModel):
    user_id: int
    item_id: int
    quantity: int = Field(gt=0)

@app.on_event("startup")
def on_startup():
    init_db()
    seed_burgers_if_empty() #comment out if you don't want auto-seeding

@app.get("/menu")
def get_menu():
    return {"items": list_menu()}

@app.post("/register")
def api_register(req: registerrequest):
    ok, msg = register_user(req.username, req.password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)    
    
    user_id = get_user_id_by_username(req.username)
    return {"message": msg, "user_id": user_id}

@app.post("/login")
def api_login(req: loginrequest):
    ok, msg, user_id = login_user(req.username, req.password)
    if not ok or user_id is None:
        raise HTTPException(status_code=401, detail=msg)
    return {"message": msg, "user_id": user_id}

@app.post("/order")
def api_order(req: OrderRequest):
    result = validate_and_place_order(req.user_id, req.item_id, req.quantity)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@app.get("/orders/{user_id}")
def api_user_orders(user_id: int):
    return {"orders": list_user_orders(user_id)}

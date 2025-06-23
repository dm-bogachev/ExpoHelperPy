from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from UserService import UserService
from UserData import UserCreate, UserUpdate, UserResponse

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Запускаем TCP сервер в фоне
#     asyncio.create_task(robot.start())
#     yield

app = FastAPI(
    root_path="/api/database",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    # lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users", response_model=List[UserResponse])
def get_all_users():
    users = UserService.get_all_users()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/by_chat/{chat_id}", response_model=List[UserResponse])
def get_users_by_chat_id(chat_id: int):
    users = UserService.get_users_by_chat_id(chat_id)
    if not users:
        raise HTTPException(status_code=404, detail="No users found with this chat_id")
    return users

@app.get("/users/by_status/{status}", response_model=List[UserResponse])
def get_users_by_status(status: int):
    users = UserService.get_users_by_status(status)
    if not users:
        raise HTTPException(status_code=404, detail="No users found with this status")
    return users

@app.post("/users", response_model=UserResponse)
def add_user(user: UserCreate):
    UserService.add_user(**user.dict())
    new_user = UserService.get_users_by_chat_id(user.chat_id)
    return new_user[-1]

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate):
    UserService.update_user(user_id, **user.dict())
    updated_user = UserService.get_user(user_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    UserService.delete_user(user_id)
    return {"detail": "User deleted"}


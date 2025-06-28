from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from typing import List, Optional, Any

status_list = {
    -1: "Created",
    0: "Registered",
    1: "Recorded",
    2: "Processed",
    3: "Uploaded",
    4: "WaitSubscription",
    5: "Sent",
    10: "Recording",
    20: "Processing",
}

Base = declarative_base()

class UserData(Base):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    chat_id = Column(Integer)
    status = Column(Integer)
    video_link = Column(String)
    recorded_file_name = Column(String)
    processed_file_name = Column(String)
   
class UserBase(BaseModel):
    chat_id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[int] = -1
    video_link: Optional[str] = None
    recorded_file_name: Optional[str] = None
    processed_file_name: Optional[str] = None

class UserCreate(UserBase):
    chat_id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[int] = -1
    video_link: Optional[str] = None
    recorded_file_name: Optional[str] = None
    processed_file_name: Optional[str] = None

class UserUpdate(BaseModel):
    chat_id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[int] = None
    video_link: Optional[str] = None
    recorded_file_name: Optional[str] = None
    processed_file_name: Optional[str] = None

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
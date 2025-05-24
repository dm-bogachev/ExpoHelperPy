from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserData(Base):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String)
    phone_number = Column(String)
    email = Column(String)
    company_name = Column(String)
    position = Column(String)
    user_interest = Column(String)
    chat_id = Column(Integer, unique=True, nullable=False)
    video_link = Column(String)
    is_subscribed = Column(Boolean, default=False)
    service_interest = Column(Boolean, default=False)
    questionnaire_status = Column(Integer, default=0)
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from UserData import Base, UserData
from Config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class UserService:
    _engine = None
    _Session = None

    @classmethod
    def init(cls):
        db_name = Config.get('database_name')
        db_url = f"sqlite:///{db_name}"
        if cls._engine is None:
            logger.info("Initializing database engine using URL: %s", db_url)
            cls._engine = create_engine(db_url, echo=False)
            if not os.path.exists(db_name):
                logger.info("Database file '%s' not found. Creating new database.", db_name)
                Base.metadata.create_all(cls._engine)
            cls._Session = sessionmaker(bind=cls._engine)
            logger.info("Database engine initialized.")

    @classmethod
    def add_user(cls, **kwargs):
        logger.info("Adding new user with chat_id: %s", kwargs.get("chat_id"))
        with cls._Session() as session:
            user = UserData(**kwargs)
            session.add(user)
            session.commit()
            logger.info("User added successfully.")

    @classmethod
    def add_user_from_userdata(cls, user_data):
        logger.info("Adding user from userdata with chat_id: %s", user_data.chat_id)
        with cls._Session() as session:
            user = UserData(
                full_name=user_data.full_name,
                phone_number=user_data.phone_number,
                email=user_data.email,
                company_name=getattr(user_data, "company_name", None),
                position=getattr(user_data, "position", None),
                user_interest=getattr(user_data, "user_interest", None),
                chat_id=user_data.chat_id,
                video_link=getattr(user_data, "video_link", None),
                is_subscribed=getattr(user_data, "is_subscribed", None),
                service_interest=getattr(user_data, "service_interest", None)
            )
            session.add(user)
            session.commit()
            logger.info("User from userdata added successfully.")

    @classmethod
    def get_user_by_chat_id(cls, chat_id):
        logger.info("Fetching user with chat_id: %s", chat_id)
        with cls._Session() as session:
            user = session.query(UserData).filter_by(chat_id=chat_id).first()
            if user:
                logger.info("User found: %s", user.full_name)
            else:
                logger.warning("User with chat_id %s not found", chat_id)
            return user

    @classmethod
    def update_user(cls, chat_id, **kwargs):
        logger.info("Updating user with chat_id: %s", chat_id)
        with cls._Session() as session:
            user = session.query(UserData).filter_by(chat_id=chat_id).first()
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        logger.info("Updating field '%s' to '%s'", key, value)
                        setattr(user, key, value)
                session.commit()
                logger.info("User updated successfully.")
            else:
                logger.warning("User with chat_id %s not found. Update skipped.", chat_id)

    @classmethod
    def update_user_from_userdata(cls, user_data):
        logger.info("Updating user from userdata with chat_id: %s", user_data.chat_id)
        with cls._Session() as session:
            user = session.query(UserData).filter_by(chat_id=user_data.chat_id).first()
            if user:
                for key, value in user_data.__dict__.items():
                    if key.startswith("_"):  # пропускаем служебные поля
                        continue
                    if hasattr(user, key):
                        logger.info("Updating field '%s' to '%s'", key, value)
                        setattr(user, key, value)
                session.commit()
                logger.info("User from userdata updated successfully.")
            else:
                logger.warning("User with chat_id %s not found. Update skipped.", user_data.chat_id)

    @classmethod
    def delete_user(cls, chat_id):
        logger.info("Deleting user with chat_id: %s", chat_id)
        with cls._Session() as session:
            user = session.query(UserData).filter_by(chat_id=chat_id).first()
            if user:
                session.delete(user)
                session.commit()
                logger.info("User deleted successfully.")
            else:
                logger.warning("User with chat_id %s not found. Delete skipped.", chat_id)

    @classmethod
    def get_all_users(cls):
        logger.info("Fetching all users from the database.")
        with cls._Session() as session:
            users = session.query(UserData).all()
            logger.info("Fetched %d users", len(users))
            return users

if __name__ == "__main__":
    # Example usage
    Config.init()
    UserService.init()
    
    UserService.add_user(
        full_name="Иван Иванов",
        phone_number="+71234567890",
        email="ivan@example.com",
        company_name="ООО Пример",
        position="Инженер",
        user_interest="AI",
        chat_id=9287654321,
        video_link="https://video.link",
        is_subscribed=True,
        service_interest=True
    )

    user = UserService.get_user_by_chat_id(987654321)
    print(user.full_name)
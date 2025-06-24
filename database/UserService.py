import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from UserData import Base, UserData
from Config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)

if os.environ.get("DOCKER"):
    database_path = "/shared_data"
else:
    database_path = os.path.join(os.path.dirname(__file__), 'local')
os.makedirs(database_path, exist_ok=True)


class UserService:
    _engine = None
    _Session = None

    @classmethod
    def init(cls):
        db_name = Config.get('database_name')
        db_url = f"sqlite:///{database_path}/{db_name}"
        if cls._engine is None:
            logger.info("Initializing database engine using URL: %s", db_url)
            cls._engine = create_engine(db_url, echo=False)
            if not os.path.exists(db_name):
                logger.info("Database file '%s' not found. Creating new database.", db_name)
                Base.metadata.create_all(cls._engine)
            cls._Session = sessionmaker(bind=cls._engine)
            logger.info("Database engine initialized.")

    @classmethod
    def get_all_users(cls):
        logger.debug("Fetching all users from the database.")
        with cls._Session() as session:
            users = session.query(UserData).all()
            logger.debug("Fetched %d users", len(users))
            return users

    @classmethod
    def get_user(cls, id):
        logger.debug("Fetching user with id: %s", id)
        with cls._Session() as session:
            user = session.query(UserData).filter_by(id=id).first()
            if user:
                logger.debug("User found: %s", user.name)
            else:
                logger.warning("User with id %s not found", id)
            return user
        
    @classmethod
    def get_users_by_chat_id(cls, chat_id):
        logger.debug("Fetching user with chat_id: %s", chat_id)
        with cls._Session() as session:
            users = session.query(UserData).filter_by(chat_id=chat_id).all()
            if users:
                logger.debug("Found %d users with chat_id %s", len(users), chat_id)
            else:
                logger.warning("User with chat_id %s not found", chat_id)
            return users

    @classmethod
    def get_users_by_status(cls, status):
        logger.debug("Fetching users with status: %s", status)
        with cls._Session() as session:
            users = session.query(UserData).filter_by(status=status).all()
            if users:
                logger.debug("Found %d users with status %s", len(users), status)
            else:
                logger.warning("No users found with status %s", status)
            return users
        
    @classmethod
    def add_user(cls, **kwargs):
        logger.debug("Adding new user with chat_id: %s", kwargs.get("chat_id"))
        with cls._Session() as session:
            user = UserData(**kwargs)
            session.add(user)
            session.commit()
            logger.debug("User added successfully.")

    @classmethod
    def update_user(cls, idd, **kwargs):
        logger.debug("Updating user with id: %s", idd)
        with cls._Session() as session:
            user = session.query(UserData).filter_by(id=idd).first()
            if user:
                for key, value in kwargs.items():
                    if key.startswith("_"):
                        continue
                    if hasattr(user, key) and value is not None:
                        logger.debug("Updating field '%s' to '%s'", key, value)
                        setattr(user, key, value)
                session.commit()
                logger.debug("User updated successfully.")
            else:
                logger.warning("User with id %s not found. Update skipped.", idd)

    @classmethod
    def delete_user(cls, idd):
        logger.debug("Deleting user with id: %s", idd)
        with cls._Session() as session:
            user = session.query(UserData).filter_by(id=idd).first()
            if user:
                session.delete(user)
                session.commit()
                logger.debug("User deleted successfully.")
            else:
                logger.warning("User with id %s not found. Delete skipped.", idd)

UserService.init()

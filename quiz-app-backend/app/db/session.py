# filename: app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from app.core import settings_core

engine = create_engine(settings_core.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Import all the models here to ensure they are registered with SQLAlchemy
    from app.models import UserModel, QuestionSetModel, QuestionModel, AnswerChoiceModel, RevokedTokenModel
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

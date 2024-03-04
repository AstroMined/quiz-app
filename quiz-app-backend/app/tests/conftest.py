# filename: conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
# from app.core.config import settings
# from app.tests.utils.user import authentication_token_from_email
# from app.tests.utils.utils import get_superuser_token_headers
from main import app  # Adjust the import path as needed
from app.schemas.user import UserCreate
from app.crud.crud_user import create_user, remove_user
from app.db.session import get_db
import random
import string
from sqlalchemy import create_engine
from app.db.base_class import Base


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=8))

@pytest.fixture(scope="session")
def db_session():
    # Setup for database session
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)  # Create all tables for the test database
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def test_app(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield app
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def client(test_app):
    with TestClient(test_app) as c:
        yield c

@pytest.fixture(scope="session")
def test_user(db_session):
    db = db_session
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = create_user(db=db, user=user_in)
    db.commit()
    yield user, password
    remove_user(db=db, user_id=user.id)
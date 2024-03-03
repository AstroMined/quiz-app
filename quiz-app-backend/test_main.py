# filename: test_main.py
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app  # Adjust the import path based on your project structure
from app.db.base_class import Base
from app.db.session import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_user_registration():
    response = client.post(
        "/register/",
        json={"username": "testuser3", "password": "testpassword3"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser3"
    # Add more assertions as needed

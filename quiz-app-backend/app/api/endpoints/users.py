# filename: app/api/endpoints/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/users/")
def read_users():
    return [{"username": "user1"}, {"username": "user2"}]

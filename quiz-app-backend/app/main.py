# filename: main.py

from fastapi import FastAPI, Request, HTTPException, status
from app.api.endpoints import (
    users as users_router,
    register as register_router,
    token as token_router,
    auth as auth_router,
    question_sets as question_sets_router,
    questions as questions_router,
    user_responses as user_responses_router
)
from app.db import get_db, SessionLocal
from app.models import RevokedToken

app = FastAPI()

# Use the aliased name for the router
app.include_router(users_router.router, tags=["User Management"])
app.include_router(register_router.router, tags=["Authentication"])
app.include_router(token_router.router, tags=["Authentication"])
app.include_router(auth_router.router, tags=["Authentication"])
app.include_router(question_sets_router.router, tags=["Question Sets"])
app.include_router(questions_router.router, tags=["Questions"])
app.include_router(user_responses_router.router, tags=["User Responses"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Middleware to check if the token is blacklisted
@app.middleware("http")
async def check_blacklist(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        db = SessionLocal()
        if db.query(RevokedToken).filter(RevokedToken.token == token).first():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
        db.close()
    response = await call_next(request)
    return response

@app.middleware("http")
async def check_revoked_token(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        db = next(get_db())
        revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
        if revoked_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    response = await call_next(request)
    return response

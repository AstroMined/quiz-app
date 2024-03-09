# filename: main.py
from fastapi import FastAPI
from app.api.endpoints import (
    users as users_router,
    register as register_router,
    token as token_router,
    question_sets as question_sets_router,
    questions as questions_router,
    user_responses as user_responses_router
)
# Import models if necessary, but it looks like you might not need to import them here unless you're initializing them
from app.db.base_class import Base  # This might not be needed here if you're not directly using Base in main.py
from app.models import (
    answer_choices,
    user_responses,
    users,
    questions,
    subjects,
    topics,
    subtopics
)

app = FastAPI()

# Use the aliased name for the router
app.include_router(users_router.router)
app.include_router(register_router.router)
app.include_router(token_router.router)
app.include_router(question_sets_router.router)
app.include_router(questions_router.router, prefix="/questions", tags=["Questions"])
app.include_router(user_responses_router.router, prefix="/user-responses", tags=["User Responses"])

@app.get("/")
def read_root():
    return {"Hello": "World"}
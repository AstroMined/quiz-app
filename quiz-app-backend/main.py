# filename: main.py
from fastapi import FastAPI
from app.api.endpoints import (
    # Alias the router import
    users as users_router,
    register as register_router,
    token as token_router
)
# Import models if necessary, but it looks like you might not need to import them here unless you're initializing them
from app.db.base_class import Base  # This might not be needed here if you're not directly using Base in main.py
from app.models import (
    # Adjust as necessary
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

@app.get("/")
def read_root():
    return {"Hello": "World"}
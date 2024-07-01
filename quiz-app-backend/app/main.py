# filename: main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import authentication as authentication_router
from app.api.endpoints import filters as filters_router
from app.api.endpoints import groups as groups_router
from app.api.endpoints import leaderboard as leaderboard_router
from app.api.endpoints import question_sets as question_sets_router
from app.api.endpoints import question as question_router
from app.api.endpoints import questions as questions_router
from app.api.endpoints import register as register_router
from app.api.endpoints import subjects as subjects_router
from app.api.endpoints import topics as topics_router
from app.api.endpoints import user_responses as user_responses_router
from app.api.endpoints import users as users_router
from app.middleware.authorization_middleware import AuthorizationMiddleware
from app.middleware.blacklist_middleware import BlacklistMiddleware
from app.middleware.cors_middleware import add_cors_middleware
from app.services.permission_generator_service import generate_permissions
from app.services.validation_service import register_validation_listeners
from app.db.session import get_db

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs when the application starts up
    app.state.db = get_db()
    db = next(app.state.db)
    generate_permissions(app, db)
    register_validation_listeners()
    yield
    # Anything after the yield runs when the application shuts down
    app.state.db.close()

app.router.lifespan_context = lifespan

# app.add_middleware(AuthorizationMiddleware)
# app.add_middleware(BlacklistMiddleware)
# add_cors_middleware(app)

# Use the aliased name for the router
app.include_router(authentication_router.router, tags=["Authentication"])
app.include_router(register_router.router, tags=["Authentication"])
app.include_router(filters_router.router, tags=["Filters"])
app.include_router(groups_router.router, tags=["Groups"])
app.include_router(leaderboard_router.router, tags=["Leaderboard"])
app.include_router(question_sets_router.router, tags=["Question Sets"])
app.include_router(question_router.router, tags=["Question"])
app.include_router(questions_router.router, tags=["Questions"])
app.include_router(subjects_router.router, tags=["Subjects"])
app.include_router(user_responses_router.router, tags=["User Responses"])
app.include_router(users_router.router, tags=["User Management"])
app.include_router(topics_router.router, tags=["Topics"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

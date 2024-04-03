
# Directory: /code/quiz-app/quiz-app-backend/app

## File: __init__.py
```py
from .main import app
```

## File: main.py
```py
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

```

# Directory: /code/quiz-app/quiz-app-backend/app/schemas

## File: __init__.py
```py
from .answer_choices import AnswerChoice, AnswerChoiceBase, AnswerChoiceCreate
from .auth import LoginForm
from .questions import QuestionBase, Question, QuestionCreate, QuestionUpdate
from .question_sets import QuestionSetCreate, QuestionSetBase, QuestionSet, QuestionSetUpdate
from .subtopics import Subtopic, SubtopicBase, SubtopicCreate
from .token import Token
from .user import UserCreate, UserLogin, UserBase, User
from .user_responses import UserResponseBase, UserResponse, UserResponseCreate

```

## File: answer_choices.py
```py
# app/schemas/answer_choices.py
from pydantic import BaseModel

class AnswerChoiceBase(BaseModel):
    """
    The base schema for an AnswerChoice.

    Attributes:
        text (str): The text of the answer choice.
        is_correct (bool): Indicates whether the answer choice is correct.
    """
    text: str
    is_correct: bool

class AnswerChoiceCreate(AnswerChoiceBase):
    """
    The schema for creating an AnswerChoice.

    Inherits from AnswerChoiceBase.
    """
    pass

class AnswerChoice(AnswerChoiceBase):
    """
    The schema representing a stored AnswerChoice.

    Inherits from AnswerChoiceBase and includes additional attributes.

    Attributes:
        id (int): The unique identifier of the answer choice.
    """
    id: int

    class Config:
        from_attributes = True

```

## File: auth.py
```py
from pydantic import BaseModel, Field

class LoginForm(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

```

## File: question_sets.py
```py
# filename: app/schemas/question_sets.py
"""
This module defines the Pydantic schemas for the QuestionSet model.

The schemas are used for input validation and serialization/deserialization of QuestionSet objects.
"""

from pydantic import BaseModel

class QuestionSetBase(BaseModel):
    """
    The base schema for a QuestionSet.

    Attributes:
        name (str): The name of the question set.
    """
    name: str

class QuestionSetCreate(QuestionSetBase):
    """
    The schema for creating a QuestionSet.

    Inherits from QuestionSetBase.
    """
    pass

class QuestionSetUpdate(QuestionSetBase):
    """
    The schema for updating a QuestionSet.

    Inherits from QuestionSetBase.
    """
    pass

class QuestionSet(QuestionSetBase):
    """
    The schema representing a stored QuestionSet.

    Inherits from QuestionSetBase and includes additional attributes.

    Attributes:
        id (int): The unique identifier of the question set.
    """
    id: int

    class Config:
        from_attributes = True

```

## File: questions.py
```py
# filename: app/schemas/questions.py
"""
This module defines the Pydantic schemas for the Question model.

The schemas are used for input validation and serialization/deserialization of Question objects.
"""

from typing import List
from pydantic import BaseModel
from app.schemas import AnswerChoiceCreate, AnswerChoice

class QuestionBase(BaseModel):
    """
    The base schema for a Question.

    Attributes:
        text (str): The text of the question.
    """
    text: str

class QuestionCreate(QuestionBase):
    """
    The schema for creating a Question.

    Inherits from QuestionBase.
    """
    subtopic_id: int
    question_set_id: int
    answer_choices: List[AnswerChoiceCreate]
    explanation: str

class QuestionUpdate(QuestionBase):
    """
    The schema for updating a Question.

    Inherits from QuestionBase.
    """
    pass

class Question(QuestionBase):
    """
    The schema representing a stored Question.

    Inherits from QuestionBase and includes additional attributes.

    Attributes:
        id (int): The unique identifier of the question.
        subtopic_id (int): The ID of the associated subtopic.
        question_set_id (int): The ID of the associated question set.
    """
    id: int
    subtopic_id: int
    question_set_id: int
    answer_choices: List[AnswerChoice]

    class Config:
        from_attributes = True

```

## File: subtopics.py
```py
# schemas/subtopics.py

from pydantic import BaseModel

class SubtopicBase(BaseModel):
    name: str

class SubtopicCreate(SubtopicBase):
    pass

class Subtopic(SubtopicBase):
    id: int

    class Config:
        from_attributes = True
```

## File: token.py
```py
# filename: app/schemas/token.py
"""
This module defines the Pydantic schema for the Token model.
"""

from pydantic import BaseModel

class Token(BaseModel):
    """
    The schema representing an access token.

    Attributes:
        access_token (str): The access token.
        token_type (str): The type of the token.
    """
    access_token: str
    token_type: str

```

## File: user.py
```py
# filename: app/schemas/user.py
"""
This module defines the Pydantic schemas for the User model.
"""

import string
from pydantic import BaseModel, validator

class UserBase(BaseModel):
    """
    The base schema for a User.
    """
    username: str

class UserCreate(UserBase):
    """
    The schema for creating a User.
    """
    password: str

    @validator('password')
    def validate_password(cls, password):
        """
        Validate the password.

        The password must be at least 8 characters long and contain at least one digit,
        one uppercase letter, one lowercase letter, and one special character.
        """
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in password):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in password):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char in string.punctuation for char in password):
            raise ValueError('Password must contain at least one special character')
        if any(char.isspace() for char in password):
            raise ValueError('Password must not contain whitespace characters')
        weak_passwords = ['password', '123456', 'qwerty', 'abc123', 'letmein', 'admin', 'welcome', 'monkey', '111111', 'iloveyou']
        if password.lower() in weak_passwords:
            raise ValueError('Password is too common. Please choose a stronger password.')
        return password

class UserLogin(BaseModel):
    """
    The schema for user login.

    Attributes:
        username (str): The username of the user.
        password (str): The password of the user.
    """
    username: str
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

```

## File: user_responses.py
```py
# filename: app/schemas/user_responses.py
"""
This module defines the Pydantic schemas for the UserResponse model.

The schemas are used for input validation and serialization/deserialization of UserResponse objects.
"""

from datetime import datetime
from pydantic import BaseModel

class UserResponseBase(BaseModel):
    """
    The base schema for a UserResponse.

    Attributes:
        user_id (int): The ID of the user.
        question_id (int): The ID of the question.
        answer_choice_id (int): The ID of the answer choice.
        is_correct (bool): Indicates whether the user's response is correct.
    """
    user_id: int
    question_id: int
    answer_choice_id: int
    is_correct: bool

class UserResponseCreate(UserResponseBase):
    """
    The schema for creating a UserResponse.

    Inherits from UserResponseBase.
    """
    pass

class UserResponse(UserResponseBase):
    """
    The schema representing a stored UserResponse.

    Inherits from UserResponseBase and includes additional attributes.

    Attributes:
        id (int): The unique identifier of the user response.
        timestamp (datetime): The timestamp of the user's response.
    """
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

```

# Directory: /code/quiz-app/quiz-app-backend/app/services

## File: __init__.py
```py
# filename: app/services/__init__.py

from .auth_service import authenticate_user
from .user_service import get_current_user, oauth2_scheme

```

## File: auth_service.py
```py
# filename: app/services/auth_service.py
"""
This module provides authentication and authorization services.
"""

from sqlalchemy.orm import Session
from app.crud import get_user_by_username
from app.core import verify_password
from app.models import User

def authenticate_user(db: Session, username: str, password: str) -> User:
    """
    Authenticate a user.

    Args:
        db (Session): The database session.
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        User: The authenticated user, or False if authentication fails.
    """
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if not user.is_active:
        return False
    return user

```

## File: user_service.py
```py
# filename: app/services/user_service.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core import decode_access_token
from app.crud import get_user_by_username
from app.db import get_db
from app.models import RevokedToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to get the current authenticated user.

    Args:
        token (str): The JWT access token.
        db (Session): The database session.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid, expired, or revoked, or if the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
        if revoked_token:
            raise credentials_exception
        user = get_user_by_username(db, username=username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

```

# Directory: /code/quiz-app/quiz-app-backend/app/crud

## File: __init__.py
```py
# filename: app/crud/__init__.py

from .crud_question_sets import create_question_set, get_question_sets, update_question_set, delete_question_set
from .crud_questions import create_question, get_question, get_questions, update_question, delete_question
from .crud_user import create_user, remove_user
from .crud_user_responses import create_user_response, get_user_responses
from .crud_user_utils import get_user_by_username
from .crud_subtopics import create_subtopic

```

## File: crud_question_sets.py
```py
# filename: app/crud/crud_question_sets.py
"""
This module provides CRUD operations for question sets.
"""

from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import QuestionSet
from app.schemas import QuestionSetCreate, QuestionSetUpdate

def get_question_sets(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSet]:
    """
    Retrieve a list of question sets.

    Args:
        db (Session): The database session.
        skip (int): The number of question sets to skip.
        limit (int): The maximum number of question sets to retrieve.

    Returns:
        List[QuestionSet]: The list of question sets.
    """
    return db.query(QuestionSet).offset(skip).limit(limit).all()

def create_question_set(db: Session, question_set: QuestionSetCreate) -> QuestionSet:
    """
    Create a new question set.
    """
    existing_question_set = db.query(QuestionSet).filter(QuestionSet.name == question_set.name).first()
    if existing_question_set:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Question set with name '{question_set.name}' already exists.")
    
    db_question_set = QuestionSet(**question_set.dict())
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def update_question_set(db: Session, question_set_id: int, question_set: QuestionSetUpdate) -> QuestionSet:
    db_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if not db_question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    update_data = question_set.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_question_set, field, value)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def delete_question_set(db: Session, question_set_id: int) -> bool:
    db_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if not db_question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    db.delete(db_question_set)
    db.commit()
    return True

```

## File: crud_questions.py
```py
# filename: app/crud/crud_questions.py
"""
This module provides CRUD operations for questions.

It includes functions for creating, retrieving, updating, and deleting questions.
"""

from typing import List
from sqlalchemy.orm import Session
from app.models import Question, AnswerChoice
from app.schemas import QuestionCreate, QuestionUpdate

def create_question(db: Session, question: QuestionCreate) -> Question:
    db_question = Question(
        text=question.text,
        question_set_id=question.question_set_id,
        subtopic_id=question.subtopic_id,
        explanation=question.explanation
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.answer_choices:
        db_choice = AnswerChoice(
            text=choice.text,
            is_correct=choice.is_correct,
            question=db_question
        )
        db.add(db_choice)

    db.commit()
    return db_question

def get_questions(db: Session, skip: int = 0, limit: int = 100) -> List[Question]:
    """
    Retrieve a list of questions.

    Args:
        db (Session): The database session.
        skip (int): The number of questions to skip.
        limit (int): The maximum number of questions to retrieve.

    Returns:
        List[Question]: The list of questions.
    """
    questions = db.query(Question).offset(skip).limit(limit).all()
    return questions

def get_question(db: Session, question_id: int) -> Question:
    """
    Retrieve a question by ID.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.

    Returns:
        Question: The retrieved question, or None if not found.
    """
    return db.query(Question).filter(Question.id == question_id).first()

def update_question(db: Session, question_id: int, question: QuestionUpdate) -> Question:
    """
    Update a question.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to update.
        question (QuestionUpdate): The updated question data.

    Returns:
        Question: The updated question, or None if not found.
    """
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if db_question:
        update_data = question.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
    return db_question

def delete_question(db: Session, question_id: int) -> bool:
    """
    Delete a question.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question to delete.

    Returns:
        bool: True if the question was deleted, False otherwise.
    """
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False
```

## File: crud_subtopics.py
```py
# crud/crud_subtopics.py

from sqlalchemy.orm import Session
from app.models import Subtopic
from app.schemas import SubtopicCreate

def create_subtopic(db: Session, subtopic: SubtopicCreate) -> Subtopic:
    db_subtopic = Subtopic(**subtopic.dict())
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)
    return db_subtopic
```

## File: crud_user.py
```py
# filename: app/crud/crud_user.py
"""
This module provides CRUD operations for users.
"""

from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from app.core.security import get_password_hash  # Import from app.core.security

def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db (Session): The database session.
        user (UserCreate): The user data.

    Returns:
        User: The created user.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def remove_user(db: Session, user_id: int) -> User:
    """
    Remove a user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to remove.

    Returns:
        User: The removed user, or None if the user doesn't exist.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    return None

```

## File: crud_user_responses.py
```py
# filename: app/crud/crud_user_responses.py
"""
This module provides CRUD operations for user responses.

It includes functions for creating and retrieving user responses.
"""

from typing import List
from sqlalchemy.orm import Session
from app.models import UserResponse
from app.schemas import UserResponseCreate

def create_user_response(db: Session, user_response: UserResponseCreate) -> UserResponse:
    """
    Create a new user response.

    Args:
        db (Session): The database session.
        user_response (UserResponseCreate): The user response data.

    Returns:
        UserResponse: The created user response.
    """
    db_user_response = UserResponse(**user_response.dict())
    db.add(db_user_response)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

def get_user_responses(db: Session, skip: int = 0, limit: int = 100) -> List[UserResponse]:
    """
    Retrieve a list of user responses.

    Args:
        db (Session): The database session.
        skip (int): The number of user responses to skip.
        limit (int): The maximum number of user responses to retrieve.

    Returns:
        List[UserResponse]: The list of user responses.
    """
    return db.query(UserResponse).offset(skip).limit(limit).all()
```

## File: crud_user_utils.py
```py
# filename: app/crud/crud_user_utils.py
"""
This module provides utility functions for user-related operations.
"""

from sqlalchemy.orm import Session
from app.models import User

def get_user_by_username(db: Session, username: str) -> User:
    """
    Retrieve a user by username.

    Args:
        db (Session): The database session.
        username (str): The username of the user.

    Returns:
        User: The user with the specified username.
    """
    return db.query(User).filter(User.username == username).first()

```

# Directory: /code/quiz-app/quiz-app-backend/app/db

## File: __init__.py
```py
from .base_class import Base
from .session import get_db, init_db, SessionLocal
```

## File: base_class.py
```py
# filename: app/db/base_class.py
"""
This module defines the base class for SQLAlchemy models.

It provides a declarative base class that can be used to create database models.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

## File: session.py
```py
# filename: app/db/session.py
"""
This module provides database session management.

It includes functions for creating database engines, sessions, and handling database connections.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base

# Development database
SQLALCHEMY_DATABASE_URL = "sqlite:///./quiz_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """
    Initialize the database.

    This function creates all the tables defined in the models.
    """
    Base.metadata.create_all(bind=engine)

def get_db() -> SessionLocal:
    """
    Get a database session.

    This function creates a new database session and closes it when the request is finished.

    Yields:
        SessionLocal: A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```

# Directory: /code/quiz-app/quiz-app-backend/app/api

## File: __init__.py
```py
# filename: app/api/__init__.py
"""
This module serves as the main entry point for the API package.

It can be used to perform any necessary initialization or configuration for the API package.
"""
```

# Directory: /code/quiz-app/quiz-app-backend/app/api/endpoints

## File: __init__.py
```py
# filename: app/api/endpoints/__init__.py
"""
This module serves as a central point to import and organize the various endpoint routers.

It imports the router objects from each endpoint file and makes them available for use in the main FastAPI application.
"""

```

## File: auth.py
```py
# filename: app/api/endpoints/auth.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core import create_access_token, verify_password
from app.db import get_db
from app.models import User, RevokedToken
from app.schemas import Token, LoginForm

logger = logging.getLogger(__name__)

router = APIRouter()

blacklist = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: LoginForm, db: Session = Depends(get_db)):
    """
    Endpoint to authenticate a user and generate an access token.
    """
    user = db.query(User).filter(User.username == form_data.username).first()

    if user:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Endpoint to logout the current user and invalidate the access token.
    
    Args:
        token (str): The access token to be invalidated.
        db (Session): The database session.
        
    Returns:
        dict: A success message indicating the user has been logged out.
        
    Raises:
        HTTPException: If an error occurs during token decoding or user logout.
    """
    try:
        # Check if the token is already revoked
        revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
        if revoked_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token has been revoked")

        # Revoke the token
        revoked_token = RevokedToken(token=token)
        db.add(revoked_token)
        db.commit()
        return {"message": "Successfully logged out"}

    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token") from exc
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to logout user") from exc

```

## File: question_sets.py
```py
# filename: app/api/endpoints/question_sets.py
"""
This module provides endpoints for managing question sets.

It defines routes for uploading question sets and retrieving question sets from the database.
"""

import json
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.crud import (
    get_question_sets,
    update_question_set,
    delete_question_set,
    create_question_set,
    create_question
)
from app.db import get_db
from app.schemas import (
    QuestionSet,
    QuestionSetCreate,
    QuestionSetUpdate,
    QuestionCreate
)
from app.services import get_current_user
from app.models.users import User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload-questions/")
async def upload_question_set_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Endpoint to upload a question set in JSON format.
    """
    try:
        content = await file.read()
        question_data = json.loads(content.decode('utf-8'))

        # Validate question data
        for question in question_data:
            QuestionCreate(**question)  # Validate question against schema

        # Create question set
        question_set = QuestionSetCreate(name=file.filename)
        question_set_created = create_question_set(db, question_set)

        # Create questions and associate with question set
        for question in question_data:
            question['question_set_id'] = question_set_created.id
            try:
                create_question(db, QuestionCreate(**question))
            except ValidationError as exc:
                raise HTTPException(status_code=400, detail=f"Invalid question data: {exc}")

        return {"message": "Question set uploaded successfully"}

    except (json.JSONDecodeError, ValidationError) as exc:
        logger.exception("Invalid JSON data")  # Add logging statement
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(exc)}")

    except Exception as exc:
        logger.exception("Error uploading question set")  # Add logging statement
        raise HTTPException(status_code=500, detail=f"Error uploading question set: {str(exc)}")

@router.get("/question-set/", response_model=List[QuestionSet])
def read_questions_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve question sets from the database.
    
    Args:
        skip: The number of question sets to skip (for pagination).
        limit: The maximum number of question sets to retrieve (for pagination).
        db: A database session dependency injected by FastAPI.
        
    Returns:
        A list of question set objects.
    """
    questions = get_question_sets(db, skip=skip, limit=limit)
    return questions

@router.post("/question-sets/", response_model=QuestionSet, status_code=201)
def create_question_set_endpoint(question_set: QuestionSetCreate, db: Session = Depends(get_db)):
    """
    Create a new question set.
    """
    return create_question_set(db=db, question_set=question_set)

@router.get("/question-sets/", response_model=List[QuestionSet])
def read_question_sets_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of question sets.
    """
    question_sets = get_question_sets(db, skip=skip, limit=limit)
    return question_sets

@router.put("/question-sets/{question_set_id}", response_model=QuestionSet)
def update_question_set_endpoint(question_set_id: int, question_set: QuestionSetUpdate, db: Session = Depends(get_db)):
    """
    Update a question set.

    Args:
        question_set_id (int): The ID of the question set to update.
        question_set (QuestionSetUpdate): The updated question set data.
        db (Session): The database session.

    Returns:
        QuestionSet: The updated question set.

    Raises:
        HTTPException: If the question set is not found.
    """
    db_question_set = update_question_set(db, question_set_id=question_set_id, question_set=question_set)
    if db_question_set is None:
        raise HTTPException(status_code=404, detail="Question set not found")
    return db_question_set

@router.delete("/question-sets/{question_set_id}", status_code=204)
def delete_question_set_endpoint(question_set_id: int, db: Session = Depends(get_db)):
    """
    Delete a question set.

    Args:
        question_set_id (int): The ID of the question set to delete.
        db (Session): The database session.

    Raises:
        HTTPException: If the question set is not found.
    """
    deleted = delete_question_set(db, question_set_id=question_set_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question set not found")
    return Response(status_code=204)

```

## File: questions.py
```py
# filename: app/api/endpoints/questions.py
"""
This module provides endpoints for managing questions.

It defines routes for creating, retrieving, updating, and deleting questions.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.crud import (
    create_question,
    get_question,
    get_questions,
    update_question,
    delete_question
)
from app.db import get_db
from app.schemas import QuestionCreate, Question, QuestionUpdate
from app.services import get_current_user
from app.models.users import User

router = APIRouter()

@router.post("/questions/", response_model=Question, status_code=201)
def create_question_endpoint(question: QuestionCreate, db: Session = Depends(get_db)):
    """
    Create a new question.

    Args:
        question (QuestionCreate): The question data.
        db (Session): The database session.

    Returns:
        Question: The created question.
    """
    return create_question(db, question)

@router.get("/questions/{question_id}", response_model=Question)
def get_question_endpoint(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)):
    """
    Retrieve a question.

    Args:
        question_id (int): The ID of the question to retrieve.
        db (Session): The database session.

    Returns:
        Question: The question.
    """
    question = get_question(db, question_id)
    return question

@router.get("/questions/", response_model=List[Question])
def get_questions_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a list of questions.

    Args:
        skip (int): The number of questions to skip.
        limit (int): The maximum number of questions to retrieve.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        List[Question]: The list of questions.
    """
    questions = get_questions(db, skip=skip, limit=limit)
    return questions

@router.put("/questions/{question_id}", response_model=Question)
def update_question_endpoint(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)):
    """
    Update a question.

    Args:
        question_id (int): The ID of the question to update.
        question (QuestionUpdate): The updated question data.
        db (Session): The database session.

    Returns:
        Question: The updated question.

    Raises:
        HTTPException: If the question is not found.
    """
    db_question = update_question(db, question_id=question_id, question=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@router.delete("/questions/{question_id}", status_code=204)
def delete_question_endpoint(question_id: int, db: Session = Depends(get_db)):
    """
    Delete a question.

    Args:
        question_id (int): The ID of the question to delete.
        db (Session): The database session.

    Raises:
        HTTPException: If the question is not found.
    """
    deleted = delete_question(db, question_id=question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return Response(status_code=204)
```

## File: register.py
```py
# filename: app/api/endpoints/register.py
"""
This module provides an endpoint for user registration.

It defines a route for registering new users by validating the provided data and creating a new user in the database.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import get_password_hash
from app.crud import create_user, get_user_by_username
from app.db import get_db
from app.schemas import UserCreate

router = APIRouter()

@router.post("/register/", status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user.
    
    Args:
        user: A UserCreate schema object containing the user's registration information.
        db: A database session dependency injected by FastAPI.
        
    Raises:
        HTTPException: If the username is already registered.
        
    Returns:
        The newly created user object.
    """
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=422, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    user_create = UserCreate(username=user.username, password=hashed_password)
    created_user = create_user(db=db, user=user_create)
    return created_user

```

## File: token.py
```py
# filename: app/api/endpoints/token.py
"""
This module provides an endpoint for user authentication and token generation.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.services.auth_service import authenticate_user
from app.core import create_access_token, settings
from app.db import get_db
from app.schemas import Token

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint to authenticate a user and issue a JWT access token.
    
    Args:
        form_data: An OAuth2PasswordRequestForm object containing the user's login credentials.
        db: A database session dependency injected by FastAPI.
        
    Raises:
        HTTPException: If the username or password is incorrect, or if an internal server error occurs.
        
    Returns:
        Token: A Token object containing the access token and token type.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

```

## File: user_responses.py
```py
# filename: app/api/endpoints/user_responses.py
"""
This module provides endpoints for managing user responses.

It defines routes for creating and retrieving user responses.
"""

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.crud.crud_user_responses import create_user_response, get_user_responses
from app.db.session import get_db
from app.schemas.user_responses import UserResponse, UserResponseCreate
from app.models.users import User
from app.models.questions import Question
from app.models.answer_choices import AnswerChoice

router = APIRouter()

@router.post("/user-responses/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_response_endpoint(user_response: UserResponseCreate, db: Session = Depends(get_db)):
    """
    Create a new user response.

    Args:
        user_response (UserResponseCreate): The user response data.
        db (Session): The database session.

    Returns:
        UserResponse: The created user response.

    Raises:
        HTTPException: If the provided data is invalid or any referenced entities do not exist.
    """
    # Validate the user_id
    user = db.query(User).filter(User.id == user_response.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id")

    # Validate the question_id
    question = db.query(Question).filter(Question.id == user_response.question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question_id")

    # Validate the answer_choice_id
    answer_choice = db.query(AnswerChoice).filter(AnswerChoice.id == user_response.answer_choice_id).first()
    if not answer_choice:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid answer_choice_id")

    return create_user_response(db=db, user_response=user_response)

@router.get("/user-responses/", response_model=List[UserResponse])
def get_user_responses_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of user responses.

    Args:
        skip (int): The number of user responses to skip.
        limit (int): The maximum number of user responses to retrieve.
        db (Session): The database session.

    Returns:
        List[UserResponse]: The list of user responses.
    """
    user_responses = get_user_responses(db, skip=skip, limit=limit)
    return user_responses

```

## File: users.py
```py
# filename: app/api/endpoints/users.py
"""
This module provides a simple endpoint for retrieving user information.

It defines a route for retrieving a list of users (currently hardcoded).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User as UserModel
from app.crud.crud_user import create_user as create_user_crud  # Import from crud_user module
from app.schemas.user import UserCreate as UserCreateSchema, User as UserSchema
from app.services import get_current_user

router = APIRouter()

@router.get("/users/", response_model=List[UserSchema])
def read_users(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    users = db.query(UserModel).all()
    return users

@router.post("/users/", response_model=UserSchema, status_code=201)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    """
    Create a new user in the database.

    This endpoint receives user data as a request payload, validates it against
    the UserCreateSchema, and then proceeds to create a new user record in the
    database using the provided details. It returns the newly created user data
    as per the UserModelSchema.

    Args:
        user (UserCreateSchema): The user information required to create a new user.
                                  This includes, but is not limited to, the username
                                  and password.
        db (Session, optional): The database session used to perform database
                                operations. This dependency is injected by FastAPI
                                via Depends(get_db).

    Returns:
        UserModelSchema: The schema of the newly created user, which includes
                         the user's id, username, and other fields as defined
                         in the schema but not including sensitive information
                         like passwords.

    Raises:
        HTTPException: A 400 error if the user creation process fails, which
                       could occur if the username already exists.
    """
    # Attempt to create a new user in the database using CRUD operations
    try:
        new_user = create_user_crud(db=db, user=user)
        return new_user
    except Exception as e:
        # If there's an error (e.g., username already exists), raise an HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
            ) from e

```

# Directory: /code/quiz-app/quiz-app-backend/app/models

## File: __init__.py
```py
# filename: app/models/__init__.py

from .answer_choices import AnswerChoice
from .question_sets import QuestionSet
from .questions import Question
from .subjects import Subject
from .subtopics import Subtopic
from .topics import Topic
from .token import RevokedToken
from .user_responses import UserResponse
from .users import User
```

## File: answer_choices.py
```py
# filename: app/models/answer_choices.py
"""
This module defines the AnswerChoice model.

The AnswerChoice model represents an answer choice for a question in the quiz app.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AnswerChoice(Base):
    """
    The AnswerChoice model.

    Attributes:
        id (int): The primary key of the answer choice.
        text (str): The text of the answer choice.
        is_correct (bool): Indicates whether the answer choice is correct.
        question_id (int): The foreign key referencing the associated question.
        question (Question): The relationship to the associated question.
    """
    __tablename__ = "answer_choices"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    is_correct = Column(Boolean)
    question_id = Column(Integer, ForeignKey('questions.id'))
    
    question = relationship("Question", back_populates="answer_choices")
```

## File: question_sets.py
```py
# filename: app/models/question_sets.py
"""
This module defines the QuestionSet model.

The QuestionSet model represents a set of questions in the quiz app.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class QuestionSet(Base):
    """
    The QuestionSet model.

    Attributes:
        id (int): The primary key of the question set.
        name (str): The name of the question set.
        questions (List[Question]): The relationship to the associated questions.
    """
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    questions = relationship("Question", back_populates="question_set")
```

## File: questions.py
```py
# filename: app/models/questions.py
"""
This module defines the Question model.

The Question model represents a question in the quiz app.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Question(Base):
    """
    The Question model.
    """
    __tablename__ = "questions"
    def __repr__(self):
        return f"<Question(id={self.id}, text={self.text}, subtopic_id={self.subtopic_id}, question_set_id={self.question_set_id})>"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'))
    question_set_id = Column(Integer, ForeignKey('question_sets.id'))
    explanation = Column(String)  # Add this line
    
    subtopic = relationship("Subtopic", back_populates="questions")
    question_set = relationship("QuestionSet", back_populates="questions")
    answer_choices = relationship("AnswerChoice", back_populates="question")

```

## File: subjects.py
```py
# filename: app/models/subjects.py
"""
This module defines the Subject model.

The Subject model represents a subject in the quiz app.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Subject(Base):
    """
    The Subject model.

    Attributes:
        id (int): The primary key of the subject.
        name (str): The name of the subject.
        topics (List[Topic]): The relationship to the associated topics.
    """
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    topics = relationship("Topic", back_populates="subject")
```

## File: subtopics.py
```py
# filename: app/models/subtopics.py
"""
This module defines the Subtopic model.

The Subtopic model represents a subtopic in the quiz app.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Subtopic(Base):
    """
    The Subtopic model.

    Attributes:
        id (int): The primary key of the subtopic.
        name (str): The name of the subtopic.
        topic_id (int): The foreign key referencing the associated topic.
        topic (Topic): The relationship to the associated topic.
        questions (List[Question]): The relationship to the associated questions.
    """
    __tablename__ = "subtopics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    
    topic = relationship("Topic", back_populates="subtopics")
    questions = relationship("Question", back_populates="subtopic")
```

## File: token.py
```py
from sqlalchemy import Column, Integer, String, DateTime
from app.db.base_class import Base
from datetime import datetime

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)

```

## File: topics.py
```py
# filename: app/models/topics.py
"""
This module defines the Topic model.

The Topic model represents a topic in the quiz app.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Topic(Base):
    """
    The Topic model.

    Attributes:
        id (int): The primary key of the topic.
        name (str): The name of the topic.
        subject_id (int): The foreign key referencing the associated subject.
        subject (Subject): The relationship to the associated subject.
        subtopics (List[Subtopic]): The relationship to the associated subtopics.
    """
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    
    subject = relationship("Subject", back_populates="topics")
    subtopics = relationship("Subtopic", back_populates="topic")
```

## File: user_responses.py
```py
# filename: app/models/user_responses.py
"""
This module defines the UserResponse model.

The UserResponse model represents a user's response to a question in the quiz app.
"""

from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime
from app.db.base_class import Base

class UserResponse(Base):
    """
    The UserResponse model.

    Attributes:
        id (int): The primary key of the user response.
        user_id (int): The foreign key referencing the associated user.
        question_id (int): The foreign key referencing the associated question.
        answer_choice_id (int): The foreign key referencing the associated answer choice.
        is_correct (bool): Indicates whether the user's response is correct.
        timestamp (datetime): The timestamp of the user's response.
        user (User): The relationship to the associated user.
        question (Question): The relationship to the associated question.
        answer_choice (AnswerChoice): The relationship to the associated answer choice.
    """
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_choice_id = Column(Integer, ForeignKey('answer_choices.id'))
    is_correct = Column(Boolean)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="responses")
    question = relationship("Question")
    answer_choice = relationship("AnswerChoice")
```

## File: users.py
```py
# filename: app/models/users.py
"""
This module defines the User model.

The User model represents a user in the quiz app.
"""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    """
    The User model.
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Add this line

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    responses = relationship("UserResponse", back_populates="user")

```

# Directory: /code/quiz-app/quiz-app-backend/app/core

## File: __init__.py
```py
# filename: app/core/__init__.py
"""
This module serves as the main entry point for the core package.

It can be used to perform any necessary initialization or configuration for the core package.
"""
from .config import Settings, settings
from .jwt import create_access_token, verify_token, decode_access_token
from .security import verify_password, get_password_hash

```

## File: config.py
```py
# filename: app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()

```

## File: jwt.py
```py
# filename: app/core/jwt.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.core import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except jwt.JWTError:
        raise credentials_exception

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")  # Use the correct error message here
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")  # Use the correct error message here

```

## File: security.py
```py
# filename: app/core/security.py
"""
This module provides security-related utilities for the Quiz App backend.

It includes functions for password hashing and verification using the bcrypt algorithm.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    Verify a plain-text password against a hashed password.

    Args:
        plain_password (str): The plain-text password to be verified.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Generate a hash for the provided password.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The generated hash of the password.
    """
    return pwd_context.hash(password)
```

# Directory: /code/quiz-app/quiz-app-backend/tests

## File: conftest.py
```py
# filename: tests/conftest.py
import sys
sys.path.insert(0, "/code/quiz-app/quiz-app-backend")

# pylint: disable=wrong-import-position
import random
import string
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app
from app.db import Base, get_db
from app.crud import (
    create_user,
    create_question,
    create_question_set,
    create_subtopic
)
from app.schemas import (
    UserCreate,
    QuestionSetCreate,
    QuestionCreate,
    AnswerChoiceCreate,
    SubtopicCreate
    )
from app.models import AnswerChoice
from app.core import create_access_token

# Testing database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db):
    yield db

@pytest.fixture(scope="function")
def random_username():
    return "testuser_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture(scope="function")
def test_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="TestPassword123!")
    user = create_user(db_session, user_data)
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()

@pytest.fixture(scope="function")
def test_question_set(db_session):
    question_set_data = QuestionSetCreate(name="Test Question Set")
    question_set = create_question_set(db_session, question_set_data)
    yield question_set
    db_session.delete(question_set)
    db_session.commit()

@pytest.fixture(scope="function")
def test_subtopic(db_session):
    subtopic_data = SubtopicCreate(name="Test Subtopic")
    subtopic = create_subtopic(db=db_session, subtopic=subtopic_data)
    yield subtopic
    db_session.delete(subtopic)
    db_session.commit()

@pytest.fixture(scope="function")
def test_question(db_session, test_question_set, test_subtopic):
    answer_choice_1 = AnswerChoiceCreate(text="Test Answer 1", is_correct=True)
    answer_choice_2 = AnswerChoiceCreate(text="Test Answer 2", is_correct=False)
    question_data = QuestionCreate(
        text="Test Question",
        question_set_id=test_question_set.id,
        subtopic_id=test_subtopic.id,
        answer_choices=[answer_choice_1, answer_choice_2],
        explanation="Test Explanation"
    )
    question = create_question(db_session, question_data)
    yield question
    db_session.delete(question)
    db_session.commit()

@pytest.fixture(scope="function")
def test_token(test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    return access_token

@pytest.fixture(scope="function")
def test_answer_choice(db_session, test_question):
    answer_choice = AnswerChoice(text="Test Answer", is_correct=True, question=test_question)
    db_session.add(answer_choice)
    db_session.commit()
    yield answer_choice
    db_session.delete(answer_choice)
    db_session.commit()

```

## File: test_api_authentication.py
```py
# filename: tests/test_api_authentication.py

from datetime import timedelta
from app.core import create_access_token
from app.models import RevokedToken

def test_user_authentication(client, test_user):
    """Test user authentication and token retrieval."""
    response = client.post("/token", data={"username": test_user.username, "password": "TestPassword123!"})
    assert response.status_code == 200, "Authentication failed."
    assert "access_token" in response.json(), "Access token missing in response."
    assert response.json()["token_type"] == "bearer", "Incorrect token type."

def test_register_user_success(client, db_session):
    user_data = {"username": "new_user", "password": "NewPassword123!"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201, "User registration failed"

def test_login_user_success(client, test_user):
    """Test successful user login and token retrieval."""
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200, "User login failed."
    assert "access_token" in response.json(), "Access token missing in login response."

def test_registration_user_exists(client, test_user):
    response = client.post("/register/", json={"username": test_user.username, "password": "anotherpassword"})
    assert response.status_code == 422, "Registration should fail for existing username."

def test_token_access_with_invalid_credentials(client, db_session):
    """Test token access with invalid credentials."""
    response = client.post("/token", data={"username": "nonexistentuser", "password": "wrongpassword"})
    assert response.status_code == 401, "Token issuance should fail with invalid credentials."

def test_register_user_duplicate(client, test_user):
    """
    Test registration with a username that already exists.
    """
    user_data = {"username": test_user.username, "password": "DuplicatePass123!"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "already registered" in str(response.content)

def test_login_wrong_password(client, test_user):
    """
    Test login with incorrect password.
    """
    login_data = {"username": test_user.username, "password": "wrongpassword"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_and_access_protected_endpoint(client, test_user):
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Access a protected endpoint using the token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200

def test_access_protected_endpoint_without_token(client):
    response = client.get("/users/")
    assert response.status_code == 401

def test_access_protected_endpoint_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401

def test_register_user_invalid_password(client):
    """Test registration with an invalid password."""
    user_data = {"username": "newuser", "password": "weak"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in response.json()["detail"][0]["msg"]

def test_register_user_missing_digit_in_password(client):
    """Test registration with a password missing a digit."""
    user_data = {"username": "newuser", "password": "NoDigitPassword"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one digit" in str(response.content)

def test_register_user_missing_uppercase_in_password(client):
    """Test registration with a password missing an uppercase letter."""
    user_data = {"username": "newuser", "password": "nouppercasepassword123"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one uppercase letter" in str(response.content)

def test_register_user_missing_lowercase_in_password(client):
    """Test registration with a password missing a lowercase letter."""
    user_data = {"username": "newuser", "password": "NOLOWERCASEPASSWORD123"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one lowercase letter" in str(response.content)

def test_login_success(client, test_user):
    """
    Test successful user login.
    """
    response = client.post("/login", json={"username": test_user.username, "password": "TestPassword123!"})
    assert response.status_code == 200, "Authentication failed."
    assert "access_token" in response.json(), "Access token missing in response."
    assert response.json()["token_type"] == "bearer", "Incorrect token type."

def test_login_invalid_credentials(client, db_session):
    """
    Test login with invalid credentials.
    """
    response = client.post("/login", json={"username": "invalid_user", "password": "invalid_password"})
    assert response.status_code == 401
    assert "Username not found" in response.json()["detail"]

def test_logout_success(client, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.post("/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

def test_login_inactive_user(client, test_user, db_session):
    """
    Test login with an inactive user.
    """
    # Set the user as inactive
    test_user.is_active = False
    db_session.commit()
    
    response = client.post("/login", json={"username": test_user.username, "password": "TestPassword123"})
    assert response.status_code == 401
    assert "inactive" in response.json()["detail"]

def test_login_invalid_token_format(client):
    headers = {"Authorization": "Bearer invalid_token_format"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]

def test_login_expired_token(client, test_user):
    """
    Test accessing a protected route with an expired token.
    """
    # Create an expired token
    expired_token = create_access_token(data={"sub": test_user.username}, expires_delta=timedelta(minutes=-1)) 
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]

def test_login_nonexistent_user(client, db_session):
    """
    Test login with a non-existent username.
    """
    login_data = {"username": "nonexistent_user", "password": "password123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 401
    assert "Username not found" in response.json()["detail"]

def test_logout_revoked_token(client, test_user, test_token, db_session):
    """
    Test logout with an already revoked token.
    """
    # Revoke the token manually
    revoked_token = RevokedToken(token=test_token)
    db_session.add(revoked_token)
    db_session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.post("/logout", headers=headers)
    assert response.status_code == 401
    assert "Token has been revoked" in response.json()["detail"]

def test_protected_endpoint_expired_token(client, test_user, db_session):
    """
    Test accessing a protected endpoint with an expired token after logout.
    """
    # Create an access token with a short expiration time
    access_token_expires = timedelta(minutes=-1)
    access_token = create_access_token(data={"sub": test_user.username}, expires_delta=access_token_expires)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]

def test_login_logout_flow(client, test_user):
    """
    Test the complete login and logout flow.
    """
    # Login
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    login_response = client.post("/login", json=login_data)
    access_token = login_response.json()["access_token"]
    assert login_response.status_code == 200, "Authentication failed."
    assert "access_token" in login_response.json(), "Access token missing in response."
    assert login_response.json()["token_type"] == "bearer", "Incorrect token type."
    
    # Access a protected endpoint with the token
    headers = {"Authorization": f"Bearer {access_token}"}
    protected_response = client.get("/users/", headers=headers)
    assert protected_response.status_code == 200
    
    # Logout
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200
    
    # Try accessing the protected endpoint again after logout
    protected_response_after_logout = client.get("/users/", headers=headers)
    assert protected_response_after_logout.status_code == 401
    assert "Could not validate credentials" in protected_response_after_logout.json()["detail"]

```

## File: test_api_question_sets.py
```py
# filename: tests/test_api_question_sets.py

import json
import tempfile

def test_create_question_set(client, db_session):
    data = {"name": "Test Create Question Set"}
    response = client.post("/question-sets/", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Create Question Set"

def test_read_question_sets(client, db_session, test_question_set):
    response = client.get("/question-sets/")
    assert response.status_code == 200
    assert any(qs["id"] == test_question_set.id and qs["name"] == test_question_set.name for qs in response.json())

def test_update_nonexistent_question_set(client, test_user):
    """
    Test updating a question set that does not exist.
    """
    question_set_update = {"name": "Updated Name"}
    response = client.put("/question-sets/99999", json=question_set_update)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_update_question_set_not_found(client, db_session):
    question_set_id = 999
    question_set_update = {"name": "Updated Name"}
    response = client.put(f"/question-sets/{question_set_id}", json=question_set_update)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_delete_question_set_not_found(client, db_session):
    """
    Test deleting a question set that does not exist.
    """
    question_set_id = 999
    response = client.delete(f"/question-sets/{question_set_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question set with ID {question_set_id} not found."

def test_upload_question_set_success(client, db_session, test_user):
    # Login
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    login_response = client.post("/login", json=login_data)
    access_token = login_response.json()["access_token"]
    assert login_response.status_code == 200, "Authentication failed."
    assert "access_token" in login_response.json(), "Access token missing in response."
    assert login_response.json()["token_type"] == "bearer", "Incorrect token type."
    
    # Prepare valid JSON data
    json_data = [
        {
            "text": "Question 1",
            "subtopic_id": 1,
            "question_set_id": 1,
            "answer_choices": [
                {"text": "Answer 1", "is_correct": True},
                {"text": "Answer 2", "is_correct": False}
            ],
            "explanation": "Explanation for Question 1"
        },
        {
            "text": "Question 2",
            "subtopic_id": 1,
            "question_set_id": 1,
            "answer_choices": [
                {"text": "Answer 1", "is_correct": False},
                {"text": "Answer 2", "is_correct": True}
            ],
            "explanation": "Explanation for Question 2"
        }
    ]
    
    # Create a temporary file with the JSON data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        json.dump(json_data, temp_file)
        temp_file.flush()  # Ensure the contents are written to the file
        # Access a protected endpoint with the token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/upload-questions/",
                               files={"file": ("question_set.json", open(temp_file.name, 'rb'), "application/json")},
                               headers=headers)
        
    assert response.status_code == 200
    assert response.json() == {"message": "Question set uploaded successfully"}

def test_upload_question_set_invalid_json(client, test_user):
    # Login
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    login_response = client.post("/login", json=login_data)
    access_token = login_response.json()["access_token"]

    # Prepare invalid JSON data
    invalid_json = "{'invalid': 'json'}"
    
    # Create a temporary file with the invalid JSON data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_file.write(invalid_json)
        temp_file.flush()  # Ensure the contents are written to the file
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/upload-questions/", files={"file": ("invalid.json", open(temp_file.name, 'rb'), "application/json")}, headers=headers)
 
    assert response.status_code == 400
    assert "Invalid JSON data" in response.json()["detail"]

```

## File: test_api_questions.py
```py
# filename: tests/test_api_questions.py

def test_create_question(client, db_session, test_question_set, test_subtopic):
    data = {
        "text": "Test Question",
        "question_set_id": test_question_set.id,
        "subtopic_id": test_subtopic.id,
        "answer_choices": [
            {"text": "Answer 1", "is_correct": True},
            {"text": "Answer 2", "is_correct": False}
        ],
        "explanation": "Test Explanation"
    }
    response = client.post("/questions/", json=data)
    assert response.status_code == 201, response.text

def test_read_questions_without_token(client, db_session, test_question):
    response = client.get("/questions/")
    assert response.status_code == 401

def test_read_questions_with_token(client, db_session, test_question, test_user):
    # Authenticate and get the access token
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/token", data=login_data)
    access_token = response.json()["access_token"]
    assert response.status_code == 200, "Authentication failed."
    assert "access_token" in response.json(), "Access token missing in response."
    assert response.json()["token_type"] == "bearer", "Incorrect token type."

    # Make the request to the /questions/ endpoint with the access token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/questions/", headers=headers)
    assert response.status_code == 200
    # Deserialize the response to find our test question
    questions = response.json()
    found_test_question = next((q for q in questions if q["id"] == test_question.id), None)

    # Now we assert that our test question is indeed found and has the correct data
    assert found_test_question is not None, "Test question was not found in the response."
    assert found_test_question["text"] == test_question.text
    assert found_test_question["question_set_id"] == test_question.question_set_id
    assert found_test_question["subtopic_id"] == test_question.subtopic_id

def test_update_question_not_found(client, db_session):
    """
    Test updating a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    response = client.put(f"/questions/{question_id}", json=question_update)
    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found"

def test_delete_question_not_found(client, db_session):
    """
    Test deleting a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    response = client.delete(f"/questions/{question_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found"

```

## File: test_api_user_responses.py
```py
# filename: tests/test_api_user_responses.py

def test_create_user_response_invalid_data(client, db_session):
    """
    Test creating a user response with invalid data.
    """
    invalid_data = {
        "user_id": 999,  # Assuming this user ID does not exist
        "question_id": 999,  # Assuming this question ID does not exist
        "answer_choice_id": 999,  # Assuming this answer choice ID does not exist
        "is_correct": True
    }
    response = client.post("/user-responses/", json=invalid_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid user_id"
```

## File: test_api_users.py
```py
# filename: tests/test_api_users.py
def test_create_user(client, db_session, random_username):
    data = {"username": random_username, "password": "TestPassword123!"}
    response = client.post("/users/", json=data)
    assert response.status_code == 201

def test_read_users(client, db_session, test_user):
    # Authenticate and get the access token
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Make the request to the /users/ endpoint with the access token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert test_user.username in [user["username"] for user in response.json()]

# Add more tests for user API endpoints

```

## File: test_auth_integration.py
```py
def test_protected_route_with_valid_token(client, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200

def test_protected_route_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401

def test_protected_route_with_revoked_token(client, test_user, test_token):
    """
    Test accessing a protected route with a revoked token.
    """
    # Logout to revoke the token
    headers = {"Authorization": f"Bearer {test_token}"}
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200
    
    # Try accessing the protected route with the revoked token
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]

```

## File: test_core_auth.py
```py
# filename: tests/test_core_auth.py

from app.services import oauth2_scheme

def test_oauth2_scheme():
    """
    Test the OAuth2 authentication scheme.
    """
    assert oauth2_scheme.scheme_name == "OAuth2PasswordBearer"
    assert oauth2_scheme.auto_error is True

```

## File: test_core_jwt.py
```py
# filename: tests/test_core_jwt.py

from datetime import timedelta
import pytest
from jose import JWTError
from app.core import create_access_token, verify_token

def test_jwt_token_creation_and_verification():
    """
    Test the JWT token creation and verification process.
    """
    test_data = {"sub": "testuser"}
    token = create_access_token(data=test_data, expires_delta=timedelta(minutes=30))
    assert token is not None
    decoded_sub = verify_token(token, credentials_exception=ValueError("Invalid token"))
    assert decoded_sub == test_data["sub"], "Decoded subject does not match the expected value."

def test_create_access_token_with_expiration():
    """
    Test creating an access token with a specific expiration time.
    """
    expires_delta = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": "testuser"}, expires_delta=expires_delta)
    assert access_token is not None

def test_verify_token_invalid():
    """
    Test verifying an invalid token.
    """
    invalid_token = "invalid_token"
    with pytest.raises(JWTError):
        verify_token(invalid_token, credentials_exception=JWTError)

def test_verify_token_expired():
    """
    Test verifying an expired token.
    """
    expires_delta = timedelta(minutes=-1)  # Expired token
    expired_token = create_access_token(data={"sub": "testuser"}, expires_delta=expires_delta)
    with pytest.raises(JWTError):
        verify_token(expired_token, credentials_exception=JWTError)

```

## File: test_crud.py
```py
# filename: tests/test_crud.py

from app.crud import create_user, create_question_set
from app.schemas import UserCreate, QuestionSetCreate
from app.services import authenticate_user

def test_create_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="NewPassword123!")
    created_user = create_user(db_session, user_data)
    assert created_user.username == random_username

def test_authenticate_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="AuthPassword123!")
    create_user(db_session, user_data)
    authenticated_user = authenticate_user(db_session, username=random_username, password="AuthPassword123!")
    assert authenticated_user
    assert authenticated_user.username == random_username

def test_create_question_set(db_session):
    question_set_data = QuestionSetCreate(name="Test CRUD Question Set")
    created_question_set = create_question_set(db_session, question_set_data)
    assert created_question_set.name == "Test CRUD Question Set"

# Add similar tests for other CRUD operations
```

## File: test_crud_question_sets.py
```py
# filename: tests/test_crud_question_sets.py
import pytest
from fastapi import HTTPException
from app.crud import (
    create_question_set,
    delete_question_set,
    update_question_set
)
from app.schemas import QuestionSetCreate, QuestionSetUpdate

@pytest.fixture
def question_set_data():
    return QuestionSetCreate(name="Sample Question Set")

def test_create_question_set(db_session, question_set_data):
    """Test creation of a question set."""
    question_set_data.name = "Unique Question Set"
    question_set = create_question_set(db=db_session, question_set=question_set_data)
    assert question_set is not None, "Question set was not created."
    assert question_set.name == question_set_data.name, "Question set name mismatch."

def test_delete_question_set(db_session, question_set_data):
    """Test deletion of a question set."""
    question_set_data.name = "Unique Question Set for Deletion"
    question_set = create_question_set(db=db_session, question_set=question_set_data)
    assert delete_question_set(db=db_session, question_set_id=question_set.id) is True, "Question set deletion failed."

def test_create_question_set_duplicate_name(db_session, question_set_data):
    create_question_set(db=db_session, question_set=question_set_data)
    with pytest.raises(HTTPException) as exc_info:
        create_question_set(db=db_session, question_set=question_set_data)
    assert exc_info.value.status_code == 400
    assert f"Question set with name '{question_set_data.name}' already exists." in str(exc_info.value.detail)

def test_update_question_set_not_found(db_session):
    question_set_id = 999
    question_set_update = QuestionSetUpdate(name="Updated Name")
    with pytest.raises(HTTPException) as exc_info:
        update_question_set(db=db_session, question_set_id=question_set_id, question_set=question_set_update)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)

def test_delete_question_set_not_found(db_session):
    question_set_id = 999  # Assuming this ID does not exist
    with pytest.raises(HTTPException) as exc_info:
        delete_question_set(db=db_session, question_set_id=question_set_id)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)

```

## File: test_crud_questions.py
```py
# filename: tests/test_crud_questions.py
from app.schemas import QuestionCreate, AnswerChoiceCreate
from app.crud import (
    create_question,
    get_question,
    update_question,
    delete_question
)
def test_create_and_retrieve_question(db_session, test_question_set, test_subtopic):
    """Test creation and retrieval of a question."""
    test_question_set.name = "Unique Question Set for Question Creation"
    answer_choice_1 = AnswerChoiceCreate(text="Test Answer 1", is_correct=True)
    answer_choice_2 = AnswerChoiceCreate(text="Test Answer 2", is_correct=False)
    question_data = QuestionCreate(
        text="Sample Question?",
        subtopic_id=test_subtopic.id,
        question_set_id=test_question_set.id,
        answer_choices=[answer_choice_1, answer_choice_2],
        explanation="Test Explanation"
    )
    created_question = create_question(db=db_session, question=question_data)
    retrieved_question = get_question(db_session, question_id=created_question.id)
    assert retrieved_question is not None, "Failed to retrieve created question."
    assert retrieved_question.text == "Sample Question?", "Question text does not match."
    assert len(retrieved_question.answer_choices) == 2, "Answer choices not created correctly."

def test_get_nonexistent_question(db_session):
    """Test retrieval of a non-existent question."""
    question = get_question(db_session, question_id=999)
    assert question is None, "Fetching a non-existent question should return None."

def test_delete_nonexistent_question(db_session):
    """Test deletion of a non-existent question."""
    result = delete_question(db_session, question_id=999)
    assert result is False, "Deleting a non-existent question should return False."

def test_update_question_not_found(db_session):
    """
    Test updating a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    updated_question = update_question(db_session, question_id, question_update)
    assert updated_question is None

def test_delete_question_not_found(db_session):
    """
    Test deleting a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    deleted = delete_question(db_session, question_id)
    assert deleted is False

```

## File: test_crud_user.py
```py
# filename: tests/test_crud_user.py
from app.crud import crud_user

def test_remove_user_not_found(db_session):
    """
    Test removing a user that does not exist.
    """
    user_id = 999  # Assuming this ID does not exist
    removed_user = crud_user.remove_user(db_session, user_id)
    assert removed_user is None

```

## File: test_crud_user_responses.py
```py
# filename: tests/test_crud_user_responses.py
from app.schemas import UserResponseCreate
from app.crud import crud_user_responses

def test_create_and_retrieve_user_response(db_session, test_user, test_question, test_answer_choice):
    """Test creation and retrieval of a user response."""
    response_data = UserResponseCreate(user_id=test_user.id, question_id=test_question.id, answer_choice_id=test_answer_choice.id, is_correct=True)
    created_response = crud_user_responses.create_user_response(db=db_session, user_response=response_data)
    assert created_response is not None, "Failed to create user response."
    assert created_response.is_correct is True, "User response correctness does not match."

```

## File: test_db_session.py
```py
# filename: tests/test_db_session.py

def test_database_session_lifecycle(db_session):
    """Test the lifecycle of a database session."""
    # Assuming 'db_session' is already using the correct test database ('test.db') as configured in conftest.py
    assert db_session.bind.url.__to_string__() == "sqlite:///./test.db", "Not using the test database"

```

## File: test_jwt.py
```py
# filename: tests/test_jwt.py
import pytest
from app.core import jwt
from datetime import timedelta

@pytest.fixture
def test_data():
    return {"sub": "testuser"}

def test_jwt_token_generation_and_validation(test_data):
    """Test JWT token generation and subsequent validation."""
    # Generate a token
    token = jwt.create_access_token(data=test_data, expires_delta=timedelta(minutes=15))
    assert token is not None, "Failed to generate JWT token."
    
    # Validate the token
    decoded_username = jwt.verify_token(token, credentials_exception=Exception("Invalid token"))
    assert decoded_username == test_data["sub"], "JWT token validation failed. Username mismatch."

```

## File: test_models.py
```py
# filename: tests/test_models.py
import pytest
from app.models import User, Subject, Topic, Subtopic, Question, AnswerChoice, QuestionSet

def test_user_model(db_session, random_username):
    username = random_username
    user = User(username=username, hashed_password="hashedpassword")
    db_session.add(user)
    db_session.commit()
    assert user.id > 0
    assert user.username == username
    assert user.hashed_password == "hashedpassword"

def test_subject_model(db_session):
    subject = Subject(name="Test Subject")
    db_session.add(subject)
    db_session.commit()
    assert subject.id > 0
    assert subject.name == "Test Subject"

def test_question_model(db_session):
    question_set = QuestionSet(name="Test Question Set")
    db_session.add(question_set)
    db_session.commit()
    question = Question(text="Test Question", question_set=question_set)
    db_session.add(question)
    db_session.commit()
    assert question.id
    assert question.text == "Test Question"
    assert question.question_set == question_set
    
# Add similar tests for other models: Topic, Subtopic, Question, AnswerChoice

```

## File: test_schemas.py
```py
# filename: tests/test_schemas.py

from app.schemas import UserCreate, QuestionCreate

def test_user_create_schema():
    user_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    user_schema = UserCreate(**user_data)
    assert user_schema.username == "testuser"
    assert user_schema.password == "TestPassword123!"

def test_user_create_schema_password_validation():
    user_data = {"username": "testuser", "password": "ValidPassword123!"}
    user_schema = UserCreate(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_question_create_schema():
    question_data = {
        "text": "Test question",
        "subtopic_id": 1,
        "question_set_id": 1,
        "answer_choices": [
            {"text": "Answer 1", "is_correct": True},
            {"text": "Answer 2", "is_correct": False}
        ],
        "explanation": "Test explanation"
    }
    question_schema = QuestionCreate(**question_data)
    assert question_schema.text == "Test question"
    assert question_schema.subtopic_id == 1
    assert question_schema.question_set_id == 1
    assert len(question_schema.answer_choices) == 2
    assert question_schema.explanation == "Test explanation"

```

## File: test_schemas_user.py
```py
# filename: tests/test_schemas_user.py

import pytest
from app.schemas.user import UserCreate

def test_user_create_schema_password_validation():
    """
    Test password validation in UserCreate schema.
    """
    # Test password too short
    with pytest.raises(ValueError):
        UserCreate(username="testuser", password="short")

    # Test password valid
    user_data = {"username": "testuser", "password": "ValidPassword123!"}
    user_schema = UserCreate(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_user_create_schema_password_complexity_validation():
    """Test password complexity validation in UserCreate schema."""
    # Test password missing a digit
    with pytest.raises(ValueError, match="Password must contain at least one digit"):
        UserCreate(username="testuser", password="NoDigitPassword")

    # Test password missing an uppercase letter
    with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
        UserCreate(username="testuser", password="nouppercasepassword123")

    # Test password missing a lowercase letter
    with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
        UserCreate(username="testuser", password="NOLOWERCASEPASSWORD123")

    # Test valid password
    user_data = {"username": "testuser", "password": "ValidPassword123!"}
    user_schema = UserCreate(**user_data)
    assert user_schema.password == "ValidPassword123!"

```

# Directory: /code/quiz-app/quiz-app-backend/new-work-items

## File: generate_new_work_items_prompt.py
```py
import pandas as pd

def convert_csv_to_markdown(csv_file_path, template_file_path, output_file_path):
    # Load the CSV
    csv_data = pd.read_csv(csv_file_path)
    
    # Sort the dataframe by Work Item Type and then by ID
    csv_data_sorted = csv_data.sort_values(by=['Work Item Type', 'ID'], ascending=[False, True])
    
    # Function to convert a row to markdown section
    def row_to_markdown(row):
        md = f"### {row['Title']}\n\n"
        md += f"**ID:** {row['ID']}\n\n"
        md += f"**Work Item Type:** {row['Work Item Type']}\n\n"
        md += f"**State:** {row['State']}\n\n"
        md += f"**Tags:** {row['Tags']}\n\n"
        if pd.notnull(row['Description']):
            md += f"**Description:**\n\n{row['Description']}\n\n"
        if pd.notnull(row['Acceptance Criteria']):
            # Splitting the acceptance criteria by newline and converting to bullet points
            criteria_list = row['Acceptance Criteria'].split('\n')
            criteria_md = '\n'.join([f"- {item}" for item in criteria_list if item.strip() != ''])
            md += f"**Acceptance Criteria:**\n\n{criteria_md}\n\n"
        return md

    # Applying the conversion function to each row
    markdown_sections = csv_data_sorted.apply(row_to_markdown, axis=1)
    
    # Combining all sections into one markdown string
    markdown_content = "\n".join(markdown_sections)
    
    # Load the markdown template
    with open(template_file_path, 'r') as file:
        template_content = file.read()
    
    # Replace the placeholder with the actual markdown content
    final_markdown = template_content.replace('<details from /code/quiz-app/quiz-app-backend/new-work-items/new-work-items.csv>', markdown_content)
    
    # Saving the combined markdown output
    with open(output_file_path, 'w') as file:
        file.write(final_markdown)
    
    print(f"Markdown document saved to {output_file_path}")

# Example usage:
if __name__ == "__main__":
    csv_file_path = '/code/quiz-app/quiz-app-backend/new-work-items/new-work-items.csv'
    template_file_path = '/code/quiz-app/quiz-app-backend/new-work-items/new-work-items-prompt-template.md'
    output_file_path = '/code/quiz-app/quiz-app-backend/new-work-items/new-work-items-prompt.md'
    convert_csv_to_markdown(csv_file_path, template_file_path, output_file_path)

```


# Directory: /code/quiz-app/quiz-app-backend/app

## File: __init__.py
```py

```

## File: main.py
```py
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
from app.db.base_class import Base
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
app.include_router(users_router.router, tags=["User Management"])
app.include_router(register_router.router, tags=["Authentication"])
app.include_router(token_router.router, tags=["Authentication"])
app.include_router(question_sets_router.router, tags=["Question Sets"])
app.include_router(questions_router.router, tags=["Questions"])
app.include_router(user_responses_router.router, tags=["User Responses"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

```

# Directory: /code/quiz-app/quiz-app-backend/app/schemas

## File: __init__.py
```py
from .user import UserCreate, UserLogin, UserBase, User
from .questions import QuestionBase, Question, QuestionCreate, QuestionUpdate
from .question_sets import QuestionSetCreate, QuestionSetBase, QuestionSet, QuestionSetUpdate
from .token import Token
from .user_responses import UserResponseBase, UserResponse, UserResponseCreate

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

from pydantic import BaseModel

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

The schemas are used for input validation and serialization/deserialization of User objects.
"""

from pydantic import BaseModel, validator

class UserBase(BaseModel):
    """
    The base schema for a User.

    Attributes:
        username (str): The username of the user.
    """
    username: str

class UserCreate(UserBase):
    """
    The schema for creating a User.

    Inherits from UserBase and includes additional attributes required for user creation.

    Attributes:
        password (str): The password of the user.
    """
    password: str

    @validator('password')
    def password_validation(cls, v):
        """
        Validate the password.

        The password must be at least 8 characters long.
        Additional validation rules can be added as needed.

        Args:
            v (str): The password value.

        Returns:
            str: The validated password.

        Raises:
            ValueError: If the password is invalid.
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v

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

# Directory: /code/quiz-app/quiz-app-backend/app/crud

## File: __init__.py
```py
from .crud_user import create_user, get_user_by_username, authenticate_user, remove_user
from .crud_user_responses import create_user_response, get_user_responses
from .crud_questions import create_question, get_question, get_questions, update_question, delete_question
from .crud_question_sets import create_question_set, get_question_sets, update_question_set, delete_question_set
```

## File: crud_question_sets.py
```py
# filename: app/crud/crud_questions.py
"""
This module provides CRUD operations for question sets.

It includes functions for creating, retrieving, updating, and deleting question sets.
"""

from sqlalchemy.orm import Session
from app.models.question_sets import QuestionSet
from app.schemas.question_sets import QuestionSetCreate, QuestionSetUpdate
from typing import List

def create_question_set(db: Session, question_set: QuestionSetCreate) -> QuestionSet:
    """
    Create a new question set.

    Args:
        db (Session): The database session.
        question_set (QuestionSetCreate): The question set data.

    Returns:
        QuestionSet: The created question set.
    """
    db_question_set = QuestionSet(**question_set.dict())
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

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

def update_question_set(db: Session, question_set_id: int, question_set: QuestionSetUpdate) -> QuestionSet:
    """
    Update a question set.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set to update.
        question_set (QuestionSetUpdate): The updated question set data.

    Returns:
        QuestionSet: The updated question set.
    """
    db_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if db_question_set:
        for var, value in vars(question_set).items():
            setattr(db_question_set, var, value) if value else None
        db.commit()
        db.refresh(db_question_set)
    return db_question_set

def delete_question_set(db: Session, question_set_id: int) -> bool:
    """
    Delete a question set.

    Args:
        db (Session): The database session.
        question_set_id (int): The ID of the question set to delete.

    Returns:
        bool: True if the question set was deleted, False otherwise.
    """
    db_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if db_question_set:
        db.delete(db_question_set)
        db.commit()
        return True
    return False
```

## File: crud_questions.py
```py
# filename: app/crud/crud_questions.py
"""
This module provides CRUD operations for questions.

It includes functions for creating, retrieving, updating, and deleting questions.
"""

from sqlalchemy.orm import Session
from app.models.questions import Question
from app.schemas.questions import QuestionCreate, QuestionUpdate
from typing import List

def create_question(db: Session, question: QuestionCreate) -> Question:
    """
    Create a new question.

    Args:
        db (Session): The database session.
        question (QuestionCreate): The question data.

    Returns:
        Question: The created question.
    """
    db_question = Question(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
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
    return db.query(Question).offset(skip).limit(limit).all()

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

## File: crud_user.py
```py
# filename: app/crud/crud_user.py
"""
This module provides CRUD operations for users.

It includes functions for creating users, retrieving users by username,
authenticating users, and removing users.
"""

from app.schemas.user import UserCreate, UserLogin
from sqlalchemy.orm import Session
from app.models.users import User
from app.core.security import verify_password, get_password_hash

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
    return user

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
from app.models.user_responses import UserResponse
from app.schemas.user_responses import UserResponseCreate

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

# Directory: /code/quiz-app/quiz-app-backend/app/db

## File: __init__.py
```py
from .base_class import Base
from .session import get_db, init_db
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
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
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

## File: question_sets.py
```py
# filename: app/api/endpoints/question_sets.py
"""
This module provides endpoints for managing question sets.

It defines routes for uploading question sets and retrieving question sets from the database.
"""

import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response  # Import Response
from sqlalchemy.orm import Session
from app.crud.crud_question_sets import get_question_sets, update_question_set, delete_question_set
from app.crud.crud_question_sets import create_question_set as create_question_set_crud
from app.db.session import get_db
from app.schemas.question_sets import QuestionSet, QuestionSetCreate, QuestionSetUpdate

router = APIRouter()

@router.post("/upload-questions/")
async def upload_question_set(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Endpoint to upload a question set in JSON format.
    
    Args:
        file: An UploadFile object representing the JSON file containing the question set data.
        db: A database session dependency injected by FastAPI.
        
    Raises:
        HTTPException: If the uploaded file is not a valid JSON file.
        
    Returns:
        The created question set object.
    """
    content = await file.read()
    try:
        question_data = json.loads(content.decode('utf-8'))
        # Assuming you have a function to process and validate the JSON data
        question_set_created = create_question_set(db, question_data)
        return question_set_created
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

@router.get("/question-set/", response_model=List[QuestionSet])
def read_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
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
def create_question_set(question_set: QuestionSetCreate, db: Session = Depends(get_db)):
    """
    Create a new question set.
    """
    return create_question_set_crud(db=db, question_set=question_set)

@router.get("/question-sets/", response_model=List[QuestionSet])
def read_question_sets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
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
from fastapi import APIRouter, Depends, HTTPException, Response  # Import Response
from sqlalchemy.orm import Session
from app.crud import crud_questions
from app.db.session import get_db
from app.schemas.questions import QuestionCreate, Question, QuestionUpdate

router = APIRouter()

@router.post("/questions/", response_model=Question, status_code=201)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """
    Create a new question.

    Args:
        question (QuestionCreate): The question data.
        db (Session): The database session.

    Returns:
        Question: The created question.
    """
    return crud_questions.create_question(db, question)

@router.get("/questions/", response_model=List[Question])
def read_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of questions.

    Args:
        skip (int): The number of questions to skip.
        limit (int): The maximum number of questions to retrieve.
        db (Session): The database session.

    Returns:
        List[Question]: The list of questions.
    """
    questions = crud_questions.get_questions(db, skip=skip, limit=limit)
    return questions

@router.put("/questions/{question_id}", response_model=Question)
def update_question(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db)):
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
    db_question = crud_questions.update_question(db, question_id=question_id, question=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@router.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """
    Delete a question.

    Args:
        question_id (int): The ID of the question to delete.
        db (Session): The database session.

    Raises:
        HTTPException: If the question is not found.
    """
    deleted = crud_questions.delete_question(db, question_id=question_id)
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
from app.core.security import get_password_hash
from app.crud.crud_user import create_user, get_user_by_username
from app.db.session import get_db
from app.schemas.user import UserCreate

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
        raise HTTPException(status_code=400, detail="Username already registered")
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

It defines a route for authenticating users and issuing access tokens upon successful authentication.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.crud.crud_user import authenticate_user
from app.core.jwt import create_access_token
from app.core.config import settings
from app.db.session import get_db
from app.schemas.token import Token

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
from app.crud.crud_user import create_user as create_user_crud
from app.schemas.user import UserCreate as UserCreateSchema, User as UserSchema
from app.core.auth import get_current_user

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
from .users import User
from .subjects import Subject
from .topics import Topic
from .subtopics import Subtopic
from .questions import Question
from .answer_choices import AnswerChoice
from .question_sets import QuestionSet  # Add this line
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

    Attributes:
        id (int): The primary key of the question.
        text (str): The text of the question.
        subtopic_id (int): The foreign key referencing the associated subtopic.
        question_set_id (int): The foreign key referencing the associated question set.
        subtopic (Subtopic): The relationship to the associated subtopic.
        question_set (QuestionSet): The relationship to the associated question set.
        answer_choices (List[AnswerChoice]): The relationship to the associated answer choices.
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'))
    question_set_id = Column(Integer, ForeignKey('question_sets.id'))
    
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

from app.models.user_responses import UserResponse
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    """
    The User model.

    Attributes:
        id (int): The primary key of the user.
        username (str): The username of the user.
        hashed_password (str): The hashed password of the user.
        is_active (bool): Indicates whether the user is active.
        responses (List[UserResponse]): The relationship to the associated user responses.
    """
    __tablename__ = "users"

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
```

## File: auth.py
```py
# filename: app/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.jwt import verify_token
from app.crud.crud_user import get_user_by_username
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user
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
from jose import jwt
from app.core.config import settings

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
import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import string
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
from app.crud import crud_user, crud_questions, crud_question_sets
from app.schemas import UserCreate, QuestionSetCreate, QuestionCreate
from app.models import User, QuestionSet, Question, Subtopic

# Testing database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    print("Creating test database and tables...")
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal
    print("Dropping test database tables...")
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db):
    session = db()
    print(f"Starting a new test session: {session}")
    try:
        yield session
        session.commit()
        print("Test session committed.")
    except:
        session.rollback()
        print("Test session rolled back.")
        raise
    finally:
        session.close()
        print(f"Test session closed: {session}")

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        print(f"Overriding get_db dependency with test session: {db_session}")
        try:
            yield db_session
        finally:
            print(f"Ending use of test session: {db_session}")

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    del app.dependency_overrides[get_db]
    print("Removed get_db override.")

@pytest.fixture(scope="function")
def random_username():
    return "testuser_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture
def test_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="TestPassword123")
    user = crud_user.create_user(db_session, user_data)
    db_session.commit()
    return user

@pytest.fixture
def test_question_set(db_session):
    question_set_data = QuestionSetCreate(name="Test Question Set")
    question_set = crud_question_sets.create_question_set(db_session, question_set_data)
    return question_set

@pytest.fixture
def test_question(db_session, test_question_set):
    # Create a test subtopic
    subtopic = Subtopic(name="Test Subtopic")
    db_session.add(subtopic)
    db_session.commit()

    question_data = QuestionCreate(text="Test Question", question_set_id=test_question_set.id, subtopic_id=subtopic.id)
    question = crud_questions.create_question(db_session, question_data)
    return question
```

## File: test_api.py
```py
# filename: tests/test_api.py
import pytest
from app.schemas.user import UserCreate
from app.crud import crud_user


def test_register_user(client, db_session, random_username):
    user_data = {
        "username": random_username,
        "password": "TestPassword123"
    }
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201

def test_login_user(client, db_session, random_username):
    password = "TestPassword123"
    user_data = UserCreate(username=random_username, password=password)
    crud_user.create_user(db_session, user_data)
    response = client.post("/token", data={"username": random_username, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_question_set(client):
    question_set_data = {
        "name": "Test Question Set"
    }
    response = client.post("/question-sets/", json=question_set_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Question Set"

# Add more API endpoint tests for other routes
```

## File: test_api_authentication.py
```py
# filename: tests/test_api_authentication.py
def test_user_authentication(client, test_user):
    """Test user authentication and token retrieval."""
    response = client.post("/token", data={"username": test_user.username, "password": "TestPassword123"})
    assert response.status_code == 200, "Authentication failed."
    assert "access_token" in response.json(), "Access token missing in response."
    assert response.json()["token_type"] == "bearer", "Incorrect token type."

def test_register_user_success(client):
    user_data = {"username": "new_user", "password": "NewPassword123"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201

def test_login_user_success(client, test_user):
    """Test successful user login and token retrieval."""
    login_data = {"username": test_user.username, "password": "TestPassword123"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200, "User login failed."
    assert "access_token" in response.json(), "Access token missing in login response."

def test_registration_user_exists(client, test_user):
    """Test registration with an existing username."""
    response = client.post("/register/", json={"username": test_user.username, "password": "anotherpassword"})
    assert response.status_code == 422, "Registration should fail for existing username."

def test_token_access_with_invalid_credentials(client):
    """Test token access with invalid credentials."""
    response = client.post("/token", data={"username": "nonexistentuser", "password": "wrongpassword"})
    assert response.status_code == 401, "Token issuance should fail with invalid credentials."

def test_register_user_duplicate(client, test_user):
    """
    Test registration with a username that already exists.
    """
    user_data = {"username": test_user.username, "password": "DuplicatePass123"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_wrong_password(client, test_user):
    """
    Test login with incorrect password.
    """
    login_data = {"username": test_user.username, "password": "wrongpassword"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

# filename: tests/test_api_authentication.py
def test_login_and_access_protected_endpoint(client, test_user):
    login_data = {"username": test_user.username, "password": "TestPassword123"}
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
    assert "Password must be at least 8 characters long" in str(response.content)

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
```

## File: test_api_question_sets.py
```py
# filename: tests/test_api_question_sets.py
def test_create_question_set(client, db_session):
    data = {"name": "Test Question Set"}
    response = client.post("/question-sets/", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Question Set"

def test_read_question_sets(client, db_session, test_question_set):
    response = client.get("/question-sets/")
    assert response.status_code == 200
    assert any(qs["id"] == test_question_set.id and qs["name"] == test_question_set.name for qs in response.json())

def test_update_nonexistent_question_set(client, test_user):
    """
    Test updating a question set that does not exist.
    """
    question_set_update = {"name": "Updated Name"}
    response = client.put(f"/question-sets/99999", json=question_set_update)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_update_question_set_not_found(client, db_session):
    """
    Test updating a question set that does not exist.
    """
    question_set_id = 999  # Assuming this ID does not exist
    question_set_update = {"name": "Updated Name"}
    response = client.put(f"/question-sets/{question_set_id}", json=question_set_update)
    assert response.status_code == 404
    assert "Question set not found" in response.json()["detail"]

def test_delete_question_set_not_found(client, db_session):
    """
    Test deleting a question set that does not exist.
    """
    question_set_id = 999  # Assuming this ID does not exist
    response = client.delete(f"/question-sets/{question_set_id}")
    assert response.status_code == 404
    assert "Question set not found" in response.json()["detail"]

```

## File: test_api_questions.py
```py
# filename: tests/test_api_questions.py
def test_create_question(client, db_session, test_question_set):
    # Example modification, assuming 'subtopic_id' is required
    data = {
        "text": "Test Question",
        "question_set_id": test_question_set.id,
        "subtopic_id": 1
    }
    response = client.post("/questions/", json=data)
    assert response.status_code == 201, response.text


def test_read_questions(client, db_session, test_question):
    response = client.get("/questions/")
    assert response.status_code == 200

    # Deserialize the response to find our test question
    questions = response.json()
    found_test_question = next((q for q in questions if q["id"] == test_question.id), None)

    # Now we assert that our test question is indeed found
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
    data = {"username": random_username, "password": "TestPassword123"}
    response = client.post("/users/", json=data)
    assert response.status_code == 201

def test_read_users(client, db_session, test_user):
    # Authenticate and get the access token
    login_data = {"username": test_user.username, "password": "TestPassword123"}
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

## File: test_core_auth.py
```py
# filename: tests/test_core_auth.py

from app.core.auth import oauth2_scheme

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
import pytest
from datetime import datetime, timedelta
from jose import JWTError
from app.core import jwt

def test_jwt_token_creation_and_verification():
    """
    Test the JWT token creation and verification process.
    """
    test_data = {"sub": "testuser"}
    token = jwt.create_access_token(data=test_data, expires_delta=timedelta(minutes=30))
    assert token is not None
    decoded_sub = jwt.verify_token(token, credentials_exception=ValueError("Invalid token"))
    assert decoded_sub == test_data["sub"], "Decoded subject does not match the expected value."

def test_create_access_token_with_expiration():
    """
    Test creating an access token with a specific expiration time.
    """
    expires_delta = timedelta(minutes=30)
    access_token = jwt.create_access_token(data={"sub": "testuser"}, expires_delta=expires_delta)
    assert access_token is not None

def test_verify_token_invalid():
    """
    Test verifying an invalid token.
    """
    invalid_token = "invalid_token"
    with pytest.raises(JWTError):
        jwt.verify_token(invalid_token, credentials_exception=JWTError)

def test_verify_token_expired():
    """
    Test verifying an expired token.
    """
    expires_delta = timedelta(minutes=-1)  # Expired token
    expired_token = jwt.create_access_token(data={"sub": "testuser"}, expires_delta=expires_delta)
    with pytest.raises(JWTError):
        jwt.verify_token(expired_token, credentials_exception=JWTError)

```

## File: test_crud.py
```py
# filename: tests/test_crud.py
import pytest
from app.crud import crud_user, crud_question_sets
from app.schemas import UserCreate, QuestionSetCreate

def test_create_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="NewPassword123")
    created_user = crud_user.create_user(db_session, user_data)
    assert created_user.username == random_username

def test_authenticate_user(db_session, random_username):
    user_data = UserCreate(username=random_username, password="AuthPassword123")
    crud_user.create_user(db_session, user_data)
    authenticated_user = crud_user.authenticate_user(db_session, username=random_username, password="AuthPassword123")
    assert authenticated_user
    assert authenticated_user.username == random_username

def test_create_question_set(db_session):
    question_set_data = QuestionSetCreate(name="Test Question Set")
    created_question_set = crud_question_sets.create_question_set(db_session, question_set_data)
    assert created_question_set.name == "Test Question Set"

# Add similar tests for other CRUD operations
```

## File: test_crud_question_sets.py
```py
# filename: tests/test_crud_question_sets.py
import pytest
from app.crud import crud_question_sets
from app.schemas import QuestionSetCreate

@pytest.fixture
def question_set_data():
    return QuestionSetCreate(name="Sample Question Set")

def test_create_question_set(db_session, question_set_data):
    """Test creation of a question set."""
    question_set = crud_question_sets.create_question_set(db=db_session, question_set=question_set_data)
    assert question_set is not None, "Question set was not created."
    assert question_set.name == question_set_data.name, "Question set name mismatch."

def test_delete_question_set(db_session, question_set_data):
    """Test deletion of a question set."""
    question_set = crud_question_sets.create_question_set(db=db_session, question_set=question_set_data)
    assert crud_question_sets.delete_question_set(db=db_session, question_set_id=question_set.id) is True, "Question set deletion failed."

# filename: tests/test_crud_question_sets.py

def test_update_question_set_not_found(db_session):
    """
    Test updating a question set that does not exist.
    """
    question_set_id = 999  # Assuming this ID does not exist
    question_set_update = {"name": "Updated Name"}
    updated_question_set = crud_question_sets.update_question_set(db_session, question_set_id, question_set_update)
    assert updated_question_set is None

```

## File: test_crud_questions.py
```py
# filename: tests/test_crud_questions.py
from app.schemas import QuestionCreate
from app.crud import crud_questions

def test_create_and_retrieve_question(db_session, test_question_set):
    """Test creation and retrieval of a question."""
    question_data = QuestionCreate(text="Sample Question?", subtopic_id=1, question_set_id=test_question_set.id)
    created_question = crud_questions.create_question(db=db_session, question=question_data)
    retrieved_question = crud_questions.get_question(db_session, question_id=created_question.id)
    assert retrieved_question is not None, "Failed to retrieve created question."
    assert retrieved_question.text == "Sample Question?", "Question text does not match."

def test_get_nonexistent_question(db_session):
    """Test retrieval of a non-existent question."""
    question = crud_questions.get_question(db_session, question_id=999)
    assert question is None, "Fetching a non-existent question should return None."

def test_delete_nonexistent_question(db_session):
    """Test deletion of a non-existent question."""
    result = crud_questions.delete_question(db_session, question_id=999)
    assert result is False, "Deleting a non-existent question should return False."

def test_update_question_not_found(db_session):
    """
    Test updating a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    updated_question = crud_questions.update_question(db_session, question_id, question_update)
    assert updated_question is None

def test_delete_question_not_found(db_session):
    """
    Test deleting a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    deleted = crud_questions.delete_question(db_session, question_id)
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

def test_create_and_retrieve_user_response(db_session, test_user, test_question):
    """Test creation and retrieval of a user response."""
    response_data = UserResponseCreate(user_id=test_user.id, question_id=test_question.id, answer_choice_id=1, is_correct=True)
    created_response = crud_user_responses.create_user_response(db=db_session, user_response=response_data)
    assert created_response is not None, "Failed to create user response."
    assert created_response.is_correct == True, "User response correctness does not match."

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
import pytest
from app.schemas import UserCreate, QuestionCreate

def test_user_create_schema():
    user_data = {
        "username": "testuser",
        "password": "TestPassword123"
    }
    user_schema = UserCreate(**user_data)
    assert user_schema.username == "testuser"
    assert user_schema.password == "TestPassword123"

def test_user_create_schema_password_validation():
    user_data = {"username": "testuser", "password": "ValidPassword123"}
    user_schema = UserCreate(**user_data)
    assert user_schema.password == "ValidPassword123"

def test_question_create_schema():
    question_data = {
        "text": "Test question",
        "subtopic_id": 1,
        "question_set_id": 1
    }
    question_schema = QuestionCreate(**question_data)
    assert question_schema.text == "Test question"
    assert question_schema.subtopic_id == 1
    assert question_schema.question_set_id == 1

# Add similar tests for other schemas
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
    user_data = {"username": "testuser", "password": "ValidPassword123"}
    user_schema = UserCreate(**user_data)
    assert user_schema.password == "ValidPassword123"

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
    user_data = {"username": "testuser", "password": "ValidPassword123"}
    user_schema = UserCreate(**user_data)
    assert user_schema.password == "ValidPassword123"

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

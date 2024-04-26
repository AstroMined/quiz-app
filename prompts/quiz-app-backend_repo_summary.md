
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
    question as question_router,
    questions as questions_router,
    user_responses as user_responses_router,
    filters as filters_router,
    subjects as subjects_router,
    topics as topics_router
)
from app.db import get_db, SessionLocal
from app.models import RevokedTokenModel

app = FastAPI()

# Use the aliased name for the router
app.include_router(users_router.router, tags=["User Management"])
app.include_router(register_router.router, tags=["Authentication"])
app.include_router(token_router.router, tags=["Authentication"])
app.include_router(auth_router.router, tags=["Authentication"])
app.include_router(question_sets_router.router, tags=["Question Sets"])
app.include_router(question_router.router, tags=["Question"])
app.include_router(questions_router.router, tags=["Questions"])
app.include_router(user_responses_router.router, tags=["User Responses"])
app.include_router(filters_router.router, tags=["Filters"])
app.include_router(topics_router.router, tags=["Topics"])
app.include_router(subjects_router.router, tags=["Subjects"])

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
        if db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
        db.close()
    response = await call_next(request)
    return response

# main.py

@app.middleware("http")
async def check_revoked_token(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        db = next(get_db())
        revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
        if revoked_token:
            # Raise a more specific exception for revoked tokens
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    try:
        response = await call_next(request)
    except HTTPException as e:
        if e.status_code == 401:
            # Handle invalid token exception
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        raise e
    return response

```

# Directory: /code/quiz-app/quiz-app-backend/app/schemas

## File: __init__.py
```py
from .answer_choices import AnswerChoiceSchema, AnswerChoiceBaseSchema, AnswerChoiceCreateSchema
from .auth import LoginFormSchema
from .questions import QuestionBaseSchema, QuestionSchema, QuestionCreateSchema, QuestionUpdateSchema
from .question_sets import QuestionSetCreateSchema, QuestionSetBaseSchema, QuestionSetSchema, QuestionSetUpdateSchema
from .subtopics import SubtopicSchema, SubtopicBaseSchema, SubtopicCreateSchema
from .token import TokenSchema
from .user import UserCreateSchema, UserLoginSchema, UserBaseSchema, UserSchema, UserUpdateSchema
from .user_responses import UserResponseBaseSchema, UserResponseSchema, UserResponseCreateSchema, UserResponseUpdateSchema
from .filters import FilterParamsSchema
from .subjects import SubjectSchema, SubjectBaseSchema, SubjectCreateSchema
from .topics import TopicSchema, TopicBaseSchema, TopicCreateSchema
from .question_tags import QuestionTagSchema, QuestionTagBaseSchema, QuestionTagCreateSchema

```

## File: answer_choices.py
```py
# app/schemas/answer_choices.py
from pydantic import BaseModel

class AnswerChoiceBaseSchema(BaseModel):
    text: str
    is_correct: bool
    explanation: str

class AnswerChoiceCreateSchema(AnswerChoiceBaseSchema):
    pass

class AnswerChoiceSchema(BaseModel):
    id: int
    text: str
    is_correct: bool
    explanation: str

    class Config:
        from_attributes = True

```

## File: auth.py
```py
from pydantic import BaseModel, Field

class LoginFormSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

```

## File: filters.py
```py
# filename: app/schemas/filters.py

from typing import Optional, List
from pydantic import BaseModel, Field, validator, ValidationError

class FilterParamsSchema(BaseModel):
    subject: Optional[str] = Field(None, description="Filter questions by subject")
    topic: Optional[str] = Field(None, description="Filter questions by topic")
    subtopic: Optional[str] = Field(None, description="Filter questions by subtopic")
    difficulty: Optional[str] = Field(None, description="Filter questions by difficulty level")
    tags: Optional[List[str]] = Field(None, description="Filter questions by tags")

    class Config:
        extra = 'forbid'  # Allows extra fields but you can manually handle them
        json_schema_extra = {
            "example": {
                "subject": "Math",
                "topic": "Algebra",
                "subtopic": "Linear Equations",
                "difficulty": "Easy",
                "tags": ["equations", "solving"]
            }
        }

```

## File: question_sets.py
```py
# filename: app/schemas/question_sets.py

from typing import List, Optional
from pydantic import BaseModel

class QuestionSetBaseSchema(BaseModel):
    name: str

class QuestionSetCreateSchema(QuestionSetBaseSchema):
    is_public: bool = True

class QuestionSetUpdateSchema(BaseModel):
    name: Optional[str] = None
    is_public: Optional[bool] = None
    question_ids: Optional[List[int]] = None

class QuestionSetSchema(QuestionSetBaseSchema):
    id: int
    is_public: bool = True
    question_ids: List[int] = []

    class Config:
        from_attributes = True

```

## File: question_tags.py
```py
# filename: app/schemas/question_tags.py

from typing import List, Optional
from pydantic import BaseModel

class QuestionTagBaseSchema(BaseModel):
    tag: str

class QuestionTagCreateSchema(QuestionTagBaseSchema):
    pass

class QuestionTagSchema(QuestionTagBaseSchema):
    id: int

    class Config:
        from_attributes = True

```

## File: questions.py
```py
# filename: app/schemas/questions.py

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.answer_choices import AnswerChoiceSchema, AnswerChoiceCreateSchema
from app.schemas.question_tags import QuestionTagSchema

class QuestionBaseSchema(BaseModel):
    text: str
    subject_id: int
    topic_id: int
    subtopic_id: int

class QuestionCreateSchema(QuestionBaseSchema):
    text: Optional[str] = Field(None, description="The text of the question")
    difficulty: Optional[str] = Field(None, description="The difficulty level of the question")
    subject_id: Optional[int] = Field(None, description="ID of the subject associated with the question")
    topic_id: Optional[int] = Field(None, description="ID of the topic associated with the question")
    subtopic_id: Optional[int] = Field(None, description="ID of the subtopic associated with the question")
    answer_choices: Optional[List[AnswerChoiceCreateSchema]] = Field(None, description="A list of answer choices")
    tags: Optional[List[QuestionTagSchema]] = Field(None, description="A list of tags associated with the question")
    question_set_ids: Optional[List[int]] = Field(None, description="Updated list of question set IDs the question belongs to")

class QuestionUpdateSchema(BaseModel):
    text: Optional[str] = Field(None, description="The text of the question")
    difficulty: Optional[str] = Field(None, description="The difficulty level of the question")
    subject_id: Optional[int] = Field(None, description="ID of the subject associated with the question")
    topic_id: Optional[int] = Field(None, description="ID of the topic associated with the question")
    subtopic_id: Optional[int] = Field(None, description="ID of the subtopic associated with the question")
    answer_choices: Optional[List[AnswerChoiceCreateSchema]] = Field(None, description="A list of answer choices")
    tags: Optional[List[QuestionTagSchema]] = Field(None, description="A list of tags associated with the question")
    question_set_ids: Optional[List[int]] = Field(None, description="Updated list of question set IDs the question belongs to")

class QuestionSchema(BaseModel):
    id: int
    text: str
    subject_id: int
    topic_id: int
    subtopic_id: int
    difficulty: Optional[str] = None
    tags: Optional[List[QuestionTagSchema]] = []
    answer_choices: List[AnswerChoiceSchema] = []
    question_set_ids: Optional[List[int]] = []

    class Config:
        from_attributes = True

```

## File: sessions.py
```py
# filename: app/schemas/tags.py

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SessionQuestionSchema(BaseModel):
    question_id: int
    answered: bool
    correct: Optional[bool] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class SessionQuestionSetSchema(BaseModel):
    question_set_id: int
    question_limit: Optional[int] = None  # Limit on questions from this set, if any

    class Config:
        from_attributes = True

class SessionBaseSchema(BaseModel):
    # Define basic session fields here. For simplicity, we'll just assume a name for the session.
    name: str = Field(..., description="The name of the session")

class SessionCreateSchema(SessionBaseSchema):
    # IDs of question sets to include in the session. Actual question selection/logic to be handled elsewhere.
    question_sets: List[int] = Field(default=[], description="List of question set IDs for the session")

class SessionUpdateSchema(SessionBaseSchema):
    # Assuming we might want to update the name or the question sets associated with the session.
    question_sets: Optional[List[int]] = Field(default=None, description="Optionally update the list of question set IDs for the session")

class SessionSchema(SessionBaseSchema):
    id: int
    question_sets: List[SessionQuestionSetSchema]
    questions: List[SessionQuestionSchema]
    # Assuming additional fields as necessary, for instance, session creation or modification dates.

    class Config:
        from_attributes = True


```

## File: subjects.py
```py
# filename: app/schemas/subjects.py

from pydantic import BaseModel

class SubjectBaseSchema(BaseModel):
    name: str

class SubjectCreateSchema(SubjectBaseSchema):
    pass

class SubjectSchema(SubjectBaseSchema):
    id: int

    class Config:
        from_attributes = True

```

## File: subtopics.py
```py
# schemas/subtopics.py

from pydantic import BaseModel

class SubtopicBaseSchema(BaseModel):
    name: str
    topic_id: int

class SubtopicCreateSchema(SubtopicBaseSchema):
    pass

class SubtopicSchema(SubtopicBaseSchema):
    id: int

    class Config:
        from_attributes = True

```

## File: token.py
```py
# filename: app/schemas/token.py

from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

```

## File: topics.py
```py
# filename: app/schemas/topics.py

from pydantic import BaseModel

class TopicBaseSchema(BaseModel):
    name: str
    subject_id: int

class TopicCreateSchema(TopicBaseSchema):
    pass

class TopicSchema(TopicBaseSchema):
    id: int

    class Config:
        from_attributes = True
```

## File: user.py
```py
# filename: app/schemas/user.py

import string
from typing import Optional
from pydantic import BaseModel, validator

class UserBaseSchema(BaseModel):
    username: str

class UserCreateSchema(UserBaseSchema):
    password: str

    @validator('password')
    def validate_password(cls, password):
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

class UserLoginSchema(BaseModel):
    username: str
    password: str

class UserSchema(UserBaseSchema):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

```

## File: user_responses.py
```py
# filename: app/schemas/user_responses.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class UserResponseBaseSchema(BaseModel):
    user_id: int
    question_id: int
    answer_choice_id: int
    is_correct: bool

class UserResponseCreateSchema(UserResponseBaseSchema):
    pass

class UserResponseUpdateSchema(BaseModel):
    is_correct: Optional[bool] = None

class UserResponseSchema(UserResponseBaseSchema):
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
from .randomization_service import randomize_answer_choices, randomize_questions
```

## File: auth_service.py
```py
# filename: app/services/auth_service.py

from sqlalchemy.orm import Session
from app.crud.crud_user_utils import get_user_by_username_crud
from app.core import verify_password
from app.models import UserModel

def authenticate_user(db: Session, username: str, password: str) -> UserModel:
    user = get_user_by_username_crud(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if not user.is_active:
        return False
    return user

```

## File: randomization_service.py
```py
# filename: app/utils/randomization.py

import random

def randomize_questions(questions):
    return random.sample(questions, len(questions))

def randomize_answer_choices(answer_choices):
    return random.sample(answer_choices, len(answer_choices))

```

## File: user_service.py
```py
# filename: app/services/user_service.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core import decode_access_token
from app.crud.crud_user_utils import get_user_by_username_crud
from app.db import get_db
from app.models import RevokedTokenModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
        if revoked_token:
            raise credentials_exception
        user = get_user_by_username_crud(db, username=username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError as e:
        raise credentials_exception from e

```

# Directory: /code/quiz-app/quiz-app-backend/app/crud

## File: __init__.py
```py
# filename: app/crud/__init__.py

from .crud_filters import filter_questions_crud
from .crud_question_sets import create_question_set_crud, read_question_sets_crud, read_question_set_crud, update_question_set_crud, delete_question_set_crud
from .crud_questions import create_question_crud, get_question_crud, get_questions_crud, update_question_crud, delete_question_crud
from .crud_user import create_user_crud, delete_user_crud, update_user_crud
from .crud_user_responses import create_user_response_crud, get_user_response_crud, get_user_responses_crud, update_user_response_crud, delete_user_response_crud
from .crud_user_utils import get_user_by_username_crud
from .crud_subtopics import create_subtopic_crud
from .crud_subjects import create_subject_crud, read_subject_crud, update_subject_crud, delete_subject_crud
from .crud_topics import create_topic_crud, read_topic_crud, update_topic_crud, delete_topic_crud

```

## File: crud_filters.py
```py
# filename: app/crud/crud_filters.py

from typing import List, Optional
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import (
    QuestionModel,
    SubjectModel,
    TopicModel,
    SubtopicModel,
    QuestionTagModel
)
from app.schemas import QuestionSchema, FilterParamsSchema

def filter_questions_crud(
    db: Session,
    filters: dict,  # Change this parameter to expect a dictionary
    skip: int = 0,
    limit: int = 100
) -> Optional[List[QuestionSchema]]:
    print("Entering filter_questions function")
    print(f"Received filters: {filters}")
    try:
        # Validate filters dictionary against the Pydantic model
        validated_filters = FilterParamsSchema(**filters)
    except ValidationError as e:
        print(f"Invalid filters: {str(e)}")
        raise e

    if not any(value for value in filters.values()):
        print("No filters provided")
        return None

    query = db.query(QuestionModel).join(SubjectModel).join(TopicModel).join(SubtopicModel).outerjoin(QuestionModel.tags)

    if validated_filters.subject:
        query = query.filter(func.lower(SubjectModel.name) == func.lower(validated_filters.subject))
    if validated_filters.topic:
        query = query.filter(func.lower(TopicModel.name) == func.lower(validated_filters.topic))
    if validated_filters.subtopic:
        query = query.filter(func.lower(SubtopicModel.name) == func.lower(validated_filters.subtopic))
    if validated_filters.difficulty:
        query = query.filter(func.lower(QuestionModel.difficulty) == func.lower(validated_filters.difficulty))
    if validated_filters.tags:
        query = query.filter(QuestionTagModel.tag.in_([tag.lower() for tag in validated_filters.tags]))

    questions = query.offset(skip).limit(limit).all()

    print("Returning filtered questions")
    return [QuestionSchema.model_validate(question) for question in questions]

```

## File: crud_question_sets.py
```py
# filename: app/crud/crud_question_sets.py

from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import QuestionSetModel,QuestionModel
from app.schemas import (
    QuestionSetCreateSchema,
    QuestionSetUpdateSchema
)

def read_question_set_crud(db: Session, question_set_id: int) -> QuestionSetModel:
    question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    return question_set


def read_question_sets_crud(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSetModel]:
    question_sets = db.query(QuestionSetModel).offset(skip).limit(limit).all()
    if not question_sets:
        raise HTTPException(status_code=404, detail="No question sets found.")
    
    return question_sets

def create_question_set_crud(db: Session, question_set: QuestionSetCreateSchema) -> QuestionSetModel:
    existing_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.name == question_set.name).first()
    if existing_question_set:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Question set with name '{question_set.name}' already exists.")

    db_question_set = QuestionSetModel(**question_set.model_dump())
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def update_question_set_crud(db: Session, question_set_id: int, question_set: QuestionSetUpdateSchema) -> QuestionSetModel:
    db_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not db_question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    update_data = question_set.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "question_ids":
            db_question_set.question_ids = value
        else:
            setattr(db_question_set, field, value)

    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def delete_question_set_crud(db: Session, question_set_id: int) -> bool:
    db_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not db_question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    db.delete(db_question_set)
    db.commit()
    return True

```

## File: crud_questions.py
```py
# filename: app/crud/crud_questions.py

from typing import List
from sqlalchemy.orm import Session, joinedload
from app.models import QuestionModel, AnswerChoiceModel
from app.schemas import QuestionCreateSchema, QuestionUpdateSchema
from app.services import randomize_questions, randomize_answer_choices

def create_question_crud(db: Session, question: QuestionCreateSchema) -> QuestionModel:
    db_question = QuestionModel(
        text=question.text,
        subject_id=question.subject_id,
        topic_id=question.topic_id,
        subtopic_id=question.subtopic_id,
        difficulty=question.difficulty
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.answer_choices:
        db_choice = AnswerChoiceModel(
            text=choice.text,
            is_correct=choice.is_correct,
            explanation=choice.explanation,
            question_id=db_question.id
        )
        db.add(db_choice)

    db_question.question_set_ids = question.question_set_ids

    db.commit()
    return db_question

def get_questions_crud(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionModel]:
    questions = db.query(QuestionModel).offset(skip).limit(limit).all()
    questions = randomize_questions(questions)  # Randomize the order of questions
    for question in questions:
        question.answer_choices = randomize_answer_choices(question.answer_choices)  # Randomize the order of answer choices
    return questions

def get_question_crud(db: Session, question_id: int) -> QuestionModel:
    return db.query(QuestionModel).options(
        joinedload(QuestionModel.subject),
        joinedload(QuestionModel.topic),
        joinedload(QuestionModel.subtopic),
        joinedload(QuestionModel.tags),
        joinedload(QuestionModel.answer_choices)
    ).filter(QuestionModel.id == question_id).first()

def update_question_crud(db: Session, question_id: int, question: QuestionUpdateSchema) -> QuestionModel:
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if not db_question:
        return None

    update_data = question.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "answer_choices":
            # Remove existing answer choices
            db_question.answer_choices = []
            db.commit()

            for choice_data in value:
                db_choice = AnswerChoiceModel(
                    text=choice_data["text"],
                    is_correct=choice_data["is_correct"],
                    explanation=choice_data["explanation"],
                    question_id=db_question.id
                )
                db.add(db_choice)
        else:
            setattr(db_question, field, value)

    if question.question_set_ids is not None:
        db_question.question_set_ids = question.question_set_ids

    db.commit()
    db.refresh(db_question)
    return db_question

def delete_question_crud(db: Session, question_id: int) -> bool:
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False

```

## File: crud_subjects.py
```py
# filename: app/crud/crud_subjects.py
from sqlalchemy.orm import Session
from app.models.subjects import SubjectModel
from app.schemas.subjects import SubjectCreateSchema

def create_subject_crud(db: Session, subject: SubjectCreateSchema) -> SubjectModel:
    db_subject = SubjectModel(**subject.model_dump())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def read_subject_crud(db: Session, subject_id: int) -> SubjectModel:
    return db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()

def update_subject_crud(db: Session, subject_id: int, subject: SubjectCreateSchema) -> SubjectModel:
    db_subject = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
    if db_subject:
        db_subject.name = subject.name
        db.commit()
        db.refresh(db_subject)
    return db_subject

def delete_subject_crud(db: Session, subject_id: int) -> bool:
    db_subject = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
    if db_subject:
        db.delete(db_subject)
        db.commit()
        return True
    return False

```

## File: crud_subtopics.py
```py
# crud/crud_subtopics.py

from sqlalchemy.orm import Session
from app.models import SubtopicModel
from app.schemas import SubtopicCreateSchema

def create_subtopic_crud(db: Session, subtopic: SubtopicCreateSchema) -> SubtopicModel:
    db_subtopic = SubtopicModel(**subtopic.model_dump())
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)
    return db_subtopic

```

## File: crud_topics.py
```py
# filename: app/crud/crud_topics.py

from sqlalchemy.orm import Session
from app.models import TopicModel
from app.schemas import TopicCreateSchema

def create_topic_crud(db: Session, topic: TopicCreateSchema) -> TopicModel:
    db_topic = TopicModel(**topic.model_dump())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def read_topic_crud(db: Session, topic_id: int) -> TopicModel:
    return db.query(TopicModel).filter(TopicModel.id == topic_id).first()

def update_topic_crud(db: Session, topic_id: int, topic: TopicCreateSchema) -> TopicModel:
    db_topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
    if db_topic:
        db_topic.name = topic.name
        db_topic.subject_id = topic.subject_id
        db.commit()
        db.refresh(db_topic)
    return db_topic

def delete_topic_crud(db: Session, topic_id: int) -> bool:
    db_topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
    if db_topic:
        db.delete(db_topic)
        db.commit()
        return True
    return False

```

## File: crud_user.py
```py
# filename: app/crud/crud_user.py

from sqlalchemy.orm import Session
from app.models import UserModel
from app.schemas import UserCreateSchema, UserUpdateSchema
from app.core import get_password_hash

def create_user_crud(db: Session, user: UserCreateSchema) -> UserModel:
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_crud(db: Session, user_id: int, updated_user: UserUpdateSchema) -> UserModel:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return None
    update_data = updated_user.dict(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user_crud(db: Session, user_id: int) -> UserModel:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    return None

```

## File: crud_user_responses.py
```py
# filename: app/crud/crud_user_responses.py

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import UserResponseModel
from app.schemas import UserResponseCreateSchema, UserResponseUpdateSchema

def create_user_response_crud(db: Session, user_response: UserResponseCreateSchema) -> UserResponseModel:
    db_user_response = UserResponseModel(**user_response.model_dump())
    db.add(db_user_response)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

def get_user_response_crud(db: Session, user_response_id: int) -> Optional[UserResponseModel]:
    return db.query(UserResponseModel).filter(UserResponseModel.id == user_response_id).first()

def get_user_responses_crud(db: Session, skip: int = 0, limit: int = 100) -> List[UserResponseModel]:
    return db.query(UserResponseModel).offset(skip).limit(limit).all()

def update_user_response_crud(db: Session, user_response_id: int, user_response: UserResponseUpdateSchema) -> UserResponseModel:
    db_user_response = db.query(UserResponseModel).filter(UserResponseModel.id == user_response_id).first()
    if not db_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    update_data = user_response.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user_response, key, value)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

def delete_user_response_crud(db: Session, user_response_id: int) -> None:
    db_user_response = db.query(UserResponseModel).filter(UserResponseModel.id == user_response_id).first()
    if not db_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    db.delete(db_user_response)
    db.commit()
```

## File: crud_user_utils.py
```py
# filename: app/crud/crud_user_utils.py

from sqlalchemy.orm import Session
from app.models import UserModel

def get_user_by_username_crud(db: Session, username: str) -> UserModel:
    return db.query(UserModel).filter(UserModel.username == username).first()

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
from app.models import UserModel, RevokedTokenModel
from app.schemas import TokenSchema, LoginFormSchema

logger = logging.getLogger(__name__)

router = APIRouter()

blacklist = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/login", response_model=TokenSchema)
async def login_for_access_token(form_data: LoginFormSchema, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()

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
    try:
        revoked_token = RevokedTokenModel(token=token)
        db.add(revoked_token)
        db.commit()
        return {"message": "Successfully logged out"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout user"
        ) from e

```

## File: filters.py
```py
# filename: app/api/endpoints/filters.py

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.schemas import QuestionSchema, FilterParamsSchema
from app.crud import filter_questions_crud
from app.db import get_db

router = APIRouter()

async def forbid_extra_params(request: Request):
    allowed_params = {'subject', 'topic', 'subtopic', 'difficulty', 'tags', 'skip', 'limit'}
    actual_params = set(request.query_params.keys())
    extra_params = actual_params - allowed_params
    if extra_params:
        raise HTTPException(status_code=422, detail=f"Unexpected parameters provided: {extra_params}")

@router.get("/questions/filter", response_model=List[QuestionSchema], status_code=200)
async def filter_questions_endpoint(
    request: Request,
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    subtopic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    await forbid_extra_params(request)
    try:
        # Constructing the filters model from the query parameters directly
        filters = FilterParamsSchema(
            subject=subject,
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            tags=tags
        )
        questions = filter_questions_crud(
            db=db,
            filters=filters.model_dump(),
            skip=skip,
            limit=limit
        )
        return questions if questions else []
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

```

## File: question.py
```py
# filename: app/api/endpoints/question.py

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.crud import (
    create_question_crud,
    get_question_crud,
    update_question_crud,
    delete_question_crud
)
from app.db import get_db
from app.schemas import (
    AnswerChoiceSchema,
    QuestionCreateSchema,
    QuestionUpdateSchema,
    QuestionSchema,
    QuestionTagSchema
)

router = APIRouter()

@router.post("/question", response_model=QuestionSchema, status_code=201)
def create_question_endpoint(question: QuestionCreateSchema, db: Session = Depends(get_db)):
    if not all([question.subject_id, question.topic_id, question.subtopic_id]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="subject_id, topic_id, and subtopic_id are required")

    question_db = create_question_crud(db, question)
    return QuestionSchema(
        id=question_db.id,
        text=question_db.text,
        subject_id=question_db.subject_id,
        topic_id=question_db.topic_id,
        subtopic_id=question_db.subtopic_id,
        difficulty=question_db.difficulty,
        tags=[QuestionTagSchema.model_validate(tag) for tag in question_db.tags],
        answer_choices=[AnswerChoiceSchema.model_validate(choice) for choice in question_db.answer_choices],
        question_set_ids=question_db.question_set_ids
    )

@router.get("/question/question_id}", response_model=QuestionSchema)
def get_question_endpoint(question_id: int, question: QuestionUpdateSchema, db: Session = Depends(get_db)):
    question = get_question_crud(db, question_id)
    return question

@router.put("/question/{question_id}", response_model=QuestionSchema)
def update_question_endpoint(question_id: int, question: QuestionUpdateSchema, db: Session = Depends(get_db)):
    db_question = update_question_crud(db, question_id=question_id, question=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
    return QuestionSchema(
        id=db_question.id,
        text=db_question.text,
        subject_id=db_question.subject_id,
        topic_id=db_question.topic_id,
        subtopic_id=db_question.subtopic_id,
        difficulty=db_question.difficulty,
        tags=[QuestionTagSchema.model_validate(tag) for tag in db_question.tags],
        answer_choices=[AnswerChoiceSchema.model_validate(choice) for choice in db_question.answer_choices],
        question_set_ids=db_question.question_set_ids
    )

@router.delete("/question/{question_id}", status_code=204)
def delete_question_endpoint(question_id: int, db: Session = Depends(get_db)):
    deleted = delete_question_crud(db, question_id=question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
    return Response(status_code=204)

```

## File: question_sets.py
```py
# filename: app/api/endpoints/question_sets.py

import json
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Response,
    status
)
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.db import get_db
from app.services import get_current_user
from app.models import UserModel, QuestionSetModel
from app.crud import (
    create_question_crud,
    read_question_sets_crud,
    read_question_set_crud,
    update_question_set_crud,
    delete_question_set_crud,
    create_question_set_crud
)
from app.schemas import (
    QuestionSetSchema,
    QuestionSetCreateSchema,
    QuestionSetUpdateSchema,
    QuestionCreateSchema
)

router = APIRouter()

@router.post("/upload-questions/")
async def upload_question_set_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can upload question sets")

    try:
        content = await file.read()
        question_data = json.loads(content.decode('utf-8'))

        # Validate question data
        for question in question_data:
            QuestionCreateSchema(**question)  # Validate question against schema

        # Create question set
        question_set = QuestionSetCreateSchema(name=file.filename)
        question_set_created = create_question_set_crud(db, question_set)

        # Create questions and associate with question set
        for question in question_data:
            question['question_set_id'] = question_set_created.id
            create_question_crud(db, QuestionCreateSchema(**question))

        return {"message": "Question set uploaded successfully"}

    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON data: {str(exc)}") from exc

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading question set: {str(exc)}") from exc

@router.get("/question-set/", response_model=List[QuestionSetSchema])
def read_questions_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    questions = read_question_sets_crud(db, skip=skip, limit=limit)
    return questions

@router.post("/question-sets/", response_model=QuestionSetSchema, status_code=201)
def create_question_set_endpoint(question_set: QuestionSetCreateSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can create question sets")

    return create_question_set_crud(db=db, question_set=question_set)

@router.get("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def get_question_set_endpoint(question_set_id: int, db: Session = Depends(get_db)):
    question_set = read_question_set_crud(db, question_set_id=question_set_id)
    if not question_set:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question set with ID {question_set_id} not found")
    return question_set

@router.get("/question-sets/", response_model=List[QuestionSetSchema])
def read_question_sets_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    question_sets = read_question_sets_crud(db, skip=skip, limit=limit)
    return question_sets

@router.put("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def update_question_set_endpoint(question_set_id: int, question_set: QuestionSetUpdateSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can update question sets")

    db_question_set = update_question_set_crud(db, question_set_id=question_set_id, question_set=question_set)
    if db_question_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found")
    return QuestionSetSchema(
        id=db_question_set.id,
        name=db_question_set.name,
        is_public=db_question_set.is_public,
        question_ids=db_question_set.question_ids
    )

@router.delete("/question-sets/{question_set_id}", status_code=204)
def delete_question_set_endpoint(question_set_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can delete question sets")

    deleted = delete_question_set_crud(db, question_set_id=question_set_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

```

## File: questions.py
```py
# filename: app/api/endpoints/questions.py

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud import get_questions_crud
from app.db import get_db
from app.schemas import QuestionSchema
from app.services import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.get("/questions/", response_model=List[QuestionSchema])
def get_questions_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    questions = get_questions_crud(db, skip=skip, limit=limit)
    if not questions:
        return []
    return questions

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
from app.crud import create_user_crud, get_user_by_username_crud
from app.db import get_db
from app.schemas import UserCreateSchema

router = APIRouter()

@router.post("/register/", status_code=201)
def register_user(user: UserCreateSchema, db: Session = Depends(get_db)):
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
    db_user = get_user_by_username_crud(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=422, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    user_create = UserCreateSchema(username=user.username, password=hashed_password)
    created_user = create_user_crud(db=db, user=user_create)
    return created_user

```

## File: subjects.py
```py
# filename: app/api/endpoints/subjects.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.subjects import SubjectSchema, SubjectCreateSchema
from app.crud import create_subject_crud, read_subject_crud, update_subject_crud, delete_subject_crud

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
def create_subject_endpoint(subject: SubjectCreateSchema, db: Session = Depends(get_db)):
    return create_subject_crud(db=db, subject=subject)

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
def read_subject_endpoint(subject_id: int, db: Session = Depends(get_db)):
    subject = read_subject_crud(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.put("/subjects/{subject_id}", response_model=SubjectSchema)
def update_subject_endpoint(subject_id: int, subject: SubjectCreateSchema, db: Session = Depends(get_db)):
    updated_subject = update_subject_crud(db, subject_id, subject)
    if not updated_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return updated_subject

@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject_endpoint(subject_id: int, db: Session = Depends(get_db)):
    deleted = delete_subject_crud(db, subject_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subject not found")
    return None

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
from app.core import create_access_token, settings_core
from app.db import get_db
from app.schemas import TokenSchema

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/token", response_model=TokenSchema)
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
    access_token_expires = timedelta(minutes=settings_core.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

```

## File: topics.py
```py
# filename: app/api/endpoints/topics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import TopicSchema, TopicCreateSchema
from app.crud import create_topic_crud, read_topic_crud, update_topic_crud, delete_topic_crud

router = APIRouter()

@router.post("/topics/", response_model=TopicSchema, status_code=201)
def create_topic_endpoint(topic: TopicCreateSchema, db: Session = Depends(get_db)):
    return create_topic_crud(db=db, topic=topic)

@router.get("/topics/{topic_id}", response_model=TopicSchema)
def read_topic_endpoint(topic_id: int, db: Session = Depends(get_db)):
    topic = read_topic_crud(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.put("/topics/{topic_id}", response_model=TopicSchema)
def update_topic_endpoint(topic_id: int, topic: TopicCreateSchema, db: Session = Depends(get_db)):
    updated_topic = update_topic_crud(db, topic_id, topic)
    if not updated_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return updated_topic

@router.delete("/topics/{topic_id}", status_code=204)
def delete_topic_endpoint(topic_id: int, db: Session = Depends(get_db)):
    deleted = delete_topic_crud(db, topic_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Topic not found")
    return None
```

## File: user_responses.py
```py
# filename: app/api/endpoints/user_responses.py

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from app.crud import (
    create_user_response_crud,
    get_user_response_crud,
    get_user_responses_crud,
    update_user_response_crud,
    delete_user_response_crud
)
from app.db import get_db
from app.schemas import UserResponseSchema, UserResponseCreateSchema, UserResponseUpdateSchema
from app.models import AnswerChoiceModel, UserModel, QuestionModel

router = APIRouter()

@router.post("/user-responses/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def create_user_response_endpoint(user_response: UserResponseCreateSchema, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_response.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id")

    question = db.query(QuestionModel).filter(QuestionModel.id == user_response.question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question_id")

    answer_choice = db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id == user_response.answer_choice_id).first()
    if not answer_choice:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid answer_choice_id")

    return create_user_response_crud(db=db, user_response=user_response)

@router.get("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def get_user_response_endpoint(user_response_id: int, db: Session = Depends(get_db)):
    user_response = get_user_response_crud(db, user_response_id)
    if not user_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User response not found")
    return user_response

@router.get("/user-responses/", response_model=List[UserResponseSchema])
def get_user_responses_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user_responses = get_user_responses_crud(db, skip=skip, limit=limit)
    return user_responses

@router.put("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def update_user_response_endpoint(user_response_id: int, user_response: UserResponseUpdateSchema, db: Session = Depends(get_db)):
    updated_user_response = update_user_response_crud(db, user_response_id, user_response)
    return updated_user_response

@router.delete("/user-responses/{user_response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_response_endpoint(user_response_id: int, db: Session = Depends(get_db)):
    delete_user_response_crud(db, user_response_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

```

## File: users.py
```py
# filename: app/api/endpoints/users.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import UserModel
from app.crud import create_user_crud, update_user_crud
from app.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema
from app.services import get_current_user

router = APIRouter()

@router.get("/users/", response_model=List[UserSchema])
def read_users(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    users = db.query(UserModel).all()
    return users

@router.post("/users/", response_model=UserSchema, status_code=201)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    try:
        new_user = create_user_crud(db=db, user=user)
        return new_user
    except Exception as e:
        # If there's an error (e.g., username already exists), raise an HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
            ) from e

@router.get("/users/me", response_model=UserSchema)
def read_user_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.put("/users/me", response_model=UserSchema)
def update_user_me(updated_user: UserUpdateSchema, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_user_crud(db=db, user_id=current_user.id, updated_user=updated_user)

```

# Directory: /code/quiz-app/quiz-app-backend/app/models

## File: __init__.py
```py
# filename: app/models/__init__.py

from .answer_choices import AnswerChoiceModel
from .question_sets import QuestionSetModel
from .question_tags import QuestionTagModel, QuestionTagAssociation
from .questions import QuestionModel
from .sessions import SessionModel, SessionQuestionModel, SessionQuestionSetModel
from .subjects import SubjectModel
from .subtopics import SubtopicModel
from .topics import TopicModel
from .token import RevokedTokenModel
from .user_responses import UserResponseModel
from .users import UserModel

```

## File: answer_choices.py
```py
# filename: app/models/answer_choices.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base

class AnswerChoiceModel(Base):
    __tablename__ = "answer_choices"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    is_correct = Column(Boolean)
    explanation = Column(Text)  # Add the explanation field
    question_id = Column(Integer, ForeignKey('questions.id'))

    question = relationship("QuestionModel", back_populates="answer_choices")

```

## File: question_sets.py
```py
# filename: app/models/question_sets.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.questions import question_set_question

class QuestionSetModel(Base):
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_public = Column(Boolean, default=True)

    questions = relationship("QuestionModel", secondary=question_set_question, back_populates="question_sets")
    sessions = relationship("SessionQuestionSetModel", back_populates="question_set")

```

## File: question_tags.py
```py
# filename: app/models/question_tags.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class QuestionTagModel(Base):
    __tablename__ = "question_tags"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, index=True)

    questions = relationship("QuestionModel", secondary="question_tag_association", overlaps="tags")

class QuestionTagAssociation(Base):
    __tablename__ = "question_tag_association"

    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("question_tags.id"), primary_key=True)

```

## File: questions.py
```py
# filename: app/models/questions.py

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.inspection import inspect
from app.db.base_class import Base

question_set_question = Table('question_set_question', Base.metadata,
    Column('question_id', ForeignKey('questions.id'), primary_key=True),
    Column('question_set_id', ForeignKey('question_sets.id'), primary_key=True)
)

class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"))
    difficulty = Column(String)

    subject = relationship("SubjectModel", back_populates="questions")
    topic = relationship("TopicModel", back_populates="questions")
    subtopic = relationship("SubtopicModel", back_populates="questions")
    tags = relationship("QuestionTagModel", secondary="question_tag_association")
    answer_choices = relationship("AnswerChoiceModel", back_populates="question")
    question_sets = relationship("QuestionSetModel", secondary=question_set_question, back_populates="questions")
    sessions = relationship("SessionQuestionModel", back_populates="question")

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

```

## File: sessions.py
```py
# filename: app/models/sessions.py

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class SessionQuestionModel(Base):
    __tablename__ = 'session_question'
    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    answered = Column(Boolean, default=False)
    correct = Column(Boolean, nullable=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    session = relationship("SessionModel", back_populates="questions")
    question = relationship("QuestionModel", back_populates="sessions")

class SessionQuestionSetModel(Base):
    __tablename__ = 'session_question_set'
    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    question_set_id = Column(Integer, ForeignKey('question_sets.id'), primary_key=True)
    question_limit = Column(Integer, nullable=True)  # Optional limit on questions from this set

    session = relationship("SessionModel", back_populates="question_sets")
    question_set = relationship("QuestionSetModel", back_populates="sessions")

class SessionModel(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    # Additional fields as needed, e.g., session name, date, etc.

    questions = relationship("SessionQuestionModel", back_populates="session")
    question_sets = relationship("SessionQuestionSetModel", back_populates="session")

```

## File: subjects.py
```py
# filename: app/models/subjects.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class SubjectModel(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    topics = relationship("TopicModel", back_populates="subject")
    questions = relationship("QuestionModel", back_populates="subject")

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

class SubtopicModel(Base):
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

    topic = relationship("TopicModel", back_populates="subtopics")
    questions = relationship("QuestionModel", back_populates="subtopic")

```

## File: token.py
```py
# filename: app/models/token.py

from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base_class import Base

class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    # pylint: disable=not-callable
    revoked_at = Column(DateTime, server_default=func.now())

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
from app.db import Base

class TopicModel(Base):
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

    subject = relationship("SubjectModel", back_populates="topics")
    subtopics = relationship("SubtopicModel", back_populates="topic")
    questions = relationship("QuestionModel", back_populates="topic")
```

## File: user_responses.py
```py
# filename: app/models/user_responses.py

from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime
from app.db.base_class import Base

class UserResponseModel(Base):
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_choice_id = Column(Integer, ForeignKey('answer_choices.id'))
    is_correct = Column(Boolean)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("UserModel", back_populates="responses")
    question = relationship("QuestionModel")
    answer_choice = relationship("AnswerChoiceModel")

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

class UserModel(Base):
    """
    The User model.
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Add this line

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
 
    responses = relationship("UserResponseModel", back_populates="user")

```

# Directory: /code/quiz-app/quiz-app-backend/app/core

## File: __init__.py
```py
# filename: app/core/__init__.py
"""
This module serves as the main entry point for the core package.

It can be used to perform any necessary initialization or configuration for the core package.
"""
from .config import SettingsCore, settings_core
from .jwt import create_access_token, verify_token, decode_access_token
from .security import verify_password, get_password_hash

```

## File: config.py
```py
# filename: app/core/config.py
from pydantic_settings import BaseSettings

class SettingsCore(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"

settings_core = SettingsCore()

```

## File: jwt.py
```py
# filename: app/core/jwt.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.core import settings_core

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings_core.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings_core.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings_core.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except jwt.JWTError:
        raise credentials_exception

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings_core.SECRET_KEY, algorithms=["HS256"])
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
    create_user_crud,
    create_question_crud,
    create_question_set_crud,
    create_subtopic_crud,
    create_subject_crud,
    create_topic_crud
)
from app.schemas import (
    UserCreateSchema,
    QuestionSetCreateSchema,
    QuestionCreateSchema,
    AnswerChoiceCreateSchema,
    SubtopicCreateSchema,
    SubjectCreateSchema,
    TopicCreateSchema
    )
from app.models import (
    AnswerChoiceModel,
    SubjectModel,
    TopicModel,
    SubtopicModel,
    QuestionModel,
    QuestionTagModel,
    QuestionSetModel
)
from app.core import create_access_token, settings_core

# Testing database
DATABASE_URL = settings_core.DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

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
    yield "testuser_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture(scope="function")
def test_user(db_session, random_username):
    user_data = UserCreateSchema(username=random_username, password="TestPassword123!")
    user = create_user_crud(db_session, user_data)
    user.is_admin = True
    db_session.add(user)
    db_session.commit()
    yield user

@pytest.fixture
def test_question_set_data(db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    subject = create_subject_crud(db_session, subject_data)
    return QuestionSetCreateSchema(name="Sample Question Set", subject_id=subject.id)

@pytest.fixture(scope="function")
def test_question_set(db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    subject = create_subject_crud(db_session, subject_data)
    question_set_data = QuestionSetCreateSchema(name="Test Question Set", subject_id=subject.id)
    question_set = create_question_set_crud(db_session, question_set_data)
    db_session.commit()
    yield question_set

@pytest.fixture(scope="function")
def test_subject(db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    subject = create_subject_crud(db=db_session, subject=subject_data)
    yield subject

@pytest.fixture(scope="function")
def test_topic(db_session, test_subject):
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=test_subject.id)
    topic = create_topic_crud(db=db_session, topic=topic_data)
    yield topic

@pytest.fixture(scope="function")
def test_subtopic(db_session, test_topic):
    subtopic_data = SubtopicCreateSchema(name="Test Subtopic", topic_id=test_topic.id)
    subtopic = create_subtopic_crud(db=db_session, subtopic=subtopic_data)
    yield subtopic

@pytest.fixture(scope="function")
def test_question(db_session, test_question_set, test_subtopic, test_topic, test_subject):
    answer_choice_1 = AnswerChoiceCreateSchema(text="Test Answer 1", is_correct=True, explanation="Test Explanation 1")
    answer_choice_2 = AnswerChoiceCreateSchema(text="Test Answer 2", is_correct=False, explanation="Test Explanation 2")
    question_data = QuestionCreateSchema(
        text="Test Question",
        subject_id=test_subject.id,
        topic_id=test_topic.id,
        subtopic_id=test_subtopic.id,
        difficulty="Easy",
        answer_choices=[answer_choice_1, answer_choice_2],
        question_set_ids=[test_question_set.id]
    )
    question = create_question_crud(db_session, question_data)
    yield question

@pytest.fixture(scope="function")
def test_token(test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    yield access_token

@pytest.fixture(scope="function")
def test_answer_choice_1(db_session, test_question):
    answer_choice = AnswerChoiceModel(text="Test Answer 1", is_correct=True, question=test_question)
    db_session.add(answer_choice)
    db_session.commit()
    yield answer_choice

@pytest.fixture(scope="function")
def test_answer_choice_2(db_session, test_question):
    answer_choice = AnswerChoiceModel(text="Test Answer 2", is_correct=False, question=test_question)
    db_session.add(answer_choice)
    db_session.commit()
    yield answer_choice

@pytest.fixture(scope="function")
def logged_in_client(client, test_user):
    # Perform login
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/login", json=login_data)
    access_token = response.json()["access_token"]
    assert response.status_code == 200, "Authentication failed."
    
    # Set Authorization header for subsequent requests
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client

@pytest.fixture(scope="function")
def setup_filter_questions_data(db_session):
    # Create multiple subjects, topics, and subtopics
    subject1 = SubjectModel(name="Math")
    subject2 = SubjectModel(name="Science")
    topic1 = TopicModel(name="Algebra", subject=subject1)
    topic2 = TopicModel(name="Geometry", subject=subject1)
    topic3 = TopicModel(name="Physics", subject=subject2)
    subtopic1 = SubtopicModel(name="Linear Equations", topic=topic1)
    subtopic2 = SubtopicModel(name="Quadratic Equations", topic=topic1)
    subtopic3 = SubtopicModel(name="Triangles", topic=topic2)
    subtopic4 = SubtopicModel(name="Mechanics", topic=topic3)
    db_session.add_all([subject1, subject2, topic1, topic2, topic3, subtopic1, subtopic2, subtopic3, subtopic4])
    db_session.commit()

    # Create multiple question tags
    tag1 = QuestionTagModel(tag="equations")
    tag2 = QuestionTagModel(tag="solving")
    tag3 = QuestionTagModel(tag="geometry")
    tag4 = QuestionTagModel(tag="physics")
    db_session.add_all([tag1, tag2, tag3, tag4])
    db_session.commit()

    # Create multiple question sets
    question_set1 = QuestionSetModel(name="Math Question Set", is_public=True)
    question_set2 = QuestionSetModel(name="Science Question Set", is_public=True)
    db_session.add_all([question_set1, question_set2])
    db_session.commit()

    # Create multiple questions with different filter criteria
    question1 = QuestionModel(
        text="What is x if 2x + 5 = 11?",
        subject=subject1,
        topic=topic1,
        subtopic=subtopic1,
        difficulty="Easy",
        tags=[tag1, tag2]
    )
    question2 = QuestionModel(
        text="Find the roots of the equation: x^2 - 5x + 6 = 0",
        subject=subject1,
        topic=topic1,
        subtopic=subtopic2,
        difficulty="Medium",
        tags=[tag1, tag2]
    )
    question3 = QuestionModel(
        text="Calculate the area of a right-angled triangle with base 4 cm and height 3 cm.",
        subject=subject1,
        topic=topic2,
        subtopic=subtopic3,
        difficulty="Easy",
        tags=[tag3]
    )
    question4 = QuestionModel(
        text="A car accelerates from rest at 2 m/s^2. What is its velocity after 5 seconds?",
        subject=subject2,
        topic=topic3,
        subtopic=subtopic4,
        difficulty="Medium",
        tags=[tag4]
    )
    db_session.add_all([question1, question2, question3, question4])
    db_session.commit()

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_integration

## File: test_integration_auth.py
```py
# filename: tests/test_auth_integration.py

import pytest
from fastapi import HTTPException

def test_protected_route_with_valid_token(client, test_user, test_token, db_session):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200

def test_protected_route_with_invalid_token(client, db_session):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_protected_route_with_revoked_token(client, test_user, test_token, db_session):
    # Logout to revoke the token
    headers = {"Authorization": f"Bearer {test_token}"}
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200

    # Try accessing the protected route with the revoked token
    with pytest.raises(HTTPException) as exc_info:
        client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has been revoked"

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_schemas

## File: test_schemas_filters.py
```py
import pytest
from pydantic import ValidationError
from app.schemas import FilterParamsSchema

def test_filter_params_schema_invalid_params():
    invalid_data = {
        "subject": "Math",
        "topic": "Algebra",
        "subtopic": "Linear Equations",
        "difficulty": "Easy",
        "tags": ["equations", "solving"],
        "invalid_param": "value"  # Invalid parameter
    }
    
    with pytest.raises(ValidationError) as exc_info:
        FilterParamsSchema(**invalid_data)
    
    assert "Extra inputs are not permitted" in str(exc_info.value)

```

## File: test_schemas_schemas.py
```py
# filename: tests/test_schemas.py

from app.schemas import UserCreateSchema, QuestionCreateSchema

def test_user_create_schema():
    user_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.username == "testuser"
    assert user_schema.password == "TestPassword123!"

def test_user_create_schema_password_validation():
    user_data = {"username": "testuser", "password": "ValidPassword123!"}
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_question_create_schema():
    question_data = {
        "text": "Test question",
        "subject_id": 1,
        "topic_id": 1,
        "subtopic_id": 1,
        "question_set_ids": [1],
        "difficulty": "Easy",
        "answer_choices": [
            {"text": "Answer 1", "is_correct": True, "explanation": "Test explanation 1"},
            {"text": "Answer 2", "is_correct": False, "explanation": "Test explanation 2"}
        ]
    }
    question_schema = QuestionCreateSchema(**question_data)
    assert question_schema.text == "Test question"
    assert question_schema.subject_id == 1
    assert question_schema.topic_id == 1
    assert question_schema.subtopic_id == 1
    assert question_schema.question_set_ids == [1]
    assert question_schema.difficulty == "Easy"
    assert len(question_schema.answer_choices) == 2

```

## File: test_schemas_user.py
```py
# filename: tests/test_schemas_user.py

import pytest
from app.schemas.user import UserCreateSchema

def test_user_create_schema_password_validation():
    """
    Test password validation in UserCreate schema.
    """
    # Test password too short
    with pytest.raises(ValueError):
        UserCreateSchema(username="testuser", password="short")

    # Test password valid
    user_data = {"username": "testuser", "password": "ValidPassword123!"}
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_user_create_schema_password_complexity_validation():
    """Test password complexity validation in UserCreate schema."""
    # Test password missing a digit
    with pytest.raises(ValueError, match="Password must contain at least one digit"):
        UserCreateSchema(username="testuser", password="NoDigitPassword")

    # Test password missing an uppercase letter
    with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
        UserCreateSchema(username="testuser", password="nouppercasepassword123")

    # Test password missing a lowercase letter
    with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
        UserCreateSchema(username="testuser", password="NOLOWERCASEPASSWORD123")

    # Test valid password
    user_data = {"username": "testuser", "password": "ValidPassword123!"}
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.password == "ValidPassword123!"

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_api

## File: test_api_authentication.py
```py
# filename: tests/test_api_authentication.py

import pytest
from fastapi import HTTPException
from datetime import timedelta
from app.core import create_access_token
from app.models import RevokedTokenModel

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

def test_access_protected_endpoint_with_invalid_token(client, db_session):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

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

def test_login_invalid_token_format(client, db_session):
    headers = {"Authorization": "Bearer invalid_token_format"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

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
    # Revoke the token manually
    revoked_token = RevokedTokenModel(token=test_token)
    db_session.add(revoked_token)
    db_session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    with pytest.raises(HTTPException) as exc_info:
        client.post("/logout", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has been revoked"

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
    with pytest.raises(HTTPException) as exc_info:
        client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has been revoked"

```

## File: test_api_filters.py
```py
# filename: tests/test_api_filters.py

import pytest
from app.models import (
    SubjectModel,
    TopicModel,
    SubtopicModel,
    QuestionTagModel,
    QuestionSetModel,
    QuestionModel
)
from app.api.endpoints.filters import filter_questions_endpoint

def test_setup_filter_questions_data(db_session, setup_filter_questions_data):
    # Check if the required data is created in the database
    assert db_session.query(SubjectModel).filter(SubjectModel.name == "Math").first() is not None
    assert db_session.query(SubjectModel).filter(SubjectModel.name == "Science").first() is not None
    assert db_session.query(TopicModel).filter(TopicModel.name == "Algebra").first() is not None
    assert db_session.query(TopicModel).filter(TopicModel.name == "Geometry").first() is not None
    assert db_session.query(TopicModel).filter(TopicModel.name == "Physics").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Linear Equations").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Quadratic Equations").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Triangles").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Mechanics").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "equations").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "solving").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "geometry").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "physics").first() is not None
    assert db_session.query(QuestionSetModel).filter(QuestionSetModel.name == "Math Question Set").first() is not None
    assert db_session.query(QuestionSetModel).filter(QuestionSetModel.name == "Science Question Set").first() is not None
    assert db_session.query(QuestionModel).count() == 4

def test_filter_questions(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "Math",
            "topic": "Algebra",
            "subtopic": "Linear Equations",
            "difficulty": "Easy",
            "tags": ["equations", "solving"]
        }
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    if questions:
        subject = db_session.query(SubjectModel).filter(SubjectModel.name == "Math").first()
        topic = db_session.query(TopicModel).filter(TopicModel.name == "Algebra").first()
        subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Linear Equations").first()
        for question in questions:
            assert question["subject_id"] == subject.id
            assert question["topic_id"] == topic.id
            assert question["subtopic_id"] == subtopic.id
            assert question["difficulty"] == "Easy"
            assert "equations" in [tag["tag"] for tag in question["tags"]]
            assert "solving" in [tag["tag"] for tag in question["tags"]]

def test_filter_questions_by_subject(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"subject": "Math"}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    subject = db_session.query(SubjectModel).filter(SubjectModel.name == "Math").first()
    assert all(question["subject_id"] == subject.id for question in questions)

def test_filter_questions_by_topic(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"topic": "Algebra"}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    topic = db_session.query(TopicModel).filter(TopicModel.name == "Algebra").first()
    assert all(question["topic_id"] == topic.id for question in questions)

def test_filter_questions_by_subtopic(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"subtopic": "Linear Equations"}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Linear Equations").first()
    assert all(question["subtopic_id"] == subtopic.id for question in questions)

def test_filter_questions_by_difficulty(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"difficulty": "Easy"}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    assert all(question["difficulty"] == "Easy" for question in questions)

def test_filter_questions_by_single_tag(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"tags": ["equations"]}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    tag = db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "equations").first()
    assert all(tag.id in [t.id for t in question["tags"]] for question in questions)

def test_filter_questions_by_tags(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"tags": ["geometry"]}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    tag = db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "geometry").first()
    assert all(tag.id in [t.id for t in question["tags"]] for question in questions)

def test_filter_questions_by_multiple_criteria(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "Math",
            "topic": "Algebra",
            "difficulty": "Easy"
        }
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    subject = db_session.query(SubjectModel).filter(SubjectModel.name == "Math").first()
    topic = db_session.query(TopicModel).filter(TopicModel.name == "Algebra").first()
    for question in questions:
        assert question["subject_id"] == subject.id
        assert question["topic_id"] == topic.id
        assert question["difficulty"] == "Easy"

def test_filter_questions_with_pagination(logged_in_client, db_session, setup_filter_questions_data):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "Math",
            "skip": 1,
            "limit": 2
        }
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert len(questions) <= 2
    assert all(question["subject_id"] == 1 for question in questions)

def test_filter_questions_no_results(logged_in_client, db_session, setup_filter_questions_data):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "NonexistentSubject"
        }
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert len(questions) == 0

def test_filter_questions_no_params(logged_in_client, db_session):
    response = logged_in_client.get("/questions/filter")
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)

def test_filter_questions_endpoint_invalid_params(logged_in_client, db_session):
    response = logged_in_client.get("/questions/filter", params={"invalid_param": "value"})
    assert response.status_code == 422, f"Failed with response: {response.json()}"
    assert "Unexpected parameters provided" in response.json()["detail"]

@pytest.mark.asyncio
async def test_filter_questions_endpoint_invalid_params_direct(db_session):
    invalid_params = {
        "invalid_param": "value",  # This should cause validation to fail
        "subject": None,
        "topic": None,
        "subtopic": None,
        "difficulty": None,
        "tags": None
    }
    with pytest.raises(TypeError) as exc_info:
        # Simulate the endpoint call with invalid parameters
        # pylint: disable=unexpected-keyword-arg
        await filter_questions_endpoint(db=db_session, **invalid_params)
    assert "got an unexpected keyword argument" in str(exc_info.value)

```

## File: test_api_question_sets.py
```py
# filename: tests/test_api_question_sets.py

import json
import tempfile

def test_create_question_set_endpoint(logged_in_client):
    data = {"name": "Test Question Set", "is_public": True}
    response = logged_in_client.post("/question-sets/", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Question Set"
    assert response.json()["is_public"] == True

def test_read_question_sets(logged_in_client, db_session, test_question_set):
    response = logged_in_client.get("/question-sets/")
    assert response.status_code == 200
    assert any(qs["id"] == test_question_set.id and qs["name"] == test_question_set.name for qs in response.json())

def test_update_question_set_not_found(logged_in_client):
    question_set_id = 999
    question_set_update = {"name": "Updated Name"}
    response = logged_in_client.put(f"/question-sets/{question_set_id}", json=question_set_update)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

# def test_delete_question_set_not_found(logged_in_client):
#     """
#     Test deleting a question set that does not exist.
#     """
#     question_set_id = 999
#     response = logged_in_client.delete(f"/question-sets/{question_set_id}")
#     assert response.status_code == 404
#     assert response.json()["detail"] == f"Question set with ID {question_set_id} not found."

# def test_upload_question_set_success(logged_in_client, db_session, test_question):
#     # Prepare valid JSON data
#     json_data = [
#         {
#             "text": test_question.text,
#             "subject_id": test_question.subject_id,
#             "topic_id": test_question.topic_id,
#             "subtopic_id": test_question.subtopic_id,
#             "difficulty": test_question.difficulty,
#             "answer_choices": test_question.answer_choices,
#             "explanation": test_question.explanation,
#             "question_set_id": test_question.question_set_ids
#         }
#     ]
    
#     # Create a temporary file with the JSON data
#     with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
#         json.dump(json_data, temp_file)
#         temp_file.flush()  # Ensure the contents are written to the file
#         response = logged_in_client.post("/upload-questions/",
#                                files={"file": ("question_set.json", open(temp_file.name, 'rb'), "application/json")})
        
#     assert response.status_code == 200
#     assert response.json() == {"message": "Question set uploaded successfully"}

def test_upload_question_set_invalid_json(logged_in_client, db_session):
    # Prepare invalid JSON data
    invalid_json = "{'invalid': 'json'}"

    # Create a temporary file with the invalid JSON data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_file.write(invalid_json)
        temp_file.flush()  # Ensure the contents are written to the file
        response = logged_in_client.post("/upload-questions/", files={"file": ("invalid.json", open(temp_file.name, 'rb'), "application/json")})

    assert response.status_code == 400
    assert "Invalid JSON data" in response.json()["detail"]

def test_create_question_set_with_existing_name(logged_in_client, test_question_set, test_subject):
    data = {"name": test_question_set.name, "subject_id": test_subject.id}
    response = logged_in_client.post("/question-sets/", json=data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_retrieve_question_set_with_questions(logged_in_client, test_question_set, test_question):
    response = logged_in_client.get(f"/question-sets/{test_question_set.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_question_set.id
    assert response.json()["name"] == test_question_set.name

def test_update_question_set_endpoint(logged_in_client, test_question_set, test_question):
    data = {"name": "Updated Question Set", "question_ids": [test_question.id]}
    response = logged_in_client.put(f"/question-sets/{test_question_set.id}", json=data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Question Set"
    assert test_question.id in response.json()["question_ids"]

def test_delete_question_set(logged_in_client, test_question_set, db_session):
    question_set_id = test_question_set.id
    response = logged_in_client.delete(f"/question-sets/{question_set_id}")
    assert response.status_code == 204
    response = logged_in_client.get("/question-sets/")
    question_sets_after_deletion = response.json()
    if isinstance(question_sets_after_deletion, list):
        assert not any(qs['id'] == question_set_id for qs in question_sets_after_deletion), "Question set was not deleted."
    elif isinstance(question_sets_after_deletion, dict) and 'detail' in question_sets_after_deletion:
        assert question_sets_after_deletion['detail'] == 'No question sets found.', "Unexpected response after deletion."
    else:
        raise AssertionError("Unexpected response format after attempting to delete the question set.")

def test_create_private_question_set(logged_in_client):
    response = logged_in_client.post("/question-sets/", json={"name": "Test Private Set", "is_public": False})
    assert response.status_code == 201
    assert response.json()["is_public"] == False

```

## File: test_api_questions.py
```py
# filename: tests/test_api_questions.py

from app.schemas import AnswerChoiceCreateSchema

def test_create_question_endpoint(logged_in_client, test_subject, test_topic, test_subtopic, test_question_set):
    data = {
        "text": "Test Question",
        "subject_id": test_subject.id,
        "topic_id": test_topic.id,
        "subtopic_id": test_subtopic.id,
        "difficulty": "Easy",
        "answer_choices": [
            {"text": "Answer 1", "is_correct": True, "explanation": "Answer 1 is correct."},
            {"text": "Answer 2", "is_correct": False, "explanation": "Answer 2 is incorrect."}
        ],
        "question_set_ids": [test_question_set.id]
    }
    response = logged_in_client.post("/question/", json=data)
    assert response.status_code == 201

def test_read_questions_without_token(client, db_session, test_question):
    response = client.get("/questions/")
    assert response.status_code == 401

def test_read_questions_with_token(logged_in_client, db_session, test_question):
    response = logged_in_client.get("/questions/")
    assert response.status_code == 200
    questions = response.json()
    found_test_question = next((q for q in questions if q["id"] == test_question.id), None)

    # Now we assert that our test question is indeed found and has the correct data
    assert found_test_question is not None, "Test question was not found in the response."
    assert found_test_question["id"] == test_question.id
    assert found_test_question["text"] == test_question.text
    assert found_test_question["subject_id"] == test_question.subject_id
    assert found_test_question["subtopic_id"] == test_question.subtopic_id
    assert found_test_question["topic_id"] == test_question.topic_id
    assert found_test_question["difficulty"] == test_question.difficulty

def test_update_question_not_found(logged_in_client, db_session):
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    response = logged_in_client.put(f"/question/{question_id}", json=question_update)
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question with ID {question_id} not found"

def test_delete_question_not_found(logged_in_client, db_session):
    question_id = 999  # Assuming this ID does not exist
    response = logged_in_client.delete(f"/question/{question_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question with ID {question_id} not found"

def test_update_question_endpoint(logged_in_client, test_question, test_question_set):
    data = {
        "text": "Updated Question",
        "difficulty": "Medium",
        "answer_choices": [
            {"text": "Updated Answer 1", "is_correct": True, "explanation": "Updated Answer 1 is correct."},
            {"text": "Updated Answer 2", "is_correct": False, "explanation": "Updated Answer 2 is incorrect."}
        ],
        "question_set_ids": [test_question_set.id]
    }
    response = logged_in_client.put(f"/question/{test_question.id}", json=data)
    assert response.status_code == 200
    assert response.json()["text"] == "Updated Question"
    assert response.json()["difficulty"] == "Medium"
    assert test_question_set.id in response.json()["question_set_ids"]
    assert any(choice["text"] == "Updated Answer 1" and choice["explanation"] == "Updated Answer 1 is correct." for choice in response.json()["answer_choices"])
    assert any(choice["text"] == "Updated Answer 2" and choice["explanation"] == "Updated Answer 2 is incorrect." for choice in response.json()["answer_choices"])

```

## File: test_api_subjects.py
```py
# filename: tests/test_api_subjects.py

from app.schemas import SubjectCreateSchema

def test_create_subject(logged_in_client, db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    response = logged_in_client.post("/subjects/", json=subject_data.dict())
    assert response.status_code == 201
    assert response.json()["name"] == "Test Subject"

def test_read_subject(logged_in_client, db_session):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject")
    created_subject = logged_in_client.post("/subjects/", json=subject_data.dict()).json()

    # Read the created subject
    response = logged_in_client.get(f"/subjects/{created_subject['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Subject"

def test_update_subject(logged_in_client, db_session):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject")
    created_subject = logged_in_client.post("/subjects/", json=subject_data.dict()).json()

    # Update the subject
    updated_data = {"name": "Updated Subject"}
    response = logged_in_client.put(f"/subjects/{created_subject['id']}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Subject"

def test_delete_subject(logged_in_client, db_session):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject")
    created_subject = logged_in_client.post("/subjects/", json=subject_data.dict()).json()

    # Delete the subject
    response = logged_in_client.delete(f"/subjects/{created_subject['id']}")
    assert response.status_code == 204

    # Check if the subject was deleted
    response = logged_in_client.get(f"/subjects/{created_subject['id']}")
    assert response.status_code == 404
```

## File: test_api_topics.py
```py
# filename: tests/test_api_topics.py

from app.schemas import TopicCreateSchema

def test_create_topic(logged_in_client, db_session):
    # Create a test subject
    subject_data = {"name": "Test Subject"}
    created_subject = logged_in_client.post("/subjects/", json=subject_data).json()

    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    response = logged_in_client.post("/topics/", json=topic_data.dict())
    assert response.status_code == 201
    assert response.json()["name"] == "Test Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_read_topic(logged_in_client, db_session):
    # Create a test subject and topic
    subject_data = {"name": "Test Subject"}
    created_subject = logged_in_client.post("/subjects/", json=subject_data).json()
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.dict()).json()

    # Read the created topic
    response = logged_in_client.get(f"/topics/{created_topic['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_update_topic(logged_in_client, db_session):
    # Create a test subject and topic
    subject_data = {"name": "Test Subject"}
    created_subject = logged_in_client.post("/subjects/", json=subject_data).json()
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.dict()).json()

    # Update the topic
    updated_data = {"name": "Updated Topic", "subject_id": created_subject["id"]}
    response = logged_in_client.put(f"/topics/{created_topic['id']}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_delete_topic(logged_in_client, db_session):
    # Create a test subject and topic
    subject_data = {"name": "Test Subject"}
    created_subject = logged_in_client.post("/subjects/", json=subject_data).json()
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.dict()).json()

    # Delete the topic
    response = logged_in_client.delete(f"/topics/{created_topic['id']}")
    assert response.status_code == 204

    # Check if the topic was deleted
    response = logged_in_client.get(f"/topics/{created_topic['id']}")
    assert response.status_code == 404

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

def test_update_user_response(logged_in_client, db_session, test_user, test_question, test_answer_choice_1):
    response_data = {"user_id": test_user.id, "question_id": test_question.id, "answer_choice_id": test_answer_choice_1.id, "is_correct": True}
    created_response = logged_in_client.post("/user-responses/", json=response_data).json()
    update_data = {"is_correct": False}
    response = logged_in_client.put(f"/user-responses/{created_response['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["is_correct"] is False

def test_delete_user_response(logged_in_client, db_session, test_user, test_question, test_answer_choice_1):
    response_data = {"user_id": test_user.id, "question_id": test_question.id, "answer_choice_id": test_answer_choice_1.id, "is_correct": True}
    created_response = logged_in_client.post("/user-responses/", json=response_data).json()
    response = logged_in_client.delete(f"/user-responses/{created_response['id']}")
    assert response.status_code == 204
    response = logged_in_client.get(f"/user-responses/{created_response['id']}")
    assert response.status_code == 404

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

def test_read_user_me(client, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == test_user.username

def test_update_user_me(client, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    updated_data = {"username": "updated_username"}
    response = client.put("/users/me", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "updated_username"

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_services

## File: test_randomization_service.py
```py
# filename: tests/test_utils/test_randomization.py

from app.services import randomize_questions, randomize_answer_choices
from app.models import QuestionModel, AnswerChoiceModel

def test_randomize_questions():
    questions = [
        QuestionModel(text="Question 1"),
        QuestionModel(text="Question 2"),
        QuestionModel(text="Question 3"),
    ]
    randomized_questions = randomize_questions(questions)
    assert len(randomized_questions) == len(questions)
    assert set(randomized_questions) == set(questions)

def test_randomize_answer_choices():
    answer_choices = [
        AnswerChoiceModel(text="Choice 1"),
        AnswerChoiceModel(text="Choice 2"),
        AnswerChoiceModel(text="Choice 3"),
    ]
    randomized_choices = randomize_answer_choices(answer_choices)
    assert len(randomized_choices) == len(answer_choices)
    assert set(randomized_choices) == set(answer_choices)

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_db

## File: test_db_session.py
```py
# filename: tests/test_db_session.py

from sqlalchemy import inspect

def test_revoked_tokens_table_exists(db):
    inspector = inspect(db.bind)
    available_tables = inspector.get_table_names()
    assert "revoked_tokens" in available_tables, "Table 'revoked_tokens' does not exist in the test database."


def test_database_session_lifecycle(db_session):
    """Test the lifecycle of a database session."""
    # Assuming 'db_session' is already using the correct test database ('test.db') as configured in conftest.py
    assert db_session.bind.url.__to_string__() == "sqlite:///./test.db", "Not using the test database"

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_crud

## File: test_crud_filters.py
```py
import pytest
from pydantic import ValidationError
from app.crud.crud_filters import filter_questions_crud
from app.schemas.filters import FilterParamsSchema

def test_filter_questions_extra_invalid_parameter(db_session):
    # Test case: Extra invalid parameter
    filters = {
        "subject": "Math",
        "invalid_param": "InvalidValue"
    }
    with pytest.raises(ValidationError) as exc_info:
        filter_questions_crud(db=db_session, filters=filters)
    assert "Extra inputs are not permitted" in str(exc_info.value)

def test_filter_questions_invalid_parameter_type(db_session):
    # Test case: Invalid parameter type
    filters = {
        "subject": 123,  # Invalid type, should be a string
        "topic": "Geometry"
    }
    with pytest.raises(ValidationError) as exc_info:
        filter_questions_crud(db=db_session, filters=filters)
    assert "Input should be a valid string" in str(exc_info.value)

def test_filter_questions_invalid_tag_type(db_session):
    # Test case: Invalid tag type
    filters = {
        "tags": "InvalidTag"  # Invalid type, should be a list of strings
    }
    with pytest.raises(ValidationError) as exc_info:
        filter_questions_crud(db=db_session, filters=filters)
    assert "Input should be a valid list" in str(exc_info.value)

def test_filter_questions_no_filters(db_session):
    # Test case: No filters provided
    filters = {}
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result is None

def test_filter_questions_invalid_subject(db_session):
    # Test case: Invalid subject filter
    filters = {
        "subject": "InvalidSubject"
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_topic(db_session):
    # Test case: Invalid topic filter
    filters = {
        "topic": "InvalidTopic"
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_subtopic(db_session):
    # Test case: Invalid subtopic filter
    filters = {
        "subtopic": "InvalidSubtopic"
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_difficulty(db_session):
    # Test case: Invalid difficulty filter
    filters = {
        "difficulty": "InvalidDifficulty"
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_tags(db_session):
    # Test case: Invalid tags filter
    filters = {
        "tags": ["InvalidTag"]
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_valid_filters(db_session, test_question):
    # Test case: Valid filters
    subject = test_question.subject
    topic = test_question.topic
    subtopic = test_question.subtopic
    difficulty = test_question.difficulty
    tags = [tag.tag for tag in test_question.tags]

    filters = {
        "subject": subject.name,
        "topic": topic.name,
        "subtopic": subtopic.name,
        "difficulty": difficulty,
        "tags": tags
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert len(result) == 1
    assert result[0].id == test_question.id

```

## File: test_crud_question_sets.py
```py
# filename: tests/test_crud_question_sets.py

import pytest
from fastapi import HTTPException
from app.crud import (
    create_question_set_crud,
    delete_question_set_crud,
    update_question_set_crud,
    create_subject_crud
)
from app.schemas import QuestionSetUpdateSchema, SubjectCreateSchema, QuestionSetCreateSchema

def test_create_question_set_crud(db_session):
    question_set_data = QuestionSetCreateSchema(name="Test Question Set", is_public=True)
    question_set = create_question_set_crud(db_session, question_set_data)

    assert question_set.name == "Test Question Set"
    assert question_set.is_public == True

def test_delete_question_set(db_session, test_question_set_data):
    test_question_set_data.name = "Unique Question Set for Deletion"
    question_set = create_question_set_crud(db=db_session, question_set=test_question_set_data)
    assert delete_question_set_crud(db=db_session, question_set_id=question_set.id) is True, "Question set deletion failed."

def test_create_question_set_duplicate_name(db_session, test_question_set_data):
    create_question_set_crud(db=db_session, question_set=test_question_set_data)
    with pytest.raises(HTTPException) as exc_info:
        create_question_set_crud(db=db_session, question_set=test_question_set_data)
    assert exc_info.value.status_code == 400
    assert f"Question set with name '{test_question_set_data.name}' already exists." in str(exc_info.value.detail)

def test_update_question_set_not_found(db_session):
    question_set_id = 999
    subject_data = SubjectCreateSchema(name="Test Subject")
    subject = create_subject_crud(db_session, subject_data)
    question_set_update = QuestionSetUpdateSchema(name="Updated Name", subject_id=subject.id)
    with pytest.raises(HTTPException) as exc_info:
        update_question_set_crud(db=db_session, question_set_id=question_set_id, question_set=question_set_update)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)

def test_delete_question_set_not_found(db_session):
    question_set_id = 999  # Assuming this ID does not exist
    with pytest.raises(HTTPException) as exc_info:
        delete_question_set_crud(db=db_session, question_set_id=question_set_id)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)

def test_update_question_set_crud(db_session, test_question_set, test_question):
    question_set_update = QuestionSetUpdateSchema(name="Updated Question Set", question_ids=[test_question.id])
    updated_question_set = update_question_set_crud(db_session, test_question_set.id, question_set_update)

    assert updated_question_set.name == "Updated Question Set"
    assert test_question.id in updated_question_set.question_ids

```

## File: test_crud_questions.py
```py
# filename: tests/test_crud_questions.py

from app.schemas import (
    QuestionCreateSchema,
    QuestionUpdateSchema,
    AnswerChoiceCreateSchema,
    SubjectCreateSchema,
    TopicCreateSchema
)    
from app.crud import (
    create_question_crud,
    get_question_crud,
    update_question_crud,
    delete_question_crud,
    create_topic_crud,
    create_subject_crud
)

def test_create_and_retrieve_question(db_session, test_question_set, test_subtopic):
    """Test creation and retrieval of a question."""
    test_question_set.name = "Unique Question Set for Question Creation"
    subject_data = SubjectCreateSchema(name="Test Subject")
    subject = create_subject_crud(db_session, subject_data)
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=subject.id)
    topic = create_topic_crud(db_session, topic_data)
    answer_choice_1 = AnswerChoiceCreateSchema(text="Test Answer 1", is_correct=True, explanation="Answer 1 is correct.")
    answer_choice_2 = AnswerChoiceCreateSchema(text="Test Answer 2", is_correct=False, explanation="Answer 2 is incorrect.")
    question_data = QuestionCreateSchema(
        text="Sample Question?",
        subject_id=subject.id,
        topic_id=topic.id,
        subtopic_id=test_subtopic.id,
        difficulty="Easy",
        answer_choices=[answer_choice_1, answer_choice_2]
    )
    created_question = create_question_crud(db=db_session, question=question_data)
    retrieved_question = get_question_crud(db_session, question_id=created_question.id)
    assert retrieved_question is not None, "Failed to retrieve created question."
    assert retrieved_question.text == "Sample Question?", "Question text does not match."
    assert retrieved_question.difficulty == "Easy", "Question difficulty level does not match."
    assert len(retrieved_question.answer_choices) == 2, "Answer choices not created correctly."
    assert any(choice.text == "Test Answer 1" and choice.explanation == "Answer 1 is correct." for choice in retrieved_question.answer_choices)
    assert any(choice.text == "Test Answer 2" and choice.explanation == "Answer 2 is incorrect." for choice in retrieved_question.answer_choices)

def test_get_nonexistent_question(db_session):
    """Test retrieval of a non-existent question."""
    question = get_question_crud(db_session, question_id=999)
    assert question is None, "Fetching a non-existent question should return None."

def test_delete_nonexistent_question(db_session):
    """Test deletion of a non-existent question."""
    result = delete_question_crud(db_session, question_id=999)
    assert result is False, "Deleting a non-existent question should return False."

def test_update_question_not_found(db_session):
    """
    Test updating a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    updated_question = update_question_crud(db_session, question_id, question_update)
    assert updated_question is None

def test_delete_question_not_found(db_session):
    """
    Test deleting a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    deleted = delete_question_crud(db_session, question_id)
    assert deleted is False

def test_update_question_crud(db_session, test_question, test_question_set):
    question_update = QuestionUpdateSchema(
        text="Updated Question",
        difficulty="Medium",
        answer_choices=[
            {"text": "Updated Answer 1", "is_correct": True, "explanation": "Updated Answer 1 is correct."},
            {"text": "Updated Answer 2", "is_correct": False, "explanation": "Updated Answer 2 is incorrect."}
        ],
        question_set_ids=[test_question_set.id]
    )
    updated_question = update_question_crud(db_session, test_question.id, question_update)

    assert updated_question.text == "Updated Question"
    assert updated_question.difficulty == "Medium"
    assert test_question_set.id in updated_question.question_set_ids
    assert any(choice.text == "Updated Answer 1" and choice.explanation == "Updated Answer 1 is correct." for choice in updated_question.answer_choices)
    assert any(choice.text == "Updated Answer 2" and choice.explanation == "Updated Answer 2 is incorrect." for choice in updated_question.answer_choices)

```

## File: test_crud_subjects.py
```py
# filename: tests/test_crud_subjects.py

from app.schemas import SubjectCreateSchema
from app.crud import create_subject_crud

def test_create_subject(db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    created_subject = create_subject_crud(db=db_session, subject=subject_data)
    assert created_subject.name == "Test Subject"

```

## File: test_crud_user.py
```py
# filename: tests/test_crud_user.py
from app.crud import delete_user_crud, create_user_crud, update_user_crud
from app.schemas import UserCreateSchema, UserUpdateSchema
from app.services import authenticate_user

def test_remove_user_not_found(db_session):
    """
    Test removing a user that does not exist.
    """
    user_id = 999  # Assuming this ID does not exist
    removed_user = delete_user_crud(db_session, user_id)
    assert removed_user is None

def test_authenticate_user(db_session, random_username):
    user_data = UserCreateSchema(username=random_username, password="AuthPassword123!")
    create_user_crud(db_session, user_data)
    authenticated_user = authenticate_user(db_session, username=random_username, password="AuthPassword123!")
    assert authenticated_user
    assert authenticated_user.username == random_username

def test_create_user(db_session, random_username):
    user_data = UserCreateSchema(username=random_username, password="NewPassword123!")
    created_user = create_user_crud(db_session, user_data)
    assert created_user.username == random_username

def test_update_user(db_session, test_user):
    updated_data = UserUpdateSchema(username="updated_username")
    updated_user = update_user_crud(db=db_session, user_id=test_user.id, updated_user=updated_data)
    assert updated_user.username == "updated_username"
```

## File: test_crud_user_responses.py
```py
# filename: tests/test_crud_user_responses.py
from app.schemas import UserResponseCreateSchema, UserResponseUpdateSchema
from app.crud import crud_user_responses
from app.models import UserResponseModel

def test_create_and_retrieve_user_response(db_session, test_user, test_question, test_answer_choice_1):
    """Test creation and retrieval of a user response."""
    response_data = UserResponseCreateSchema(user_id=test_user.id, question_id=test_question.id, answer_choice_id=test_answer_choice_1.id, is_correct=True)
    created_response = crud_user_responses.create_user_response_crud(db=db_session, user_response=response_data)
    assert created_response is not None, "Failed to create user response."
    assert created_response.is_correct is True, "User response correctness does not match."

def test_update_user_response(db_session, test_user, test_question, test_answer_choice_1):
    response_data = UserResponseCreateSchema(user_id=test_user.id, question_id=test_question.id, answer_choice_id=test_answer_choice_1.id, is_correct=True)
    created_response = crud_user_responses.create_user_response_crud(db=db_session, user_response=response_data)
    update_data = UserResponseUpdateSchema(is_correct=False)
    updated_response = crud_user_responses.update_user_response_crud(db=db_session, user_response_id=created_response.id, user_response=update_data)
    assert updated_response.is_correct is False

def test_delete_user_response(db_session, test_user, test_question, test_answer_choice_1):
    response_data = UserResponseCreateSchema(user_id=test_user.id, question_id=test_question.id, answer_choice_id=test_answer_choice_1.id, is_correct=True)
    created_response = crud_user_responses.create_user_response_crud(db=db_session, user_response=response_data)
    crud_user_responses.delete_user_response_crud(db=db_session, user_response_id=created_response.id)
    deleted_response = db_session.query(UserResponseModel).filter(UserResponseModel.id == created_response.id).first()
    assert deleted_response is None

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_models

## File: test_models_models.py
```py
# filename: tests/test_models.py
#import pytest
#from sqlalchemy.exc import IntegrityError
from app.models import (
    UserModel,
    SubjectModel,
    QuestionModel,
    AnswerChoiceModel
)

def test_user_model(db_session, random_username):
    username = random_username
    user = UserModel(username=username, hashed_password="hashedpassword")
    db_session.add(user)
    db_session.commit()
    assert user.id > 0
    assert user.username == username
    assert user.hashed_password == "hashedpassword"

def test_subject_model(db_session):
    subject = SubjectModel(name="Test Subject")
    db_session.add(subject)
    db_session.commit()
    assert subject.id > 0
    assert subject.name == "Test Subject"

def test_question_model_creation(db_session):
    question = QuestionModel(text="What is the capital of France?", difficulty="Easy")
    db_session.add(question)
    db_session.commit()
    assert question.id is not None
    assert question.text == "What is the capital of France?"
    assert question.difficulty == "Easy"

def test_question_model_with_answers(db_session):
    question = QuestionModel(text="What is the capital of France?", difficulty="Easy")
    answer = AnswerChoiceModel(text="Paris", is_correct=True, explanation="Paris is the capital and largest city of France.", question=question)
    db_session.add_all([question, answer])
    db_session.commit()
    assert len(question.answer_choices) == 1
    assert question.answer_choices[0].text == "Paris"
    assert question.answer_choices[0].explanation == "Paris is the capital and largest city of France."

def test_question_model_deletion_cascades_to_answers(db_session):
    question = QuestionModel(text="What is the capital of France?", difficulty="Easy")
    answer = AnswerChoiceModel(text="Paris", is_correct=True, question=question)
    db_session.add_all([question, answer])
    db_session.commit()
    db_session.delete(question)
    db_session.commit()
    assert db_session.query(AnswerChoiceModel).filter_by(question_id=question.id).first() is None

# Additional tests could include invalid data submissions, updating questions, etc.
# Add similar tests for other models: Topic, Subtopic, Question, AnswerChoice

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_core

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

@pytest.fixture
def test_data():
    return {"sub": "testuser"}

def test_jwt_token_generation_and_validation(test_data):
    """Test JWT token generation and subsequent validation."""
    # Generate a token
    token = create_access_token(data=test_data, expires_delta=timedelta(minutes=15))
    assert token is not None, "Failed to generate JWT token."
    
    # Validate the token
    decoded_username = verify_token(token, credentials_exception=Exception("Invalid token"))
    assert decoded_username == test_data["sub"], "JWT token validation failed. Username mismatch."

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

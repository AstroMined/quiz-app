
# Directory: /code/quiz-app/quiz-app-backend

## File: logging_fixer.py
```py
import re
import os

def replace_fstring_with_percent_format(line):
    # Match lines that include a logging statement with f-string
    pattern = r'(\s*)logger\.(\w+)\(f"(.*?)"\)'
    match = re.search(pattern, line)
    if match:
        indent = match.group(1)
        level = match.group(2)
        fstring_content = match.group(3)

        # Extract variable names within {}
        variables = re.findall(r'{(.*?)}', fstring_content)
        percent_format_string = re.sub(r'{(.*?)}', r'%s', fstring_content)
        
        # Join the variables to be used as arguments in logging
        variables_string = ', '.join(variables)

        new_line = f'{indent}logger.{level}("{percent_format_string}", {variables_string})\n'
        return new_line
    return line

def process_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    with open(filepath, 'w') as file:
        for line in lines:
            new_line = replace_fstring_with_percent_format(line)
            file.write(new_line)

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))

# Example usage: process the directory containing your Python files
process_directory('tests')

```

## File: pyproject.toml
```toml
# pyproject.toml
[tool.app]
secret_key = "your_default_secret_key"
access_token_expire_minutes = 30
database_url_dev = "sqlite:///./quiz_app.db"
database_url_test = "sqlite:///./test.db"
unprotected_endpoints = ["/", "/login", "/logout", "/register", "/docs", "/redoc", "/openapi.json"]

[tool.pylint.METHOD]
no-self-argument = "cls"

[tool.pytest.ini_options]
python_files = ["test_*.py"]
testpaths = [
    "tests",
]
filterwarnings = [
    "ignore::DeprecationWarning"
]

```

# Directory: /code/quiz-app/quiz-app-backend/app

## File: __init__.py
```py

```

## File: main.py
```py
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

app.add_middleware(AuthorizationMiddleware)
app.add_middleware(BlacklistMiddleware)
add_cors_middleware(app)

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

```

# Directory: /code/quiz-app/quiz-app-backend/app/schemas

## File: __init__.py
```py

```

## File: answer_choices.py
```py
# filename: app/schemas/answer_choices.py

from pydantic import BaseModel, validator


class AnswerChoiceBaseSchema(BaseModel):
    text: str
    is_correct: bool
    explanation: str

class AnswerChoiceCreateSchema(AnswerChoiceBaseSchema):
    @validator('text')
    def validate_text(cls, text):
        if not text.strip():
            raise ValueError('Answer choice text cannot be empty or whitespace')
        if len(text) > 5000:
            raise ValueError('Answer choice text cannot exceed 5000 characters')
        return text

    @validator('explanation')
    def validate_explanation(cls, explanation):
        if len(explanation) > 10000:
            raise ValueError('Answer choice explanation cannot exceed 10000 characters')
        return explanation

class AnswerChoiceSchema(BaseModel):
    id: int
    text: str
    is_correct: bool
    explanation: str

    class Config:
        from_attributes = True

```

## File: authentication.py
```py
# filename: app/schemas/authentication.py

from pydantic import BaseModel, Field


class LoginFormSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

```

## File: filters.py
```py
# filename: app/schemas/filters.py

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class FilterParamsSchema(BaseModel):
    subject: Optional[str] = Field(None, description="Filter questions by subject")
    topic: Optional[str] = Field(None, description="Filter questions by topic")
    subtopic: Optional[str] = Field(None, description="Filter questions by subtopic")
    difficulty: Optional[str] = Field(None, description="Filter questions by difficulty level")
    tags: Optional[List[str]] = Field(None, description="Filter questions by tags")

    @validator('difficulty')
    def validate_difficulty(cls, difficulty):
        valid_difficulties = ['Beginner', 'Easy', 'Medium', 'Hard', 'Expert']
        if difficulty and difficulty not in valid_difficulties:
            raise ValueError(f'Invalid difficulty. Must be one of: {", ".join(valid_difficulties)}')
        return difficulty

    class Config:
        extra = 'forbid'
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

## File: groups.py
```py
# filename: app/schemas/groups.py

import re
from typing import Optional
from pydantic import BaseModel, validator, Field
from sqlalchemy.orm import Session
from app.services.logging_service import logger


class GroupBaseSchema(BaseModel):
    name: str
    creator_id: int
    description: Optional[str] = None
    db: Optional[Session] = Field(default=None, exclude=True)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class GroupCreateSchema(GroupBaseSchema):
    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Group name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Group name cannot exceed 100 characters')
        if not re.match(r'^[\w\-\s]+$', name):
            raise ValueError('Group name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return name

    @validator('description')
    def validate_description(cls, description):
        if description and len(description) > 500:
            raise ValueError('Group description cannot exceed 500 characters')
        return description

class GroupUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, name):
        if name == '':
            raise ValueError('Group name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Group name cannot exceed 100 characters')
        if not re.match(r'^[\w\-\s]+$', name):
            raise ValueError('Group name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return name

    @validator('description')
    def validate_description(cls, description):
        if description and len(description) > 500:
            raise ValueError('Group description cannot exceed 500 characters')
        return description

class GroupSchema(GroupBaseSchema):
    id: int
    creator_id: int
    description: Optional[str] = None

    class Config:
        from_attributes = True

```

## File: leaderboard.py
```py
# filename: app/schemas/leaderboard.py

from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.time_period import TimePeriodModel
from app.services.logging_service import logger


class LeaderboardSchema(BaseModel):
    id: int
    user_id: int
    score: int
    time_period: TimePeriodModel
    group_id: Optional[int] = None

    class Config:
        from_attributes = True


```

## File: permissions.py
```py
# filename: app/schemas/permissions.py

import re
from pydantic import BaseModel, validator


class PermissionBaseSchema(BaseModel):
    name: str
    description: str

class PermissionCreateSchema(PermissionBaseSchema):
    @validator('name')
    def validate_name(cls, name):
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValueError('Permission name can only contain alphanumeric characters, underscores, and hyphens')
        return name

class PermissionUpdateSchema(BaseModel):
    name: str = None
    description: str = None

    @validator('name')
    def validate_name(cls, name):
        if name and not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValueError('Permission name can only contain alphanumeric characters, underscores, and hyphens')
        return name

class PermissionSchema(PermissionBaseSchema):
    id: int

    class Config:
        from_attributes = True
```

## File: question_sets.py
```py
# filename: app/schemas/question_sets.py

import re
from typing import List, Optional
from pydantic import BaseModel, validator


class QuestionSetBaseSchema(BaseModel):
    name: str
    is_public: bool = True
    question_ids: Optional[List[int]] = []
    creator_id: int = None
    group_ids: Optional[List[int]] = []

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class QuestionSetCreateSchema(QuestionSetBaseSchema):
    name: str
    is_public: bool = True

    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Question set name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Question set name cannot exceed 100 characters')
        if not re.match(r'^[\w\-\s]+$', name):
            raise ValueError(
                'Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces'
            )
        return name


class QuestionSetUpdateSchema(BaseModel):
    name: Optional[str] = None
    is_public: Optional[bool] = None
    question_ids: Optional[List[int]] = None
    group_ids: Optional[List[int]] = None

    class Config:
        arbitrary_types_allowed = True

    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Question set name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Question set name cannot exceed 100 characters')
        if not re.match(r'^[\w\-\s]+$', name):
            raise ValueError(
                'Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces'
            )
        return name


class QuestionSetSchema(QuestionSetBaseSchema):
    id: int
    is_public: bool = True
    question_ids: Optional[List[int]] = []
    creator_id: int = None
    group_ids: Optional[List[int]] = []

    class Config:
        from_attributes = True

```

## File: question_tags.py
```py
# filename: app/schemas/question_tags.py

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
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from app.schemas.answer_choices import AnswerChoiceSchema, AnswerChoiceCreateSchema
from app.schemas.question_tags import QuestionTagSchema


class QuestionBaseSchema(BaseModel):
    text: str
    subject_id: int
    topic_id: int
    subtopic_id: int
    db: Optional[Session] = Field(default=None, exclude=True)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class QuestionCreateSchema(QuestionBaseSchema):
    text: Optional[str] = Field(None, description="The text of the question", max_length=1000)
    difficulty: Optional[str] = Field(None, description="The difficulty level of the question")
    subject_id: Optional[int] = Field(None, description="ID of the subject associated with the question")
    topic_id: Optional[int] = Field(None, description="ID of the topic associated with the question")
    subtopic_id: Optional[int] = Field(None, description="ID of the subtopic associated with the question")
    answer_choices: Optional[List[AnswerChoiceCreateSchema]] = Field(None, description="A list of answer choices")
    tags: Optional[List[QuestionTagSchema]] = Field(None, description="A list of tags associated with the question")
    question_set_ids: Optional[List[int]] = Field(None, description="Updated list of question set IDs the question belongs to")

    @validator('difficulty')
    def validate_difficulty(cls, difficulty):
        valid_difficulties = [
            'Beginner',
            'Easy',
            'Medium',
            'Hard',
            'Expert'
        ]
        if difficulty not in valid_difficulties:
            raise ValueError(f'Invalid difficulty. Must be one of: {", ".join(valid_difficulties)}')
        return difficulty

class QuestionUpdateSchema(QuestionBaseSchema):
    text: Optional[str] = Field(None, description="The text of the question")
    difficulty: Optional[str] = Field(None, description="The difficulty level of the question")
    subject_id: Optional[int] = Field(None, description="ID of the subject associated with the question")
    topic_id: Optional[int] = Field(None, description="ID of the topic associated with the question")
    subtopic_id: Optional[int] = Field(None, description="ID of the subtopic associated with the question")
    answer_choices: Optional[List[AnswerChoiceCreateSchema]] = Field(None, description="A list of answer choices")
    tags: Optional[List[QuestionTagSchema]] = Field(None, description="A list of tags associated with the question")
    question_set_ids: Optional[List[int]] = Field(None, description="Updated list of question set IDs the question belongs to")

class QuestionSchema(QuestionBaseSchema):
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

## File: roles.py
```py
#filename: /app/schemas/roles.py

from typing import List
from pydantic import BaseModel


class RoleBaseSchema(BaseModel):
    name: str
    description: str

class RoleCreateSchema(RoleBaseSchema):
    permissions: List[str]

class RoleUpdateSchema(RoleBaseSchema):
    permissions: List[str]

class RoleSchema(RoleBaseSchema):
    id: int
    permissions: List[str]

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

from pydantic import BaseModel, validator


class SubjectBaseSchema(BaseModel):
    name: str

class SubjectCreateSchema(SubjectBaseSchema):
    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Subject name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Subject name cannot exceed 100 characters')
        return name

class SubjectSchema(SubjectBaseSchema):
    id: int

    class Config:
        from_attributes = True

```

## File: subtopics.py
```py
# schemas/subtopics.py

from pydantic import BaseModel, validator


class SubtopicBaseSchema(BaseModel):
    name: str
    topic_id: int

class SubtopicCreateSchema(SubtopicBaseSchema):
    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Subtopic name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Subtopic name cannot exceed 100 characters')
        return name

class SubtopicSchema(SubtopicBaseSchema):
    id: int

    class Config:
        from_attributes = True

```

## File: topics.py
```py
# filename: app/schemas/topics.py

from pydantic import BaseModel, validator


class TopicBaseSchema(BaseModel):
    name: str
    subject_id: int

class TopicCreateSchema(TopicBaseSchema):
    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Topic name cannot be empty or whitespace')
        if len(name) > 100:
            raise ValueError('Topic name cannot exceed 100 characters')
        return name

class TopicSchema(TopicBaseSchema):
    id: int

    class Config:
        from_attributes = True

```

## File: user.py
```py
# filename: app/schemas/user.py

import string
import re
from typing import Optional, List
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator, EmailStr, Field, model_validator
from app.schemas.groups import GroupSchema
from app.schemas.question_sets import QuestionSetSchema
from app.models.groups import GroupModel
from app.services.logging_service import logger


def validate_password(password: str) -> str:
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

def validate_username(username: str) -> str:
    if len(username) < 3:
        raise ValueError('Username must be at least 3 characters long')
    if len(username) > 50:
        raise ValueError('Username must not exceed 50 characters')
    if not re.match(r'^[\w\-\.]+$', username):
        raise ValueError('Username must contain only alphanumeric characters, hyphens, underscores, and periods')
    return username

def validate_email(email: str) -> str:
    if not email:
        raise ValueError('Email is required')
    return email

class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr
    role: Optional[str] = Field(default='user')
    db: Optional[Session] = Field(default=None, exclude=True)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class UserCreateSchema(UserBaseSchema):
    password: str

    @validator('password')
    def validate_password(cls, password):
        return validate_password(password)

    @validator('username')
    def validate_username(cls, username):
        return validate_username(username)

    @validator('email')
    def validate_email(cls, email):
        return validate_email(email)

class UserUpdateSchema(UserBaseSchema):
    username: Optional[str] = None
    password: Optional[str] = None
    group_ids: Optional[List[int]] = None
    email: Optional[str] = None

    @validator('password')
    def validate_password(cls, password):
        return validate_password(password)

    @model_validator(mode='before')
    def validate_group_ids(cls, values):
        logger.debug("UserUpdateSchema received data: %s", values)
        if values.get('group_ids'):
            group_ids = values.get('group_ids')
            db = values.get('db')
            if not db:
                raise ValueError("Database session not provided")
            for group_id in group_ids:
                if not db.query(GroupModel).filter(GroupModel.id == group_id).first():
                    raise ValueError(f"Invalid group_id: {group_id}")
        return values

class UserSchema(UserBaseSchema):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    is_admin: bool
    group_ids: List[GroupSchema] = []
    created_groups: List[GroupSchema] = []
    created_question_sets: List[QuestionSetSchema] = []

    class Config:
        from_attributes = True
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
    is_correct: Optional[bool] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponseCreateSchema(UserResponseBaseSchema):
    pass

class UserResponseUpdateSchema(UserResponseBaseSchema):
    answer_choice_id: Optional[int] = None

class UserResponseSchema(UserResponseBaseSchema):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt
        }

```

# Directory: /code/quiz-app/quiz-app-backend/app/services

## File: __init__.py
```py

```

## File: authentication_service.py
```py
# filename: app/services/authentication_service.py

from sqlalchemy.orm import Session
from app.services.user_service import get_user_by_username
from app.core.security import verify_password
from app.models.users import UserModel


def authenticate_user(db: Session, username: str, password: str) -> UserModel:
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if not user.is_active:
        return False
    return user

```

## File: authorization_service.py
```py
# filename: app/services/authorization_service.py

from typing import List
from sqlalchemy.orm import Session
from app.services.logging_service import logger
from app.models.users import UserModel
from app.models.groups import GroupModel
from app.models.roles import RoleModel


def get_user_permissions(db: Session, user: UserModel) -> List[str]:
    role = db.query(RoleModel).filter(RoleModel.name == user.role).first()
    if role:
        return [permission.name for permission in role.permissions]
    return []

def has_permission(db: Session, user: UserModel, required_permission: str) -> bool:
    logger.debug("Checking permission '%s' for user: %s", required_permission, user)
    user_role = db.query(RoleModel).filter(RoleModel.name == user.role).first()
    if user_role:
        user_permissions = [permission.name for permission in user_role.permissions]
        logger.debug("User permissions: %s", user_permissions)
        has_perm = required_permission in user_permissions
        logger.debug("User has permission '%s': %s", required_permission, has_perm)
        return has_perm
    logger.debug("User role not found")
    return False

def is_group_owner(user: UserModel, group: GroupModel) -> bool:
    """
    Check if the user is the owner of the specified group.
    """
    return user.id == group.creator_id


```

## File: logging_service.py
```py
# app/services/logging_service.py

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
import os
from sqlalchemy.inspection import inspect


def sqlalchemy_obj_to_dict(obj):
    """
    Convert a SQLAlchemy model instance to a dictionary.
    """
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

class UTCFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            t = dt.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

    def format(self, record):
        # Add the relative path, function name, and line number to the record
        record.relativepath = os.path.relpath(record.pathname)
        record.funcname = record.funcName
        record.lineno = record.lineno
        return super().format(record)

def setup_logging(disable_logging=False, disable_cli_logging=False):
    logger_setup = logging.getLogger("backend")

    if disable_logging:
        logger_setup.disabled = True
        return logger_setup
    
    logger_setup.setLevel(logging.DEBUG)

    # File Handler
    log_file = "/var/log/quiz-app/backend/backend.log"
    if not disable_logging:
        handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)
    else:
        handler = logging.NullHandler()  # Redirect logs to /dev/null if logging is disabled

    handler.setLevel(logging.DEBUG)
    formatter = UTCFormatter("%(asctime)s - %(name)s - %(levelname)s - %(relativepath)s - %(funcname)s - line %(lineno)d - %(message)s")
    handler.setFormatter(formatter)
    logger_setup.addHandler(handler)

    # CLI Handler
    if not disable_cli_logging:
        cli_handler = logging.StreamHandler()
        cli_handler.setLevel(logging.DEBUG)
        cli_handler.setFormatter(formatter)
        logger_setup.addHandler(cli_handler)

    return logger_setup

# Example usage:
logger = setup_logging(disable_logging=False, disable_cli_logging=True)

```

## File: permission_generator_service.py
```py
# app/services/permission_generator_service.py

from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.core.config import settings_core
from app.services.logging_service import logger
from app.models.permissions import PermissionModel

def generate_permissions(app: FastAPI, db: Session):
    permissions = []
    method_map = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "DELETE": "delete",
    }

    for route in app.routes:
        if hasattr(route, "methods"):
            for method in route.methods:
                if method in method_map:
                    path = route.path.replace("/", "_").replace("{", "").replace("}", "")
                    if path not in settings_core.UNPROTECTED_ENDPOINTS:
                        permission = f"{method_map[method]}_{path}"
                        permissions.append(permission)
                        logger.debug("Generated permission: %s", permission)



    # Check if the generated permissions exist in the database and add them if they don't
    for permission in permissions:
        db_permission = db.query(PermissionModel).filter(PermissionModel.name == permission).first()
        if not db_permission:
            logger.debug("Adding permission to the database: %s", permission)
            db_permission = PermissionModel(name=permission)
            db.add(db_permission)

    # Delete permissions from the database that are not in the generated list
    db_permissions = db.query(PermissionModel).all()
    for db_permission in db_permissions:
        if db_permission.name not in permissions:
            logger.debug("Deleting permission from the database: %s", db_permission.name)
            db.delete(db_permission)

    db.commit()

    return set(permissions)

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

## File: scoring_service.py
```py
# filename: app/services/scoring_service.py

from typing import Dict
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.user_responses import UserResponseModel
from app.models.users import UserModel
from app.models.time_period import TimePeriodModel
from app.models.associations import UserToGroupAssociation


def calculate_user_score(user_id: int, db: Session) -> int:
    user_responses = db.query(UserResponseModel).filter(UserResponseModel.user_id == user_id).all()
    total_score = sum(response.is_correct for response in user_responses)
    return total_score

def calculate_leaderboard_scores(
    db: Session,
    time_period: TimePeriodModel,
    group_id: int = None
) -> Dict[int, int]:
    user_scores = {}
    query = db.query(UserResponseModel)

    if time_period == TimePeriodModel.DAILY:
        start_time = datetime.now(timezone.utc) - timedelta(days=1)
    elif time_period == TimePeriodModel.WEEKLY:
        start_time = datetime.now(timezone.utc) - timedelta(weeks=1)
    elif time_period == TimePeriodModel.MONTHLY:
        start_time = datetime.now(timezone.utc) - timedelta(days=30)
    elif time_period == TimePeriodModel.YEARLY:
        start_time = datetime.now(timezone.utc) - timedelta(days=365)
    else:
        start_time = None

    if start_time:
        query = query.filter(UserResponseModel.timestamp >= start_time)

    if group_id:
        query = query.join(UserModel).join(UserToGroupAssociation).filter(UserToGroupAssociation.group_id == group_id)

    user_responses = query.all()

    for response in user_responses:
        if response.user_id not in user_scores:
            user_scores[response.user_id] = 0
        if response.is_correct:
            user_scores[response.user_id] += 1

    return user_scores

```

## File: user_service.py
```py
# filename: app/services/user_service.py

from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from jose import JWTError
from app.services.logging_service import logger
from app.core.jwt import decode_access_token
from app.db.session import get_db
from app.models.authentication import RevokedTokenModel
from app.models.users import UserModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    logger.debug("get_current_user called with token: %s", token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        token_exp = payload.get("exp")
        logger.debug("Token expiration: %s", datetime.fromtimestamp(token_exp, tz=timezone.utc))
        if username is None:
            logger.error("Username not found in token payload")
            raise credentials_exception
        revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
        if revoked_token:
            logger.debug("Token is revoked")
            raise credentials_exception
        user = get_user_by_username(db, username=username)
        if user is None:
            logger.debug("User not found for username: %s", username)
            raise credentials_exception
        logger.debug("User found: %s", user)
        return user
    except JWTError as e:
        logger.exception("JWT Error: %s", str(e))
        raise credentials_exception from e
    except HTTPException as e:
        logger.error("HTTPException occurred: %s", e.detail)
        raise e
    except Exception as e:
        logger.exception("Unexpected error: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e

def get_user_by_username(db: Session, username: str) -> UserModel:
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_by_email(db: Session, email: str) -> UserModel:
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(UserModel).options(joinedload(UserModel.groups)).filter(UserModel.id == user_id).first()
```

## File: validation_service.py
```py
# filename: app/services/validation_service.py

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from sqlalchemy.orm.base import instance_state
from sqlalchemy.orm.attributes import instance_dict
from fastapi import HTTPException
from app.db.base_class import Base
from app.services.logging_service import logger, sqlalchemy_obj_to_dict
from app.models.questions import QuestionModel
from app.models.groups import GroupModel
from app.models.users import UserModel
from app.models.permissions import PermissionModel
from app.models.roles import RoleModel
from app.models.subjects import SubjectModel
from app.models.topics import TopicModel
from app.models.subtopics import SubtopicModel
from app.models.question_tags import QuestionTagModel
from app.models.leaderboard import LeaderboardModel
from app.models.user_responses import UserResponseModel
from app.models.answer_choices import AnswerChoiceModel
from app.models.question_sets import QuestionSetModel
from app.models.sessions import SessionModel
from app.models.authentication import RevokedTokenModel


def validate_foreign_keys(mapper, connection, target):
    target_contents = sqlalchemy_obj_to_dict(target)
    logger.debug(f"Validating foreign keys for target: {target_contents}")
    db = Session(bind=connection)
    inspector = inspect(target.__class__)

    for relationship in inspector.relationships:
        logger.debug(f"Validating {relationship.direction.name} relationship: {relationship}")
        if relationship.direction.name == 'MANYTOONE':
            validate_single_foreign_key(target, relationship, db)
        elif relationship.direction.name in ['ONETOMANY', 'MANYTOMANY']:
            validate_multiple_foreign_keys(target, relationship, db)

    validate_direct_foreign_keys(target, db)

def validate_single_foreign_key(target, relationship, db):
    foreign_key = relationship.key
    foreign_key_value = getattr(target, foreign_key)

    if foreign_key_value is not None:
        logger.debug(f"Foreign key value: {foreign_key_value}")
        try:
            if isinstance(foreign_key_value, Base):
                foreign_key_value = inspect(foreign_key_value).identity[0]
        except Exception as e:
            logger.error(f"Error getting foreign key value: {e}")
            raise HTTPException(status_code=400, detail="Invalid foreign key value")
        
        related_class = relationship.entity.class_
        related_object = db.query(related_class).filter(related_class.id == foreign_key_value).first()
        
        if not related_object:
            logger.error(f"Invalid {foreign_key}: {foreign_key_value}")
            raise HTTPException(status_code=400, detail=f"Invalid {foreign_key}")
    else:
        logger.debug(f"Foreign key {foreign_key} is None")


def validate_multiple_foreign_keys(target, relationship, db):
    foreign_key = relationship.key
    logger.debug("Validating multiple foreign key: %s", foreign_key)
    foreign_key_values = getattr(target, foreign_key)
    logger.debug("Foreign key values: %s", foreign_key_values)

    if foreign_key_values:
        for foreign_key_value in foreign_key_values:
            logger.debug("Validating multiple foreign key value: %s", foreign_key_value)
            try:
                if isinstance(foreign_key_value, Base):
                    state = instance_state(foreign_key_value)
                    if state.key is None:
                        logger.warning("Foreign key value has no identity key. It may not have been persisted yet.")
                        continue
                    foreign_key_value = state.key[1][0]  # Get the first primary key value
                logger.debug("Extracted foreign key value: %s", foreign_key_value)

                related_class = relationship.mapper.class_
                related_object = db.query(related_class).filter(related_class.id == foreign_key_value).first()
                
                if not related_object:
                    logger.error(f"Invalid {foreign_key}: {foreign_key_value}")
                    raise HTTPException(status_code=400, detail=f"Invalid {foreign_key}: {foreign_key_value}")
            except Exception as e:
                logger.exception(f"Error validating foreign key {foreign_key}: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error validating {foreign_key}: {str(e)}")


def validate_direct_foreign_keys(target, db):
    target_contents = sqlalchemy_obj_to_dict(target)
    logger.debug("Direct validation of foreign keys for target: %s", target_contents)

    # Iterate through each attribute in the target object
    for attribute, value in target_contents.items():
        if isinstance(value, int):  # Assuming foreign keys are integers
            logger.debug("Validating direct foreign key %s with value %s", attribute, value)
            related_class = find_related_class(attribute)
            if related_class:
                related_object = db.query(related_class).filter(related_class.id == value).first()
                if not related_object:
                    logger.error(f"Invalid {attribute}: {value}")
                    raise HTTPException(status_code=400, detail=f"Invalid {attribute}: {value}")


def find_related_class(attribute_name):
    """
    Maps attribute names to their corresponding SQLAlchemy model classes.
    This function should be periodically reviewed and updated to ensure all mappings are current.

    Args:
        attribute_name (str): The name of the attribute to map.

    Returns:
        type: The corresponding SQLAlchemy model class, or None if no mapping is found.
    """
    related_classes = {
        'question_id': QuestionModel,
        'group_id': GroupModel,
        'user_id': UserModel,
        'permission_id': PermissionModel,
        'role_id': RoleModel,
        'subject_id': SubjectModel,
        'topic_id': TopicModel,
        'subtopic_id': SubtopicModel,
        'question_tag_id': QuestionTagModel,
        'leaderboard_id': LeaderboardModel,
        'user_response_id': UserResponseModel,
        'answer_choice_id': AnswerChoiceModel,
        'question_set_id': QuestionSetModel,
        'session_id': SessionModel,
        'token_id': RevokedTokenModel,
        
        # We don't need to map the association tables here, as their columns
        # are already covered by the above mappings (e.g., 'user_id', 'group_id', etc.)
    }

    return related_classes.get(attribute_name)


def register_validation_listeners():
    if hasattr(Base, '_decl_class_registry'):
        logger.debug("Using _decl_class_registry")
        model_classes = Base._decl_class_registry.values()
    else:
        logger.debug("Using _class_registry")
        model_classes = Base.registry._class_registry.values()

    for model_class in model_classes:
        if hasattr(model_class, '__tablename__'):
            logger.debug("Registering validation listener for model: %s", model_class.__name__)
            event.listen(model_class, 'before_insert', validate_foreign_keys)
            event.listen(model_class, 'before_update', validate_foreign_keys)

```

# Directory: /code/quiz-app/quiz-app-backend/app/crud

## File: __init__.py
```py

```

## File: crud_answer_choices.py
```py
# filename: app/crud/crud_answer_choices.py

from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.answer_choices import AnswerChoiceModel
from app.schemas.answer_choices import AnswerChoiceCreateSchema

def create_answer_choice_crud(db: Session, answer_choice: AnswerChoiceCreateSchema) -> AnswerChoiceModel:
    db_answer_choice = AnswerChoiceModel(**answer_choice.model_dump())
    db.add(db_answer_choice)
    db.commit()
    db.refresh(db_answer_choice)
    return db_answer_choice

def create_answer_choices_bulk(db: Session, answer_choices: List[AnswerChoiceCreateSchema], question_id: int) -> List[AnswerChoiceModel]:
    db_answer_choices = [
        AnswerChoiceModel(
            text=choice.text,
            is_correct=choice.is_correct,
            explanation=choice.explanation,
            question_id=question_id
        )
        for choice in answer_choices
    ]
    db.add_all(db_answer_choices)
    db.commit()
    for db_choice in db_answer_choices:
        db.refresh(db_choice)
    return db_answer_choices

def read_answer_choice_crud(db: Session, answer_choice_id: int) -> AnswerChoiceModel:
    return db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id == answer_choice_id).first()

def update_answer_choice_crud(db: Session, answer_choice_id: int, answer_choice: AnswerChoiceCreateSchema) -> AnswerChoiceModel:
    db_answer_choice = read_answer_choice_crud(db, answer_choice_id)
    if db_answer_choice:
        update_data = answer_choice.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_answer_choice, key, value)
        db.commit()
        db.refresh(db_answer_choice)
    return db_answer_choice

def update_answer_choices_bulk(db: Session, question_id: int, new_answer_choices: List[Dict]) -> List[AnswerChoiceModel]:
    # Get existing answer choices
    existing_choices = db.query(AnswerChoiceModel).filter(AnswerChoiceModel.question_id == question_id).all()
    existing_choices_dict = {choice.id: choice for choice in existing_choices}

    updated_choices = []
    for choice_data in new_answer_choices:
        if 'id' in choice_data and choice_data['id'] in existing_choices_dict:
            # Update existing choice
            choice = existing_choices_dict[choice_data['id']]
            for key, value in choice_data.items():
                setattr(choice, key, value)
            updated_choices.append(choice)
        else:
            # Create new choice
            new_choice = AnswerChoiceModel(question_id=question_id, **choice_data)
            db.add(new_choice)
            updated_choices.append(new_choice)

    # Remove choices that are not in the new data
    for choice in existing_choices:
        if choice not in updated_choices:
            db.delete(choice)

    db.flush()
    return updated_choices

def delete_answer_choice_crud(db: Session, answer_choice_id: int) -> None:
    db_answer_choice = read_answer_choice_crud(db, answer_choice_id)
    if db_answer_choice:
        db.delete(db_answer_choice)
        db.commit()

```

## File: crud_filters.py
```py
# filename: app/crud/crud_filters.py

from typing import List, Optional
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.questions import QuestionModel
from app.models.subjects import SubjectModel
from app.models.topics import TopicModel
from app.models.subtopics import SubtopicModel
from app.models.question_tags import QuestionTagModel
from app.schemas.questions import QuestionSchema
from app.schemas.filters import FilterParamsSchema

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

## File: crud_groups.py
```py
# filename: app/crud/crud_groups.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.groups import GroupModel
from app.schemas.groups import GroupCreateSchema, GroupUpdateSchema
from app.services.logging_service import logger

def create_group_crud(db: Session, group: GroupCreateSchema, creator_id: int):
    try:
        db_group = GroupModel(
            name=group.name,
            description=group.description,
            creator_id=creator_id
        )
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

def read_group_crud(db: Session, group_id: int):
    return db.query(GroupModel).filter(GroupModel.id == group_id).first()

def update_group_crud(db: Session, group_id: int, group: GroupUpdateSchema):
    db_group = read_group_crud(db, group_id)
    if db_group:
        try:
            update_data = group.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_group, key, value)
            db.commit()
            db.refresh(db_group)
            return db_group
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
    return None

def delete_group_crud(db: Session, group_id: int):
    db_group = read_group_crud(db, group_id)
    if db_group:
        group_dict = db_group.__dict__.copy()
        group_dict.pop('_sa_instance_state', None)
        print(f"Group: {group_dict}")
        db.delete(db_group)
        db.commit()
        return True
    return False

```

## File: crud_leaderboard.py
```py
# filename: app/crud/crud_leaderboard.py

from sqlalchemy.orm import Session
from app.models.leaderboard import LeaderboardModel
from app.models.time_period import TimePeriodModel


def create_leaderboard_entry_crud(db: Session, user_id: int, score: int, time_period: TimePeriodModel, group_id: int = None):
    db_leaderboard_entry = LeaderboardModel(user_id=user_id, score=score, time_period=time_period, group_id=group_id)
    db.add(db_leaderboard_entry)
    db.commit()
    db.refresh(db_leaderboard_entry)
    return db_leaderboard_entry

def read_leaderboard_crud(db: Session, time_period: TimePeriodModel, group_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(LeaderboardModel).filter(LeaderboardModel.time_period == time_period)
    if group_id:
        query = query.filter(LeaderboardModel.group_id == group_id)
    return query.order_by(LeaderboardModel.score.desc()).offset(skip).limit(limit).all()

def update_leaderboard_entry_crud(db: Session, leaderboard_entry_id: int, score: int):
    db_leaderboard_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_entry_id).first()
    if db_leaderboard_entry:
        db_leaderboard_entry.score = score
        db.commit()
        db.refresh(db_leaderboard_entry)
    return db_leaderboard_entry

def delete_leaderboard_entry_crud(db: Session, leaderboard_entry_id: int):
    db_leaderboard_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_entry_id).first()
    if db_leaderboard_entry:
        db.delete(db_leaderboard_entry)
        db.commit()
    return db_leaderboard_entry

```

## File: crud_permissions.py
```py
# filename: app/crud/crud_permissions.py

from sqlalchemy.orm import Session
from app.models.permissions import PermissionModel
from app.schemas.permissions import PermissionCreateSchema, PermissionUpdateSchema


def create_permission_crud(db: Session, permission: PermissionCreateSchema) -> PermissionModel:
    db_permission = PermissionModel(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def read_permission_crud(db: Session, permission_id: int) -> PermissionModel:
    return db.query(PermissionModel).filter(PermissionModel.id == permission_id).first()

def read_permissions_crud(db: Session, skip: int = 0, limit: int = 100) -> list[PermissionModel]:
    return db.query(PermissionModel).offset(skip).limit(limit).all()

def update_permission_crud(db: Session, permission_id: int, permission: PermissionUpdateSchema) -> PermissionModel:
    db_permission = read_permission_crud(db, permission_id)
    if db_permission:
        update_data = permission.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_permission, key, value)
        db.commit()
        db.refresh(db_permission)
    return db_permission

def delete_permission_crud(db: Session, permission_id: int) -> bool:
    db_permission = read_permission_crud(db, permission_id)
    if db_permission:
        db.delete(db_permission)
        db.commit()
        return True
    return False

```

## File: crud_question_set_associations.py
```py
# filename: app/crud/crud_question_set_associations.py

from typing import List
from sqlalchemy.orm import Session
from app.models.associations import QuestionSetToQuestionAssociation, QuestionSetToGroupAssociation
from app.models.question_sets import QuestionSetModel


def create_question_set_question_associations(db: Session, question_set_id: int, question_ids: List[int]):
    associations = [
        QuestionSetToQuestionAssociation(question_set_id=question_set_id, question_id=q_id)
        for q_id in question_ids
    ]
    db.add_all(associations)
    db.commit()

def create_question_set_group_associations(db: Session, question_set_id: int, group_ids: List[int]):
    associations = [
        QuestionSetToGroupAssociation(question_set_id=question_set_id, group_id=g_id)
        for g_id in group_ids
    ]
    db.add_all(associations)
    db.commit()

def get_question_set_with_associations(db: Session, question_set_id: int) -> QuestionSetModel:
    return db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()

```

## File: crud_question_sets.py
```py
# filename: app/crud/crud_question_sets.py

from typing import List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.question_sets import QuestionSetModel
from app.models.groups import GroupModel
from app.models.questions import QuestionModel
from app.schemas.question_sets import QuestionSetCreateSchema, QuestionSetUpdateSchema
from app.services.logging_service import logger, sqlalchemy_obj_to_dict
from app.crud.crud_question_set_associations import (
    create_question_set_question_associations,
    create_question_set_group_associations,
    get_question_set_with_associations
)


def create_question_set_crud(
    db: Session,
    question_set: QuestionSetCreateSchema,
) -> QuestionSetModel:
    existing_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.name == question_set.name).first()
    if existing_question_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question set with name '{question_set.name}' already exists."
        )

    db_question_set = QuestionSetModel(
        name=question_set.name,
        is_public=question_set.is_public,
        creator_id=question_set.creator_id
    )
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)

    if question_set.question_ids:
        create_question_set_question_associations(db, db_question_set.id, question_set.question_ids)

    if question_set.group_ids:
        create_question_set_group_associations(db, db_question_set.id, question_set.group_ids)

    return get_question_set_with_associations(db, db_question_set.id)

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

def update_question_set_crud(
    db: Session,
    question_set_id: int,
    question_set: QuestionSetUpdateSchema
) -> QuestionSetModel:
    logger.debug("Starting update for question set ID: %d", question_set_id)
    
    db_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not db_question_set:
        logger.error("Question set with ID %d not found", question_set_id)
        raise HTTPException(
            status_code=404,
            detail=f"Question set with ID {question_set_id} not found."
        )

    update_data = question_set.model_dump(exclude_unset=True)
    logger.debug("Update data after model_dump: %s", update_data)
    
    # Update basic fields
    for field, value in update_data.items():
        if field not in ['question_ids', 'group_ids']:
            setattr(db_question_set, field, value)
            logger.debug("Set attribute %s to %s", field, value)

    # Update question associations
    if 'question_ids' in update_data:
        logger.debug("Updating question associations with IDs: %s", update_data['question_ids'])
        db_question_set.questions.clear()
        db.flush()
        create_question_set_question_associations(db, db_question_set.id, update_data['question_ids'])

    # Update group associations
    if 'group_ids' in update_data:
        logger.debug("Updating group associations with IDs: %s", update_data['group_ids'])
        db_question_set.groups.clear()
        db.flush()
        create_question_set_group_associations(db, db_question_set.id, update_data['group_ids'])

    db.commit()
    db.refresh(db_question_set)

    updated_question_set_dict = sqlalchemy_obj_to_dict(db_question_set)
    logger.debug("Updated question set: %s", updated_question_set_dict)

    return get_question_set_with_associations(db, db_question_set.id)

def delete_question_set_crud(db: Session, question_set_id: int) -> bool:
    db_question_set = db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()
    if not db_question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found.")
    
    db.delete(db_question_set)
    db.commit()
    return True

```

## File: crud_question_tag_associations.py
```py
# filename: app/crud/crud_question_tag_associations.py

from sqlalchemy.orm import Session
from app.models.associations import QuestionToTagAssociation
from app.models.questions import QuestionModel
from app.models.question_tags import QuestionTagModel


def add_tag_to_question(db: Session, question_id: int, tag_id: int):
    association = QuestionToTagAssociation(question_id=question_id, tag_id=tag_id)
    db.add(association)
    db.commit()

def remove_tag_from_question(db: Session, question_id: int, tag_id: int):
    db.query(QuestionToTagAssociation).filter_by(question_id=question_id, tag_id=tag_id).delete()
    db.commit()

def get_question_tags(db: Session, question_id: int):
    return db.query(QuestionTagModel).join(QuestionToTagAssociation).filter(QuestionToTagAssociation.question_id == question_id).all()

def get_questions_by_tag(db: Session, tag_id: int):
    return db.query(QuestionModel).join(QuestionToTagAssociation).filter(QuestionToTagAssociation.tag_id == tag_id).all()

```

## File: crud_question_tags.py
```py
# filename: app/crud/crud_question_tags.py

from sqlalchemy.orm import Session
from app.models.question_tags import QuestionTagModel
from app.schemas.question_tags import QuestionTagCreateSchema


def create_question_tag_crud(db: Session, question_tag: QuestionTagCreateSchema) -> QuestionTagModel:
    db_question_tag = QuestionTagModel(**question_tag.model_dump())
    db.add(db_question_tag)
    db.commit()
    db.refresh(db_question_tag)
    return db_question_tag

def get_question_tag_by_id_crud(db: Session, question_tag_id: int) -> QuestionTagModel:
    return db.query(QuestionTagModel).filter(QuestionTagModel.id == question_tag_id).first()

def get_question_tag_by_tag_crud(db: Session, tag: str) -> QuestionTagModel:
    return db.query(QuestionTagModel).filter(QuestionTagModel.tag == tag).first()

def update_question_tag_crud(db: Session, question_tag_id: int, updated_tag: str) -> QuestionTagModel:
    db_question_tag = get_question_tag_by_id_crud(db, question_tag_id)
    if db_question_tag:
        db_question_tag.tag = updated_tag
        db.commit()
        db.refresh(db_question_tag)
    return db_question_tag

def delete_question_tag_crud(db: Session, question_tag_id: int) -> None:
    db_question_tag = get_question_tag_by_id_crud(db, question_tag_id)
    if db_question_tag:
        db.delete(db_question_tag)
        db.commit()
```

## File: crud_questions.py
```py
# filename: app/crud/crud_questions.py

from typing import List
from sqlalchemy.orm import Session, joinedload
from app.crud.crud_answer_choices import create_answer_choices_bulk, update_answer_choices_bulk
from app.crud.crud_question_tag_associations import add_tag_to_question
from app.models.questions import QuestionModel
from app.models.associations import QuestionToTagAssociation
from app.schemas.questions import QuestionCreateSchema, QuestionUpdateSchema
from app.services.randomization_service import randomize_questions, randomize_answer_choices
from app.services.logging_service import logger, sqlalchemy_obj_to_dict

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
    logger.debug("Question created: %s", sqlalchemy_obj_to_dict(db_question))

    if question.answer_choices:
        answer_choices = create_answer_choices_bulk(db, question.answer_choices, db_question.id)
        for choice in answer_choices:
            db_question.answer_choices.append(choice)
            logger.debug("Answer choices created: %s", sqlalchemy_obj_to_dict(choice))
        db.commit()

    if question.question_set_ids:
        db_question.question_set_ids = question.question_set_ids
        db.commit()

    logger.debug("Question before the return: %s", sqlalchemy_obj_to_dict(db_question))

    return db_question

def read_questions_crud(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionModel]:
    questions = db.query(QuestionModel).offset(skip).limit(limit).all()
    questions = randomize_questions(questions)  # Randomize the order of questions
    for question in questions:
        question.answer_choices = randomize_answer_choices(question.answer_choices)  # Randomize the order of answer choices
    return questions

def read_question_crud(db: Session, question_id: int) -> QuestionModel:
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
    
    if "answer_choices" in update_data:
        answer_choices = update_data.pop("answer_choices")
        update_answer_choices_bulk(db, question_id, answer_choices)

    if "tags" in update_data:
        # Remove existing tags
        db.query(QuestionToTagAssociation).filter_by(question_id=question_id).delete()
        # Add new tags
        for tag_id in update_data["tags"]:
            add_tag_to_question(db, question_id, tag_id)

    for field, value in update_data.items():
        setattr(db_question, field, value)

    if question.question_set_ids is not None:
        db_question.question_set_ids = question.question_set_ids

    db.flush()
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

## File: crud_role_permission_associations.py
```py
# filename: app/crud/crud_role_permission_associations.py

from sqlalchemy.orm import Session
from app.models.associations import RoleToPermissionAssociation
from app.models.roles import RoleModel
from app.models.permissions import PermissionModel
from app.services.logging_service import logger

def add_permission_to_role(db: Session, role_id: int, permission_id: int | str):
    if isinstance(permission_id, str):
        # If permission_id is a string, query the PermissionModel to get the actual permission ID
        permission = db.query(PermissionModel).filter(PermissionModel.name == permission_id).first()
        if not permission:
            raise ValueError(f"Permission with name '{permission_id}' not found")
        permission_id = permission.id

    association = RoleToPermissionAssociation(role_id=role_id, permission_id=permission_id)
    db.add(association)
    db.commit()

def remove_permission_from_role(db: Session, role_id: int, permission_id: int):
    db.query(RoleToPermissionAssociation).filter_by(role_id=role_id, permission_id=permission_id).delete()
    db.commit()

def get_role_permissions(db: Session, role_id: int):
    return db.query(PermissionModel).join(RoleToPermissionAssociation).filter(RoleToPermissionAssociation.role_id == role_id).all()

def get_roles_by_permission(db: Session, permission_id: int):
    return db.query(RoleModel).join(RoleToPermissionAssociation).filter(RoleToPermissionAssociation.permission_id == permission_id).all()

```

## File: crud_roles.py
```py
# filename: app/crud/crud_roles.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.roles import RoleModel
from app.models.permissions import PermissionModel
from app.schemas.roles import RoleCreateSchema, RoleUpdateSchema
from app.crud.crud_role_permission_associations import add_permission_to_role, remove_permission_from_role, get_role_permissions
from app.services.logging_service import logger

def create_role_crud(db: Session, role: RoleCreateSchema) -> RoleModel:
    db_role = RoleModel(name=role.name, description=role.description)
    logger.debug("Creating role: %s", db_role)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    # Add permissions to the role
    for permission_id in role.permissions:
        logger.debug("Adding permission %s to role %s", permission_id, db_role.id)
        add_permission_to_role(db, db_role.id, permission_id)

    logger.debug("Role created with id %s, name %s, and permissions %s", db_role.id, db_role.name, db_role.permissions)
    return db_role

def read_role_crud(db: Session, role_id: int) -> RoleModel:
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with id {role_id} not found")
    return role

def read_roles_crud(db: Session, skip: int = 0, limit: int = 100) -> list[RoleModel]:
    return db.query(RoleModel).offset(skip).limit(limit).all()

def update_role_crud(db: Session, role_id: int, role: RoleUpdateSchema) -> RoleModel:
    db_role = read_role_crud(db, role_id)
    
    # Update basic fields
    for field, value in role.model_dump(exclude_unset=True).items():
        if field != "permissions":
            setattr(db_role, field, value)
    
    # Update permissions
    if role.permissions is not None:
        current_permissions = get_role_permissions(db, role_id)
        current_permission_names = {p.name for p in current_permissions}
        new_permission_names = set(role.permissions)

        # Remove permissions that are no longer associated
        for permission in current_permissions:
            if permission.name not in new_permission_names:
                remove_permission_from_role(db, role_id, permission.id)

        # Add new permissions
        for permission_name in new_permission_names:
            if permission_name not in current_permission_names:
                permission = db.query(PermissionModel).filter(PermissionModel.name == permission_name).first()
                if permission:
                    add_permission_to_role(db, role_id, permission.id)

    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role_crud(db: Session, role_id: int) -> bool:
    db_role = read_role_crud(db, role_id)
    db.delete(db_role)
    db.commit()
    return True

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
from app.models.subtopics import SubtopicModel
from app.schemas.subtopics import SubtopicCreateSchema

def create_subtopic_crud(db: Session, subtopic: SubtopicCreateSchema) -> SubtopicModel:
    db_subtopic = SubtopicModel(**subtopic.model_dump())
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)
    return db_subtopic

def read_subtopic_crud(db: Session, subtopic_id: int) -> SubtopicModel:
    return db.query(SubtopicModel).filter(SubtopicModel.id == subtopic_id).first()

def update_subtopic_crud(db: Session, subtopic_id: int, subtopic: SubtopicCreateSchema) -> SubtopicModel:
    db_subtopic = read_subtopic_crud(db, subtopic_id)
    if db_subtopic:
        update_data = subtopic.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_subtopic, key, value)
        db.commit()
        db.refresh(db_subtopic)
    return db_subtopic

def delete_subtopic_crud(db: Session, subtopic_id: int) -> None:
    db_subtopic = read_subtopic_crud(db, subtopic_id)
    if db_subtopic:
        db.delete(db_subtopic)
        db.commit()

```

## File: crud_topics.py
```py
# filename: app/crud/crud_topics.py

from sqlalchemy.orm import Session
from app.models.topics import TopicModel
from app.schemas.topics import TopicCreateSchema

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
from app.models.users import UserModel
from app.models.groups import GroupModel
from app.models.roles import RoleModel
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.core.security import get_password_hash
from app.services.logging_service import logger

def create_user_crud(db: Session, user: UserCreateSchema) -> UserModel:
    hashed_password = get_password_hash(user.password)
    default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
    logger.debug("Default role: %s", default_role)
    user_role = user.role if user.role else default_role.name
    logger.debug("User role: %s", user_role)
    db_user = UserModel(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
        role=user_role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_crud(db: Session, user_id: int, updated_user: UserUpdateSchema) -> UserModel:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return None
    update_data = updated_user.model_dump(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    if "role" in update_data:
        setattr(user, "role", update_data["role"])
    for key, value in update_data.items():
        setattr(user, key, value)
    if updated_user.group_ids is not None:
        user.groups = db.query(GroupModel).filter(GroupModel.id.in_(updated_user.group_ids)).all()
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

## File: crud_user_group_associations.py
```py
# filename: app/crud/crud_user_group_associations.py

from sqlalchemy.orm import Session
from app.models.associations import UserToGroupAssociation
from app.models.users import UserModel
from app.models.groups import GroupModel

def add_user_to_group(db: Session, user_id: int, group_id: int):
    association = UserToGroupAssociation(user_id=user_id, group_id=group_id)
    db.add(association)
    db.commit()

def remove_user_from_group(db: Session, user_id: int, group_id: int):
    db.query(UserToGroupAssociation).filter_by(user_id=user_id, group_id=group_id).delete()
    db.commit()

def get_user_groups(db: Session, user_id: int):
    return db.query(GroupModel).join(UserToGroupAssociation).filter(UserToGroupAssociation.user_id == user_id).all()

def get_group_users(db: Session, group_id: int):
    return db.query(UserModel).join(UserToGroupAssociation).filter(UserToGroupAssociation.group_id == group_id).all()

```

## File: crud_user_responses.py
```py
# filename: app/crud/crud_user_responses.py

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user_responses import UserResponseModel
from app.schemas.user_responses import UserResponseCreateSchema, UserResponseUpdateSchema


def create_user_response_crud(
    db: Session,
    user_response: UserResponseCreateSchema
) -> UserResponseModel:
    db_user_response = UserResponseModel(**user_response.model_dump())
    db.add(db_user_response)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

def get_user_response_crud(db: Session, user_response_id: int) -> Optional[UserResponseModel]:
    return db.query(UserResponseModel).filter(UserResponseModel.id == user_response_id).first()

def get_user_responses_crud(
    db: Session,
    user_id: Optional[int] = None,
    question_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[UserResponseModel]:
    query = db.query(UserResponseModel)

    if user_id:
        query = query.filter(UserResponseModel.user_id == user_id)
    if question_id:
        query = query.filter(UserResponseModel.question_id == question_id)
    if start_time:
        query = query.filter(UserResponseModel.timestamp >= start_time)
    if end_time:
        query = query.filter(UserResponseModel.timestamp <= end_time)

    user_responses = query.offset(skip).limit(limit).all()
    return user_responses

def update_user_response_crud(
    db: Session,
    user_response_id: int,
    user_response: UserResponseUpdateSchema
) -> UserResponseModel:
    db_user_response = db.query(UserResponseModel).filter(
        UserResponseModel.id == user_response_id).first()
    if not db_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    update_data = user_response.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user_response, key, value)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

def delete_user_response_crud(db: Session, user_response_id: int) -> None:
    db_user_response = db.query(UserResponseModel).filter(
        UserResponseModel.id == user_response_id).first()
    if not db_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    db.delete(db_user_response)
    db.commit()

```

# Directory: /code/quiz-app/quiz-app-backend/app/db

## File: __init__.py
```py

```

## File: base_class.py
```py
# filename: app/db/base_class.py

from sqlalchemy.orm import declarative_base


Base = declarative_base()

```

## File: session.py
```py
# filename: app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from app.core.config import settings_core
from app.models.permissions import PermissionModel
from app.models.roles import RoleModel
from app.services.logging_service import logger

engine = create_engine(settings_core.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Import all the models here to ensure they are registered with SQLAlchemy
    db = SessionLocal()
    try:
        # Add default roles
        superadmin_permissions = db.query(PermissionModel).all()
        superadmin_role = RoleModel(name="superadmin", description="Super Administrator", permissions=superadmin_permissions, default=False)
        logger.debug("Superadmin role: %s", superadmin_role)
        
        user_permissions = db.query(PermissionModel).filter(
            PermissionModel.name.in_([
                'read__docs', 'read__redoc', 'read__openapi.json', 'read__',
                'create__login', 'create__register_', 'read__users_me', 'update__users_me'
            ])
        ).all()
        user_role = RoleModel(name="user", description="Regular User", permissions=user_permissions, default=True)
        logger.debug("User role: %s", user_role)

        db.add_all([superadmin_role, user_role])
        db.commit()
    finally:
        db.close()

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

```

# Directory: /code/quiz-app/quiz-app-backend/app/api/endpoints

## File: __init__.py
```py

```

## File: authentication.py
```py
# filename: app/api/endpoints/authentication.py

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.jwt import create_access_token
from app.core.config import settings_core
from app.db.session import get_db
from app.models.authentication import RevokedTokenModel
from app.schemas.authentication import TokenSchema
from app.services.authentication_service import authenticate_user

router = APIRouter()

blacklist = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/login", response_model=TokenSchema)
async def login_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=settings_core.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_endpoint(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    This function logs out a user by adding their token to the revoked tokens list.
    """
    revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
    if not revoked_token:
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
    else:
        return {"message": "Token already revoked"}

```

## File: filters.py
```py
# filename: app/api/endpoints/filters.py
"""
This module defines the API endpoints for filtering questions in the application.

It includes a function to forbid extra parameters in the request, and an endpoint 
to filter questions based on various parameters like subject, topic, subtopic, 
difficulty, tags, skip and limit.

Functions:
----------
forbid_extra_params(request: Request) -> None:
    Checks if the request contains any extra parameters that are not allowed.
    If found, raises an HTTPException.

filter_questions_endpoint(
    request: Request,
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    subtopic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100
) -> List[QuestionSchema]:
    Filters questions based on the provided parameters.
    Returns a list of questions that match the filters.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.schemas.filters import FilterParamsSchema
from app.schemas.questions import QuestionSchema
from app.crud.crud_filters import filter_questions_crud
from app.db.session import get_db
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()


async def forbid_extra_params(request: Request):
    """
    This function checks if the request contains any extra parameters that are not allowed.
    If found, it raises an HTTPException.

    Parameters:
    ----------
    request: Request
        The request object containing all the parameters.

    Raises:
    ----------
    HTTPException
        If any extra parameters are found in the request.
    """
    allowed_params = {'subject', 'topic', 'subtopic',
                      'difficulty', 'tags', 'skip', 'limit'}
    actual_params = set(request.query_params.keys())
    extra_params = actual_params - allowed_params
    if extra_params:
        raise HTTPException(
            status_code=422, detail=f"Unexpected parameters provided: {extra_params}")


@router.get("/questions/filter", response_model=List[QuestionSchema], status_code=200)
# pylint: disable=unused-argument
async def filter_questions_endpoint(
    request: Request,
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    subtopic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user)
):
    """
    This function filters questions based on the provided parameters.
    Returns a list of questions that match the filters.

    Parameters:
    ----------
    request: Request
        The request object containing all the parameters.
    subject: Optional[str]
        The subject to filter the questions by.
    topic: Optional[str]
        The topic to filter the questions by.
    subtopic: Optional[str]
        The subtopic to filter the questions by.
    difficulty: Optional[str]
        The difficulty level to filter the questions by.
    tags: Optional[List[str]]
        The tags to filter the questions by.
    db: Session
        The database session.
    skip: int
        The number of records to skip.
    limit: int
        The maximum number of records to return.

    Returns:
    ----------
    List[QuestionSchema]
        A list of questions that match the filters.
    """
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

## File: groups.py
```py
# filename: app/api/endpoints/groups.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.db.session import get_db
from app.services.user_service import get_current_user
from app.services.logging_service import logger
from app.crud.crud_groups import create_group_crud, read_group_crud, update_group_crud, delete_group_crud
from app.schemas.groups import GroupCreateSchema, GroupUpdateSchema, GroupSchema
from app.models.users import UserModel


router = APIRouter()

@router.post("/groups", response_model=GroupSchema)
def create_group_endpoint(
    group_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Creating group with data: %s", group_data)
    try:
        logger.debug("Before calling create_group_crud")
        group_data["db"] = db
        group_data["creator_id"] = current_user.id
        group = GroupCreateSchema(**group_data)
        created_group = create_group_crud(db=db, group=group, creator_id=current_user.id)
        logger.debug("After calling create_group_crud")
        logger.debug("Group created successfully: %s", created_group)
        logger.debug("Before returning the response")
        return created_group
    except ValidationError as e:
        logger.error("Validation error creating group: %s", e.errors())
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"msg": err["msg"], "type": err["type"]} for err in e.errors()]
        ) from e
    except Exception as e:
        logger.exception("Error creating group: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e

@router.get("/groups/{group_id}", response_model=GroupSchema)
def get_group_endpoint(
    group_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_group = read_group_crud(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group

@router.put("/groups/{group_id}", response_model=GroupSchema)
def update_group_endpoint(
    group_id: int, 
    group_data: dict,
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    db_group = read_group_crud(db, group_id=group_id)
    logger.debug("db_group: %s", db_group)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if db_group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group creator can update the group")
    try:
        logger.debug("Updating group with data: %s", group_data)
        group = GroupUpdateSchema(**group_data)
        logger.debug("group: %s", group)
        updated_group = update_group_crud(db=db, group_id=group_id, group=group)
        logger.debug("updated_group: %s", updated_group)
        return updated_group
    except ValidationError as e:
        logger.error("Validation error updating group: %s", e.errors())
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"msg": err["msg"], "type": err["type"]} for err in e.errors()]
        ) from e
    except Exception as e:
        logger.exception("Error updating group: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e

@router.delete("/groups/{group_id}")
def delete_group_endpoint(
    group_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    db_group = read_group_crud(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if db_group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group creator can delete the group")
    delete_group_crud(db=db, group_id=group_id)
    return {"message": "Group deleted successfully"}

```

## File: leaderboard.py
```py
# filename: app/api/endpoints/leaderboard.py

# filename: app/api/endpoints/leaderboard.py

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.time_period import TimePeriodModel
from app.models.users import UserModel
from app.models.leaderboard import LeaderboardModel
from app.schemas.leaderboard import LeaderboardSchema
from app.services.scoring_service import calculate_leaderboard_scores
from app.services.user_service import get_current_user

router = APIRouter()

@router.get("/leaderboard/", response_model=List[LeaderboardSchema])
def get_leaderboard(
    time_period: TimePeriodModel,
    group_id: int = None,
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user: UserModel = Depends(get_current_user)
):
    leaderboard_scores = calculate_leaderboard_scores(db, time_period, group_id)
    leaderboard_data = [
        {
            "id": index + 1,
            "user_id": user_id,
            "score": score,
            "time_period": time_period,
            "group_id": group_id,
            "db": db
        }
        for index, (user_id, score) in enumerate(leaderboard_scores.items())
    ]
    leaderboard_schemas = [LeaderboardSchema(**data) for data in leaderboard_data]
    leaderboard_schemas.sort(key=lambda x: x.score, reverse=True)
    return leaderboard_schemas[:limit]

```

## File: question.py
```py
# filename: app/api/endpoints/question.py

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.crud.crud_questions import (
    create_question_crud,
    read_question_crud,
    update_question_crud,
    delete_question_crud
)
from app.db.session import get_db
from app.schemas.answer_choices import AnswerChoiceSchema
from app.schemas.questions import (
    QuestionCreateSchema,
    QuestionUpdateSchema,
    QuestionSchema,
    QuestionTagSchema
)
from app.services.user_service import get_current_user
from app.models.users import UserModel


router = APIRouter()

@router.post("/question", response_model=QuestionSchema, status_code=201)
def create_question_endpoint(
    question_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question_data['db'] = db
    question = QuestionCreateSchema(**question_data)
    db_question = create_question_crud(db, question)
    return db_question

@router.get("/question/question_id}", response_model=QuestionSchema)
# pylint: disable=unused-argument
def get_question_endpoint(
    question_id: int,
    question: QuestionUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question = read_question_crud(db, question_id)
    return question

@router.put("/question/{question_id}", response_model=QuestionSchema)
def update_question_endpoint(
    question_id: int,
    question_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question_data['db'] = db
    question = QuestionUpdateSchema(**question_data)
    db_question = update_question_crud(db, question_id=question_id, question=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
    return db_question

@router.delete("/question/{question_id}", status_code=204)
# pylint: disable=unused-argument
def delete_question_endpoint(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    deleted = delete_question_crud(db, question_id=question_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"Question with ID {question_id} not found")
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
    Form,
    HTTPException,
    UploadFile,
    File,
    Response,
    status
)
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.crud.crud_questions import create_question_crud
from app.crud.crud_question_sets import (
    read_question_sets_crud,
    read_question_set_crud,
    update_question_set_crud,
    delete_question_set_crud,
    create_question_set_crud
)
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.question_sets import QuestionSetSchema, QuestionSetCreateSchema, QuestionSetUpdateSchema
from app.schemas.questions import QuestionCreateSchema
from app.services.user_service import get_current_user
from app.services.logging_service import logger, sqlalchemy_obj_to_dict


router = APIRouter()


@router.post("/upload-questions/")
async def upload_question_set_endpoint(
    file: UploadFile = File(...),
    question_set_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin users can upload question sets")

    try:
        content = await file.read()
        question_data = json.loads(content.decode('utf-8'))

        # Validate question data
        for question in question_data:
            # Validate question against schema
            question['db'] = db
            QuestionCreateSchema(**question)

        # Create question set with the provided name
        question_set = QuestionSetCreateSchema(name=question_set_name, db=db)
        question_set_created = create_question_set_crud(db, question_set)

        # Create questions and associate with the newly created question set
        for question in question_data:
            question['question_set_id'] = question_set_created.id
            question['db'] = db
            create_question_crud(db, QuestionCreateSchema(**question))

        return {"message": "Question set uploaded successfully"}

    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON data: {str(exc)}"
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading question set: {str(exc)}"
        ) from exc

@router.get("/question-set/", response_model=List[QuestionSetSchema])
# pylint: disable=unused-argument
def read_questions_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    questions = read_question_sets_crud(db, skip=skip, limit=limit)
    return questions

@router.post("/question-sets/", response_model=QuestionSetSchema, status_code=201)
def create_question_set_endpoint(
    question_set_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Received question set data: %s", question_set_data)
    question_set_data['db'] = db
    question_set_data['creator_id'] = current_user.id
    if question_set_data.get('group_ids'):
        question_set_data['group_ids'] = list(set(question_set_data['group_ids']))

    # Add the database session to the schema data for validation
    logger.debug("Question set data after adding db: %s", question_set_data)

    # Manually create the schema instance with the updated data
    try:
        question_set = QuestionSetCreateSchema(**question_set_data)
        logger.debug("Re-instantiated question set: %s", question_set)

        created_question_set = create_question_set_crud(db=db, question_set=question_set)
        logger.debug("Question set created successfully: %s", created_question_set)
        return created_question_set
    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        logger.error("Error creating user response: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def get_question_set_endpoint(
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question_set = read_question_set_crud(db, question_set_id=question_set_id)
    if not question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found")
    return question_set

@router.get("/question-sets/", response_model=List[QuestionSetSchema])
def read_question_sets_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question_sets = read_question_sets_crud(db, skip=skip, limit=limit)
    return question_sets

@router.put("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def update_question_set_endpoint(
    question_set_id: int,
    question_set_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Received update data for question set %d: %s", question_set_id, question_set_data)
    question_set_data['db'] = db
    question_set_data['question_set_id'] = question_set_id
    question_set_data['creator_id'] = current_user.id
    if question_set_data.get('group_ids'):
        question_set_data['group_ids'] = list(set(question_set_data['group_ids']))
    if question_set_data.get('question_ids'):
        question_set_data['question_ids'] = list(set(question_set_data['question_ids']))

    try:
        question_set = QuestionSetUpdateSchema(**question_set_data)
        logger.debug("Re-instantiated question set for update: %s", question_set)

        updated_question_set = update_question_set_crud(
            db,
            question_set_id=question_set_id,
            question_set=question_set
        )
        logger.debug("Updated question set: %s", sqlalchemy_obj_to_dict(updated_question_set))
        if updated_question_set is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found")

        logger.debug("Question set updated successfully: %s", sqlalchemy_obj_to_dict(updated_question_set))
        
        response_data = {
            "id": updated_question_set.id,
            "name": updated_question_set.name,
            "is_public": updated_question_set.is_public,
            "creator_id": updated_question_set.creator_id,
            "question_ids": [question.id for question in updated_question_set.questions],
            "group_ids": [group.id for group in updated_question_set.groups]
        }
        
        return response_data
    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        logger.error("Error updating question set: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete("/question-sets/{question_set_id}", status_code=204)
def delete_question_set_endpoint(
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    deleted = delete_question_set_crud(db, question_set_id=question_set_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question set not found")
    return Response(status_code=204)

```

## File: questions.py
```py
# filename: app/api/endpoints/questions.py

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud.crud_questions import read_questions_crud
from app.db.session import get_db
from app.schemas.questions import QuestionSchema
from app.services.user_service import get_current_user
from app.models.users import UserModel


router = APIRouter()

@router.get("/questions/", response_model=List[QuestionSchema])
def get_questions_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    questions = read_questions_crud(db, skip=skip, limit=limit)
    if not questions:
        return []
    return questions

```

## File: register.py
```py
# filename: app/api/endpoints/register.py
"""
This module provides an endpoint for user registration.

It defines a route for registering new users by validating 
the provided data and creating a new user in the database.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.services.user_service import get_user_by_username, get_user_by_email
from app.crud.crud_user import create_user_crud
from app.db.session import get_db
from app.schemas.user import UserCreateSchema
from app.models.roles import RoleModel

router = APIRouter()

@router.post("/register", status_code=201)
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
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=422, detail="Username already registered")
    db_email = get_user_by_email(db, email=user.email)
    if db_email:
        raise HTTPException(status_code=422, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    if not user.role:
        default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
        user.role = default_role.name
    user_create = UserCreateSchema(
        username=user.username,
        password=hashed_password,
        email=user.email,
        role=user.role
    )
    created_user = create_user_crud(db=db, user=user_create)
    return created_user

```

## File: subjects.py
```py
# filename: app/api/endpoints/subjects.py
"""
This module defines the API endpoints for managing subjects in the application.

It includes endpoints to create and read subjects.
It also includes a service to get the database session and CRUD operations to manage subjects.

Imports:
----------
fastapi: For creating API routes and handling HTTP exceptions.
sqlalchemy.orm: For handling database sessions.
app.db.session: For getting the database session.
app.schemas.subjects: For validating and deserializing subject data.
app.crud: For performing CRUD operations on the subjects.

Variables:
----------
router: The API router instance.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.subjects import SubjectSchema, SubjectCreateSchema
from app.crud.crud_subjects import (
    create_subject_crud,
    read_subject_crud,
    update_subject_crud,
    delete_subject_crud
)
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
# pylint: disable=unused-argument
def create_subject_endpoint(
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new subject.

    Args:
        subject (SubjectCreateSchema): The subject data to be created.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        SubjectSchema: The created subject.
    """
    return create_subject_crud(db=db, subject=subject)

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
# pylint: disable=unused-argument
def read_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Read a subject by ID.

    Args:
        subject_id (int): The ID of the subject to be read.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        SubjectSchema: The read subject.

    Raises:
        HTTPException: If the subject is not found.
    """
    subject = read_subject_crud(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.put("/subjects/{subject_id}", response_model=SubjectSchema)
# pylint: disable=unused-argument
def update_subject_endpoint(
    subject_id: int,
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a subject by ID.

    Args:
        subject_id (int): The ID of the subject to be updated.
        subject (SubjectCreateSchema): The updated subject data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        SubjectSchema: The updated subject.

    Raises:
        HTTPException: If the subject is not found.
    """
    updated_subject = update_subject_crud(db, subject_id, subject)
    if not updated_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return updated_subject

@router.delete("/subjects/{subject_id}", status_code=204)
# pylint: disable=unused-argument
def delete_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a subject by ID.

    Args:
        subject_id (int): The ID of the subject to be deleted.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the subject is not found.
    """
    deleted = delete_subject_crud(db, subject_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subject not found")
    return None

```

## File: topics.py
```py
# filename: app/api/endpoints/topics.py
"""
This module defines the API endpoints for managing topics in the application.

It includes endpoints to create and read topics.
It also includes a service to get the database session and CRUD operations to manage topics.

Imports:
----------
fastapi: For creating API routes and handling HTTP exceptions.
sqlalchemy.orm: For handling database sessions.
app.db: For getting the database session.
app.schemas: For validating and deserializing topic data.
app.crud: For performing CRUD operations on the topics.

Variables:
----------
router: The API router instance.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.topics import TopicSchema, TopicCreateSchema
from app.crud.crud_topics import create_topic_crud, read_topic_crud, update_topic_crud, delete_topic_crud
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/topics/", response_model=TopicSchema, status_code=201)
# pylint: disable=unused-argument
def create_topic_endpoint(
    topic: TopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new topic.

    Args:
        topic (TopicCreateSchema): The topic data to be created.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        TopicSchema: The created topic.
    """
    return create_topic_crud(db=db, topic=topic)

@router.get("/topics/{topic_id}", response_model=TopicSchema)
# pylint: disable=unused-argument
def read_topic_endpoint(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Read a topic by its ID.

    Args:
        topic_id (int): The ID of the topic to be read.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        TopicSchema: The read topic.

    Raises:
        HTTPException: If the topic is not found.
    """
    topic = read_topic_crud(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.put("/topics/{topic_id}", response_model=TopicSchema)
# pylint: disable=unused-argument
def update_topic_endpoint(
    topic_id: int,
    topic: TopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a topic by its ID.

    Args:
        topic_id (int): The ID of the topic to be updated.
        topic (TopicCreateSchema): The updated topic data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        TopicSchema: The updated topic.

    Raises:
        HTTPException: If the topic is not found.
    """
    updated_topic = update_topic_crud(db, topic_id, topic)
    if not updated_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return updated_topic

@router.delete("/topics/{topic_id}", status_code=204)
# pylint: disable=unused-argument
def delete_topic_endpoint(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a topic by its ID.

    Args:
        topic_id (int): The ID of the topic to be deleted.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the topic is not found.
    """
    deleted = delete_topic_crud(db, topic_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Topic not found")
    return None

```

## File: user_responses.py
```py
# filename: app/api/endpoints/user_responses.py

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from app.crud.crud_user_responses import (
    create_user_response_crud,
    get_user_response_crud,
    get_user_responses_crud,
    update_user_response_crud,
    delete_user_response_crud
)
from app.db.session import get_db
from app.schemas.user_responses import UserResponseSchema, UserResponseCreateSchema, UserResponseUpdateSchema
from app.models.users import UserModel
from app.services.user_service import get_current_user
from app.services.logging_service import logger


router = APIRouter()

@router.post(
    "/user-responses/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED
)
def create_user_response_endpoint(
    user_response_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Received user response data: %s", user_response_data)

    # Manually create the schema instance with the updated data
    try:
        user_response = UserResponseCreateSchema(**user_response_data)
        logger.debug("Re-instantiated user response: %s", user_response)

        created_response = create_user_response_crud(db=db, user_response=user_response)
        logger.debug("User response created successfully: %s", created_response)
        return created_response
    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except HTTPException as e:
        logger.error("Error creating user response: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e

@router.get("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def get_user_response_endpoint(
    user_response_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_response = get_user_response_crud(db, user_response_id)
    if not user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    return user_response

@router.get("/user-responses/", response_model=List[UserResponseSchema])
def get_user_responses_endpoint(
    user_id: Optional[int] = None,
    question_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_responses = get_user_responses_crud(
        db,
        user_id=user_id,
        question_id=question_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )
    return user_responses

@router.put("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def update_user_response_endpoint(
    user_response_id: int,
    user_response_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_response = UserResponseUpdateSchema(**user_response_data)
    updated_user_response = update_user_response_crud(db, user_response_id, user_response)
    return updated_user_response

@router.delete("/user-responses/{user_response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_response_endpoint(
    user_response_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
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
from app.crud.crud_user import create_user_crud, update_user_crud
from app.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema
from app.services.user_service import get_current_user
from app.services.logging_service import logger

router = APIRouter()

@router.post("/users/", response_model=UserSchema, status_code=201)
def create_user(
    user_data: dict, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_data['db'] = db
    user = UserCreateSchema(**user_data)
    try:
        new_user = create_user_crud(db=db, user=user)
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
            ) from e

@router.get("/users/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    users = db.query(UserModel).all()
    return users

@router.get("/users/me", response_model=UserSchema)
def read_user_me(
    current_user: UserModel = Depends(get_current_user)
):
    return current_user

@router.put(
    "/users/me",
    response_model=UserSchema,
)
def update_user_me(
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Received user data: %s", user_data)

    # Add the database session to the schema data for validation
    user_data['db'] = db
    user_data['id'] = current_user.id
    logger.debug("User data after adding db: %s", user_data)

    # Manually create the schema instance with the updated data
    try:
        user_update = UserUpdateSchema(**user_data)
        logger.debug("Re-instantiated user update: %s", user_update)

        updated_user = update_user_crud(db=db, user_id=current_user.id, updated_user=user_update)
        logger.debug("User updated successfully: %s", updated_user)
        return updated_user
    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        logger.error("Error updating user: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail)

```

# Directory: /code/quiz-app/quiz-app-backend/app/models

## File: __init__.py
```py

```

## File: answer_choices.py
```py
# filename: app/models/answer_choices.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class AnswerChoiceModel(Base):
    __tablename__ = "answer_choices"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    is_correct = Column(Boolean)
    explanation = Column(Text)  # Add the explanation field
    question_id = Column(Integer, ForeignKey('questions.id'))

    question = relationship("QuestionModel", back_populates="answer_choices")

```

## File: associations.py
```py
# filename: app/models/associations.py

from sqlalchemy import Column, Integer, ForeignKey
from app.db.base_class import Base


class UserToGroupAssociation(Base):
    __tablename__ = "user_to_group_association"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)

class QuestionToTagAssociation(Base):
    __tablename__ = "question_to_tag_association"

    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("question_tags.id"), primary_key=True)

class QuestionSetToQuestionAssociation(Base):
    __tablename__ = "question_set_to_question_association"

    question_id = Column(ForeignKey('questions.id'), primary_key=True)
    question_set_id = Column(ForeignKey('question_sets.id'), primary_key=True)

class QuestionSetToGroupAssociation(Base):
    __tablename__ = "question_set_to_group_association"

    question_set_id = Column(ForeignKey('question_sets.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)

class RoleToPermissionAssociation(Base):
    __tablename__ = "role_permission_association"

    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)

```

## File: authentication.py
```py
# filename: app/models/authentication.py

from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base_class import Base


class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    # pylint: disable=not-callable
    revoked_at = Column(DateTime, server_default=func.now())

```

## File: groups.py
```py
# filename: app/models/groups.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import UserToGroupAssociation, QuestionSetToGroupAssociation


class GroupModel(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))

# Define relationships after all classes have been defined
GroupModel.users = relationship(
    "UserModel",
    secondary=UserToGroupAssociation.__tablename__,
    back_populates="groups"
)
GroupModel.creator = relationship("UserModel", back_populates="created_groups")
GroupModel.leaderboards = relationship("LeaderboardModel", back_populates="group")
GroupModel.question_sets = relationship(
    "QuestionSetModel",
    secondary=QuestionSetToGroupAssociation.__tablename__,
    back_populates="groups"
)

```

## File: leaderboard.py
```py
# filename: app/models/leaderboard.py

from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.time_period import TimePeriodModel


class LeaderboardModel(Base):
    __tablename__ = "leaderboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer)
    time_period = Column(Enum(TimePeriodModel))
    group_id = Column(Integer, ForeignKey("groups.id"))

# Define relationships after all classes have been defined
LeaderboardModel.user = relationship("UserModel", back_populates="leaderboards")
LeaderboardModel.group = relationship("GroupModel", back_populates="leaderboards")


```

## File: permissions.py
```py
# filename: app/models/roles.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import RoleToPermissionAssociation


class PermissionModel(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    roles = relationship(
        "RoleModel",
        secondary=RoleToPermissionAssociation.__tablename__,
        back_populates="permissions"
    )

    def __repr__(self):
        return f"<PermissionModel(id={self.id}, name='{self.name}')>"

```

## File: question_sets.py
```py
# filename: app/models/question_sets.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, inspect, ARRAY
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import QuestionSetToQuestionAssociation, QuestionSetToGroupAssociation


class QuestionSetModel(Base):
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_public = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey("users.id"))

    creator = relationship("UserModel", back_populates="created_question_sets")
    questions = relationship(
        "QuestionModel",
        secondary=QuestionSetToQuestionAssociation.__table__,
        back_populates="question_sets"
    )
    sessions = relationship("SessionQuestionSetModel", back_populates="question_set")
    groups = relationship(
        "GroupModel",
        secondary=QuestionSetToGroupAssociation.__table__,
        back_populates="question_sets"
    )

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

```

## File: question_tags.py
```py
# filename: app/models/question_tags.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import QuestionToTagAssociation


class QuestionTagModel(Base):
    __tablename__ = "question_tags"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, index=True)

    questions = relationship("QuestionModel", secondary=QuestionToTagAssociation.__table__, overlaps="tags")

```

## File: questions.py
```py
# filename: app/models/questions.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.inspection import inspect
from app.db.base_class import Base
from app.models.associations import (
    QuestionSetToQuestionAssociation,
    QuestionToTagAssociation
)
from app.models.sessions import SessionQuestionModel


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
    tags = relationship("QuestionTagModel", secondary=QuestionToTagAssociation.__table__)
    answer_choices = relationship("AnswerChoiceModel", back_populates="question")
    question_sets = relationship(
        "QuestionSetModel",
        secondary=QuestionSetToQuestionAssociation.__table__,
        back_populates="questions"
    )
    session_questions = relationship("SessionQuestionModel", back_populates="question")

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

```

## File: roles.py
```py
# filename: app/models/roles.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import RoleToPermissionAssociation


class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    default = Column(Boolean, default=False)

    permissions = relationship(
        "PermissionModel",
        secondary=RoleToPermissionAssociation.__tablename__,
        back_populates="roles"
    )

    def __repr__(self):
        return f"<RoleModel(id={self.id}, name='{self.name}')>"

```

## File: sessions.py
```py
# filename: app/models/sessions.py

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class SessionQuestionModel(Base):
    __tablename__ = 'session_questions'
    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    answered = Column(Boolean, default=False)
    correct = Column(Boolean, nullable=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    session = relationship("SessionModel", back_populates="questions")
    question = relationship("QuestionModel", back_populates="session_questions")

class SessionQuestionSetModel(Base):
    __tablename__ = 'session_question_sets'
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

## File: time_period.py
```py
# filename: app/models/time_period.py

from enum import Enum


class TimePeriodModel(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

```

## File: topics.py
```py
# filename: app/models/topics.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class TopicModel(Base):
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

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import UserToGroupAssociation


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String)

# Define relationships after all classes have been defined
UserModel.responses = relationship("UserResponseModel", back_populates="user")
UserModel.groups = relationship(
    "GroupModel",
    secondary=UserToGroupAssociation.__table__,
    back_populates="users"
)
UserModel.leaderboards = relationship("LeaderboardModel", back_populates="user")
UserModel.created_groups = relationship("GroupModel", back_populates="creator")
UserModel.created_question_sets = relationship("QuestionSetModel", back_populates="creator")

```

# Directory: /code/quiz-app/quiz-app-backend/app/middleware

## File: __init__.py
```py

```

## File: authorization_middleware.py
```py
# app/middleware/authorization_middleware.py

from fastapi import Request, HTTPException, status
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.user_service import get_current_user, oauth2_scheme
from app.services.authorization_service import has_permission
from app.services.logging_service import logger
from app.db.session import get_db
from app.core.config import settings_core
from app.models.permissions import PermissionModel

class AuthorizationMiddleware(BaseHTTPMiddleware):
    method_map = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "DELETE": "delete",
    }

    async def dispatch(self, request: Request, call_next):
        logger.debug("AuthorizationMiddleware - Requested URL: %s", request.url.path)
        if request.url.path in settings_core.UNPROTECTED_ENDPOINTS:
            logger.debug("AuthorizationMiddleware - Unprotected endpoint, skipping authorization")
            response = await call_next(request)
            return response

        logger.debug("AuthorizationMiddleware - Protected endpoint, checking authorization")
        token = await oauth2_scheme(request)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")        
        try:
            db = next(get_db())
            current_user = await get_current_user(token, db)
            logger.debug("Current user: %s", current_user)
            route = request.url.path
            crud_verb = self.method_map.get(request.method)

            if crud_verb:
                logger.debug("AuthorizationMiddleware - CRUD verb: %s", crud_verb)
                required_permission = db.query(PermissionModel).filter(
                    PermissionModel.name == f"{crud_verb}_{route.replace('/', '_')}"
                ).first()

                if required_permission:
                    logger.debug("AuthorizationMiddleware - Required permission: %s", required_permission.name)
                    if not has_permission(db, current_user, required_permission.name):
                        logger.debug("AuthorizationMiddleware - User does not have the required permission")
                        raise HTTPException(status_code=403, detail="User does not have the required permission")
                else:
                    logger.debug("AuthorizationMiddleware - No permission found for the current route and CRUD verb")
            else:
                logger.debug("AuthorizationMiddleware - No CRUD verb found for the current request method")

            logger.debug("AuthorizationMiddleware - Before calling the next middleware or endpoint")
            response = await call_next(request)
            logger.debug("AuthorizationMiddleware - After calling the next middleware or endpoint")
            return response
        except HTTPException as e:
            logger.error("HTTPException occurred: %s", e.detail)
            raise e
        except ValidationError as e:
            logger.error("ValidationError occurred: %s", e.errors())
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()) from e
        except Exception as e:
            logger.exception("Unexpected error: %s", str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e
        finally:
            db.close()

```

## File: blacklist_middleware.py
```py
# filename: app/middleware/blacklist_middleware.py

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.db.session import get_db
from app.models.authentication import RevokedTokenModel
from app.core.config import settings_core
from app.services.logging_service import logger


async def check_revoked_tokens(request: Request, call_next):
    logger.debug("check_revoked_tokens - Requested URL: %s", request.url.path)
    if request.url.path in settings_core.UNPROTECTED_ENDPOINTS:
        logger.debug("check_revoked_tokens - Unprotected endpoint, skipping blacklist check")
        return await call_next(request)
    
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        logger.debug("check_revoked_tokens - Token: %s", token)
        db = next(get_db())
        try:
            revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
            if revoked_token:
                logger.debug("check_revoked_tokens - Token is revoked")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
            logger.debug("check_revoked_tokens - Token is not revoked")
        except Exception as e:
            logger.error("check_revoked_tokens - Error during DB query: %s", e)
        finally:
            db.close()
            logger.debug("check_revoked_tokens - DB session closed")
    
    logger.debug("check_revoked_tokens - Before calling next middleware or endpoint")
    response = await call_next(request)
    logger.debug("check_revoked_tokens - After calling next middleware or endpoint")
    return response

class BlacklistMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug("BlacklistMiddleware - Requested URL: %s", request.url.path)
        response = await check_revoked_tokens(request, call_next)
        logger.debug("BlacklistMiddleware - After calling check_revoked_tokens")
        return response

```

## File: cors_middleware.py
```py
# filename: app/middleware/cors_middleware.py

from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",  # Add the URL of your frontend application
]

def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

```

# Directory: /code/quiz-app/quiz-app-backend/app/core

## File: __init__.py
```py

```

## File: config.py
```py
# filename: app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import ValidationError
import toml
import os
import dotenv
from app.services.logging_service import logger


class SettingsCore(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    UNPROTECTED_ENDPOINTS: list

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        logger.debug("Looking for .env file at: %s", env_file)

def load_config_from_toml() -> dict:
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pyproject.toml")
    logger.debug("Loading configuration from %s", config_path)
    try:
        config = toml.load(config_path)["tool"]["app"]
        logger.debug("Configuration loaded from toml: %s", config)
        return config
    except FileNotFoundError:
        logger.error("pyproject.toml file not found at %s", config_path)
        raise
    except KeyError:
        logger.error("Required 'tool.app' section not found in pyproject.toml")
        raise

def load_settings() -> SettingsCore:
    logger.debug("Entering load_settings()")
    
    try:
        # Load SECRET_KEY from .env
        logger.debug("Loading SECRET_KEY from .env file")
        env_settings = dotenv.dotenv_values(".env")
        secret_key = env_settings.get("SECRET_KEY")
        if not secret_key:
            raise ValueError("SECRET_KEY not found in .env file")
        logger.debug("SECRET_KEY loaded from .env")
    except Exception as e:
        logger.error("Error loading SECRET_KEY from .env: %s", str(e))
        raise
    
    try:
        # Load settings from pyproject.toml 
        logger.debug("Loading settings from pyproject.toml")
        toml_config = load_config_from_toml()

        # Determine the environment
        environment = os.getenv("ENVIRONMENT", "dev")
        logger.debug("Current environment: %s", environment)
        
        # Get DATABASE_URL based on environment
        if environment == "dev":
            database_url = toml_config["database_url_dev"]
        elif environment == "test":
            database_url = toml_config["database_url_test"]
        else:
            raise ValueError(f"Invalid environment specified: {environment}")

        logger.debug("Database URL for environment (%s): %s", environment, database_url)

        # Create the settings instance with values from pyproject.toml and .env
        settings = SettingsCore(
            SECRET_KEY=secret_key,
            ACCESS_TOKEN_EXPIRE_MINUTES=toml_config["access_token_expire_minutes"],
            DATABASE_URL=database_url,
            UNPROTECTED_ENDPOINTS=toml_config["unprotected_endpoints"],
        )
        
        logger.debug("Settings created: %s", settings.model_dump())
    except KeyError as e:
        logger.error("Missing required setting in pyproject.toml: %s", str(e))
        raise
    except ValidationError as e:
        logger.error("Error creating settings instance: %s", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error loading settings: %s", str(e))
        raise
    
    logger.debug("Exiting load_settings()")
    return settings

# Load settings based on the environment variable
settings_core = load_settings()

```

## File: jwt.py
```py
# filename: app/core/jwt.py

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.core.config import settings_core
from app.services.logging_service import logger


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings_core.ACCESS_TOKEN_EXPIRE_MINUTES)
    logger.debug("Creating access token with expiration: %s", expire)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings_core.SECRET_KEY, algorithm="HS256")
    logger.debug("Access token created: %s", encoded_jwt)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        logger.debug("Decoding access token: %s", token)
        payload = jwt.decode(token, settings_core.SECRET_KEY, algorithms=["HS256"])
        logger.debug("Access token decoded: %s", payload)
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        logger.error("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings_core.SECRET_KEY, algorithms=["HS256"])
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
import sys
sys.path.insert(0, "/code/quiz-app/quiz-app-backend")

import random
import os
import string
import toml
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base_class import Base
from app.db.session import get_db, init_db
from app.crud.crud_user import create_user_crud
from app.crud.crud_questions import create_question_crud
from app.crud.crud_question_sets import create_question_set_crud
from app.crud.crud_question_tags import create_question_tag_crud, delete_question_tag_crud
from app.crud.crud_roles import create_role_crud, delete_role_crud
from app.crud.crud_subtopics import create_subtopic_crud
from app.crud.crud_subjects import create_subject_crud
from app.crud.crud_topics import create_topic_crud
from app.crud.crud_groups import create_group_crud, read_group_crud
from app.schemas.user import UserCreateSchema
from app.schemas.groups import GroupCreateSchema
from app.schemas.question_sets import QuestionSetCreateSchema
from app.schemas.question_tags import QuestionTagCreateSchema
from app.schemas.questions import QuestionCreateSchema
from app.schemas.roles import RoleCreateSchema
from app.schemas.answer_choices import AnswerChoiceCreateSchema
from app.schemas.subtopics import SubtopicCreateSchema
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.topics import TopicCreateSchema
from app.models.associations import (
    UserToGroupAssociation,
    QuestionSetToGroupAssociation,
    QuestionToTagAssociation,
    QuestionSetToQuestionAssociation,
    RoleToPermissionAssociation
)
from app.models.answer_choices import AnswerChoiceModel
from app.models.authentication import RevokedTokenModel
from app.models.groups import GroupModel
from app.models.leaderboard import LeaderboardModel
from app.models.permissions import PermissionModel
from app.models.question_sets import QuestionSetModel
from app.models.question_tags import QuestionTagModel
from app.models.questions import QuestionModel
from app.models.roles import RoleModel
from app.models.sessions import SessionQuestionModel, SessionQuestionSetModel, SessionModel
from app.models.subjects import SubjectModel
from app.models.subtopics import SubtopicModel
from app.models.time_period import TimePeriodModel
from app.models.topics import TopicModel
from app.models.user_responses import UserResponseModel
from app.models.users import UserModel
from app.core.jwt import create_access_token
from app.services.permission_generator_service import generate_permissions
from app.services.logging_service import logger


# Set the environment to test for pytest
os.environ["ENVIRONMENT"] = "test"

# Load the test database URL from pyproject.toml (one level above the current directory)
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
config = toml.load(config_path)
SQLALCHEMY_TEST_DATABASE_URL = config["tool"]["app"]["database_url_test"]


@pytest.fixture(autouse=True)
def log_test_name(request):
    logger.debug("Running test: %s", request.node.nodeid)
    yield
    logger.debug("Finished test: %s", request.node.nodeid)

def reset_database(db_url):
    engine = create_engine(db_url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture(scope='function')
def db_session():
    logger.debug("Begin setting up database fixture")
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    reset_database(SQLALCHEMY_TEST_DATABASE_URL)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        logger.debug("Begin tearing down database fixture")
        session.close()
        reset_database(SQLALCHEMY_TEST_DATABASE_URL)
        logger.debug("Finished tearing down database fixture")

@pytest.fixture(scope='function')
def client(db_session):
    logger.debug("Begin setting up client fixture")
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[override_get_db] = override_get_db
    with TestClient(app) as client:
        logger.debug("Finished setting up client fixture")
        yield client
    app.dependency_overrides.clear()
    logger.debug("Finished tearing down client fixture")

@pytest.fixture
def test_permission(db_session):
    from app.models.permissions import PermissionModel
    permission = PermissionModel(name="test_permission", description="A test permission")
    db_session.add(permission)
    db_session.commit()
    return permission

@pytest.fixture(scope="function")
def test_permissions(db_session):
    from app.main import app  # Import the actual FastAPI app instance
    from app.services.permission_generator_service import generate_permissions

    # Generate permissions
    permissions = generate_permissions(app, db_session)
    
    # Ensure permissions are in the database
    for permission_name in permissions:
        if not db_session.query(PermissionModel).filter_by(name=permission_name).first():
            db_session.add(PermissionModel(name=permission_name))
    db_session.commit()
    
    yield permissions

    # Clean up (optional, depending on your test isolation needs)
    db_session.query(PermissionModel).delete()
    db_session.commit()

@pytest.fixture(scope="function")
def test_role(db_session, test_permissions):
    # Create a test role with all permissions
    role_data = {
        "name": "test_role",
        "description": "Test Role",
        "permissions": list(test_permissions),
        "default": False
    }
    logger.debug("Creating test role with data: %s", role_data)
    role_create_schema = RoleCreateSchema(**role_data)
    logger.debug("Role create schema: %s", role_create_schema.model_dump())
    role = create_role_crud(db_session, role_create_schema)
    logger.debug("Role created: %s", role)
    yield role

    # Clean up
    delete_role_crud(db_session, role.id)

@pytest.fixture(scope="function")
def random_username():
    yield "test.user_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture(scope="function")
def test_user(db_session, random_username, test_role):
    try:
        logger.debug("Setting up test_user fixture")
        email = f"{random_username}@example.com"
        user_data = UserCreateSchema(
            username=random_username,
            email=email,
            password="TestPassword123!",
            role=test_role.name
        )
        user = create_user_crud(db_session, user_data)
        user.is_admin = True
        db_session.add(user)
        db_session.commit()
        yield user
    except Exception as e:
        logger.exception("Error in test_user fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_user fixture")

@pytest.fixture(scope="function")
def test_group(db_session, test_user):
    try:
        logger.debug("Setting up test_group fixture")
        group_data = GroupCreateSchema(
            name="Test Group",
            description="This is a test group",
            creator_id=test_user.id
        )
        group = create_group_crud(db_session, group_data, test_user.id)
        db_session.add(group)
        db_session.commit()
        yield group
    except Exception as e:
        logger.exception("Error in test_group fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_group fixture")
        db_group = read_group_crud(db_session, group.id)
        if db_group:
            db_session.delete(group)
            db_session.commit()

@pytest.fixture(scope="function")
def test_user_with_group(db_session, test_user, test_group):
    try:
        logger.debug("Setting up test_user_with_group fixture")
        association = UserToGroupAssociation(user_id=test_user.id, group_id=test_group.id)
        db_session.add(association)
        db_session.commit()
        yield test_user
    except Exception as e:
        logger.exception("Error in test_user_with_group fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_user_with_group fixture")

@pytest.fixture(scope="function")
def test_tag(db_session):
    tag_data = QuestionTagCreateSchema(tag="Test Tag")
    tag = create_question_tag_crud(db_session, tag_data)
    yield tag
    delete_question_tag_crud(db_session, tag.id)

@pytest.fixture
def test_question_set_data(db_session, test_user_with_group):
    try:
        logger.debug("Setting up test_question_set_data fixture")
        test_question_set_data_create = {
            "db": db_session,
            "name": "Test Question Set",
            "is_public": True,
            "creator_id": test_user_with_group.id
        }
        created_test_question_set_data = QuestionSetCreateSchema(**test_question_set_data_create)
        return created_test_question_set_data
    except Exception as e:
        logger.exception("Error in test_question_set_data fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_question_set_data fixture")

@pytest.fixture(scope="function")
def test_question_set(db_session, test_user, test_question_set_data):
    try:
        logger.debug("Setting up test_question_set fixture")
        question_set = create_question_set_crud(
            db=db_session,
            question_set=test_question_set_data
        )
        db_session.commit()
        yield question_set
    except Exception as e:
        logger.exception("Error in test_question_set fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_question_set fixture")

@pytest.fixture(scope="function")
def test_questions(db_session, test_subject, test_topic, test_subtopic):
    try:
        logger.debug("Setting up test_questions fixture")
        questions_data = [
            QuestionCreateSchema(
                db=db_session,
                text="Test Question 1",
                subject_id=test_subject.id,
                topic_id=test_topic.id,
                subtopic_id=test_subtopic.id,
                difficulty="Easy",
                answer_choices=[
                    AnswerChoiceCreateSchema(text="Answer 1", is_correct=True, explanation="Explanation 1"),
                    AnswerChoiceCreateSchema(text="Answer 2", is_correct=False, explanation="Explanation 2")
                ]
            ),
            QuestionCreateSchema(
                db=db_session,
                text="Test Question 2",
                subject_id=test_subject.id,
                topic_id=test_topic.id,
                subtopic_id=test_subtopic.id,
                difficulty="Medium",
                answer_choices=[
                    AnswerChoiceCreateSchema(text="Answer 3", is_correct=False, explanation="Explanation 3"),
                    AnswerChoiceCreateSchema(text="Answer 4", is_correct=True, explanation="Explanation 4")
                ]
            )
        ]
        questions = [create_question_crud(db_session, q) for q in questions_data]
        yield questions
    except Exception as e:
        logger.exception("Error in test_questions fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_questions fixture")

@pytest.fixture(scope="function")
def test_subject(db_session):
    try:
        logger.debug("Setting up test_subject fixture")
        subject_data = SubjectCreateSchema(name="Test Subject")
        subject = create_subject_crud(db=db_session, subject=subject_data)
        yield subject
    except Exception as e:
        logger.exception("Error in test_subject fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_subject fixture")

@pytest.fixture(scope="function")
def test_topic(db_session, test_subject):
    try:
        logger.debug("Setting up test_topic fixture")
        topic_data = TopicCreateSchema(name="Test Topic", subject_id=test_subject.id)
        topic = create_topic_crud(db=db_session, topic=topic_data)
        yield topic
    except Exception as e:
        logger.exception("Error in test_topic fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_topic fixture")

@pytest.fixture(scope="function")
def test_subtopic(db_session, test_topic):
    try:
        logger.debug("Setting up test_subtopic fixture")
        subtopic_data = SubtopicCreateSchema(name="Test Subtopic", topic_id=test_topic.id)
        subtopic = create_subtopic_crud(db=db_session, subtopic=subtopic_data)
        yield subtopic
    except Exception as e:
        logger.exception("Error in test_subtopic fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_subtopic fixture")

@pytest.fixture(scope="function")
def test_question(db_session, test_question_set, test_subtopic, test_topic, test_subject):
    try:
        logger.debug("Setting up test_question fixture")
        answer_choice_1 = AnswerChoiceCreateSchema(text="Test Answer 1", is_correct=True, explanation="Test Explanation 1")
        answer_choice_2 = AnswerChoiceCreateSchema(text="Test Answer 2", is_correct=False, explanation="Test Explanation 2")
        question_data = QuestionCreateSchema(
            db=db_session,
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
    except Exception as e:
        logger.exception("Error in test_question fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_question fixture")

@pytest.fixture(scope="function")
def test_token(test_user):
    try:
        logger.debug("Setting up test_token fixture")
        access_token = create_access_token(data={"sub": test_user.username})
        yield access_token
    except Exception as e:
        logger.exception("Error in test_token fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_token fixture")

@pytest.fixture(scope="function")
def test_answer_choice_1(db_session, test_question):
    try:
        logger.debug("Setting up test_answer_choice_1 fixture")
        answer_choice = AnswerChoiceModel(text="Test Answer 1", is_correct=True, question=test_question)
        db_session.add(answer_choice)
        db_session.commit()
        yield answer_choice
    except Exception as e:
        logger.exception("Error in test_answer_choice_1 fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_answer_choice_1 fixture")

@pytest.fixture(scope="function")
def test_answer_choice_2(db_session, test_question):
    try:
        logger.debug("Setting up test_answer_choice_2 fixture")
        answer_choice = AnswerChoiceModel(text="Test Answer 2", is_correct=False, question=test_question)
        db_session.add(answer_choice)
        db_session.commit()
        yield answer_choice
    except Exception as e:
        logger.exception("Error in test_answer_choice_2 fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_answer_choice_2 fixture")

@pytest.fixture(scope="function")
def logged_in_client(client, test_user_with_group):
    try:
        logger.debug("Setting up logged_in_client fixture")
        login_data = {"username": test_user_with_group.username, "password": "TestPassword123!"}
        logger.debug("Logging in with username: %s", test_user_with_group.username)
        response = client.post("/login", data=login_data)
        logger.debug("Login response status code: %s", response.status_code)
        access_token = response.json()["access_token"]
        assert response.status_code == 200, "Authentication failed."
        
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        logger.debug("Access token added to client headers")
        yield client
    except Exception as e:
        logger.exception("Error in logged_in_client fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down logged_in_client fixture")

@pytest.fixture(scope="function")
def setup_filter_questions_data(db_session):
    try:
        logger.debug("Setting up filter questions data")

        subject1 = create_subject_crud(db_session, SubjectCreateSchema(name="Math"))
        subject2 = create_subject_crud(db_session, SubjectCreateSchema(name="Science"))

        topic1 = create_topic_crud(db_session, TopicCreateSchema(name="Algebra", subject_id=subject1.id))
        topic2 = create_topic_crud(db_session, TopicCreateSchema(name="Geometry", subject_id=subject1.id))
        topic3 = create_topic_crud(db_session, TopicCreateSchema(name="Physics", subject_id=subject2.id))

        subtopic1 = create_subtopic_crud(db_session, SubtopicCreateSchema(name="Linear Equations", topic_id=topic1.id))
        subtopic2 = create_subtopic_crud(db_session, SubtopicCreateSchema(name="Quadratic Equations", topic_id=topic1.id))
        subtopic3 = create_subtopic_crud(db_session, SubtopicCreateSchema(name="Triangles", topic_id=topic2.id))
        subtopic4 = create_subtopic_crud(db_session, SubtopicCreateSchema(name="Mechanics", topic_id=topic3.id))

        tag1 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="equations"))
        tag2 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="solving"))
        tag3 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="geometry"))
        tag4 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="physics"))

        question_set1 = create_question_set_crud(db_session, QuestionSetCreateSchema(name="Math Question Set", is_public=True))
        question_set2 = create_question_set_crud(db_session, QuestionSetCreateSchema(name="Science Question Set", is_public=True))

        question1 = create_question_crud(db_session, QuestionCreateSchema(
            db=db_session,
            text="What is x if 2x + 5 = 11?",
            subject_id=subject1.id,
            topic_id=topic1.id,
            subtopic_id=subtopic1.id,
            difficulty="Easy",
            tags=[tag1, tag2]
        ))
        question2 = create_question_crud(db_session, QuestionCreateSchema(
            db=db_session,
            text="Find the roots of the equation: x^2 - 5x + 6 = 0",
            subject_id=subject1.id,
            topic_id=topic1.id,
            subtopic_id=subtopic2.id,
            difficulty="Medium",
            tags=[tag1, tag2]
        ))
        question3 = create_question_crud(db_session, QuestionCreateSchema(
            db=db_session,
            text="Calculate the area of a right-angled triangle with base 4 cm and height 3 cm.",
            subject_id=subject1.id,
            topic_id=topic2.id,
            subtopic_id=subtopic3.id,
            difficulty="Easy",
            tags=[tag3]
        ))
        question4 = create_question_crud(db_session, QuestionCreateSchema(
            db=db_session,
            text="A car accelerates from rest at 2 m/s^2. What is its velocity after 5 seconds?",
            subject_id=subject2.id,
            topic_id=topic3.id,
            subtopic_id=subtopic4.id,
            difficulty="Medium",
            tags=[tag4]
        ))

    except Exception as e:
        logger.exception("Error in setup_filter_questions_data fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down setup_filter_questions_data fixture")

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_integration

## File: test_integration_auth.py
```py
# filename: tests/test_integration_auth.py

import pytest
from fastapi import HTTPException

def test_protected_route_with_valid_token(client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200

def test_protected_route_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    # Try accessing the protected route with the invalid token
    with pytest.raises(HTTPException) as exc_info:
        client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"

def test_protected_route_with_revoked_token(client, test_token):
    # Logout to revoke the token
    headers = {"Authorization": f"Bearer {test_token}"}
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200

    # Try accessing the protected route with the revoked token
    with pytest.raises(HTTPException) as exc_info:
        client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"

```

## File: test_integration_cors.py
```py
# filename: tests/test_integration_cors.py

def test_cors_configuration(logged_in_client):
    response = logged_in_client.get("/", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_schemas

## File: test_schemas_filters.py
```py
import pytest
from pydantic import ValidationError
from app.schemas.filters import FilterParamsSchema


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

## File: test_schemas_questions.py
```py
# filename: tests/test_schemas.py

from app.schemas.questions import QuestionCreateSchema


def test_question_create_schema(
    db_session,
    test_subtopic,
    test_question_set,
    test_subject,
    test_topic
):
    question_data = {
        "db": db_session,
        "text": "Test question",
        "subject_id": test_subject.id,
        "topic_id": test_topic.id,
        "subtopic_id": test_subtopic.id,
        "question_set_ids": [test_question_set.id],
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


def test_user_create_schema():
    user_data = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.username == "testuser"
    assert user_schema.password == "TestPassword123!"
    assert user_schema.email == "testuser@example.com"

def test_user_create_schema_password_validation():
    user_data = {
        "username": "testuser",
        "password": "ValidPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_user_create_schema_password_too_short():
    """
    Test password too short validation in UserCreate schema.
    """
    with pytest.raises(ValueError):
        UserCreateSchema(username="testuser", password="short")

def test_user_create_schema_password_valid():
    """
    Test valid password validation in UserCreate schema.
    """
    user_data = {
        "username": "testuser",
        "password": "ValidPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_user_create_schema_password_missing_digit():
    """
    Test password missing a digit validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match="Password must contain at least one digit"):
        UserCreateSchema(username="testuser", password="NoDigitPassword")

def test_user_create_schema_password_missing_uppercase():
    """
    Test password missing an uppercase letter validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
        UserCreateSchema(username="testuser", password="nouppercasepassword123")

def test_user_create_schema_password_missing_lowercase():
    """
    Test password missing a lowercase letter validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
        UserCreateSchema(username="testuser", password="NOLOWERCASEPASSWORD123")

def test_user_create_schema_password_valid_complexity():
    """
    Test valid password complexity validation in UserCreate schema.
    """
    user_data = {
        "username": "testuser",
        "password": "ValidPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_user_create_schema_username_too_short():
    """
    Test username too short validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match='Username must be at least 3 characters long'):
        UserCreateSchema(username='ab', password='ValidPassword123!')

def test_user_create_schema_username_too_long():
    """
    Test username too long validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match='Username must not exceed 50 characters'):
        UserCreateSchema(username='a' * 51, password='ValidPassword123!')

def test_user_create_schema_username_invalid_characters():
    """
    Test username with invalid characters validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match='Username must contain only alphanumeric characters'):
        UserCreateSchema(username='invalid_username!', password='ValidPassword123!')

def test_user_create_schema_username_valid():
    """
    Test valid username validation in UserCreate schema.
    """
    user_data = {
        "username": "validuser",
        "password": "ValidPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.username == "validuser"

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_api

## File: test_api_authentication.py
```py
# filename: tests/test_api/test_api_authentication.py

from datetime import timedelta
import pytest
from fastapi import HTTPException
from app.core.jwt import create_access_token
from app.models.authentication import RevokedTokenModel

def test_user_authentication(client, test_user):
    """Test user authentication and token retrieval."""
    # Authenticate the user and retrieve the token
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/login", data=login_data)
    print(response.json())
    assert response.status_code == 200, "Authentication failed."
    token = response.json()["access_token"]

    # Include the token in the headers for the protected route
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/", headers=headers)
    print(response.json())
    assert response.status_code == 200, "Access denied for protected route."

def test_login_user_success(client, test_user):
    """Test successful user login and token retrieval."""
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/login", data=login_data)
    assert response.status_code == 200, "User login failed."
    assert "access_token" in response.json(), "Access token missing in login response."

def test_token_access_with_invalid_credentials(client, db_session):
    """Test token access with invalid credentials."""
    response = client.post("/login", data={"username": "nonexistentuser", "password": "wrongpassword"})
    assert response.status_code == 401, "Token issuance should fail with invalid credentials."

def test_login_wrong_password(client, test_user):
    """
    Test login with incorrect password.
    """
    login_data = {"username": test_user.username, "password": "wrongpassword"}
    response = client.post("/login", data=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_login_and_access_protected_endpoint(client, test_user):
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/login", data=login_data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Access a protected endpoint using the token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200

def test_login_success(client, test_user):
    """
    Test successful user login.
    """
    response = client.post("/login", data={"username": test_user.username, "password": "TestPassword123!"})
    assert response.status_code == 200, "Authentication failed."
    assert "access_token" in response.json(), "Access token missing in response."
    assert response.json()["token_type"] == "bearer", "Incorrect token type."

def test_login_invalid_credentials(client, db_session):
    """
    Test login with invalid credentials.
    """
    response = client.post(
        "/login",
        data={
            "username": "invalid_user",
            "password": "invalid_password"
        }
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_login_inactive_user(client, test_user, db_session):
    """
    Test login with an inactive user.
    """
    # Set the user as inactive
    test_user.is_active = False
    db_session.commit()
    
    response = client.post("/login", data={"username": test_user.username, "password": "TestPassword123!"})
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_login_nonexistent_user(client, db_session):
    """
    Test login with a non-existent username.
    """
    login_data = {
        "username": "nonexistent_user",
        "password": "password123"
    }
    response = client.post("/login", data=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_logout_revoked_token(client, test_user, test_token, db_session):
    # Revoke the token manually
    revoked_token = RevokedTokenModel(token=test_token)
    db_session.add(revoked_token)
    db_session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Token already revoked"

def test_login_logout_flow(client, test_user):
    """
    Test the complete login and logout flow.
    """
    # Login
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    login_response = client.post("/login", data=login_data)
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
    assert exc_info.value.detail == "Could not validate credentials"

def test_access_protected_endpoint_without_token(client):
    with pytest.raises(HTTPException) as exc_info:
        client.get("/users/")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"

def test_access_protected_endpoint_with_invalid_token(client, db_session):
    headers = {"Authorization": "Bearer invalid_token"}
    with pytest.raises(HTTPException) as exc_info:
        response = client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"

def test_logout_success(client, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Successfully logged out"

def test_login_invalid_token_format(client, db_session):
    headers = {"Authorization": "Bearer invalid_token_format"}
    with pytest.raises(HTTPException) as exc_info:
        response = client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"

def test_login_expired_token(client, test_user, db_session):
    expired_token = create_access_token(data={"sub": test_user.username}, expires_delta=timedelta(minutes=-1))
    headers = {"Authorization": f"Bearer {expired_token}"}
    with pytest.raises(HTTPException) as exc_info:
        response = client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert "Token has expired" in exc_info.value.detail

def test_protected_endpoint_expired_token(client, test_user, db_session):
    expired_token = create_access_token(data={"sub": test_user.username}, expires_delta=timedelta(minutes=-1))
    headers = {"Authorization": f"Bearer {expired_token}"}
    with pytest.raises(HTTPException) as exc_info:
        response = client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert "Token has expired" in exc_info.value.detail
```

## File: test_api_filters.py
```py
# filename: tests/test_api_filters.py

import pytest
from app.models.subjects import SubjectModel
from app.models.topics import TopicModel
from app.models.subtopics import SubtopicModel
from app.models.question_tags import QuestionTagModel
from app.models.question_sets import QuestionSetModel
from app.models.questions import QuestionModel
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

    # Check if the topics are correctly associated with their respective subjects
    algebra_topic = db_session.query(TopicModel).filter(TopicModel.name == "Algebra").first()
    assert algebra_topic.subject.name == "Math"

    geometry_topic = db_session.query(TopicModel).filter(TopicModel.name == "Geometry").first()
    assert geometry_topic.subject.name == "Math"

    physics_topic = db_session.query(TopicModel).filter(TopicModel.name == "Physics").first()
    assert physics_topic.subject.name == "Science"

    # Check if the subtopics are correctly associated with their respective topics
    linear_equations_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Linear Equations").first()
    assert linear_equations_subtopic.topic.name == "Algebra"

    quadratic_equations_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Quadratic Equations").first()
    assert quadratic_equations_subtopic.topic.name == "Algebra"

    triangles_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Triangles").first()
    assert triangles_subtopic.topic.name == "Geometry"

    mechanics_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Mechanics").first()
    assert mechanics_subtopic.topic.name == "Physics"

    # Check if the questions are correctly associated with their respective subjects, topics, and subtopics
    questions = db_session.query(QuestionModel).all()
    for question in questions:
        assert question.subject is not None
        assert question.topic is not None
        assert question.subtopic is not None

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

## File: test_api_groups.py
```py
# filename: tests/test_api/test_api_groups.py

from app.services.logging_service import logger


def test_create_group(logged_in_client):
    logger.debug("test_create_group - Creating group data")
    group_data = {"name": "Test API Group", "description": "This is an API test group"}
    logger.debug("test_create_group - Sending POST request to /groups with data: %s", group_data)
    response = logged_in_client.post("/groups", json=group_data)
    logger.debug("test_create_group - Response received: %s", response.text)
    assert response.status_code == 200
    assert response.json()["name"] == "Test API Group"
    assert response.json()["description"] == "This is an API test group"

def test_create_group_with_logged_in_client(logged_in_client):
    logger.info("Running test_create_group_with_logged_in_client")
    logger.debug("Creating group data")
    group_data = {"name": "Test Group with Logged In Client", "description": "This is a test group created with logged_in_client"}
    logger.debug("Sending POST request to /groups with data: %s", group_data)
    response = logged_in_client.post("/groups", json=group_data)
    logger.debug("Response received: %s", response.text)
    logger.debug("Response status code: %s", response.status_code)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    logger.debug("Response data: %s", data)
    assert data["name"] == "Test Group with Logged In Client"
    assert data["description"] == "This is a test group created with logged_in_client"

def test_create_group_with_manual_auth(client, test_user):
    logger.info("Running test_create_group_with_manual_auth")
    logger.debug("Authenticating user")
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    logger.debug("Sending POST request to /login with data: %s", login_data)
    response = client.post("/login", data=login_data)
    logger.debug("Response received: %s", response.text)
    logger.debug("Response status code: %s", response.status_code)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    access_token = response.json()["access_token"]
    logger.debug("Access token retrieved: %s", access_token)

    logger.debug("Creating group data")
    group_data = {"name": "Test Group with Manual Auth", "description": "This is a test group created with manual authentication"}
    headers = {"Authorization": f"Bearer {access_token}"}
    logger.debug("Sending POST request to /groups with data: %s and headers: %s", group_data, headers)
    response = client.post("/groups", json=group_data, headers=headers)
    logger.debug("Response received: %s", response.text)
    logger.debug("Response status code: %s", response.status_code)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    logger.debug("Response data: %s", data)
    assert data["name"] == "Test Group with Manual Auth"
    assert data["description"] == "This is a test group created with manual authentication"

def test_get_group(logged_in_client, test_group):
    response = logged_in_client.get(f"/groups/{test_group.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_group.id
    assert response.json()["name"] == test_group.name

def test_update_group(logged_in_client, test_group):
    update_data = {"name": "Updated Group Name"}
    response = logged_in_client.put(f"/groups/{test_group.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Group Name"

def test_delete_group(logged_in_client, test_group):
    response = logged_in_client.delete(f"/groups/{test_group.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Group deleted successfully"

    # Try deleting the group again
    response = logged_in_client.delete(f"/groups/{test_group.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"

    response = logged_in_client.get(f"/groups/{test_group.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"

def test_create_group_valid_data(logged_in_client, test_user, db_session):
    group_data = {"name": "API Test Group", "description": "This is a test group for testing the API"}
    response = logged_in_client.post("/groups", json=group_data)
    logger.debug("Response received: %s", response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "API Test Group"
    assert response.json()["description"] == "This is a test group for testing the API"

def test_create_group_empty_name(logged_in_client):
    group_data = {"name": "", "description": "This is an API test group"}
    response = logged_in_client.post("/groups", json=group_data)
    logger.debug("Response received: %s", response.json())
    assert response.status_code == 422
    assert "Group name cannot be empty or whitespace" in response.json()["detail"][0]["msg"]

def test_create_group_long_name(logged_in_client, test_user, db_session):
    group_data = {"name": "A" * 101, "description": "This is a test group"}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 422
    assert "Group name cannot exceed 100 characters" in response.json()["detail"][0]["msg"]

def test_create_group_invalid_name(logged_in_client, test_user, db_session):
    group_data = {"name": "Test@Group", "description": "This is a test group"}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 422
    assert "Group name can only contain alphanumeric characters, hyphens, underscores, and spaces" in response.json()["detail"][0]["msg"]

def test_create_group_long_description(logged_in_client, test_user, db_session):
    group_data = {"name": "Test Group", "description": "A" * 501}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 422
    assert "Group description cannot exceed 500 characters" in response.json()["detail"][0]["msg"]

def test_update_group_valid_data(logged_in_client, test_user, test_group, db_session):
    update_data = {"name": "Updated Test Group", "description": "This is an updated test group"}
    response = logged_in_client.put(f"/groups/{test_group.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Test Group"
    assert response.json()["description"] == "This is an updated test group"

def test_update_group_empty_name(logged_in_client, test_user, test_group, db_session):
    update_data = {"name": "", "description": "This is an updated test group"}
    response = logged_in_client.put(f"/groups/{test_group.id}", json=update_data)
    logger.debug("Response received: %s", response.json())
    assert response.status_code == 422
    assert "Group name cannot be empty or whitespace" in response.json()["detail"][0]["msg"]

def test_update_group_long_name(logged_in_client, test_user, test_group, db_session):
    update_data = {"name": "A" * 101, "description": "This is an updated test group"}
    response = logged_in_client.put(f"/groups/{test_group.id}", json=update_data)
    assert response.status_code == 422
    assert "Group name cannot exceed 100 characters" in response.json()["detail"][0]["msg"]

def test_update_group_invalid_name(logged_in_client, test_user, test_group, db_session):
    update_data = {"name": "Updated@Test@Group", "description": "This is an updated test group"}
    response = logged_in_client.put(f"/groups/{test_group.id}", json=update_data)
    assert response.status_code == 422
    assert "Group name can only contain alphanumeric characters, hyphens, underscores, and spaces" in response.json()["detail"][0]["msg"]

def test_update_group_long_description(logged_in_client, test_user, test_group, db_session):
    update_data = {"name": "Updated Test Group", "description": "A" * 501}
    response = logged_in_client.put(f"/groups/{test_group.id}", json=update_data)
    assert response.status_code == 422
    assert "Group description cannot exceed 500 characters" in response.json()["detail"][0]["msg"]

```

## File: test_api_leaderboard.py
```py
# filename: tests/test_api/test_api_leaderboard.py

from app.models.user_responses import UserResponseModel
from app.models.time_period import TimePeriodModel

def test_get_leaderboard_daily(
    logged_in_client,
    db_session,
    test_user_with_group,
    test_questions
):
    # Create user responses
    db_session.add(
        UserResponseModel(
            user_id=test_user_with_group.id,
            question_id=test_questions[0].id,
            answer_choice_id=test_questions[0].answer_choices[0].id,
            is_correct=True
        )
    )
    db_session.add(
        UserResponseModel(
            user_id=test_user_with_group.id,
            question_id=test_questions[1].id,
            answer_choice_id=test_questions[1].answer_choices[0].id,
            is_correct=False
        )
    )
    db_session.commit()

    response = logged_in_client.get("/leaderboard/?time_period=daily")
    print(response.json())
    assert response.status_code == 200
    leaderboard_data = response.json()
    assert len(leaderboard_data) == 1
    assert leaderboard_data[0]["user_id"] == test_user_with_group.id
    assert leaderboard_data[0]["score"] == 1
    assert leaderboard_data[0]["time_period"] == TimePeriodModel.DAILY.value

def test_get_leaderboard_weekly(
    logged_in_client,
    db_session,
    test_user_with_group,
    test_questions
):
    # Create user responses
    db_session.add(
        UserResponseModel(
            user_id=test_user_with_group.id,
            question_id=test_questions[0].id,
            answer_choice_id=test_questions[0].answer_choices[0].id,
            is_correct=True
        )
    )
    db_session.add(
        UserResponseModel(
            user_id=test_user_with_group.id,
            question_id=test_questions[1].id,
            answer_choice_id=test_questions[1].answer_choices[0].id,
            is_correct=False
        )
    )
    db_session.commit()
    
    group_id = test_user_with_group.groups[0].id
    response = logged_in_client.get(f"/leaderboard/?time_period=weekly&group_id={group_id}")
    assert response.status_code == 200
    leaderboard_data = response.json()
    assert len(leaderboard_data) == 1
    assert leaderboard_data[0]["user_id"] == test_user_with_group.id
    assert leaderboard_data[0]["score"] == 1
    assert leaderboard_data[0]["time_period"] == TimePeriodModel.WEEKLY.value
    assert leaderboard_data[0]["group_id"] == group_id

```

## File: test_api_question_sets.py
```py
# filename: tests/test_api_question_sets.py

import json
import tempfile
from app.services.logging_service import logger

def test_create_question_set_endpoint(logged_in_client):
    data = {"name": "Test Question Set", "is_public": True}
    
    response = logged_in_client.post("/question-sets/", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Question Set"
    assert response.json()["is_public"] == True

def test_create_private_question_set(logged_in_client):
    data = {
        "name": "Test Private Set",
        "is_public": False
    }
    response = logged_in_client.post("/question-sets/", json=data)
    print(response.json())
    assert response.status_code == 201
    assert response.json()["is_public"] == False

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

def test_upload_question_set_success(logged_in_client, db_session, test_question):
    # Prepare valid JSON data
    json_data = [
        {
            "text": test_question.text,
            "subject_id": test_question.subject_id,
            "topic_id": test_question.topic_id,
            "subtopic_id": test_question.subtopic_id,
            "difficulty": test_question.difficulty,
            "answer_choices": [
                {
                    "text": choice.text,
                    "is_correct": choice.is_correct,
                    "explanation": choice.explanation
                }
                for choice in test_question.answer_choices
            ]
        }
    ]

    # Create a temporary file with the JSON data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        json.dump(json_data, temp_file)
        temp_file.flush()  # Ensure the contents are written to the file
        response = logged_in_client.post(
            "/upload-questions/",
            data={"question_set_name": "Test Uploaded Question Set"},
            files={"file": ("question_set.json", open(temp_file.name, 'rb'), "application/json")}
        )

    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "Question set uploaded successfully"}

def test_upload_question_set_invalid_json(logged_in_client, db_session):
    # Prepare invalid JSON data
    invalid_json = "{'invalid': 'json'}"

    # Create a temporary file with the invalid JSON data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_file.write(invalid_json)
        temp_file.flush()  # Ensure the contents are written to the file
        response = logged_in_client.post(
            "/upload-questions/",
            data={"question_set_name": "Test Uploaded Question Set with Invalid JSON"},
            files={"file": ("invalid.json", open(temp_file.name, 'rb'), "application/json")})

    print(response.json())
    assert response.status_code == 400
    assert "Invalid JSON data" in response.json()["detail"]

def test_create_question_set_with_existing_name(logged_in_client, test_question_set):
    logger.debug("test_question_set: %s", test_question_set)
    data = {
        "name": test_question_set.name,
        "is_public": test_question_set.is_public,
        "creator_id": test_question_set.creator_id
    }
    response = logged_in_client.post("/question-sets/", json=data)
    logger.debug("response: %s", response.json())
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_retrieve_question_set_with_questions(logged_in_client, test_question_set):
    response = logged_in_client.get(f"/question-sets/{test_question_set.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_question_set.id
    assert response.json()["name"] == test_question_set.name

def test_update_question_set_endpoint(logged_in_client, test_question_set, test_question):
    data = {"name": "Updated Question Set", "question_ids": [test_question.id]}
    logger.debug("data: %s", data)
    response = logged_in_client.put(f"/question-sets/{test_question_set.id}", json=data)
    logger.debug("response: %s", response.json())
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

def test_delete_question_set_not_found(logged_in_client):
    question_set_id = 999
    response = logged_in_client.delete(f"/question-sets/{question_set_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question set with ID {question_set_id} not found."

def test_update_question_set_with_multiple_questions(logged_in_client, db_session, test_question_set, test_questions):
    test_question_1 = test_questions[0]
    test_question_2 = test_questions[1]
    data = {"name": "Updated Question Set", "question_ids": [test_question_1.id, test_question_2.id]}
    response = logged_in_client.put(f"/question-sets/{test_question_set.id}", json=data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Question Set"
    assert test_question_1.id in response.json()["question_ids"]
    assert test_question_2.id in response.json()["question_ids"]

def test_update_question_set_remove_questions(logged_in_client, db_session, test_question_set, test_question):
    data = {"name": "Updated Question Set", "question_ids": []}
    response = logged_in_client.put(f"/question-sets/{test_question_set.id}", json=data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Question Set"
    assert len(response.json()["question_ids"]) == 0

def test_update_question_set_invalid_question_ids(logged_in_client, db_session, test_question_set):
    data = {"name": "Updated Question Set", "question_ids": [999]}  # Assuming question with ID 999 doesn't exist
    response = logged_in_client.put(f"/question-sets/{test_question_set.id}", json=data)
    assert response.status_code == 400
    assert "Invalid question_id" in response.json()["detail"]

```

## File: test_api_questions.py
```py
# filename: tests/test_api_questions.py

import pytest
from fastapi import HTTPException

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
    with pytest.raises(HTTPException) as exc_info:
        response = client.get("/questions/")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"

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

## File: test_api_register.py
```py
# filename: tests/test_api/test_api_register.py

from app.services.logging_service import logger


def test_register_user_success(client, db_session, test_role):
    user_data = {
        "username": "new_user",
        "password": "NewPassword123!",
        "email": "new_user@example.com",
        "role": test_role.name
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201, "User registration failed"

def test_register_user_invalid_password(client):
    """Test registration with an invalid password."""
    user_data = {
        "username": "newuser",
        "password": "weak",
        "email": "newuser@example.com"
    }
    response = client.post("/register", json=user_data)
    logger.debug(response.json())
    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in response.json()["detail"][0]["msg"]

def test_register_user_missing_digit_in_password(client):
    """Test registration with a password missing a digit."""
    user_data = {"username": "newuser", "password": "NoDigitPassword"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one digit" in str(response.content)

def test_register_user_missing_uppercase_in_password(client):
    """Test registration with a password missing an uppercase letter."""
    user_data = {"username": "newuser", "password": "nouppercasepassword123"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one uppercase letter" in str(response.content)

def test_register_user_missing_lowercase_in_password(client):
    """Test registration with a password missing a lowercase letter."""
    user_data = {"username": "newuser", "password": "NOLOWERCASEPASSWORD123"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one lowercase letter" in str(response.content)

def test_register_user_duplicate(client, test_user):
    """
    Test registration with a username that already exists.
    """
    user_data = {
        "username": test_user.username,
        "password": "DuplicatePass123!",
        "email": test_user.email,
        "role": test_user.role
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "already registered" in str(response.content)

def test_registration_user_exists(client, test_user):
    response = client.post(
        "/register",
        json={
            "username": test_user.username,
            "password": "anotherpassword",
            "email": test_user.email
        }
    )
    assert response.status_code == 422, "Registration should fail for existing username."
```

## File: test_api_subjects.py
```py
# filename: tests/test_api_subjects.py

from app.schemas.subjects import SubjectCreateSchema


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

from app.schemas.topics import TopicCreateSchema


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

from datetime import datetime, timezone
from app.services.logging_service import logger, sqlalchemy_obj_to_dict


def test_create_user_response_invalid_user(logged_in_client, test_questions):
    invalid_data = {
        "user_id": 999,  # Assuming this user ID does not exist
        "question_id": test_questions[0].id,
        "answer_choice_id": test_questions[0].answer_choices[0].id
    }
    response = logged_in_client.post("/user-responses/", json=invalid_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 400

    # Extract the details from the error response
    detail = response.json()["detail"]

    # Check the error messages
    assert "Invalid user_id" in detail

def test_create_user_response_invalid_question(logged_in_client, test_user_with_group, test_questions):
    invalid_data = {
        "user_id": test_user_with_group.id,
        "question_id": 999,  # Assuming this question ID does not exist
        "answer_choice_id": test_questions[0].answer_choices[0].id
    }
    response = logged_in_client.post("/user-responses/", json=invalid_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 400

    # Extract the details from the error response
    detail = response.json()["detail"]

    # Check the error messages
    assert "Invalid question_id" in detail
    
def test_create_user_response_invalid_answer(logged_in_client, test_user_with_group, test_questions):
    invalid_data = {
        "user_id": test_user_with_group.id,
        "question_id": test_questions[0].id,
        "answer_choice_id": 999  # Assuming this answer choice ID does not exist
    }
    response = logged_in_client.post("/user-responses/", json=invalid_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 400

    # Extract the details from the error response
    detail = response.json()["detail"]

    # Check the error messages
    assert "Invalid answer_choice_id" in detail

def test_update_user_response(logged_in_client, test_user, test_questions):
    logger.debug("test_questions 1: %s", sqlalchemy_obj_to_dict(test_questions[0]))
    response_data = {
        "user_id": test_user.id,
        "question_id": test_questions[0].id,
        "answer_choice_id": test_questions[0].answer_choices[0].id
    }
    created_response = logged_in_client.post(
        "/user-responses/", json=response_data).json()
    update_data = {
        "is_correct": True,
        "user_id": test_user.id,
        "question_id": test_questions[0].id,
    }
    response = logged_in_client.put(
        f"/user-responses/{created_response['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["is_correct"] is True

def test_delete_user_response(logged_in_client, test_user_with_group, test_questions):
    response_data = {
        "user_id": test_user_with_group.id,
        "question_id": test_questions[0].id,
        "answer_choice_id": test_questions[0].answer_choices[0].id
    }
    created_response = logged_in_client.post(
        "/user-responses/", json=response_data).json()
    response = logged_in_client.delete(
        f"/user-responses/{created_response['id']}")
    assert response.status_code == 204
    response = logged_in_client.get(
        f"/user-responses/{created_response['id']}")
    assert response.status_code == 404

def test_create_user_response_missing_data(logged_in_client, test_user, test_questions):
    invalid_data = {
        "user_id": test_user.id,
        "question_id": test_questions[0].id
        # Missing answer_choice_id
    }
    logger.debug("Running POST request to /user-responses/ with missing data")
    response = logged_in_client.post("/user-responses/", json=invalid_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 400

    # Extract the details from the error response
    detail = response.json()["detail"]

    # Check the error messages
    assert "Field required" in detail
    assert "answer_choice_id" in detail

def test_get_user_responses_with_filters(logged_in_client, test_user, test_questions):
    response_data_1 = {
        "user_id": test_user.id,
        "question_id": test_questions[0].id,
        "answer_choice_id": test_questions[0].answer_choices[0].id,
        "is_correct": True
    }
    response_data_2 = {
        "user_id": test_user.id,
        "question_id": test_questions[0].id,
        "answer_choice_id": test_questions[0].answer_choices[1].id,
        "is_correct": False
    }
    logged_in_client.post("/user-responses/", json=response_data_1)
    logged_in_client.post("/user-responses/", json=response_data_2)

    response = logged_in_client.get(f"/user-responses/?user_id={test_user.id}")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = logged_in_client.get(
        f"/user-responses/?question_id={test_questions[0].id}")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_user_responses_with_pagination(logged_in_client, test_user, test_questions):
    response_data_1 = {
        "user_id": test_user.id,
        "question_id": test_questions[0].id,
        "answer_choice_id": test_questions[0].answer_choices[0].id,
        "is_correct": True
    }
    response_data_2 = {
        "user_id": test_user.id,
        "question_id": test_questions[1].id,
        "answer_choice_id": test_questions[1].answer_choices[0].id,
        "is_correct": False
    }
    logged_in_client.post("/user-responses/", json=response_data_1)
    logged_in_client.post("/user-responses/", json=response_data_2)

    response = logged_in_client.get("/user-responses/?skip=0&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert isinstance(response.json()[0]['timestamp'], str)

def test_create_and_retrieve_user_response(logged_in_client, test_user, test_questions):
    response_data = {
        "user_id": test_user.id,
        "question_id": test_questions[0].id,
        "answer_choice_id": test_questions[0].answer_choices[0].id
    }
    response = logged_in_client.post("/user-responses/", json=response_data)
    assert response.status_code == 201
    created_response = response.json()
    assert created_response["user_id"] == test_user.id
    assert created_response["question_id"] == test_questions[0].id
    assert created_response["answer_choice_id"] == test_questions[0].answer_choices[0].id

    retrieve_response = logged_in_client.get(f"/user-responses/{created_response['id']}")
    assert retrieve_response.status_code == 200
    retrieved_response = retrieve_response.json()
    assert retrieved_response["id"] == created_response["id"]
    assert retrieved_response["user_id"] == test_user.id
    assert retrieved_response["question_id"] == test_questions[0].id
    assert retrieved_response["answer_choice_id"] == test_questions[0].answer_choices[0].id

def test_update_nonexistent_user_response(logged_in_client, test_user_with_group, test_questions):
    update_data = {
        "is_correct": True,
        "user_id": test_user_with_group.id,
        "question_id": test_questions[0].id,    
    }
    response = logged_in_client.put("/user-responses/999", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_delete_nonexistent_user_response(logged_in_client):
    response = logged_in_client.delete("/user-responses/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

```

## File: test_api_users.py
```py
# filename: tests/test_api_users.py

from app.services.logging_service import logger


def test_create_user(logged_in_client, random_username):
    username = random_username + "_test_create_user"
    logger.debug("Creating user with username: %s", username)
    data = {
        "username": username,
        "password": "TestPassword123!",
        "email": f"{username}@example.com"
    }
    logger.debug("Creating user with data: %s", data)
    response = logged_in_client.post("/users/", json=data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 201

def test_read_users(logged_in_client, test_user_with_group):
    response = logged_in_client.get("/users/")
    assert response.status_code == 200
    assert test_user_with_group.username in [user["username"] for user in response.json()]

def test_read_user_me(logged_in_client, test_user_with_group):
    response = logged_in_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == test_user_with_group.username

def test_update_user_me(logged_in_client, db_session):
    update_data = {
        "username": "new_username",
        "email": "new_email@example.com"
    }
    response = logged_in_client.put("/users/me", json=update_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 200

    # Extract the details from the response
    data = response.json()

    # Check the updated data
    assert data["username"] == "new_username"
    assert data["email"] == "new_email@example.com"

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_services

## File: test_authorization_service.py
```py
# filename: tests/test_services/test_authorization_service.py

from app.services.authorization_service import get_user_permissions
from app.models.roles import RoleModel
from app.models.permissions import PermissionModel
from app.models.users import UserModel


def test_get_user_permissions(db_session):
    # Create a role and permissions
    role = RoleModel(name='Test Role', description='Test role description')
    permission1 = PermissionModel(name='Test Permission 1', description='Test permission 1 description')
    permission2 = PermissionModel(name='Test Permission 2', description='Test permission 2 description')
    role.permissions.extend([permission1, permission2])

    db_session.add(role)
    db_session.commit()

    # Create a user with the test role
    user = UserModel(username='testuser', email='testuser@example.com', role='Test Role')
    db_session.add(user)
    db_session.commit()

    # Retrieve the user's permissions
    permissions = get_user_permissions(db_session, user)
    assert len(permissions) == 2
    assert 'Test Permission 1' in permissions
    assert 'Test Permission 2' in permissions
```

## File: test_randomization_service.py
```py
# filename: tests/test_utils/test_randomization.py

from app.services.randomization_service import randomize_questions, randomize_answer_choices
from app.models.questions import QuestionModel
from app.models.answer_choices import AnswerChoiceModel


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

## File: test_scoring_service.py
```py
# filename: tests/test_scoring_service.py

from app.services.scoring_service import calculate_user_score, calculate_leaderboard_scores
from app.models.user_responses import UserResponseModel
from app.models.time_period import TimePeriodModel


def test_calculate_user_score(
    db_session,
    test_user,
    test_question,
    test_answer_choice_1,
    test_answer_choice_2
):
    # Create user responses
    db_session.add(
        UserResponseModel(
            user_id=test_user.id,
            question_id=test_question.id,
            answer_choice_id=test_answer_choice_1.id,
            is_correct=True
        )
    )
    db_session.add(
        UserResponseModel(
            user_id=test_user.id,
            question_id=test_question.id,
            answer_choice_id=test_answer_choice_2.id,
            is_correct=False
        )
    )
    db_session.commit()

    user_score = calculate_user_score(test_user.id, db_session)
    assert user_score == 1

def test_calculate_leaderboard_scores(
    db_session,
    test_user,
    test_question,
    test_answer_choice_1,
    test_answer_choice_2
):
    # Create user responses
    db_session.add(
        UserResponseModel(
            user_id=test_user.id,
            question_id=test_question.id,
            answer_choice_id=test_answer_choice_1.id,
            is_correct=True
        )
    )
    db_session.add(
        UserResponseModel(
            user_id=test_user.id,
            question_id=test_question.id,
            answer_choice_id=test_answer_choice_2.id,
            is_correct=False
        )
    )
    db_session.commit()

    leaderboard_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.DAILY)
    assert leaderboard_scores == {test_user.id: 1}

    leaderboard_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.WEEKLY)
    assert leaderboard_scores == {test_user.id: 1}

    leaderboard_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.MONTHLY)
    assert leaderboard_scores == {test_user.id: 1}

    leaderboard_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.YEARLY)
    assert leaderboard_scores == {test_user.id: 1}

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_db

## File: test_db_session.py
```py
# filename: tests/test_db_session.py

from sqlalchemy import inspect

def test_revoked_tokens_table_exists(db_session):
    inspector = inspect(db_session.bind)
    available_tables = inspector.get_table_names()
    assert "revoked_tokens" in available_tables, "Table 'revoked_tokens' does not exist in the test database."


def test_database_session_lifecycle(db_session):
    """Test the lifecycle of a database session."""
    # Assuming 'db_session' is already using the correct test database ('test.db') as configured in conftest.py
    assert db_session.bind.url.__to_string__() == "sqlite:///./test.db", "Not using the test database"

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_crud

## File: test_crud_associations.py
```py
# filename: tests/test_crud/test_crud_associations.py

from app.crud.crud_question_tag_associations import add_tag_to_question, get_question_tags, get_questions_by_tag
from app.crud.crud_role_permission_associations import add_permission_to_role, get_role_permissions, get_roles_by_permission


def test_question_tag_association(db_session, test_question, test_tag):
    add_tag_to_question(db_session, test_question.id, test_tag.id)
    
    question_tags = get_question_tags(db_session, test_question.id)
    assert len(question_tags) == 1
    assert question_tags[0].id == test_tag.id

    questions_with_tag = get_questions_by_tag(db_session, test_tag.id)
    assert len(questions_with_tag) == 1
    assert questions_with_tag[0].id == test_question.id

def test_role_permission_association(db_session, test_role, test_permission):
    initial_role_permissions = get_role_permissions(db_session, test_role.id)
    initial_count = len(initial_role_permissions)

    add_permission_to_role(db_session, test_role.id, test_permission.id)
    
    role_permissions = get_role_permissions(db_session, test_role.id)
    assert len(role_permissions) == initial_count + 1
    assert test_permission in role_permissions

```

## File: test_crud_filters.py
```py
# filename: tests/test_crud_filters.py

import pytest
from pydantic import ValidationError
from app.crud.crud_filters import filter_questions_crud


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
    with pytest.raises(ValidationError) as excinfo:
        result = filter_questions_crud(db=db_session, filters=filters)
    assert "Invalid difficulty. Must be one of: Beginner, Easy, Medium, Hard, Expert" in str(excinfo.value)

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
from app.crud.crud_question_sets import create_question_set_crud, delete_question_set_crud, update_question_set_crud
from app.crud.crud_subjects import create_subject_crud
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.question_sets import QuestionSetCreateSchema, QuestionSetUpdateSchema


def test_create_question_set_crud(db_session, test_user, test_question, test_group):
    question_set_data = QuestionSetCreateSchema(
        db=db_session,
        name="test_create_question_set_crud Question Set",
        is_public=True,
        creator_id=test_user.id,
        question_ids=[test_question.id],
        group_ids=[test_group.id]
    )
    question_set = create_question_set_crud(db=db_session, question_set=question_set_data)

    assert question_set.name == "test_create_question_set_crud Question Set"
    assert question_set.is_public == True
    assert question_set.creator_id == test_user.id
    assert len(question_set.questions) == 1
    assert question_set.questions[0].id == test_question.id
    assert len(question_set.groups) == 1
    assert question_set.groups[0].id == test_group.id

def test_create_question_set_duplicate_name(db_session, test_user):
    question_set_data = QuestionSetCreateSchema(
        db=db_session,
        name="Duplicate Test Set",
        is_public=True,
        creator_id=test_user.id
    )
    create_question_set_crud(db=db_session, question_set=question_set_data)
    
    with pytest.raises(HTTPException) as exc_info:
        create_question_set_crud(db=db_session, question_set=question_set_data)
    
    assert exc_info.value.status_code == 400
    assert "already exists" in str(exc_info.value.detail)

def test_update_question_set_crud(db_session, test_question_set, test_question, test_group):
    update_data = QuestionSetUpdateSchema(
        db = db_session,
        name="Updated Question Set",
        is_public=False,
        question_ids=[test_question.id],
        group_ids=[test_group.id]
    )
    updated_question_set = update_question_set_crud(db_session, test_question_set.id, update_data)

    assert updated_question_set.name == "Updated Question Set"
    assert updated_question_set.is_public == False
    assert len(updated_question_set.questions) == 1
    assert updated_question_set.questions[0].id == test_question.id
    assert len(updated_question_set.groups) == 1
    assert updated_question_set.groups[0].id == test_group.id

def test_update_question_set_not_found(db_session):
    update_data = QuestionSetUpdateSchema(name="Updated Name")
    with pytest.raises(HTTPException) as exc_info:
        update_question_set_crud(db_session, 999, update_data)
    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail)

def test_delete_question_set(db_session, test_question_set_data, test_user):
    test_question_set_data.name = "Unique Question Set for Deletion"
    question_set_data = QuestionSetCreateSchema(**test_question_set_data.dict())
    question_set = create_question_set_crud(
        db=db_session,
        question_set=question_set_data
    )
    assert delete_question_set_crud(db=db_session, question_set_id=question_set.id) is True, "Question set deletion failed."

def test_delete_question_set_not_found(db_session):
    question_set_id = 999  # Assuming this ID does not exist
    with pytest.raises(HTTPException) as exc_info:
        delete_question_set_crud(db=db_session, question_set_id=question_set_id)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)


```

## File: test_crud_questions.py
```py
# filename: tests/test_crud_questions.py

from app.schemas.questions import QuestionCreateSchema, QuestionUpdateSchema, AnswerChoiceCreateSchema
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.topics import TopicCreateSchema
from app.crud.crud_questions import create_question_crud, read_question_crud, update_question_crud, delete_question_crud
from app.crud.crud_topics import create_topic_crud
from app.crud.crud_subjects import create_subject_crud


def test_create_and_retrieve_question(db_session, test_question_set, test_subtopic, test_topic, test_subject):
    """Test creation and retrieval of a question with answer choices."""
    answer_choice_1 = AnswerChoiceCreateSchema(text="Test Answer 1", is_correct=True, explanation="Answer 1 is correct.")
    answer_choice_2 = AnswerChoiceCreateSchema(text="Test Answer 2", is_correct=False, explanation="Answer 2 is incorrect.")
    question_data = QuestionCreateSchema(
        db=db_session,
        text="Sample Question?",
        subject_id=test_subject.id,
        topic_id=test_topic.id,
        subtopic_id=test_subtopic.id,
        difficulty="Easy",
        answer_choices=[answer_choice_1, answer_choice_2],
        question_set_ids=[test_question_set.id]
    )
    created_question = create_question_crud(db=db_session, question=question_data)
    
    assert created_question is not None, "Failed to create question."
    assert created_question.text == "Sample Question?", "Question text does not match."
    assert created_question.difficulty == "Easy", "Question difficulty level does not match."
    assert len(created_question.answer_choices) == 2, "Answer choices not created correctly."
    assert any(choice.text == "Test Answer 1" and choice.explanation == "Answer 1 is correct." for choice in created_question.answer_choices)
    assert any(choice.text == "Test Answer 2" and choice.explanation == "Answer 2 is incorrect." for choice in created_question.answer_choices)
    assert test_question_set.id in created_question.question_set_ids, "Question not associated with the question set."

def test_get_nonexistent_question(db_session):
    """Test retrieval of a non-existent question."""
    question = read_question_crud(db_session, question_id=999)
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
    """Test updating a question, including its answer choices."""
    question_update = QuestionUpdateSchema(
        text="Updated Question",
        difficulty="Medium",
        answer_choices=[
            {"text": "Updated Answer 1", "is_correct": True, "explanation": "Updated Answer 1 is correct."},
            {"text": "Updated Answer 2", "is_correct": False, "explanation": "Updated Answer 2 is incorrect."},
            {"text": "New Answer 3", "is_correct": False, "explanation": "New Answer 3 is incorrect."}
        ],
        question_set_ids=[test_question_set.id]
    )
    updated_question = update_question_crud(db_session, test_question.id, question_update)

    assert updated_question is not None, "Failed to update question."
    assert updated_question.text == "Updated Question", "Question text not updated correctly."
    assert updated_question.difficulty == "Medium", "Question difficulty not updated correctly."
    assert len(updated_question.answer_choices) == 3, "Answer choices not updated correctly."
    assert any(choice.text == "Updated Answer 1" and choice.explanation == "Updated Answer 1 is correct." for choice in updated_question.answer_choices)
    assert any(choice.text == "Updated Answer 2" and choice.explanation == "Updated Answer 2 is incorrect." for choice in updated_question.answer_choices)
    assert any(choice.text == "New Answer 3" and choice.explanation == "New Answer 3 is incorrect." for choice in updated_question.answer_choices)
    assert test_question_set.id in updated_question.question_set_ids, "Question not associated with the question set after update."

```

## File: test_crud_roles.py
```py
# filename: tests/test_crud/test_crud_roles.py

import pytest
from fastapi import HTTPException
from app.crud.crud_roles import create_role_crud, read_role_crud, read_roles_crud, update_role_crud, delete_role_crud
from app.schemas.roles import RoleCreateSchema, RoleUpdateSchema
from app.services.logging_service import logger
from app.crud.crud_permissions import read_permissions_crud


def test_create_role_crud(db_session, test_permissions):
    read_permissions = read_permissions_crud(db_session, limit=2)  # Retrieve the first two permissions from the database
    logger.debug("Permissions read: %s", read_permissions)
    permissions_id_list = [p.id for p in read_permissions]
    logger.debug("Permissions list: %s", permissions_id_list)
    permissions_name_list = [p.name for p in read_permissions]
    logger.debug("Permissions name list: %s", permissions_name_list)
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=permissions_name_list)
    logger.debug("Role data: %s", role_data)
    role = create_role_crud(db_session, role_data)
    logger.debug("Role created: %s", role)
    assert role.name == "Test Role"
    assert role.description == "Test role description"
    logger.debug("Role permissions: %s", role.permissions)
    assert len(role.permissions) == 2

def test_read_role_crud(db_session):
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=[])
    created_role = create_role_crud(db_session, role_data)
    
    read_role = read_role_crud(db_session, created_role.id)
    assert read_role.id == created_role.id
    assert read_role.name == "Test Role"

def test_read_role_crud_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        read_role_crud(db_session, 999)  # Assuming 999 is not a valid role id
    assert exc_info.value.status_code == 404

def test_read_roles_crud(db_session):
    role_data1 = RoleCreateSchema(name="Test Role 1", description="Test role description 1", permissions=[])
    role_data2 = RoleCreateSchema(name="Test Role 2", description="Test role description 2", permissions=[])
    create_role_crud(db_session, role_data1)
    create_role_crud(db_session, role_data2)

    roles = read_roles_crud(db_session)
    assert len(roles) >= 2

def test_update_role_crud(db_session, test_permissions):
    permissions = read_permissions_crud(db_session, limit=2)  # Retrieve the first two permissions from the database
    logger.debug("Permissions read: %s", permissions)
    permissions_id_list = [p.id for p in permissions]
    logger.debug("Permissions list: %s", permissions_id_list)
    permissions_name_list = [p.name for p in permissions]
    logger.debug("Permissions name list: %s", permissions_name_list)
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=permissions_name_list)
    logger.debug("Role data: %s", role_data)
    created_role = create_role_crud(db_session, role_data)
    logger.debug("Created role: %s", created_role)
    logger.debug("Created role permissions: %s", created_role.permissions)

    db_session.rollback()  # Roll back the previous transaction

    update_data = RoleUpdateSchema(name="Updated Role", description="Updated description", permissions=permissions_name_list)
    logger.debug("Update data: %s", update_data)
    updated_role = update_role_crud(db_session, created_role.id, update_data)
    logger.debug("Updated role: %s", updated_role)
    logger.debug("Updated role permissions: %s", updated_role.permissions)

    assert updated_role.name == "Updated Role"
    assert updated_role.description == "Updated description"
    assert len(updated_role.permissions) == 2

def test_delete_role_crud(db_session):
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=[])
    created_role = create_role_crud(db_session, role_data)

    assert delete_role_crud(db_session, created_role.id) == True

    with pytest.raises(HTTPException) as exc_info:
        read_role_crud(db_session, created_role.id)
    assert exc_info.value.status_code == 404

```

## File: test_crud_subjects.py
```py
# filename: tests/test_crud_subjects.py

from app.schemas.subjects import SubjectCreateSchema
from app.crud.crud_subjects import create_subject_crud


def test_create_subject(db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    created_subject = create_subject_crud(db=db_session, subject=subject_data)
    assert created_subject.name == "Test Subject"

```

## File: test_crud_user.py
```py
# filename: tests/test_crud_user.py

from app.crud.crud_user import delete_user_crud, create_user_crud, update_user_crud
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.services.authentication_service import authenticate_user

def test_remove_user_not_found(db_session):
    user_id = 999  # Assuming this ID does not exist
    removed_user = delete_user_crud(db_session, user_id)
    assert removed_user is None

def test_authenticate_user(db_session, random_username, test_role):
    user_data = UserCreateSchema(
        username=random_username,
        password="AuthPassword123!",
        email=f"{random_username}@example.com",
        role=test_role.name
    )
    create_user_crud(db_session, user_data)
    authenticated_user = authenticate_user(db_session, username=random_username, password="AuthPassword123!")
    assert authenticated_user
    assert authenticated_user.username == random_username

def test_create_user(db_session, random_username, test_role):
    user_data = UserCreateSchema(
        username=random_username,
        password="NewPassword123!",
        email=f"{random_username}@example.com",
        role=test_role.name
    )
    created_user = create_user_crud(db_session, user_data)
    assert created_user.username == random_username

def test_update_user(db_session, test_user):
    updated_data = UserUpdateSchema(
        db = db_session,
        username="updated_username"
    )
    updated_user = update_user_crud(db=db_session, user_id=test_user.id, updated_user=updated_data)
    assert updated_user.username == "updated_username"

```

## File: test_crud_user_responses.py
```py
# filename: tests/test_crud/test_crud_user_responses.py

from datetime import datetime, timezone
from app.schemas.user_responses import UserResponseCreateSchema, UserResponseUpdateSchema
from app.crud.crud_user_responses import create_user_response_crud, update_user_response_crud, delete_user_response_crud
from app.models.user_responses import UserResponseModel
from app.services.logging_service import logger, sqlalchemy_obj_to_dict

def test_create_and_retrieve_user_response(db_session, test_user_with_group, test_questions):
    response_data = UserResponseCreateSchema(
        db=db_session,
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[0].id
    )
    created_response = create_user_response_crud(db=db_session, user_response=response_data)
    assert created_response is not None, "Failed to create user response."
    assert created_response.user_id == test_user_with_group.id
    assert created_response.question_id == test_questions[0].id
    assert created_response.answer_choice_id == test_questions[0].answer_choices[0].id
    assert created_response.timestamp is not None

def test_update_user_response(db_session, test_user_with_group, test_questions):
    response_data = UserResponseCreateSchema(
        db=db_session,
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[0].id
    )
    created_response = create_user_response_crud(db=db_session, user_response=response_data)
    logger.debug("Created response: %s", sqlalchemy_obj_to_dict(created_response))
    
    update_data = UserResponseUpdateSchema(
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[1].id
    )
    logger.debug("Update data: %s", update_data.model_dump())
    updated_response = update_user_response_crud(db=db_session, user_response_id=created_response.id, user_response=update_data)
    logger.debug("Updated response: %s", sqlalchemy_obj_to_dict(updated_response))
    assert updated_response.answer_choice_id == test_questions[0].answer_choices[1].id
    assert updated_response.timestamp is not None

def test_delete_user_response(db_session, test_user_with_group, test_questions):
    response_data = UserResponseCreateSchema(
        db=db_session,
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[0].id
    )
    created_response = create_user_response_crud(db=db_session, user_response=response_data)
    delete_user_response_crud(db=db_session, user_response_id=created_response.id)
    deleted_response = db_session.query(UserResponseModel).filter(UserResponseModel.id == created_response.id).first()
    assert deleted_response is None

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_models

## File: test_models.py
```py
# filename: tests/test_models.py

import pytest
from sqlalchemy.exc import SQLAlchemyError
from app.models.users import UserModel
from app.models.subjects import SubjectModel
from app.models.questions import QuestionModel
from app.models.answer_choices import AnswerChoiceModel
from app.models.roles import RoleModel
from app.models.permissions import PermissionModel
from app.services.logging_service import logger, sqlalchemy_obj_to_dict
from app.services.validation_service import validate_foreign_keys


def test_role_permission_relationship(db_session):
    try:
        # Create a role and permissions
        role = RoleModel(name='Test Role', description='Test role description')
        permission1 = PermissionModel(name='Test Permission 1', description='Test permission 1 description')
        permission2 = PermissionModel(name='Test Permission 2', description='Test permission 2 description')
        
        logger.debug(f"Created role: {role}")
        logger.debug(f"Created permission1: {permission1}")
        logger.debug(f"Created permission2: {permission2}")

        role.permissions.extend([permission1, permission2])
        logger.debug(f"Role permissions after extend: {role.permissions}")

        db_session.add(role)
        db_session.add(permission1)
        db_session.add(permission2)
        db_session.flush()  # This will assign IDs without committing the transaction

        logger.debug(f"Role after flush: {role}")
        logger.debug(f"Permission1 after flush: {permission1}")
        logger.debug(f"Permission2 after flush: {permission2}")

        # Retrieve the role and check its permissions
        retrieved_role = db_session.query(RoleModel).filter(RoleModel.name == 'Test Role').first()
        logger.debug(f"Retrieved role: {retrieved_role}")
        
        assert retrieved_role is not None, "Role not found in database"
        assert len(retrieved_role.permissions) == 2, f"Expected 2 permissions, found {len(retrieved_role.permissions)}"
        assert permission1 in retrieved_role.permissions, "Permission 1 not found in role's permissions"
        assert permission2 in retrieved_role.permissions, "Permission 2 not found in role's permissions"

        # Refresh the permissions to ensure they have the latest data
        db_session.refresh(permission1)
        db_session.refresh(permission2)

        logger.debug(f"Permission1 roles: {permission1.roles}")
        logger.debug(f"Permission2 roles: {permission2.roles}")

        # Check the reverse relationship
        assert role in permission1.roles, "Role not found in permission1's roles"
        assert role in permission2.roles, "Role not found in permission2's roles"

        db_session.commit()

    except SQLAlchemyError as e:
        logger.exception(f"SQLAlchemy error occurred: {str(e)}")
        pytest.fail(f"SQLAlchemy error occurred: {str(e)}")
    except AssertionError as e:
        logger.exception(f"Assertion failed: {str(e)}")
        pytest.fail(f"Assertion failed: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {str(e)}")
        pytest.fail(f"Unexpected error occurred: {str(e)}")

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

def test_question_model_with_answers(db_session, test_subject, test_topic, test_subtopic):
    question = QuestionModel(text="What is the capital of France?", difficulty="Easy", 
                             subject=test_subject, topic=test_topic, subtopic=test_subtopic)
    logger.debug("Created question: %s", sqlalchemy_obj_to_dict(question))
    logger.debug("Question subject: %s", sqlalchemy_obj_to_dict(question.subject))
    logger.debug("Question topic: %s", sqlalchemy_obj_to_dict(question.topic))
    logger.debug("Question subtopic: %s", sqlalchemy_obj_to_dict(question.subtopic))
    
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    logger.debug("Added and refreshed the question: %s", sqlalchemy_obj_to_dict(question))
    
    answer = AnswerChoiceModel(text="Paris", is_correct=True, explanation="Paris is the capital and largest city of France.", question=question)
    
    db_session.add(answer)
    db_session.commit()
    db_session.refresh(answer)
    logger.debug("Added and refreshed answer: %s", sqlalchemy_obj_to_dict(answer))
    
    validate_foreign_keys(QuestionModel, db_session.connection(), question)
    validate_foreign_keys(AnswerChoiceModel, db_session.connection(), answer)
    logger.debug("Validated foreign keys")
    
    assert question.id is not None
    assert answer.id is not None
    assert answer.question == question
    logger.debug("Assertions passed")

def test_question_model_deletion_cascades_to_answers(db_session, test_subject, test_topic, test_subtopic):
    question = QuestionModel(text="What is the capital of France?", difficulty="Easy", 
                             subject=test_subject, topic=test_topic, subtopic=test_subtopic)
    logger.debug("Created question: %s", sqlalchemy_obj_to_dict(question))
    logger.debug("Question subject: %s", sqlalchemy_obj_to_dict(question.subject))
    logger.debug("Question topic: %s", sqlalchemy_obj_to_dict(question.topic))
    logger.debug("Question subtopic: %s", sqlalchemy_obj_to_dict(question.subtopic))
    
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    logger.debug("Added and refreshed the question: %s", sqlalchemy_obj_to_dict(question))
    
    answer = AnswerChoiceModel(text="Paris", is_correct=True, explanation="Paris is the capital and largest city of France.", question=question)
    
    db_session.add(answer)
    db_session.commit()
    db_session.refresh(answer)
    logger.debug("Added and refreshed answer: %s", sqlalchemy_obj_to_dict(answer))
    
    validate_foreign_keys(QuestionModel, db_session.connection(), question)
    validate_foreign_keys(AnswerChoiceModel, db_session.connection(), answer)
    logger.debug("Validated foreign keys")
    
    db_session.delete(question)
    logger.debug("Deleted question: %s", question)
    
    db_session.commit()
    logger.debug("Committed the session after deleting the question")
    
    assert db_session.query(AnswerChoiceModel).filter_by(question_id=question.id).first() is None
    logger.debug("Assertion passed: Answer choice is deleted along with the question")

```

# Directory: /code/quiz-app/quiz-app-backend/tests/test_core

## File: test_core_auth.py
```py
# filename: tests/test_core_auth.py

from app.services.user_service import oauth2_scheme


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
from app.core.jwt import create_access_token, verify_token


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

def test_jwt_token_creation_and_verification(test_data):
    """
    Test the JWT token creation and verification process.
    """
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

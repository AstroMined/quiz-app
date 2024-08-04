
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

from app.api.endpoints import answer_choices as answer_choices_router
from app.api.endpoints import authentication as authentication_router
from app.api.endpoints import filters as filters_router
from app.api.endpoints import groups as groups_router
from app.api.endpoints import leaderboard as leaderboard_router
from app.api.endpoints import question_sets as question_sets_router
from app.api.endpoints import questions as questions_router
from app.api.endpoints import register as register_router
from app.api.endpoints import domains as domains_router
from app.api.endpoints import disciplines as disciplines_router
from app.api.endpoints import concepts as concepts_router
from app.api.endpoints import subjects as subjects_router
from app.api.endpoints import topics as topics_router
from app.api.endpoints import subtopics as subtopics_router
from app.api.endpoints import user_responses as user_responses_router
from app.api.endpoints import users as users_router
from app.middleware.authorization_middleware import AuthorizationMiddleware
from app.middleware.blacklist_middleware import BlacklistMiddleware
from app.middleware.cors_middleware import add_cors_middleware
from app.services.permission_generator_service import generate_permissions, ensure_permissions_in_db
from app.services.validation_service import register_validation_listeners
from app.db.session import get_db

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs when the application starts up
    app.state.db = get_db()
    db = next(app.state.db)
    permissions = generate_permissions(app)
    ensure_permissions_in_db(db, permissions)
    register_validation_listeners()
    yield
    # Anything after the yield runs when the application shuts down
    app.state.db.close()

app.router.lifespan_context = lifespan

app.add_middleware(AuthorizationMiddleware)
app.add_middleware(BlacklistMiddleware)
add_cors_middleware(app)

# Use the aliased name for the router
app.include_router(answer_choices_router.router, tags=["Answer Choices"])
app.include_router(authentication_router.router, tags=["Authentication"])
app.include_router(register_router.router, tags=["Authentication"])
app.include_router(filters_router.router, tags=["Filters"])
app.include_router(groups_router.router, tags=["Groups"])
app.include_router(leaderboard_router.router, tags=["Leaderboard"])
app.include_router(question_sets_router.router, tags=["Question Sets"])
app.include_router(questions_router.router, tags=["Questions"])
app.include_router(subjects_router.router, tags=["Subjects"])
app.include_router(domains_router.router, tags=["Domains"])
app.include_router(disciplines_router.router, tags=["Disciplines"])
app.include_router(concepts_router.router, tags=["Concepts"])
app.include_router(user_responses_router.router, tags=["User Responses"])
app.include_router(users_router.router, tags=["User Management"])
app.include_router(topics_router.router, tags=["Topics"])
app.include_router(subtopics_router.router, tags=["Subtopics"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

```

## File: validate_openapi.py
```py
# filename: /code/quiz-app/quiz-app-backend/app/validate_openapi.py

import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.openapi.utils import get_openapi
from app.main import app  # Adjust the import based on your actual app file and instance

def validate_openapi_schema():
    try:
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        print("OpenAPI schema generated successfully!")
        print(openapi_schema)
    except Exception as e:
        print("Error generating OpenAPI schema:")
        print(e)

if __name__ == "__main__":
    validate_openapi_schema()

```

# Directory: /code/quiz-app/quiz-app-backend/app/schemas

## File: __init__.py
```py

```

## File: answer_choices.py
```py
# filename: app/schemas/answer_choices.py

from typing import Optional
from pydantic import BaseModel, Field, validator

class AnswerChoiceBaseSchema(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    is_correct: bool
    explanation: Optional[str] = Field(None, max_length=10000)

    @validator('text', 'explanation')
    def validate_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Field cannot be empty or only whitespace')
        return v

class AnswerChoiceCreateSchema(AnswerChoiceBaseSchema):
    pass

class AnswerChoiceUpdateSchema(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=10000)
    is_correct: Optional[bool] = None
    explanation: Optional[str] = Field(None, max_length=10000)

    @validator('text', 'explanation')
    def validate_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Field cannot be empty or only whitespace')
        return v

class AnswerChoiceSchema(AnswerChoiceBaseSchema):
    id: int

    class Config:
        from_attributes = True

```

## File: authentication.py
```py
# filename: app/schemas/authentication.py

from pydantic import BaseModel, Field

class LoginFormSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)

class TokenSchema(BaseModel):
    access_token: str = Field(..., min_length=1)
    token_type: str = Field(..., pattern="^bearer$", case_sensitive=False)

```

## File: concepts.py
```py
# filename: app/schemas/concepts.py

from typing import Optional, List
from pydantic import BaseModel, validator, Field

class ConceptBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the concept")

class ConceptCreateSchema(ConceptBaseSchema):
    subtopic_ids: List[int] = Field(..., min_items=1, description="List of subtopic IDs associated with this concept")

    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Concept name cannot be empty or whitespace')
        return name

    @validator('subtopic_ids')
    def validate_subtopic_ids(cls, v):
        if len(set(v)) != len(v):
            raise ValueError('Subtopic IDs must be unique')
        return v

class ConceptUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the concept")
    subtopic_ids: Optional[List[int]] = Field(None, min_items=1, description="List of subtopic IDs associated with this concept")

    @validator('name')
    def validate_name(cls, name):
        if name is not None and not name.strip():
            raise ValueError('Concept name cannot be empty or whitespace')
        return name

    @validator('subtopic_ids')
    def validate_subtopic_ids(cls, v):
        if v is not None and len(set(v)) != len(v):
            raise ValueError('Subtopic IDs must be unique')
        return v

class ConceptSchema(ConceptBaseSchema):
    id: int
    subtopic_ids: List[int] = Field(..., description="List of subtopic IDs associated with this concept")
    question_ids: List[int] = Field(..., description="List of question IDs associated with this concept")

    class Config:
        from_attributes = True

```

## File: disciplines.py
```py
# filename: app/schemas/disciplines.py

from typing import Optional, List
from pydantic import BaseModel, validator, Field

class DisciplineBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the discipline")

class DisciplineCreateSchema(DisciplineBaseSchema):
    domain_ids: List[int] = Field(..., min_items=1, description="List of domain IDs associated with this discipline")
    subject_ids: Optional[List[int]] = Field(None, description="List of subject IDs associated with this discipline")

    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Discipline name cannot be empty or whitespace')
        return name

    @validator('domain_ids', 'subject_ids')
    def validate_ids(cls, v):
        if v is not None and len(set(v)) != len(v):
            raise ValueError('IDs must be unique')
        return v

class DisciplineUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the discipline")
    domain_ids: Optional[List[int]] = Field(None, min_items=1, description="List of domain IDs associated with this discipline")
    subject_ids: Optional[List[int]] = Field(None, description="List of subject IDs associated with this discipline")

    @validator('name')
    def validate_name(cls, name):
        if name is not None and not name.strip():
            raise ValueError('Discipline name cannot be empty or whitespace')
        return name

    @validator('domain_ids', 'subject_ids')
    def validate_ids(cls, v):
        if v is not None and len(set(v)) != len(v):
            raise ValueError('IDs must be unique')
        return v

class DisciplineSchema(DisciplineBaseSchema):
    id: int
    domain_ids: List[int] = Field(..., description="List of domain IDs associated with this discipline")
    subject_ids: List[int] = Field(..., description="List of subject IDs associated with this discipline")

    class Config:
        from_attributes = True

```

## File: domains.py
```py
# filename: app/schemas/domains.py

from typing import Optional, List
from pydantic import BaseModel, validator, Field

class DomainBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the domain")

class DomainCreateSchema(DomainBaseSchema):
    discipline_ids: Optional[List[int]] = Field(None, description="List of discipline IDs associated with this domain")

    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Domain name cannot be empty or whitespace')
        return name

    @validator('discipline_ids')
    def validate_discipline_ids(cls, v):
        if v is not None and len(set(v)) != len(v):
            raise ValueError('Discipline IDs must be unique')
        return v

class DomainUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the domain")
    discipline_ids: Optional[List[int]] = Field(None, description="List of discipline IDs associated with this domain")

    @validator('name')
    def validate_name(cls, name):
        if name is not None and not name.strip():
            raise ValueError('Domain name cannot be empty or whitespace')
        return name

    @validator('discipline_ids')
    def validate_discipline_ids(cls, v):
        if v is not None and len(set(v)) != len(v):
            raise ValueError('Discipline IDs must be unique')
        return v

class DomainSchema(DomainBaseSchema):
    id: int
    discipline_ids: List[int] = Field(..., description="List of discipline IDs associated with this domain")

    class Config:
        from_attributes = True

```

## File: filters.py
```py
# filename: app/schemas/filters.py

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from app.schemas.questions import DifficultyLevel

class FilterParamsSchema(BaseModel):
    subject: Optional[str] = Field(None, max_length=100, description="Filter questions by subject")
    topic: Optional[str] = Field(None, max_length=100, description="Filter questions by topic")
    subtopic: Optional[str] = Field(None, max_length=100, description="Filter questions by subtopic")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Filter questions by difficulty level")
    question_tags: Optional[List[str]] = Field(None, max_items=10, description="Filter questions by tags")

    @validator('question_tags')
    def validate_question_tags(cls, v):
        if v:
            return [tag.lower() for tag in v]
        return v

    class Config:
        extra = 'forbid'
        json_schema_extra = {
            "example": {
                "subject": "Math",
                "topic": "Algebra",
                "subtopic": "Linear Equations",
                "difficulty": "Easy",
                "question_tags": ["equations", "solving"]
            }
        }

```

## File: groups.py
```py
# filename: app/schemas/groups.py

import re
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class GroupBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=500, description="Description of the group")

    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[\w\-\s]+$', v):
            raise ValueError('Group name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class GroupCreateSchema(GroupBaseSchema):
    creator_id: int = Field(..., gt=0, description="ID of the user creating the group")

class GroupUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=500, description="Description of the group")

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not re.match(r'^[\w\-\s]+$', v):
            raise ValueError('Group name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class GroupSchema(GroupBaseSchema):
    id: int
    creator_id: int
    user_ids: List[int] = Field(..., description="List of user IDs in this group")
    question_set_ids: List[int] = Field(..., description="List of question set IDs associated with this group")

    class Config:
        from_attributes = True

```

## File: leaderboard.py
```py
# filename: app/schemas/leaderboard.py

from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.time_period import TimePeriodSchema

class LeaderboardBaseSchema(BaseModel):
    user_id: int = Field(..., gt=0)
    score: int = Field(..., ge=0)
    time_period_id: int = Field(..., gt=0)
    group_id: Optional[int] = Field(None, gt=0)

class LeaderboardCreateSchema(LeaderboardBaseSchema):
    pass

class LeaderboardUpdateSchema(BaseModel):
    score: int = Field(..., ge=0)

class LeaderboardSchema(LeaderboardBaseSchema):
    id: int
    time_period: TimePeriodSchema

    class Config:
        from_attributes = True

```

## File: permissions.py
```py
# filename: app/schemas/permissions.py

import re
from typing import Optional
from pydantic import BaseModel, Field, validator

class PermissionBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the permission")
    description: Optional[str] = Field(None, max_length=200, description="Description of the permission")

    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Permission name can only contain alphanumeric characters, underscores, and hyphens')
        return v

class PermissionCreateSchema(PermissionBaseSchema):
    pass

class PermissionUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the permission")
    description: Optional[str] = Field(None, max_length=200, description="Description of the permission")

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Permission name can only contain alphanumeric characters, underscores, and hyphens')
        return v

class PermissionSchema(PermissionBaseSchema):
    id: int

    class Config:
        from_attributes = True

```

## File: question_sets.py
```py
# filename: app/schemas/question_sets.py

from typing import List, Optional
from pydantic import BaseModel, Field, validator
import re

class QuestionSetBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Name of the question set")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the question set")
    is_public: bool = Field(True, description="Whether the question set is public or private")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Question set name cannot be empty or whitespace')
        if not re.match(r'^[\w\-\s]+$', v):
            raise ValueError('Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class QuestionSetCreateSchema(QuestionSetBaseSchema):
    creator_id: int = Field(..., gt=0, description="ID of the user creating the question set")
    question_ids: List[int] = Field(default_factory=list, description="List of question IDs in the set")
    group_ids: List[int] = Field(default_factory=list, description="List of group IDs associated with the set")

class QuestionSetUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Name of the question set")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the question set")
    is_public: Optional[bool] = Field(None, description="Whether the question set is public or private")
    question_ids: Optional[List[int]] = Field(None, description="List of question IDs in the set")
    group_ids: Optional[List[int]] = Field(None, description="List of group IDs associated with the set")

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Question set name cannot be empty or whitespace')
            if not re.match(r'^[\w\-\s]+$', v):
                raise ValueError('Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class QuestionSetSchema(QuestionSetBaseSchema):
    id: int
    creator_id: int
    question_ids: List[int]
    group_ids: List[int]

    class Config:
        from_attributes = True

```

## File: question_tags.py
```py
# filename: app/schemas/question_tags.py

from typing import Optional
from pydantic import BaseModel, Field, validator

class QuestionTagBaseSchema(BaseModel):
    tag: str = Field(..., min_length=1, max_length=50)

    @validator('tag')
    def validate_tag(cls, v):
        if not v.strip():
            raise ValueError('Tag cannot be empty or only whitespace')
        return v.lower()  # Store tags in lowercase for consistency

class QuestionTagCreateSchema(QuestionTagBaseSchema):
    pass

class QuestionTagUpdateSchema(BaseModel):
    tag: Optional[str] = Field(None, min_length=1, max_length=50)

    @validator('tag')
    def validate_tag(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Tag cannot be empty or only whitespace')
            return v.lower()
        return v

class QuestionTagSchema(QuestionTagBaseSchema):
    id: int

    class Config:
        from_attributes = True

```

## File: questions.py
```py
# filename: app/schemas/questions.py

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator

from app.schemas.answer_choices import AnswerChoiceSchema, AnswerChoiceCreateSchema
from app.schemas.question_tags import QuestionTagSchema, QuestionTagCreateSchema
from app.schemas.question_sets import QuestionSetSchema, QuestionSetCreateSchema

class DifficultyLevel(str, Enum):
    BEGINNER = "Beginner"
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"

class QuestionBaseSchema(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="The text of the question")
    difficulty: DifficultyLevel = Field(..., description="The difficulty level of the question")

    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Question text cannot be empty or only whitespace')
        return v

class QuestionCreateSchema(QuestionBaseSchema):
    subject_ids: List[int] = Field(..., description="IDs of the subjects associated with the question")
    topic_ids: List[int] = Field(..., description="IDs of the topics associated with the question")
    subtopic_ids: List[int] = Field(..., description="IDs of the subtopics associated with the question")
    concept_ids: List[int] = Field(..., description="IDs of the concepts associated with the question")
    answer_choice_ids: Optional[List[int]] = Field(None, description="List of answer choice IDs associated with the question")
    question_tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs associated with the question")
    question_set_ids: Optional[List[int]] = Field(None, description="List of question set IDs the question belongs to")

class QuestionUpdateSchema(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=10000, description="The text of the question")
    difficulty: Optional[DifficultyLevel] = Field(None, description="The difficulty level of the question")
    subject_ids: Optional[List[int]] = Field(None, description="IDs of the subjects associated with the question")
    topic_ids: Optional[List[int]] = Field(None, description="IDs of the topics associated with the question")
    subtopic_ids: Optional[List[int]] = Field(None, description="IDs of the subtopics associated with the question")
    concept_ids: Optional[List[int]] = Field(None, description="IDs of the concepts associated with the question")
    answer_choice_ids: Optional[List[int]] = Field(None, description="List of answer choice IDs associated with the question")
    question_tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs associated with the question")
    question_set_ids: Optional[List[int]] = Field(None, description="List of question set IDs the question belongs to")

    @validator('text')
    def validate_text(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Question text cannot be empty or only whitespace')
        return v

class QuestionSchema(QuestionBaseSchema):
    id: int
    subject_ids: List[int]
    topic_ids: List[int]
    subtopic_ids: List[int]
    concept_ids: List[int]
    answer_choice_ids: List[int]
    question_tag_ids: List[int]
    question_set_ids: List[int]

    class Config:
        from_attributes = True

class DetailedQuestionSchema(QuestionSchema):
    answer_choices: List['AnswerChoiceSchema']
    question_tags: List['QuestionTagSchema']
    question_sets: List['QuestionSetSchema']

class QuestionWithAnswersCreateSchema(QuestionCreateSchema):
    answer_choices: List['AnswerChoiceCreateSchema']
    question_tags: Optional[List['QuestionTagCreateSchema']] = None
    question_sets: Optional[List['QuestionSetCreateSchema']] = None

```

## File: roles.py
```py
# filename: app/schemas/roles.py

from typing import List, Optional
from pydantic import BaseModel, Field, validator

class RoleBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Name of the role")
    description: Optional[str] = Field(None, max_length=200, description="Description of the role")
    default: bool = Field(False, description="Whether this is the default role for new users")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Role name cannot be empty or only whitespace')
        return v

class RoleCreateSchema(RoleBaseSchema):
    permissions: List[str] = Field(..., min_items=1, description="List of permission names associated with the role")

    @validator('permissions')
    def validate_permissions(cls, v):
        if not all(p.strip() for p in v):
            raise ValueError('All permissions must be non-empty strings')
        return list(set(v))  # Remove duplicates

class RoleUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Name of the role")
    description: Optional[str] = Field(None, max_length=200, description="Description of the role")
    permissions: Optional[List[str]] = Field(None, min_items=1, description="List of permission names associated with the role")
    default: Optional[bool] = Field(None, description="Whether this is the default role for new users")

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Role name cannot be empty or only whitespace')
        return v

    @validator('permissions')
    def validate_permissions(cls, v):
        if v is not None:
            if not all(p.strip() for p in v):
                raise ValueError('All permissions must be non-empty strings')
            return list(set(v))  # Remove duplicates
        return v

class RoleSchema(RoleBaseSchema):
    id: int
    permissions: List[str] = Field(..., min_items=1, description="List of permission names associated with the role")

    class Config:
        from_attributes = True

```

## File: subjects.py
```py
# filename: app/schemas/subjects.py

from typing import Optional, List
from pydantic import BaseModel, validator, Field

class SubjectBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the subject")

class SubjectCreateSchema(SubjectBaseSchema):
    discipline_ids: List[int] = Field(..., description="List of discipline IDs associated with this subject")
    topic_ids: Optional[List[int]] = Field(None, description="List of topic IDs associated with this subject")

    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Subject name cannot be empty or whitespace')
        return name

class SubjectUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the subject")
    discipline_ids: Optional[List[int]] = Field(None, description="List of discipline IDs associated with this subject")
    topic_ids: Optional[List[int]] = Field(None, description="List of topic IDs associated with this subject")

    @validator('name')
    def validate_name(cls, name):
        if name is not None and not name.strip():
            raise ValueError('Subject name cannot be empty or whitespace')
        return name

class SubjectSchema(SubjectBaseSchema):
    id: int
    discipline_ids: List[int] = Field(..., description="List of discipline IDs associated with this subject")
    topic_ids: List[int] = Field(..., description="List of topic IDs associated with this subject")

    class Config:
        from_attributes = True

```

## File: subtopics.py
```py
# filename: app/schemas/subtopics.py

from typing import Optional, List
from pydantic import BaseModel, validator, Field

class SubtopicBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the subtopic")

class SubtopicCreateSchema(SubtopicBaseSchema):
    topic_ids: List[int] = Field(..., description="List of topic IDs associated with this subtopic")
    concept_ids: Optional[List[int]] = Field(None, description="List of concept IDs associated with this subtopic")

    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Subtopic name cannot be empty or whitespace')
        return name

class SubtopicUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the subtopic")
    topic_ids: Optional[List[int]] = Field(None, description="List of topic IDs associated with this subtopic")
    concept_ids: Optional[List[int]] = Field(None, description="List of concept IDs associated with this subtopic")

    @validator('name')
    def validate_name(cls, name):
        if name is not None and not name.strip():
            raise ValueError('Subtopic name cannot be empty or whitespace')
        return name

class SubtopicSchema(SubtopicBaseSchema):
    id: int
    topic_ids: List[int] = Field(..., description="List of topic IDs associated with this subtopic")
    concept_ids: List[int] = Field(..., description="List of concept IDs associated with this subtopic")

    class Config:
        from_attributes = True

```

## File: time_period.py
```py
# filename: app/schemas/time_period.py

from pydantic import BaseModel, Field

class TimePeriodSchema(BaseModel):
    id: int = Field(..., gt=0)
    name: str

    class Config:
        from_attributes = True
```

## File: topics.py
```py
# filename: app/schemas/topics.py

from typing import Optional, List
from pydantic import BaseModel, validator, Field

class TopicBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the topic")

class TopicCreateSchema(TopicBaseSchema):
    subject_ids: List[int] = Field(..., description="List of subject IDs associated with this topic")
    subtopic_ids: Optional[List[int]] = Field(None, description="List of subtopic IDs associated with this topic")

    @validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError('Topic name cannot be empty or whitespace')
        return name

class TopicUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the topic")
    subject_ids: Optional[List[int]] = Field(None, description="List of subject IDs associated with this topic")
    subtopic_ids: Optional[List[int]] = Field(None, description="List of subtopic IDs associated with this topic")

    @validator('name')
    def validate_name(cls, name):
        if name is not None and not name.strip():
            raise ValueError('Topic name cannot be empty or whitespace')
        return name

class TopicSchema(TopicBaseSchema):
    id: int
    subject_ids: List[int] = Field(..., description="List of subject IDs associated with this topic")
    subtopic_ids: List[int] = Field(..., description="List of subtopic IDs associated with this topic")

    class Config:
        from_attributes = True

```

## File: user.py
```py
# filename: app/schemas/user.py

import string
import re
from typing import Optional, List
from pydantic import BaseModel, validator, EmailStr, Field, SecretStr

class UserBaseSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    role: str = Field(default='user', description="Role of the user")

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[\w\-\.]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, hyphens, underscores, and periods')
        return v

    class Config:
        from_attributes = True

class UserCreateSchema(UserBaseSchema):
    password: SecretStr = Field(..., min_length=8, max_length=100, description="Password for the user")

    @validator('password')
    def validate_password(cls, v):
        password = v.get_secret_value()
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
        return v

class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username of the user")
    email: Optional[EmailStr] = Field(None, description="Email address of the user")
    password: Optional[SecretStr] = Field(None, min_length=8, max_length=100, description="Password for the user")
    role: Optional[str] = Field(None, description="Role of the user")
    group_ids: Optional[List[int]] = Field(None, min_items=1, description="List of group IDs the user belongs to")

    @validator('username')
    def validate_username(cls, v):
        if v is not None and not re.match(r'^[\w\-\.]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, hyphens, underscores, and periods')
        return v

    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            return UserCreateSchema.validate_password(v)
        return v

class UserSchema(UserBaseSchema):
    id: int
    is_active: bool
    is_admin: bool
    groups: List[int] = Field(default_factory=list, description="List of group IDs the user belongs to")
    created_groups: List[int] = Field(default_factory=list, description="List of group IDs created by the user")
    created_question_sets: List[int] = Field(default_factory=list, description="List of question set IDs created by the user")
    responses: List[int] = Field(default_factory=list, description="List of user response IDs for this user")
    leaderboards: List[int] = Field(default_factory=list, description="List of leaderboard entry IDs for this user")

    class Config:
        from_attributes = True

```

## File: user_responses.py
```py
# filename: app/schemas/user_responses.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class UserResponseBaseSchema(BaseModel):
    user_id: int = Field(..., gt=0, description="ID of the user who responded")
    question_id: int = Field(..., gt=0, description="ID of the question answered")
    answer_choice_id: int = Field(..., gt=0, description="ID of the chosen answer")
    is_correct: bool = Field(..., description="Whether the answer is correct")
    response_time: Optional[int] = Field(None, ge=0, description="Response time in seconds")

class UserResponseCreateSchema(UserResponseBaseSchema):
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the response")

class UserResponseUpdateSchema(BaseModel):
    is_correct: Optional[bool] = Field(None, description="Whether the answer is correct")
    response_time: Optional[int] = Field(None, ge=0, description="Response time in seconds")

class UserResponseSchema(UserResponseBaseSchema):
    id: int
    timestamp: datetime = Field(..., description="Timestamp of the response")

    class Config:
        from_attributes = True

    @validator('timestamp', pre=True)
    def parse_timestamp(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

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
from app.core.security import verify_password, get_password_hash
from app.models.users import UserModel
from app.services.logging_service import logger


def authenticate_user(db: Session, username: str, password: str) -> UserModel:
    user = get_user_by_username(db, username)
    if not user:
        logger.error(f"User {username} not found")
        return False
    logger.debug(f"Authenticating user: {username}")
    logger.debug(f"Stored hashed password: {user.hashed_password}")
    logger.debug(f"Provided password: {password}")
    
    # Add this line to log the result of verify_password
    verification_result = verify_password(password, user.hashed_password)
    logger.debug(f"Password verification result: {verification_result}")
    
    if not verification_result:
        hashed_attempt = get_password_hash(password)
        logger.debug(f"Hashed attempt: {hashed_attempt}")
        logger.error(f"User {username} supplied an invalid password")
        return False
    if not user.is_active:
        logger.error(f"User {username} is not active")
        return False
    logger.info(f"User {username} authenticated successfully")
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

def generate_permissions(app: FastAPI):
    permissions = set()
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
                        permissions.add(permission)
                        logger.debug("Generated permission: %s", permission)

    return permissions

def ensure_permissions_in_db(db, permissions):
    existing_permissions = set(p.name for p in db.query(PermissionModel).all())
    new_permissions = permissions - existing_permissions

    for permission in new_permissions:
        db.add(PermissionModel(name=permission))

    db.commit()
    logger.debug(f"Added {len(new_permissions)} new permissions to the database")

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
from app.schemas.leaderboard import LeaderboardSchema, TimePeriodSchema
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

def time_period_to_schema(time_period_model):
    return TimePeriodSchema(
        id=time_period_model.id,
        name=time_period_model.name
    )

def leaderboard_to_schema(leaderboard_model):
    return LeaderboardSchema(
        id=leaderboard_model.id,
        user_id=leaderboard_model.user_id,
        score=leaderboard_model.score,
        time_period=time_period_to_schema(leaderboard_model.time_period),
        group_id=leaderboard_model.group_id
    )
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
from app.db.base import Base
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
# filename: /code/quiz-app/quiz-app-backend/app/crud/crud_answer_choices.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.answer_choices import AnswerChoiceModel
from app.schemas.answer_choices import AnswerChoiceCreateSchema, AnswerChoiceUpdateSchema
from app.services.logging_service import logger, sqlalchemy_obj_to_dict

def create_answer_choice_crud(db: Session, answer_choice: AnswerChoiceCreateSchema) -> AnswerChoiceModel:
    db_answer_choice = AnswerChoiceModel(**answer_choice.model_dump())
    db.add(db_answer_choice)
    db.commit()
    db.refresh(db_answer_choice)
    logger.debug(f"create_answer_choice_crud: {sqlalchemy_obj_to_dict(db_answer_choice)}")
    return db_answer_choice

def read_answer_choice_crud(db: Session, answer_choice_id: int) -> Optional[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id == answer_choice_id).first()

def read_answer_choices_crud(db: Session, skip: int = 0, limit: int = 100) -> List[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).offset(skip).limit(limit).all()

def update_answer_choice_crud(db: Session, answer_choice_id: int, answer_choice: AnswerChoiceUpdateSchema) -> Optional[AnswerChoiceModel]:
    db_answer_choice = read_answer_choice_crud(db, answer_choice_id)
    if db_answer_choice:
        update_data = answer_choice.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_answer_choice, key, value)
        db.commit()
        db.refresh(db_answer_choice)
    return db_answer_choice

def delete_answer_choice_crud(db: Session, answer_choice_id: int) -> bool:
    db_answer_choice = read_answer_choice_crud(db, answer_choice_id)
    if db_answer_choice:
        db.delete(db_answer_choice)
        db.commit()
        return True
    return False

```

## File: crud_concepts.py
```py
# filename: app/crud/crud_concepts.py

from sqlalchemy.orm import Session
from app.models.concepts import ConceptModel
from app.schemas.concepts import ConceptCreateSchema, ConceptUpdateSchema

def create_concept(db: Session, concept: ConceptCreateSchema) -> ConceptModel:
    db_concept = ConceptModel(**concept.model_dump())
    db.add(db_concept)
    db.commit()
    db.refresh(db_concept)
    return db_concept

def read_concept(db: Session, concept_id: int) -> ConceptModel:
    return db.query(ConceptModel).filter(ConceptModel.id == concept_id).first()

def read_concepts(db: Session, skip: int = 0, limit: int = 100) -> list[ConceptModel]:
    return db.query(ConceptModel).offset(skip).limit(limit).all()

def update_concept(db: Session, concept_id: int, concept: ConceptUpdateSchema) -> ConceptModel:
    db_concept = read_concept(db, concept_id)
    if db_concept:
        update_data = concept.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_concept, key, value)
        db.commit()
        db.refresh(db_concept)
    return db_concept

def delete_concept(db: Session, concept_id: int) -> bool:
    db_concept = read_concept(db, concept_id)
    if db_concept:
        db.delete(db_concept)
        db.commit()
        return True
    return False

```

## File: crud_disciplines.py
```py
# filename: app/crud/crud_disciplines.py

from sqlalchemy.orm import Session
from app.models.disciplines import DisciplineModel
from app.schemas.disciplines import DisciplineCreateSchema, DisciplineUpdateSchema

def create_discipline(db: Session, discipline: DisciplineCreateSchema) -> DisciplineModel:
    db_discipline = DisciplineModel(**discipline.model_dump())
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)
    return db_discipline

def read_discipline(db: Session, discipline_id: int) -> DisciplineModel:
    return db.query(DisciplineModel).filter(DisciplineModel.id == discipline_id).first()

def read_disciplines(db: Session, skip: int = 0, limit: int = 100) -> list[DisciplineModel]:
    return db.query(DisciplineModel).offset(skip).limit(limit).all()

def update_discipline(db: Session, discipline_id: int, discipline: DisciplineUpdateSchema) -> DisciplineModel:
    db_discipline = read_discipline(db, discipline_id)
    if db_discipline:
        update_data = discipline.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_discipline, key, value)
        db.commit()
        db.refresh(db_discipline)
    return db_discipline

def delete_discipline(db: Session, discipline_id: int) -> bool:
    db_discipline = read_discipline(db, discipline_id)
    if db_discipline:
        db.delete(db_discipline)
        db.commit()
        return True
    return False
```

## File: crud_domains.py
```py
# filename: app/crud/crud_domains.py

from sqlalchemy.orm import Session
from app.models.domains import DomainModel
from app.schemas.domains import DomainCreateSchema, DomainUpdateSchema

def create_domain(db: Session, domain: DomainCreateSchema) -> DomainModel:
    db_domain = DomainModel(**domain.model_dump())
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

def read_domain(db: Session, domain_id: int) -> DomainModel:
    return db.query(DomainModel).filter(DomainModel.id == domain_id).first()

def read_domains(db: Session, skip: int = 0, limit: int = 100) -> list[DomainModel]:
    return db.query(DomainModel).offset(skip).limit(limit).all()

def update_domain(db: Session, domain_id: int, domain: DomainUpdateSchema) -> DomainModel:
    db_domain = read_domain(db, domain_id)
    if db_domain:
        update_data = domain.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_domain, key, value)
        db.commit()
        db.refresh(db_domain)
    return db_domain

def delete_domain(db: Session, domain_id: int) -> bool:
    db_domain = read_domain(db, domain_id)
    if db_domain:
        db.delete(db_domain)
        db.commit()
        return True
    return False

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
from app.services.logging_service import logger, sqlalchemy_obj_to_dict

def filter_questions_crud(
    db: Session,
    filters: dict,  # Change this parameter to expect a dictionary
    skip: int = 0,
    limit: int = 100
) -> Optional[List[QuestionSchema]]:
    logger.debug("Entering filter_questions function")
    logger.debug(f"Received filters: {filters}")
    try:
        # Validate filters dictionary against the Pydantic model
        validated_filters = FilterParamsSchema(**filters)
    except ValidationError as e:
        logger.debug(f"Invalid filters: {str(e)}")
        raise e

    if not any(value for value in filters.values()):
        logger.debug("No filters provided")
        return None

    query = db.query(QuestionModel).join(SubjectModel).join(TopicModel).join(SubtopicModel).outerjoin(QuestionModel.question_tags)

    if validated_filters.subject:
        query = query.filter(func.lower(SubjectModel.name) == func.lower(validated_filters.subject))
    if validated_filters.topic:
        query = query.filter(func.lower(TopicModel.name) == func.lower(validated_filters.topic))
    if validated_filters.subtopic:
        query = query.filter(func.lower(SubtopicModel.name) == func.lower(validated_filters.subtopic))
    if validated_filters.difficulty:
        query = query.filter(func.lower(QuestionModel.difficulty) == func.lower(validated_filters.difficulty))
    if validated_filters.question_tags:
        query = query.filter(QuestionTagModel.tag.in_([tag.lower() for tag in validated_filters.question_tags]))

    questions = query.offset(skip).limit(limit).all()

    logger.debug(f"Filtered questions: {sqlalchemy_obj_to_dict(question) for question in questions}")
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


def add_tag_to_question(db: Session, question_id: int, question_tag_id: int):
    association = QuestionToTagAssociation(question_id=question_id, question_tag_id=question_tag_id)
    db.add(association)
    db.commit()

def remove_tag_from_question(db: Session, question_id: int, question_tag_id: int):
    db.query(QuestionToTagAssociation).filter_by(question_id=question_id, question_tag_id=question_tag_id).delete()
    db.commit()

def get_question_tags(db: Session, question_id: int):
    return db.query(QuestionTagModel).join(QuestionToTagAssociation).filter(QuestionToTagAssociation.question_id == question_id).all()

def read_questions_by_tag(db: Session, question_tag_id: int):
    return db.query(QuestionModel).join(QuestionToTagAssociation).filter(QuestionToTagAssociation.question_tag_id == question_tag_id).all()

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
# filename: /code/quiz-app/quiz-app-backend/app/crud/crud_questions.py

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.questions import QuestionModel
from app.models.answer_choices import AnswerChoiceModel
from app.models.question_tags import QuestionTagModel
from app.models.question_sets import QuestionSetModel
from app.schemas.questions import QuestionCreateSchema, QuestionUpdateSchema, QuestionWithAnswersCreateSchema, DetailedQuestionSchema
from app.crud.crud_answer_choices import create_answer_choice_crud
from app.services.randomization_service import randomize_questions, randomize_answer_choices
from app.services.logging_service import logger, sqlalchemy_obj_to_dict

def create_question(db: Session, question: QuestionCreateSchema) -> QuestionModel:
    db_question = QuestionModel(
        text=question.text,
        subject=question.subject,
        topic=question.topic,
        subtopic=question.subtopic,
        concept=question.concept,
        difficulty=question.difficulty
    )
    db.add(db_question)
    db.flush()

    if question.answer_choices:
        for question_answer_choice in question.answer_choices:
            if not question_answer_choice.id:
                db_answer_choice = create_answer_choice_crud(db, question_answer_choice)
                db_question.answer_choices.append(db_answer_choice)
            else:
                db_answer_choice = db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id == question_answer_choice.id).first()
                db_question.answer_choices.append(db_answer_choice)

    if question.question_tag_ids:
        tags = db.query(QuestionTagModel).filter(QuestionTagModel.id.in_(question.question_tag_ids)).all()
        db_question.question_tag_ids = tags

    if question.question_set_ids:
        question_sets = db.query(QuestionSetModel).filter(QuestionSetModel.id.in_(question.question_set_ids)).all()
        db_question.question_set_ids = question_sets

    db.commit()
    db.refresh(db_question)
    return db_question

def create_question_with_answers(db: Session, question: QuestionWithAnswersCreateSchema) -> QuestionModel:
    # First, create the question
    db_question = QuestionModel(
        text=question.text,
        subject_id=question.subject_id,
        topic_id=question.topic_id,
        subtopic_id=question.subtopic_id,
        concept_id=question.concept_id,
        difficulty=question.difficulty,
        answer_choices=[]
    )
    db.add(db_question)
    db.flush()  # This assigns an ID to db_question
    
    logger.debug(f"Created question: {sqlalchemy_obj_to_dict(db_question)}")

    # Now create the answer choices and associate them with the question
    for answer_choice in question.answer_choices:
        db_answer_choice = create_answer_choice_crud(db, answer_choice)
        db_question.answer_choices.append(db_answer_choice)
        logger.debug(f"Question with answer choices: {sqlalchemy_obj_to_dict(db_question)}")

    if question.question_tags:
        question_tags = db.query(QuestionTagModel).filter(QuestionTagModel.id.in_(question.question_tags)).all()
        db_question.question_tags = question_tags

    if question.question_sets:
        question_sets = db.query(QuestionSetModel).filter(QuestionSetModel.id.in_(question.question_sets)).all()
        db_question.question_sets = question_sets

    db.commit()
    db.refresh(db_question)
    
    return db_question

def read_question(db: Session, question_id: int) -> Optional[DetailedQuestionSchema]:
    db_question = db.query(QuestionModel).options(
        joinedload(QuestionModel.subject),
        joinedload(QuestionModel.topic),
        joinedload(QuestionModel.subtopic),
        joinedload(QuestionModel.concept),
        joinedload(QuestionModel.answer_choices),
        joinedload(QuestionModel.question_tags),
        joinedload(QuestionModel.question_sets)
    ).filter(QuestionModel.id == question_id).first()

    if db_question:
        return DetailedQuestionSchema(
            id=db_question.id,
            text=db_question.text,
            difficulty=db_question.difficulty,
            subject=db_question.subject.name,
            topic=db_question.topic.name,
            subtopic=db_question.subtopic.name,
            concept=db_question.concept.name,
            answer_choices=[ac for ac in db_question.answer_choices],
            question_tags=[tag.tag for tag in db_question.question_tags],
            question_sets=[qs.name for qs in db_question.question_sets]
        )
    return None

def read_questions(db: Session, skip: int = 0, limit: int = 100) -> List[DetailedQuestionSchema]:
    db_questions = db.query(QuestionModel).options(
        joinedload(QuestionModel.subject),
        joinedload(QuestionModel.topic),
        joinedload(QuestionModel.subtopic),
        joinedload(QuestionModel.concept),
        joinedload(QuestionModel.answer_choices),
        joinedload(QuestionModel.question_tag_ids),
        joinedload(QuestionModel.question_set_ids)
    ).offset(skip).limit(limit).all()

    questions = [
        DetailedQuestionSchema(
            id=q.id,
            text=q.text,
            difficulty=q.difficulty,
            subject=q.subject.name,
            topic=q.topic.name,
            subtopic=q.subtopic.name,
            concept=q.concept.name,
            answer_choices=randomize_answer_choices(q.answer_choices),
            question_tags=[tag.tag for tag in q.question_tags],
            question_sets=[qs.name for qs in q.question_sets]
        ) for q in randomize_questions(db_questions)
    ]
    return questions

def update_question(db: Session, question_id: int, question: QuestionUpdateSchema) -> Optional[QuestionModel]:
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if db_question:
        update_data = question.model_dump(exclude_unset=True)
        
        if 'answer_choice_ids' in update_data:
            answer_choice_ids = update_data.pop('answer_choice_ids')
            answer_choices = db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id.in_(answer_choice_ids)).all()
            db_question.answer_choices = answer_choices

        if 'question_tag_ids' in update_data:
            tag_ids = update_data.pop('question_tag_ids')
            tags = db.query(QuestionTagModel).filter(QuestionTagModel.id.in_(tag_ids)).all()
            db_question.question_tag_ids = tags

        if 'question_set_ids' in update_data:
            set_ids = update_data.pop('question_set_ids')
            question_sets = db.query(QuestionSetModel).filter(QuestionSetModel.id.in_(set_ids)).all()
            db_question.question_set_ids = question_sets

        for key, value in update_data.items():
            setattr(db_question, key, value)

        db.commit()
        db.refresh(db_question)
    return db_question

def delete_question(db: Session, question_id: int) -> bool:
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False

```

## File: crud_role_to_permission_associations.py
```py
# filename: app/crud/crud_role_to_permission_associations.py

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
from app.crud.crud_role_to_permission_associations import add_permission_to_role, remove_permission_from_role, get_role_permissions
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
from app.schemas.subjects import SubjectCreateSchema, SubjectUpdateSchema

def create_subject(db: Session, subject: SubjectCreateSchema) -> SubjectModel:
    db_subject = SubjectModel(**subject.model_dump())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def read_subject(db: Session, subject_id: int) -> SubjectModel:
    return db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()

def read_subjects(db: Session, skip: int = 0, limit: int = 100) -> list[SubjectModel]:
    return db.query(SubjectModel).offset(skip).limit(limit).all()

def update_subject(db: Session, subject_id: int, subject: SubjectUpdateSchema) -> SubjectModel:
    db_subject = read_subject(db, subject_id)
    if db_subject:
        update_data = subject.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_subject, key, value)
        db.commit()
        db.refresh(db_subject)
    return db_subject

def delete_subject(db: Session, subject_id: int) -> bool:
    db_subject = read_subject(db, subject_id)
    if db_subject:
        db.delete(db_subject)
        db.commit()
        return True
    return False

```

## File: crud_subtopics.py
```py
# filename: app/crud/crud_subtopics.py

from sqlalchemy.orm import Session
from app.models.subtopics import SubtopicModel
from app.schemas.subtopics import SubtopicCreateSchema, SubtopicUpdateSchema

def create_subtopic(db: Session, subtopic: SubtopicCreateSchema) -> SubtopicModel:
    db_subtopic = SubtopicModel(**subtopic.model_dump())
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)
    return db_subtopic

def read_subtopic(db: Session, subtopic_id: int) -> SubtopicModel:
    return db.query(SubtopicModel).filter(SubtopicModel.id == subtopic_id).first()

def read_subtopics(db: Session, skip: int = 0, limit: int = 100) -> list[SubtopicModel]:
    return db.query(SubtopicModel).offset(skip).limit(limit).all()

def update_subtopic(db: Session, subtopic_id: int, subtopic: SubtopicUpdateSchema) -> SubtopicModel:
    db_subtopic = read_subtopic(db, subtopic_id)
    if db_subtopic:
        update_data = subtopic.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_subtopic, key, value)
        db.commit()
        db.refresh(db_subtopic)
    return db_subtopic

def delete_subtopic(db: Session, subtopic_id: int) -> bool:
    db_subtopic = read_subtopic(db, subtopic_id)
    if db_subtopic:
        db.delete(db_subtopic)
        db.commit()
        return True
    return False

```

## File: crud_topics.py
```py
# filename: app/crud/crud_topics.py

from sqlalchemy.orm import Session
from app.models.topics import TopicModel
from app.schemas.topics import TopicCreateSchema, TopicUpdateSchema

def create_topic(db: Session, topic: TopicCreateSchema) -> TopicModel:
    db_topic = TopicModel(**topic.model_dump())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def read_topic(db: Session, topic_id: int) -> TopicModel:
    return db.query(TopicModel).filter(TopicModel.id == topic_id).first()

def read_topics(db: Session, skip: int = 0, limit: int = 100) -> list[TopicModel]:
    return db.query(TopicModel).offset(skip).limit(limit).all()

def update_topic(db: Session, topic_id: int, topic: TopicUpdateSchema) -> TopicModel:
    db_topic = read_topic(db, topic_id)
    if db_topic:
        update_data = topic.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_topic, key, value)
        db.commit()
        db.refresh(db_topic)
    return db_topic

def delete_topic(db: Session, topic_id: int) -> bool:
    db_topic = read_topic(db, topic_id)
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
from app.models.question_sets import QuestionSetModel
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.core.security import get_password_hash
from app.services.logging_service import logger

def create_user_crud(db: Session, user: UserCreateSchema) -> UserModel:
    default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
    logger.debug("Default role: %s", default_role)
    user_role = user.role if user.role else default_role.name
    logger.debug("User role: %s", user_role)
    db_user = UserModel(
        username=user.username,
        hashed_password=user.password,  # This is already hashed, don't hash it again
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

def delete_user(db: Session, user_id: int):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return None
    
    # Check for public question sets
    public_sets = db.query(QuestionSetModel).filter(
        QuestionSetModel.creator_id == user_id,
        QuestionSetModel.is_public == True
    ).first()
    if public_sets:
        raise ValueError("Cannot delete user with public question sets")
    
    # Check for groups with active members
    active_groups = db.query(GroupModel).filter(
        GroupModel.creator_id == user_id,
        GroupModel.users.any()
    ).first()
    if active_groups:
        raise ValueError("Cannot delete user who created groups with active members")
    
    db.delete(user)
    db.commit()
    return user

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

## File: base.py
```py
# filename: app/db/base.py

from sqlalchemy.orm import declarative_base


Base = declarative_base()

```

## File: session.py
```py
# filename: app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
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

## File: answer_choices.py
```py
# filename: /code/quiz-app/quiz-app-backend/app/api/endpoints/answer_choices.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.answer_choices import AnswerChoiceSchema, AnswerChoiceCreateSchema, AnswerChoiceUpdateSchema
from app.crud.crud_answer_choices import (
    create_answer_choice_crud,
    read_answer_choice_crud,
    read_answer_choices_crud,
    update_answer_choice_crud,
    delete_answer_choice_crud
)
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/answer-choices/", response_model=AnswerChoiceSchema, status_code=status.HTTP_201_CREATED)
def create_answer_choice(
    answer_choice: AnswerChoiceCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_answer_choice_crud(db=db, answer_choice=answer_choice)

@router.get("/answer-choices/", response_model=List[AnswerChoiceSchema])
def get_answer_choices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return read_answer_choices_crud(db, skip=skip, limit=limit)

@router.get("/answer-choices/{answer_choice_id}", response_model=AnswerChoiceSchema)
def get_answer_choice(
    answer_choice_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_answer_choice = read_answer_choice_crud(db, answer_choice_id=answer_choice_id)
    if db_answer_choice is None:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return db_answer_choice

@router.put("/answer-choices/{answer_choice_id}", response_model=AnswerChoiceSchema)
def update_answer_choice(
    answer_choice_id: int,
    answer_choice: AnswerChoiceUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_answer_choice = update_answer_choice_crud(db, answer_choice_id, answer_choice)
    if db_answer_choice is None:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return db_answer_choice

@router.delete("/answer-choices/{answer_choice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_answer_choice(
    answer_choice_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_answer_choice_crud(db, answer_choice_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return None

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
from app.services.logging_service import logger

router = APIRouter()

blacklist = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/login", response_model=TokenSchema)
async def login_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    logger.debug(f"User {form_data.username} is trying to log in")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.error(f"User {form_data.username} failed to log in")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        logger.error(f"User {form_data.username} is not active")
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
    if access_token:
        logger.debug(f"User {form_data.username} logged in successfully")
    else:
        logger.error(f"User {form_data.username} failed to log in")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
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

## File: concepts.py
```py
# filename: app/api/endpoints/concepts.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.concepts import ConceptSchema, ConceptCreateSchema, ConceptUpdateSchema
from app.crud.crud_concepts import create_concept, read_concept, read_concepts, update_concept, delete_concept
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/concepts/", response_model=ConceptSchema, status_code=201)
def post_concept(
    concept: ConceptCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_concept(db=db, concept=concept)

@router.get("/concepts/", response_model=List[ConceptSchema])
def get_concepts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    concepts = read_concepts(db, skip=skip, limit=limit)
    return concepts

@router.get("/concepts/{concept_id}", response_model=ConceptSchema)
def get_concept(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_concept = read_concept(db, concept_id=concept_id)
    if db_concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return db_concept

@router.put("/concepts/{concept_id}", response_model=ConceptSchema)
def put_concept(
    concept_id: int,
    concept: ConceptUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_concept = update_concept(db, concept_id, concept)
    if db_concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return db_concept

@router.delete("/concepts/{concept_id}", status_code=204)
def delete_concept_endpoint(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_concept(db, concept_id)
    if not success:
        raise HTTPException(status_code=404, detail="Concept not found")
    return success

```

## File: disciplines.py
```py
# filename: app/api/endpoints/disciplines.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.disciplines import DisciplineSchema, DisciplineCreateSchema, DisciplineUpdateSchema
from app.crud.crud_disciplines import create_discipline, read_discipline, read_disciplines, update_discipline, delete_discipline
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/disciplines/", response_model=DisciplineSchema, status_code=201)
def post_discipline(
    discipline: DisciplineCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_discipline(db=db, discipline=discipline)

@router.get("/disciplines/", response_model=List[DisciplineSchema])
def get_disciplines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    disciplines = read_disciplines(db, skip=skip, limit=limit)
    return disciplines

@router.get("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def get_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_discipline = read_discipline(db, discipline_id=discipline_id)
    if db_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return db_discipline

@router.put("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def put_discipline(
    discipline_id: int,
    discipline: DisciplineUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_discipline = update_discipline(db, discipline_id, discipline)
    if db_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return db_discipline

@router.delete("/disciplines/{discipline_id}", status_code=204)
def delete_discipline_endpoint(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_discipline(db, discipline_id)
    if not success:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return success

```

## File: domains.py
```py
# filename: app/api/endpoints/domains.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.domains import DomainSchema, DomainCreateSchema, DomainUpdateSchema
from app.crud.crud_domains import create_domain, read_domain, read_domains, update_domain, delete_domain
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/domains/", response_model=DomainSchema, status_code=201)
def post_domain(
    domain: DomainCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_domain(db=db, domain=domain)

@router.get("/domains/", response_model=List[DomainSchema])
def get_domains(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    domains = read_domains(db, skip=skip, limit=limit)
    return domains

@router.get("/domains/{domain_id}", response_model=DomainSchema)
def get_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_domain = read_domain(db, domain_id=domain_id)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return db_domain

@router.put("/domains/{domain_id}", response_model=DomainSchema)
def put_domain(
    domain_id: int,
    domain: DomainUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_domain = update_domain(db, domain_id, domain)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return db_domain

@router.delete("/domains/{domain_id}", status_code=204)
def delete_domain_endpoint(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_domain(db, domain_id)
    if not success:
        raise HTTPException(status_code=404, detail="Domain not found")
    return success

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
                      'difficulty', 'question_tags', 'skip', 'limit'}
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
    question_tags: Optional[List[str]] = Query(None),
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
    question_tags: Optional[List[str]]
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
            question_tags=question_tags
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

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.leaderboard import LeaderboardSchema, TimePeriodSchema
from app.services.scoring_service import calculate_leaderboard_scores, time_period_to_schema
from app.services.user_service import get_current_user
from app.models.time_period import TimePeriodModel

router = APIRouter()

@router.get("/leaderboard/", response_model=List[LeaderboardSchema])
def get_leaderboard(
    time_period: int = Query(..., description="Time period ID (1: daily, 7: weekly, 30: monthly, 365: yearly)"),
    group_id: int = None,
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user: UserModel = Depends(get_current_user)
):
    time_period_model = db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period).first()
    if not time_period_model:
        raise ValueError("Invalid time period")

    leaderboard_scores = calculate_leaderboard_scores(db, time_period_model, group_id)
    leaderboard_data = [
        LeaderboardSchema(
            id=index + 1,
            user_id=user_id,
            score=score,
            time_period=time_period_to_schema(time_period_model),
            group_id=group_id
        )
        for index, (user_id, score) in enumerate(leaderboard_scores.items())
    ]
    leaderboard_data.sort(key=lambda x: x.score, reverse=True)
    return leaderboard_data[:limit]

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
from app.crud.crud_questions import create_question
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
            create_question(db, QuestionCreateSchema(**question))

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
# filename: /code/quiz-app/quiz-app-backend/app/api/endpoints/questions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.questions import QuestionCreateSchema, QuestionUpdateSchema, QuestionWithAnswersCreateSchema, QuestionSchema, DetailedQuestionSchema
from app.crud.crud_questions import create_question, read_question, read_questions, update_question, delete_question, create_question_with_answers
from app.services.user_service import get_current_user
from app.services.logging_service import logger
from app.models.users import UserModel

router = APIRouter()

@router.post("/questions/", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
def create_question_endpoint(
    question: QuestionCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    created_question = create_question(db=db, question=question)
    return QuestionSchema.model_validate(created_question)

@router.post("/questions/with-answers/", response_model=DetailedQuestionSchema, status_code=status.HTTP_201_CREATED)
def create_question_with_answers_endpoint(
    question: QuestionWithAnswersCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_question_with_answers(db=db, question=question)

@router.get("/questions/", response_model=List[DetailedQuestionSchema])
def get_questions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    questions = read_questions(db, skip=skip, limit=limit)
    return questions

@router.get("/questions/{question_id}", response_model=DetailedQuestionSchema)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Reading question with ID: %s", question_id)
    db_question = read_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
    return db_question

@router.put("/questions/{question_id}", response_model=DetailedQuestionSchema)
def update_question_endpoint(
    question_id: int,
    question: QuestionUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_question = update_question(db, question_id, question)
    if db_question is None:
        raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
    return db_question

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question_endpoint(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
    return None

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
from app.services.logging_service import logger

router = APIRouter()

@router.post("/register", status_code=201)
def register_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    logger.info(f"Registering user: {user.username}")
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        logger.error(f"Username already registered: {user.username}")
        raise HTTPException(status_code=422, detail="Username already registered")
    db_email = get_user_by_email(db, email=user.email)
    if db_email:
        logger.error(f"Email already registered: {user.email}")
        raise HTTPException(status_code=422, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    logger.debug(f"Hashed password for user {user.username}: {hashed_password}")
    if not user.role:
        default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
        user.role = default_role.name
        logger.debug(f"Default role assigned: {user.role}")
    user_create = UserCreateSchema(
        username=user.username,
        password=hashed_password,  # Pass the hashed password here
        email=user.email,
        role=user.role
    )
    created_user = create_user_crud(db=db, user=user_create)
    logger.debug(f"User registered: {user.username}")
    return created_user

```

## File: subjects.py
```py
# filename: app/api/endpoints/subjects.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.subjects import SubjectSchema, SubjectCreateSchema, SubjectUpdateSchema
from app.crud.crud_subjects import create_subject, read_subject, read_subjects, update_subject, delete_subject
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
def post_subject(
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_subject(db=db, subject=subject)

@router.get("/subjects/", response_model=List[SubjectSchema])
def get_subjects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subjects = read_subjects(db, skip=skip, limit=limit)
    return subjects

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subject = read_subject(db, subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject

@router.put("/subjects/{subject_id}", response_model=SubjectSchema)
def put_subject(
    subject_id: int,
    subject: SubjectUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subject = update_subject(db, subject_id, subject)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject

@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_subject(db, subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return success

```

## File: subtopics.py
```py
# filename: app/api/endpoints/subtopics.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.subtopics import SubtopicSchema, SubtopicCreateSchema, SubtopicUpdateSchema
from app.crud.crud_subtopics import create_subtopic, read_subtopic, read_subtopics, update_subtopic, delete_subtopic
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/subtopics/", response_model=SubtopicSchema, status_code=201)
def post_subtopic(
    subtopic: SubtopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_subtopic(db=db, subtopic=subtopic)

@router.get("/subtopics/", response_model=List[SubtopicSchema])
def get_subtopics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subtopics = read_subtopics(db, skip=skip, limit=limit)
    return subtopics

@router.get("/subtopics/{subtopic_id}", response_model=SubtopicSchema)
def get_subtopic(
    subtopic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subtopic = read_subtopic(db, subtopic_id=subtopic_id)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return db_subtopic

@router.put("/subtopics/{subtopic_id}", response_model=SubtopicSchema)
def put_subtopic(
    subtopic_id: int,
    subtopic: SubtopicUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subtopic = update_subtopic(db, subtopic_id, subtopic)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return db_subtopic

@router.delete("/subtopics/{subtopic_id}", status_code=204)
def delete_subtopic_endpoint(
    subtopic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_subtopic(db, subtopic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return success

```

## File: topics.py
```py
# filename: app/api/endpoints/topics.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.topics import TopicSchema, TopicCreateSchema, TopicUpdateSchema
from app.crud.crud_topics import create_topic, read_topic, read_topics, update_topic, delete_topic
from app.services.user_service import get_current_user
from app.models.users import UserModel

router = APIRouter()

@router.post("/topics/", response_model=TopicSchema, status_code=201)
def post_topic(
    topic: TopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_topic(db=db, topic=topic)

@router.get("/topics/", response_model=List[TopicSchema])
def get_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    topics = read_topics(db, skip=skip, limit=limit)
    return topics

@router.get("/topics/{topic_id}", response_model=TopicSchema)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_topic = read_topic(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return db_topic

@router.put("/topics/{topic_id}", response_model=TopicSchema)
def put_topic(
    topic_id: int,
    topic: TopicUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_topic = update_topic(db, topic_id, topic)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return db_topic

@router.delete("/topics/{topic_id}", status_code=204)
def delete_topic_endpoint(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_topic(db, topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return success

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

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class AnswerChoiceModel(Base):
    __tablename__ = "answer_choices"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(10000), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    explanation = Column(String(10000))

    questions = relationship("QuestionModel", secondary="question_to_answer_association", back_populates="answer_choices")
    user_responses = relationship("UserResponseModel", back_populates="answer_choice")

    def __repr__(self):
        return f"<AnswerChoiceModel(id={self.id}, text='{self.text[:50]}...', is_correct={self.is_correct})>"

```

## File: associations.py
```py
# filename: app/models/associations.py

from sqlalchemy import Column, Integer, ForeignKey
from app.db.base import Base


class UserToGroupAssociation(Base):
    __tablename__ = "user_to_group_association"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)


class QuestionToAnswerAssociation(Base):
    __tablename__ = "question_to_answer_association"
    
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    answer_choice_id = Column(Integer, ForeignKey('answer_choices.id'), primary_key=True)


class QuestionToTagAssociation(Base):
    __tablename__ = "question_to_tag_association"

    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    question_tag_id = Column(Integer, ForeignKey("question_tags.id"), primary_key=True)


class QuestionSetToQuestionAssociation(Base):
    __tablename__ = "question_set_to_question_association"

    question_id = Column(ForeignKey('questions.id'), primary_key=True)
    question_set_id = Column(ForeignKey('question_sets.id'), primary_key=True)


class QuestionSetToGroupAssociation(Base):
    __tablename__ = "question_set_to_group_association"

    question_set_id = Column(ForeignKey('question_sets.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)


class RoleToPermissionAssociation(Base):
    __tablename__ = "role_to_permission_association"

    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)


class QuestionToSubjectAssociation(Base):
    __tablename__ = 'question_to_subject_association'
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), primary_key=True)


class QuestionToTopicAssociation(Base):
    __tablename__ = 'question_to_topic_association'
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), primary_key=True)


class QuestionToSubtopicAssociation(Base):
    __tablename__ = 'question_to_subtopic_association'
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'), primary_key=True)


class QuestionToConceptAssociation(Base):
    __tablename__ = 'question_to_concept_association'
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    concept_id = Column(Integer, ForeignKey('concepts.id'), primary_key=True)


class DomainToDisciplineAssociation(Base):
    __tablename__ = 'domain_to_discipline_association'
    domain_id = Column(Integer, ForeignKey('domains.id'), primary_key=True)
    discipline_id = Column(Integer, ForeignKey('disciplines.id'), primary_key=True)

class DisciplineToSubjectAssociation(Base):
    __tablename__ = 'discipline_to_subject_association'
    discipline_id = Column(Integer, ForeignKey('disciplines.id'), primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), primary_key=True)


class SubjectToTopicAssociation(Base):
    __tablename__ = 'subject_to_topic_association'
    subject_id = Column(Integer, ForeignKey('subjects.id'), primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), primary_key=True)


class TopicToSubtopicAssociation(Base):
    __tablename__ = 'topic_to_subtopic_association'
    topic_id = Column(Integer, ForeignKey('topics.id'), primary_key=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'), primary_key=True)


class SubtopicToConceptAssociation(Base):
    __tablename__ = 'subtopic_to_concept_association'
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'), primary_key=True)
    concept_id = Column(Integer, ForeignKey('concepts.id'), primary_key=True)

```

## File: authentication.py
```py
# filename: app/models/authentication.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, nullable=False, index=True)  # JWT ID
    token = Column(String(500), unique=True, nullable=False)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<RevokedTokenModel(id={self.id}, jti='{self.jti}', revoked_at='{self.revoked_at}')>"

```

## File: concepts.py
```py
# filename: app/models/concepts.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class ConceptModel(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)

    subtopics = relationship("SubtopicModel", secondary="subtopic_to_concept_association", back_populates="concepts")
    questions = relationship("QuestionModel", secondary="question_to_concept_association", back_populates="concepts")

    def __repr__(self):
        return f"<Concept(id={self.id}, name='{self.name}')>"

```

## File: disciplines.py
```py
# filename: app/models/disciplines.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class DisciplineModel(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    domains = relationship("DomainModel", secondary="domain_to_discipline_association", back_populates="disciplines")
    subjects = relationship("SubjectModel", secondary="discipline_to_subject_association", back_populates="disciplines")

    def __repr__(self):
        return f"<Discipline(id={self.id}, name='{self.name}', domain_id={self.domain_id})>"

```

## File: domains.py
```py
# filename: app/models/domains.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class DomainModel(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    disciplines = relationship("DisciplineModel", secondary="domain_to_discipline_association", back_populates="domains")

    def __repr__(self):
        return f"<Domain(id={self.id}, name='{self.name}')>"

```

## File: groups.py
```py
# filename: app/models/groups.py

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class GroupModel(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500))
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("UserModel", secondary="user_to_group_association", back_populates="groups")
    creator = relationship("UserModel", back_populates="created_groups", foreign_keys=[creator_id])
    leaderboards = relationship("LeaderboardModel", back_populates="group", cascade="all, delete-orphan")
    question_sets = relationship("QuestionSetModel", secondary="question_set_to_group_association", back_populates="groups")

    def __repr__(self):
        return f"<GroupModel(id={self.id}, name='{self.name}', creator_id={self.creator_id}, is_active={self.is_active})>"

```

## File: leaderboard.py
```py
# filename: app/models/leaderboard.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class LeaderboardModel(Base):
    __tablename__ = "leaderboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    time_period_id = Column(Integer, ForeignKey("time_periods.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="leaderboards")
    group = relationship("GroupModel", back_populates="leaderboards")
    time_period = relationship("TimePeriodModel")

    def __repr__(self):
        return f"<LeaderboardModel(id={self.id}, user_id={self.user_id}, score={self.score}, time_period={self.time_period}, group_id={self.group_id})>"

```

## File: permissions.py
```py
# filename: app/models/permissions.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.associations import RoleToPermissionAssociation

class PermissionModel(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
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

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class QuestionSetModel(Base):
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(String(1000))
    is_public = Column(Boolean, default=True, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    creator = relationship("UserModel", back_populates="created_question_sets")
    questions = relationship("QuestionModel", secondary="question_set_to_question_association", back_populates="question_sets")
    groups = relationship("GroupModel", secondary="question_set_to_group_association", back_populates="question_sets")

    def __repr__(self):
        return f"<QuestionSetModel(id={self.id}, name='{self.name}', is_public={self.is_public}, creator_id={self.creator_id})>"

```

## File: question_tags.py
```py
# filename: app/models/question_tags.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class QuestionTagModel(Base):
    __tablename__ = "question_tags"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    questions = relationship("QuestionModel", secondary="question_to_tag_association", back_populates="question_tags")

    def __repr__(self):
        return f"<QuestionTagModel(id={self.id}, tag='{self.tag}')>"

```

## File: questions.py
```py
# filename: app/models/questions.py

from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from enum import Enum as PyEnum

class DifficultyLevel(PyEnum):
    BEGINNER = "Beginner"
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"

class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(10000), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    subjects = relationship("SubjectModel", secondary="question_to_subject_association", back_populates="questions")
    topics = relationship("TopicModel", secondary="question_to_topic_association", back_populates="questions")
    subtopics = relationship("SubtopicModel", secondary="question_to_subtopic_association", back_populates="questions")
    concepts = relationship("ConceptModel", secondary="question_to_concept_association", back_populates="questions")
    question_tags = relationship("QuestionTagModel", secondary="question_to_tag_association", back_populates="questions")
    answer_choices = relationship("AnswerChoiceModel", secondary="question_to_answer_association", back_populates="questions")
    question_sets = relationship("QuestionSetModel", secondary="question_set_to_question_association", back_populates="questions")
    user_responses = relationship("UserResponseModel", back_populates="question", cascade="all, delete-orphan")
    creator = relationship("UserModel", back_populates="created_questions")

    def __repr__(self):
        return f"<QuestionModel(id={self.id}, text='{self.text[:50]}...', difficulty='{self.difficulty}')>"

```

## File: roles.py
```py
# filename: app/models/roles.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.associations import RoleToPermissionAssociation

class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200))
    default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    users = relationship("UserModel", back_populates="role")
    permissions = relationship(
        "PermissionModel",
        secondary=RoleToPermissionAssociation.__tablename__,
        back_populates="roles"
    )

    def __repr__(self):
        return f"<RoleModel(id={self.id}, name='{self.name}', default={self.default})>"

```

## File: subjects.py
```py
# filename: app/models/subjects.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class SubjectModel(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    disciplines = relationship("DisciplineModel", secondary="discipline_to_subject_association", back_populates="subjects")
    topics = relationship("TopicModel", secondary="subject_to_topic_association", back_populates="subjects")
    questions = relationship("QuestionModel", secondary="question_to_subject_association", back_populates="subjects")

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}')>"

```

## File: subtopics.py
```py
# filename: app/models/subtopics.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class SubtopicModel(Base):
    __tablename__ = "subtopics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)

    topics = relationship("TopicModel", secondary="topic_to_subtopic_association", back_populates="subtopics")
    concepts = relationship("ConceptModel", secondary="subtopic_to_concept_association", back_populates="subtopics")
    questions = relationship("QuestionModel", secondary="question_to_subtopic_association", back_populates="subtopics")

    def __repr__(self):
        return f"<Subtopic(id={self.id}, name='{self.name}')>"

```

## File: time_period.py
```py
# filename: app/models/time_period.py

from sqlalchemy import Column, Integer, String
from app.db.base import Base

class TimePeriodModel(Base):
    __tablename__ = "time_periods"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(20), unique=True, nullable=False)

    @classmethod
    def daily(cls):
        return cls(id=1, name="daily")

    @classmethod
    def weekly(cls):
        return cls(id=7, name="weekly")

    @classmethod
    def monthly(cls):
        return cls(id=30, name="monthly")

    @classmethod
    def yearly(cls):
        return cls(id=365, name="yearly")

    def __repr__(self):
        return f"<TimePeriodModel(id={self.id}, name='{self.name}')>"

```

## File: topics.py
```py
# filename: app/models/topics.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class TopicModel(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)

    subjects = relationship("SubjectModel", secondary="subject_to_topic_association", back_populates="topics")
    subtopics = relationship("SubtopicModel", secondary="topic_to_subtopic_association", back_populates="topics")
    questions = relationship("QuestionModel", secondary="question_to_topic_association", back_populates="topics")

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}')>"

```

## File: user_responses.py
```py
# filename: app/models/user_responses.py

from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class UserResponseModel(Base):
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_choice_id = Column(Integer, ForeignKey("answer_choices.id", ondelete="SET NULL"), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    response_time = Column(Integer, nullable=True)  # Response time in seconds
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("UserModel", back_populates="responses")
    question = relationship("QuestionModel", back_populates="user_responses")
    answer_choice = relationship("AnswerChoiceModel", back_populates="user_responses")

    def __repr__(self):
        return f"<UserResponseModel(id={self.id}, user_id={self.user_id}, question_id={self.question_id}, is_correct={self.is_correct})>"

```

## File: users.py
```py
# filename: app/models/users.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    # Relationships
    role = relationship("RoleModel", back_populates="users")
    responses = relationship("UserResponseModel", back_populates="user", cascade="all, delete-orphan")
    groups = relationship("GroupModel", secondary="user_to_group_association", back_populates="users")
    leaderboards = relationship("LeaderboardModel", back_populates="user", cascade="all, delete-orphan")
    created_groups = relationship("GroupModel", back_populates="creator", cascade="all, delete-orphan")
    created_question_sets = relationship("QuestionSetModel", back_populates="creator", cascade="all, delete-orphan")
    created_questions = relationship("QuestionModel", back_populates="creator")  # Add this line

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role_id='{self.role_id}')>"

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

from passlib.context import CryptContext
from app.services.logging_service import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    result = pwd_context.verify(plain_password, hashed_password)
    logger.debug(f"verify_password called with plain_password: {plain_password}, hashed_password: {hashed_password}")
    logger.debug(f"verify_password result: {result}")
    return result

def get_password_hash(password):
    hashed = pwd_context.hash(password)
    logger.debug(f"get_password_hash called with password: {password}")
    logger.debug(f"get_password_hash result: {hashed}")
    return hashed

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
from app.db.base import Base
from app.db.session import get_db, init_db

# CRUD imports
from app.crud.crud_answer_choices import create_answer_choice_crud
from app.crud.crud_user import create_user_crud
from app.crud.crud_question_sets import create_question_set_crud
from app.crud.crud_question_tags import create_question_tag_crud, delete_question_tag_crud
from app.crud.crud_roles import create_role_crud, delete_role_crud
from app.crud.crud_groups import create_group_crud, read_group_crud
from app.crud.crud_domains import create_domain
from app.crud.crud_disciplines import create_discipline
from app.crud.crud_subjects import create_subject
from app.crud.crud_topics import create_topic
from app.crud.crud_subtopics import create_subtopic
from app.crud.crud_concepts import create_concept
from app.crud.crud_questions import create_question, create_question_with_answers

# Schema imports
from app.schemas.user import UserCreateSchema
from app.schemas.groups import GroupCreateSchema
from app.schemas.question_sets import QuestionSetCreateSchema
from app.schemas.question_tags import QuestionTagCreateSchema
from app.schemas.questions import QuestionCreateSchema, QuestionWithAnswersCreateSchema
from app.schemas.roles import RoleCreateSchema
from app.schemas.answer_choices import AnswerChoiceCreateSchema
from app.schemas.domains import DomainCreateSchema
from app.schemas.disciplines import DisciplineCreateSchema
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.topics import TopicCreateSchema
from app.schemas.subtopics import SubtopicCreateSchema
from app.schemas.concepts import ConceptCreateSchema

# Model imports
from app.models.associations import UserToGroupAssociation
from app.models.answer_choices import AnswerChoiceModel
from app.models.authentication import RevokedTokenModel
from app.models.groups import GroupModel
from app.models.leaderboard import LeaderboardModel
from app.models.permissions import PermissionModel
from app.models.question_sets import QuestionSetModel
from app.models.question_tags import QuestionTagModel
from app.models.questions import QuestionModel, DifficultyLevel
from app.models.roles import RoleModel
from app.models.domains import DomainModel
from app.models.disciplines import DisciplineModel
from app.models.subjects import SubjectModel
from app.models.concepts import ConceptModel
from app.models.subtopics import SubtopicModel
from app.models.time_period import TimePeriodModel
from app.models.topics import TopicModel
from app.models.user_responses import UserResponseModel
from app.models.users import UserModel
from app.core.jwt import create_access_token
from app.core.security import get_password_hash
from app.services.permission_generator_service import generate_permissions
from app.services.logging_service import logger, sqlalchemy_obj_to_dict


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
        session.rollback()
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

@pytest.fixture(scope='function')
def test_permission(db_session):
    from app.models.permissions import PermissionModel
    permission = PermissionModel(name="test_permission", description="A test permission")
    db_session.add(permission)
    db_session.commit()
    return permission

@pytest.fixture(scope="function")
def test_permissions(db_session):
    from app.main import app  # Import the actual FastAPI app instance
    from app.services.permission_generator_service import generate_permissions, ensure_permissions_in_db

    # Generate permissions
    permissions = generate_permissions(app)
    
    # Ensure permissions are in the database
    ensure_permissions_in_db(db_session, permissions)

    # Fetch and return the permissions from the database
    db_permissions = db_session.query(PermissionModel).all()
    
    yield db_permissions

    # Clean up (optional, depending on your test isolation needs)
    db_session.query(PermissionModel).delete()
    db_session.commit()

@pytest.fixture(scope="function")
def test_role(db_session, test_permissions):
    try:
        # Create a test role with all permissions
        role = RoleModel(
            name="test_role",
            description="Test Role",
            default=False
        )
        role.permissions.extend(test_permissions)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        yield role
    except Exception as e:
        logger.exception(f"Error in test_role fixture: {str(e)}")
        raise
    finally:
        logger.debug("Tearing down test_role fixture")
        db_session.rollback()

@pytest.fixture(scope="function")
def random_username():
    yield "test.user_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))

@pytest.fixture(scope="function")
def test_user(db_session, random_username, test_role):
    try:
        logger.debug("Setting up test_user fixture")
        email = f"{random_username}@example.com"
        hashed_password = get_password_hash("TestPassword123!")
        
        logger.error(f"Creating test user with role ID: {test_role.id}")
        user = UserModel(
            username=random_username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
            role_id=test_role.id
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        logger.error(f"Created test user: {sqlalchemy_obj_to_dict(user)}")
        yield user
    except Exception as e:
        logger.exception(f"Error in test_user fixture: {str(e)}")
        raise
    finally:
        logger.debug("Tearing down test_user fixture")
        db_session.rollback()

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

@pytest.fixture(scope='function')
def test_question_set_data(db_session, test_user_with_group):
    try:
        logger.debug("Setting up test_question_set_data fixture")
        test_question_set_data_create = {
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
def test_answer_choices(db_session):
    answer_choices = [
        AnswerChoiceModel(text="Answer 1", is_correct=True, explanation="Explanation 1"),
        AnswerChoiceModel(text="Answer 2", is_correct=False, explanation="Explanation 2"),
        AnswerChoiceModel(text="Answer 3", is_correct=False, explanation="Explanation 3"),
        AnswerChoiceModel(text="Answer 4", is_correct=True, explanation="Explanation 4")
    ]
    
    db_answer_choices = []
    for answer_choice in answer_choices:
        db_session.add(answer_choice)
        db_session.commit()
        db_session.refresh(answer_choice)
        db_answer_choices.append(answer_choice)
    
    yield db_answer_choices

@pytest.fixture(scope="function")
def test_questions(db_session, test_subject, test_topic, test_subtopic, test_concept, test_answer_choices):
    try:
        logger.debug("Setting up test_questions fixture")
        question1 = QuestionModel(text="Test Question 1", difficulty=DifficultyLevel.EASY)
        #question1.answer_choices.append([test_answer_choices[0], test_answer_choices[1]])
        question2 = QuestionModel(text="Test Question 2", difficulty=DifficultyLevel.MEDIUM)
        #question2.answer_choices.append([test_answer_choices[2], test_answer_choices[3]])
        questions = [question1, question2]
        
        for question in questions:
            question.subjects.append(test_subject)
            question.topics.append(test_topic)
            question.subtopics.append(test_subtopic)
            question.concepts.append(test_concept)
        
        db_session.add_all(questions)
        db_session.commit()

        yield questions
    except Exception as e:
        logger.exception("Error in test_questions fixture: %s", str(e))
        raise
    finally:
        logger.debug("Tearing down test_questions fixture")

@pytest.fixture(scope="function")
def test_domain(db_session):
    domain = DomainModel(name="Test Domain")
    yield domain


@pytest.fixture(scope="function")
def test_discipline(db_session, test_domain):
    discipline = DisciplineModel(name="Test Discipline")
    db_session.add(discipline)
    db_session.commit()
    yield discipline


@pytest.fixture(scope="function")
def test_subject(db_session, test_discipline):
    subject = SubjectModel(name="Test Subject")
    subject.disciplines.append(test_discipline)
    db_session.add(subject)
    db_session.commit()
    yield subject


@pytest.fixture(scope="function")
def test_topic(db_session, test_subject):
    topic = TopicModel(name="Test Topic")
    topic.subjects.append(test_subject)
    db_session.add(topic)
    db_session.commit()
    yield topic


@pytest.fixture(scope="function")
def test_subtopic(db_session, test_topic):
    subtopic = SubtopicModel(name="Test Subtopic")
    subtopic.topics.append(test_topic)
    db_session.add(subtopic)
    db_session.commit()
    yield subtopic


@pytest.fixture(scope="function")
def test_concept(db_session, test_subtopic):
    concept = ConceptModel(name="Test Concept")
    concept.subtopics.append(test_subtopic)
    db_session.add(concept)
    db_session.commit()
    yield concept


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

        # Create Domains
        domain1 = create_domain(db_session, DomainCreateSchema(name="Science"))
        domain2 = create_domain(db_session, DomainCreateSchema(name="Mathematics"))

        # Create Disciplines
        discipline1 = create_discipline(db_session, DisciplineCreateSchema(name="Physics", domain=domain1))
        discipline2 = create_discipline(db_session, DisciplineCreateSchema(name="Pure Mathematics", domain=domain2))

        # Create Subjects
        subject1 = create_subject(db_session, SubjectCreateSchema(name="Classical Mechanics", discipline=discipline1))
        subject2 = create_subject(db_session, SubjectCreateSchema(name="Algebra", discipline=discipline2))

        # Create Topics
        topic1 = create_topic(db_session, TopicCreateSchema(name="Newton's Laws", subject=subject1))
        topic2 = create_topic(db_session, TopicCreateSchema(name="Linear Algebra", subject=subject2))

        # Create Subtopics
        subtopic1 = create_subtopic(db_session, SubtopicCreateSchema(name="First Law of Motion", topic=topic1))
        subtopic2 = create_subtopic(db_session, SubtopicCreateSchema(name="Second Law of Motion", topic=topic1))
        subtopic3 = create_subtopic(db_session, SubtopicCreateSchema(name="Matrices", topic=topic2))
        subtopic4 = create_subtopic(db_session, SubtopicCreateSchema(name="Vector Spaces", topic=topic2))

        # Create Concepts
        concept1 = create_concept(db_session, ConceptCreateSchema(name="Inertia", subtopic=subtopic1))
        concept2 = create_concept(db_session, ConceptCreateSchema(name="Force and Acceleration", subtopic=subtopic2))
        concept3 = create_concept(db_session, ConceptCreateSchema(name="Matrix Operations", subtopic=subtopic3))
        concept4 = create_concept(db_session, ConceptCreateSchema(name="Linear Independence", subtopic=subtopic4))

        # Create Tags
        tag1 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="physics"))
        tag2 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="mathematics"))
        tag3 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="mechanics"))
        tag4 = create_question_tag_crud(db_session, QuestionTagCreateSchema(tag="linear algebra"))

        # Create Question Sets
        question_set1 = create_question_set_crud(db_session, QuestionSetCreateSchema(name="Physics Question Set", is_public=True))
        question_set2 = create_question_set_crud(db_session, QuestionSetCreateSchema(name="Math Question Set", is_public=True))

        # Create Questions
        question1 = create_question(db_session, QuestionCreateSchema(
            text="What is Newton's First Law of Motion?",
            subject=subject1,
            topic=topic1,
            subtopic=subtopic1,
            concept=concept1,
            difficulty=DifficultyLevel.EASY,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id]
        ))
        question2 = create_question(db_session, QuestionCreateSchema(
            text="How does force relate to acceleration according to Newton's Second Law?",
            subject=subject1,
            topic=topic1,
            subtopic=subtopic2,
            concept=concept2,
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id]
        ))
        question3 = create_question(db_session, QuestionCreateSchema(
            text="What is the result of multiplying a 2x2 identity matrix with any 2x2 matrix?",
            subject=subject2,
            topic=topic2,
            subtopic=subtopic3,
            concept=concept3,
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id]
        ))
        question4 = create_question(db_session, QuestionCreateSchema(
            text="What does it mean for a set of vectors to be linearly independent?",
            subject=subject2,
            topic=topic2,
            subtopic=subtopic4,
            concept=concept4,
            difficulty=DifficultyLevel.HARD,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id]
        ))

        logger.debug("Filter questions data setup completed successfully")

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

## File: test_schemas_answer_choices.py
```py
# filename: tests/test_schemas_answer_choices.py

import pytest
from pydantic import ValidationError
from app.schemas.answer_choices import AnswerChoiceBaseSchema, AnswerChoiceCreateSchema, AnswerChoiceUpdateSchema, AnswerChoiceSchema

def test_answer_choice_base_schema_valid():
    data = {
        "text": "This is a valid answer choice",
        "is_correct": True,
        "explanation": "This is a valid explanation"
    }
    schema = AnswerChoiceBaseSchema(**data)
    assert schema.text == "This is a valid answer choice"
    assert schema.is_correct is True
    assert schema.explanation == "This is a valid explanation"

def test_answer_choice_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        AnswerChoiceBaseSchema(text="", is_correct=True)
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        AnswerChoiceBaseSchema(text="a" * 10001, is_correct=True)
    assert "String should have at most 10000 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        AnswerChoiceBaseSchema(text="Valid text", is_correct="not a boolean")
    assert "Input should be a valid boolean" in str(exc_info.value)

def test_answer_choice_create_schema():
    data = {
        "text": "This is a new answer choice",
        "is_correct": False,
        "explanation": "This is an explanation for the new answer choice"
    }
    schema = AnswerChoiceCreateSchema(**data)
    assert schema.text == "This is a new answer choice"
    assert schema.is_correct is False
    assert schema.explanation == "This is an explanation for the new answer choice"

def test_answer_choice_update_schema():
    data = {
        "text": "Updated answer choice",
        "is_correct": True
    }
    schema = AnswerChoiceUpdateSchema(**data)
    assert schema.text == "Updated answer choice"
    assert schema.is_correct is True
    assert schema.explanation is None

    # Test partial update
    partial_data = {"text": "Partially updated answer"}
    partial_schema = AnswerChoiceUpdateSchema(**partial_data)
    assert partial_schema.text == "Partially updated answer"
    assert partial_schema.is_correct is None
    assert partial_schema.explanation is None

def test_answer_choice_schema():
    data = {
        "id": 1,
        "text": "This is a complete answer choice",
        "is_correct": True,
        "explanation": "This is a complete explanation"
    }
    schema = AnswerChoiceSchema(**data)
    assert schema.id == 1
    assert schema.text == "This is a complete answer choice"
    assert schema.is_correct is True
    assert schema.explanation == "This is a complete explanation"

def test_answer_choice_schema_from_orm(test_answer_choices):
    orm_object = test_answer_choices[0]
    schema = AnswerChoiceSchema.model_validate(orm_object)
    assert schema.id == orm_object.id
    assert schema.text == orm_object.text
    assert schema.is_correct == orm_object.is_correct
    assert schema.explanation == orm_object.explanation

```

## File: test_schemas_concepts.py
```py
# filename: tests/test_schemas_concepts.py

import pytest
from pydantic import ValidationError
from app.schemas.concepts import ConceptBaseSchema, ConceptCreateSchema, ConceptUpdateSchema, ConceptSchema

def test_concept_base_schema_valid():
    data = {
        "name": "Pythagorean Theorem"
    }
    schema = ConceptBaseSchema(**data)
    assert schema.name == "Pythagorean Theorem"

def test_concept_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        ConceptBaseSchema(name="")
    assert "Concept name cannot be empty or whitespace" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        ConceptBaseSchema(name="a" * 101)
    assert "ensure this value has at most 100 characters" in str(exc_info.value)

def test_concept_create_schema():
    data = {
        "name": "Law of Cosines",
        "subtopic_ids": [1, 2]
    }
    schema = ConceptCreateSchema(**data)
    assert schema.name == "Law of Cosines"
    assert schema.subtopic_ids == [1, 2]

def test_concept_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        ConceptCreateSchema(name="Law of Cosines", subtopic_ids=[])
    assert "List should have at least 1 item after validation" in str(exc_info.value)

def test_concept_update_schema():
    data = {
        "name": "Updated Law of Cosines",
        "subtopic_ids": [2, 3]
    }
    schema = ConceptUpdateSchema(**data)
    assert schema.name == "Updated Law of Cosines"
    assert schema.subtopic_ids == [2, 3]

    # Test partial update
    partial_data = {"name": "Partially Updated Concept"}
    partial_schema = ConceptUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Concept"
    assert partial_schema.subtopic_ids is None

def test_concept_schema():
    data = {
        "id": 1,
        "name": "Complete Concept",
        "subtopic_ids": [1, 2],
        "question_ids": [1, 2]
    }
    schema = ConceptSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Concept"
    assert schema.subtopic_ids == [1, 2]
    assert schema.question_ids == [1, 2]

def test_concept_schema_from_attributes(test_concept):
    schema = ConceptSchema.model_validate(test_concept)
    assert schema.id == test_concept.id
    assert schema.name == test_concept.name
    assert set(schema.subtopic_ids) == set(st.id for st in test_concept.subtopics)

```

## File: test_schemas_disciplines.py
```py
# filename: tests/test_schemas_disciplines.py

import pytest
from pydantic import ValidationError
from app.schemas.disciplines import DisciplineBaseSchema, DisciplineCreateSchema, DisciplineUpdateSchema, DisciplineSchema

def test_discipline_base_schema_valid():
    data = {
        "name": "Natural Sciences"
    }
    schema = DisciplineBaseSchema(**data)
    assert schema.name == "Natural Sciences"

def test_discipline_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        DisciplineBaseSchema(name="")
    assert "ensure this value has at least 1 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        DisciplineBaseSchema(name="a" * 101)
    assert "ensure this value has at most 100 characters" in str(exc_info.value)

def test_discipline_create_schema():
    data = {
        "name": "Social Sciences",
        "domain_ids": [1, 2],
        "subject_ids": [3, 4, 5]
    }
    schema = DisciplineCreateSchema(**data)
    assert schema.name == "Social Sciences"
    assert schema.domain_ids == [1, 2]
    assert schema.subject_ids == [3, 4, 5]

def test_discipline_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        DisciplineCreateSchema(name="Social Sciences", domain_ids=[])
    assert "List should have at least 1 item after validation" in str(exc_info.value)

def test_discipline_update_schema():
    data = {
        "name": "Updated Social Sciences",
        "domain_ids": [2, 3],
        "subject_ids": [4, 5, 6]
    }
    schema = DisciplineUpdateSchema(**data)
    assert schema.name == "Updated Social Sciences"
    assert schema.domain_ids == [2, 3]
    assert schema.subject_ids == [4, 5, 6]

    # Test partial update
    partial_data = {"name": "Partially Updated Discipline"}
    partial_schema = DisciplineUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Discipline"
    assert partial_schema.domain_ids is None
    assert partial_schema.subject_ids is None

def test_discipline_schema():
    data = {
        "id": 1,
        "name": "Complete Discipline",
        "domain_ids": [1, 2],
        "subject_ids": [3, 4, 5]
    }
    schema = DisciplineSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Discipline"
    assert schema.domain_ids == [1, 2]
    assert schema.subject_ids == [3, 4, 5]

def test_discipline_schema_from_attributes(db_session, test_discipline):
    schema = DisciplineSchema.model_validate(test_discipline)
    assert schema.id == test_discipline.id
    assert schema.name == test_discipline.name
    assert set(schema.domain_ids) == set(d.id for d in test_discipline.domains)
    assert set(schema.subject_ids) == set(s.id for s in test_discipline.subjects)

```

## File: test_schemas_domains.py
```py
# filename: tests/test_schemas_domains.py

import pytest
from pydantic import ValidationError
from app.schemas.domains import DomainBaseSchema, DomainCreateSchema, DomainUpdateSchema, DomainSchema

def test_domain_base_schema_valid():
    data = {
        "name": "Science and Technology"
    }
    schema = DomainBaseSchema(**data)
    assert schema.name == "Science and Technology"

def test_domain_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        DomainBaseSchema(name="")
    assert "ensure this value has at least 1 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        DomainBaseSchema(name="a" * 101)
    assert "ensure this value has at most 100 characters" in str(exc_info.value)

def test_domain_create_schema():
    data = {
        "name": "Arts and Humanities",
        "discipline_ids": [1, 2, 3]
    }
    schema = DomainCreateSchema(**data)
    assert schema.name == "Arts and Humanities"
    assert schema.discipline_ids == [1, 2, 3]

def test_domain_create_schema_optional_disciplines():
    data = {
        "name": "New Domain"
    }
    schema = DomainCreateSchema(**data)
    assert schema.name == "New Domain"
    assert schema.discipline_ids is None

def test_domain_update_schema():
    data = {
        "name": "Updated Arts and Humanities",
        "discipline_ids": [2, 3, 4]
    }
    schema = DomainUpdateSchema(**data)
    assert schema.name == "Updated Arts and Humanities"
    assert schema.discipline_ids == [2, 3, 4]

    # Test partial update
    partial_data = {"name": "Partially Updated Domain"}
    partial_schema = DomainUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Domain"
    assert partial_schema.discipline_ids is None

def test_domain_schema():
    data = {
        "id": 1,
        "name": "Complete Domain",
        "discipline_ids": [1, 2, 3]
    }
    schema = DomainSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Domain"
    assert schema.discipline_ids == [1, 2, 3]

def test_domain_schema_from_attributes(db_session, test_domain):
    schema = DomainSchema.model_validate(test_domain)
    assert schema.id == test_domain.id
    assert schema.name == test_domain.name
    assert set(schema.discipline_ids) == set(d.id for d in test_domain.disciplines)

```

## File: test_schemas_filters.py
```py
# filename: tests/test_schemas_filters.py

import pytest
from pydantic import ValidationError
from app.schemas.filters import FilterParamsSchema
from app.schemas.questions import DifficultyLevel

def test_filter_params_schema_valid():
    data = {
        "subject": "Mathematics",
        "topic": "Algebra",
        "subtopic": "Linear Equations",
        "difficulty": DifficultyLevel.MEDIUM,
        "question_tags": ["math", "algebra"]
    }
    schema = FilterParamsSchema(**data)
    assert schema.subject == "Mathematics"
    assert schema.topic == "Algebra"
    assert schema.subtopic == "Linear Equations"
    assert schema.difficulty == DifficultyLevel.MEDIUM
    assert schema.question_tags == ["math", "algebra"]

def test_filter_params_schema_optional_fields():
    data = {
        "subject": "Physics"
    }
    schema = FilterParamsSchema(**data)
    assert schema.subject == "Physics"
    assert schema.topic is None
    assert schema.subtopic is None
    assert schema.difficulty is None
    assert schema.question_tags is None

def test_filter_params_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        FilterParamsSchema(subject="a" * 101)
    assert "String should have at most 100 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        FilterParamsSchema(difficulty="Invalid")
    assert "Input should be 'Beginner', 'Easy', 'Medium', 'Hard' or 'Expert'" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        FilterParamsSchema(question_tags=["tag1", "tag2"] * 6)
    assert "List should have at most 10 items after validation" in str(exc_info.value)

def test_filter_params_schema_question_tags_lowercase():
    data = {
        "question_tags": ["MATH", "Algebra", "LINEAR"]
    }
    schema = FilterParamsSchema(**data)
    assert schema.question_tags == ["math", "algebra", "linear"]

def test_filter_params_schema_extra_fields():
    with pytest.raises(ValidationError) as exc_info:
        FilterParamsSchema(subject="Math", extra_field="Invalid")
    assert "Extra inputs are not permitted" in str(exc_info.value)

```

## File: test_schemas_groups.py
```py
# filename: tests/test_schemas_groups.py

import pytest
from pydantic import ValidationError
from app.schemas.groups import GroupBaseSchema, GroupCreateSchema, GroupUpdateSchema, GroupSchema

def test_group_base_schema_valid():
    data = {
        "name": "Test Group",
        "description": "This is a test group"
    }
    schema = GroupBaseSchema(**data)
    assert schema.name == "Test Group"
    assert schema.description == "This is a test group"

def test_group_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        GroupBaseSchema(name="", description="Invalid group")
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        GroupBaseSchema(name="a" * 101, description="Invalid group")
    assert "String should have at most 100 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        GroupBaseSchema(name="Invalid@Group", description="Invalid group")
    assert "Group name can only contain alphanumeric characters, hyphens, underscores, and spaces" in str(exc_info.value)

def test_group_create_schema(test_user):
    data = {
        "name": "New Group",
        "description": "This is a new group",
        "creator_id": test_user.id
    }
    schema = GroupCreateSchema(**data)
    assert schema.name == "New Group"
    assert schema.description == "This is a new group"
    assert schema.creator_id == test_user.id

def test_group_update_schema():
    data = {
        "name": "Updated Group",
        "description": "This group has been updated"
    }
    schema = GroupUpdateSchema(**data)
    assert schema.name == "Updated Group"
    assert schema.description == "This group has been updated"

    # Test partial update
    partial_data = {"name": "Partially Updated Group"}
    partial_schema = GroupUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Group"
    assert partial_schema.description is None

def test_group_schema(test_user):
    data = {
        "id": 1,
        "name": "Complete Group",
        "description": "This is a complete group",
        "creator_id": test_user.id,
        "user_ids": [test_user.id],
        "question_set_ids": [1, 2, 3]
    }
    schema = GroupSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Group"
    assert schema.description == "This is a complete group"
    assert schema.creator_id == test_user.id
    assert schema.user_ids == [test_user.id]
    assert schema.question_set_ids == [1, 2, 3]

def test_group_schema_from_orm(test_group):
    schema = GroupSchema.model_validate(test_group)
    assert schema.id == test_group.id
    assert schema.name == test_group.name
    assert schema.description == test_group.description
    assert schema.creator_id == test_group.creator_id
    assert set(schema.user_ids) == set(user.id for user in test_group.users)
    assert set(schema.question_set_ids) == set(qs.id for qs in test_group.question_sets)

```

## File: test_schemas_leaderboard.py
```py
# filename: tests/test_schemas_leaderboard.py

import pytest
from pydantic import ValidationError
from app.schemas.leaderboard import LeaderboardBaseSchema, LeaderboardCreateSchema, LeaderboardUpdateSchema, LeaderboardSchema, TimePeriodSchema

def test_leaderboard_base_schema_valid():
    data = {
        "user_id": 1,
        "score": 100,
        "time_period_id": 1
    }
    schema = LeaderboardBaseSchema(**data)
    assert schema.user_id == 1
    assert schema.score == 100
    assert schema.time_period_id == 1
    assert schema.group_id is None

def test_leaderboard_base_schema_with_group():
    data = {
        "user_id": 1,
        "score": 100,
        "time_period_id": 1,
        "group_id": 5
    }
    schema = LeaderboardBaseSchema(**data)
    assert schema.user_id == 1
    assert schema.score == 100
    assert schema.time_period_id == 1
    assert schema.group_id == 5

def test_leaderboard_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        LeaderboardBaseSchema(user_id=0, score=100, time_period_id=1)
    assert "Input should be greater than 0" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        LeaderboardBaseSchema(user_id=1, score=-1, time_period_id=1)
    assert "Input should be greater than or equal to 0" in str(exc_info.value)

def test_leaderboard_create_schema():
    data = {
        "user_id": 1,
        "score": 100,
        "time_period_id": 1,
        "group_id": 5
    }
    schema = LeaderboardCreateSchema(**data)
    assert schema.user_id == 1
    assert schema.score == 100
    assert schema.time_period_id == 1
    assert schema.group_id == 5

def test_leaderboard_update_schema():
    data = {
        "score": 150
    }
    schema = LeaderboardUpdateSchema(**data)
    assert schema.score == 150

def test_leaderboard_schema():
    time_period = TimePeriodSchema(id=1, name="daily")
    data = {
        "id": 1,
        "user_id": 1,
        "score": 100,
        "time_period": time_period,
        "group_id": 5
    }
    schema = LeaderboardSchema(**data)
    assert schema.id == 1
    assert schema.user_id == 1
    assert schema.score == 100
    assert schema.time_period == time_period
    assert schema.group_id == 5

def test_leaderboard_schema_from_attributes(db_session, test_user):
    from app.models.leaderboard import LeaderboardModel
    from app.models.time_period import TimePeriodModel

    time_period = TimePeriodModel(id=1, name="daily")
    db_session.add(time_period)
    db_session.commit()

    leaderboard_entry = LeaderboardModel(
        user_id=test_user.id,
        score=100,
        time_period_id=time_period.id,
        group_id=None
    )
    db_session.add(leaderboard_entry)
    db_session.commit()
    db_session.refresh(leaderboard_entry)

    schema = LeaderboardSchema.model_validate(leaderboard_entry)
    assert schema.id == leaderboard_entry.id
    assert schema.user_id == test_user.id
    assert schema.score == 100
    assert schema.time_period.id == time_period.id
    assert schema.time_period.name == "daily"
    assert schema.group_id is None

def test_time_period_schema():
    data = {
        "id": 1,
        "name": "daily"
    }
    schema = TimePeriodSchema(**data)
    assert schema.id == 1
    assert schema.name == "daily"

```

## File: test_schemas_permissions.py
```py
# filename: tests/test_schemas_permissions.py

import pytest
from pydantic import ValidationError
from app.schemas.permissions import PermissionBaseSchema, PermissionCreateSchema, PermissionUpdateSchema, PermissionSchema

def test_permission_base_schema_valid():
    data = {
        "name": "create_user",
        "description": "Permission to create a new user"
    }
    schema = PermissionBaseSchema(**data)
    assert schema.name == "create_user"
    assert schema.description == "Permission to create a new user"

def test_permission_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        PermissionBaseSchema(name="", description="Invalid permission")
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        PermissionBaseSchema(name="a" * 101, description="Invalid permission")
    assert "String should have at most 100 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        PermissionBaseSchema(name="invalid@permission", description="Invalid permission")
    assert "Permission name can only contain alphanumeric characters, underscores, and hyphens" in str(exc_info.value)

def test_permission_create_schema():
    data = {
        "name": "delete_user",
        "description": "Permission to delete a user"
    }
    schema = PermissionCreateSchema(**data)
    assert schema.name == "delete_user"
    assert schema.description == "Permission to delete a user"

def test_permission_update_schema():
    data = {
        "name": "update_user",
        "description": "Updated permission to modify a user"
    }
    schema = PermissionUpdateSchema(**data)
    assert schema.name == "update_user"
    assert schema.description == "Updated permission to modify a user"

    # Test partial update
    partial_data = {"description": "Partially updated description"}
    partial_schema = PermissionUpdateSchema(**partial_data)
    assert partial_schema.name is None
    assert partial_schema.description == "Partially updated description"

def test_permission_schema():
    data = {
        "id": 1,
        "name": "read_user",
        "description": "Permission to read user information"
    }
    schema = PermissionSchema(**data)
    assert schema.id == 1
    assert schema.name == "read_user"
    assert schema.description == "Permission to read user information"

def test_permission_schema_from_attributes(db_session, test_permission):
    schema = PermissionSchema.model_validate(test_permission)
    assert schema.id == test_permission.id
    assert schema.name == test_permission.name
    assert schema.description == test_permission.description

```

## File: test_schemas_question_sets.py
```py
# filename: tests/test_schemas_question_sets.py

import pytest
from pydantic import ValidationError
from app.schemas.question_sets import QuestionSetBaseSchema, QuestionSetCreateSchema, QuestionSetUpdateSchema, QuestionSetSchema

def test_question_set_base_schema_valid():
    data = {
        "name": "Math Quiz Set",
        "description": "A set of math questions",
        "is_public": True
    }
    schema = QuestionSetBaseSchema(**data)
    assert schema.name == "Math Quiz Set"
    assert schema.description == "A set of math questions"
    assert schema.is_public is True

def test_question_set_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        QuestionSetBaseSchema(name="", description="Invalid set", is_public=True)
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QuestionSetBaseSchema(name="a" * 201, description="Invalid set", is_public=True)
    assert "String should have at most 200 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QuestionSetBaseSchema(name="Invalid@Set", description="Invalid set", is_public=True)
    assert "Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces" in str(exc_info.value)

def test_question_set_create_schema(test_user):
    data = {
        "name": "Science Quiz Set",
        "description": "A set of science questions",
        "is_public": False,
        "creator_id": test_user.id,
        "question_ids": [1, 2, 3],
        "group_ids": [1, 2]
    }
    schema = QuestionSetCreateSchema(**data)
    assert schema.name == "Science Quiz Set"
    assert schema.description == "A set of science questions"
    assert schema.is_public is False
    assert schema.creator_id == test_user.id
    assert schema.question_ids == [1, 2, 3]
    assert schema.group_ids == [1, 2]

def test_question_set_update_schema():
    data = {
        "name": "Updated Quiz Set",
        "description": "This set has been updated",
        "is_public": True,
        "question_ids": [4, 5, 6],
        "group_ids": [3, 4]
    }
    schema = QuestionSetUpdateSchema(**data)
    assert schema.name == "Updated Quiz Set"
    assert schema.description == "This set has been updated"
    assert schema.is_public is True
    assert schema.question_ids == [4, 5, 6]
    assert schema.group_ids == [3, 4]

    # Test partial update
    partial_data = {"name": "Partially Updated Set"}
    partial_schema = QuestionSetUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Set"
    assert partial_schema.description is None
    assert partial_schema.is_public is None
    assert partial_schema.question_ids is None
    assert partial_schema.group_ids is None

def test_question_set_schema():
    data = {
        "id": 1,
        "name": "Complete Quiz Set",
        "description": "This is a complete question set",
        "is_public": True,
        "creator_id": 1,
        "question_ids": [1, 2, 3, 4],
        "group_ids": [1, 2, 3]
    }
    schema = QuestionSetSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Quiz Set"
    assert schema.description == "This is a complete question set"
    assert schema.is_public is True
    assert schema.creator_id == 1
    assert schema.question_ids == [1, 2, 3, 4]
    assert schema.group_ids == [1, 2, 3]

def test_question_set_schema_from_attributes(db_session, test_question_set):
    schema = QuestionSetSchema.model_validate(test_question_set)
    assert schema.id == test_question_set.id
    assert schema.name == test_question_set.name
    assert schema.description == test_question_set.description
    assert schema.is_public == test_question_set.is_public
    assert schema.creator_id == test_question_set.creator_id
    assert set(schema.question_ids) == set(q.id for q in test_question_set.questions)
    assert set(schema.group_ids) == set(g.id for g in test_question_set.groups)

```

## File: test_schemas_question_tags.py
```py
# filename: tests/test_schemas_question_tags.py

import pytest
from pydantic import ValidationError
from app.schemas.question_tags import QuestionTagBaseSchema, QuestionTagCreateSchema, QuestionTagUpdateSchema, QuestionTagSchema

def test_question_tag_base_schema_valid():
    data = {
        "tag": "mathematics"
    }
    schema = QuestionTagBaseSchema(**data)
    assert schema.tag == "mathematics"

def test_question_tag_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        QuestionTagBaseSchema(tag="")
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QuestionTagBaseSchema(tag="a" * 51)
    assert "String should have at most 50 characters" in str(exc_info.value)

def test_question_tag_base_schema_lowercase():
    data = {
        "tag": "UPPERCASE"
    }
    schema = QuestionTagBaseSchema(**data)
    assert schema.tag == "uppercase"

def test_question_tag_create_schema():
    data = {
        "tag": "physics"
    }
    schema = QuestionTagCreateSchema(**data)
    assert schema.tag == "physics"

def test_question_tag_update_schema():
    data = {
        "tag": "updated_tag"
    }
    schema = QuestionTagUpdateSchema(**data)
    assert schema.tag == "updated_tag"

    # Test partial update (although in this case, there's only one field)
    partial_data = {}
    partial_schema = QuestionTagUpdateSchema(**partial_data)
    assert partial_schema.tag is None

def test_question_tag_schema():
    data = {
        "id": 1,
        "tag": "biology"
    }
    schema = QuestionTagSchema(**data)
    assert schema.id == 1
    assert schema.tag == "biology"

def test_question_tag_schema_from_attributes(db_session, test_tag):
    schema = QuestionTagSchema.model_validate(test_tag)
    assert schema.id == test_tag.id
    assert schema.tag == test_tag.tag

```

## File: test_schemas_questions.py
```py
# filename: tests/test_schemas_questions.py

import pytest
from pydantic import ValidationError
from app.schemas.questions import QuestionCreateSchema, QuestionUpdateSchema, QuestionWithAnswersCreateSchema, DetailedQuestionSchema, DifficultyLevel
from app.schemas.answer_choices import AnswerChoiceSchema

def test_question_create_schema(test_subject, test_topic, test_subtopic, test_concept):
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subject_ids": [test_subject.id],
        "topic_ids": [test_topic.id],
        "subtopic_ids": [test_subtopic.id],
        "concept_ids": [test_concept.id],
    }
    question_schema = QuestionCreateSchema(**question_data)
    assert question_schema.text == "What is the capital of France?"
    assert question_schema.difficulty == DifficultyLevel.EASY
    assert question_schema.subject_ids == [test_subject.id]
    assert question_schema.topic_ids == [test_topic.id]
    assert question_schema.subtopic_ids == [test_subtopic.id]
    assert question_schema.concept_ids == [test_concept.id]

def test_question_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        QuestionCreateSchema(text="", difficulty=DifficultyLevel.EASY)
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QuestionCreateSchema(text="Valid question", difficulty="Invalid")
    assert "Input should be 'Beginner', 'Easy', 'Medium', 'Hard' or 'Expert'" in str(exc_info.value)

def test_question_update_schema():
    update_data = {
        "text": "Updated question text",
        "difficulty": DifficultyLevel.MEDIUM,
    }
    update_schema = QuestionUpdateSchema(**update_data)
    assert update_schema.text == "Updated question text"
    assert update_schema.difficulty == DifficultyLevel.MEDIUM

def test_question_with_answers_create_schema(test_subject, test_topic, test_subtopic, test_concept):
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subject_ids": [test_subject.id],
        "topic_ids": [test_topic.id],
        "subtopic_ids": [test_subtopic.id],
        "concept_ids": [test_concept.id],
        "answer_choices": [
            {"text": "Paris", "is_correct": True, "explanation": "Paris is the capital of France"},
            {"text": "London", "is_correct": False, "explanation": "London is the capital of the UK"},
        ]
    }
    question_schema = QuestionWithAnswersCreateSchema(**question_data)
    assert question_schema.text == "What is the capital of France?"
    assert question_schema.difficulty == DifficultyLevel.EASY
    assert len(question_schema.answer_choices) == 2
    assert question_schema.answer_choices[0].text == "Paris"
    assert question_schema.answer_choices[0].is_correct is True

def test_detailed_question_schema(test_subject, test_topic, test_subtopic, test_concept):
    question_data = {
        "id": 1,
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subject": test_subject.name,
        "topic": test_topic.name,
        "subtopic": test_subtopic.name,
        "concept": test_concept.name,
        "answer_choices": [
            AnswerChoiceSchema(id=1, text="Paris", is_correct=True, explanation="Paris is the capital of France"),
            AnswerChoiceSchema(id=2, text="London", is_correct=False, explanation="London is the capital of the UK"),
        ],
        "question_tags": ["geography", "capitals"],
        "question_sets": ["European Capitals"]
    }
    detailed_schema = DetailedQuestionSchema(**question_data)
    assert detailed_schema.id == 1
    assert detailed_schema.text == "What is the capital of France?"
    assert detailed_schema.difficulty == DifficultyLevel.EASY
    assert detailed_schema.subject == test_subject.name
    assert detailed_schema.topic == test_topic.name
    assert detailed_schema.subtopic == test_subtopic.name
    assert detailed_schema.concept == test_concept.name
    assert len(detailed_schema.answer_choices) == 2
    assert detailed_schema.question_tags == ["geography", "capitals"]
    assert detailed_schema.question_sets == ["European Capitals"]

```

## File: test_schemas_roles.py
```py
# filename: tests/test_schemas_roles.py

import pytest
from pydantic import ValidationError
from app.schemas.roles import RoleBaseSchema, RoleCreateSchema, RoleUpdateSchema, RoleSchema

def test_role_base_schema_valid():
    data = {
        "name": "admin",
        "description": "Administrator role",
        "default": False
    }
    schema = RoleBaseSchema(**data)
    assert schema.name == "admin"
    assert schema.description == "Administrator role"
    assert schema.default is False

def test_role_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        RoleBaseSchema(name="", description="Invalid role", default=False)
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        RoleBaseSchema(name="a" * 51, description="Invalid role", default=False)
    assert "String should have at most 50 characters" in str(exc_info.value)

def test_role_create_schema():
    data = {
        "name": "moderator",
        "description": "Moderator role",
        "default": False,
        "permissions": ["read_post", "edit_post", "delete_post"]
    }
    schema = RoleCreateSchema(**data)
    assert schema.name == "moderator"
    assert schema.description == "Moderator role"
    assert schema.default is False
    assert set(schema.permissions) == set(["read_post", "edit_post", "delete_post"])

def test_role_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        RoleCreateSchema(name="invalid", description="Invalid role", default=False, permissions=[])
    assert "List should have at least 1 item after validation" in str(exc_info.value)

def test_role_update_schema():
    data = {
        "name": "editor",
        "description": "Updated editor role",
        "permissions": ["read_post", "edit_post"]
    }
    schema = RoleUpdateSchema(**data)
    assert schema.name == "editor"
    assert schema.description == "Updated editor role"
    assert schema.permissions == ["read_post", "edit_post"]

    # Test partial update
    partial_data = {"description": "Partially updated description"}
    partial_schema = RoleUpdateSchema(**partial_data)
    assert partial_schema.name is None
    assert partial_schema.description == "Partially updated description"
    assert partial_schema.permissions is None

def test_role_schema():
    data = {
        "id": 1,
        "name": "user",
        "description": "Regular user role",
        "default": True,
        "permissions": ["read_post", "create_post"]
    }
    schema = RoleSchema(**data)
    assert schema.id == 1
    assert schema.name == "user"
    assert schema.description == "Regular user role"
    assert schema.default is True
    assert schema.permissions == ["read_post", "create_post"]

def test_role_schema_from_attributes(test_role):
    schema = RoleSchema.model_validate(test_role)
    assert schema.id == test_role.id
    assert schema.name == test_role.name
    assert schema.description == test_role.description
    assert schema.default == test_role.default
    assert set(schema.permissions) == set(permission.name for permission in test_role.permissions)

```

## File: test_schemas_subjects.py
```py
# filename: tests/test_schemas_subjects.py

import pytest
from pydantic import ValidationError
from app.schemas.subjects import SubjectBaseSchema, SubjectCreateSchema, SubjectUpdateSchema, SubjectSchema

def test_subject_base_schema_valid():
    data = {
        "name": "Mathematics"
    }
    schema = SubjectBaseSchema(**data)
    assert schema.name == "Mathematics"

def test_subject_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        SubjectBaseSchema(name="")
    assert "Subject name cannot be empty or whitespace" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SubjectBaseSchema(name="a" * 101)
    assert "ensure this value has at most 100 characters" in str(exc_info.value)

def test_subject_create_schema():
    data = {
        "name": "Physics",
        "discipline_ids": [1, 2],
        "topic_ids": [3, 4, 5]
    }
    schema = SubjectCreateSchema(**data)
    assert schema.name == "Physics"
    assert schema.discipline_ids == [1, 2]
    assert schema.topic_ids == [3, 4, 5]

def test_subject_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        SubjectCreateSchema(name="Physics", discipline_ids=[])
    assert "ensure this value has at least 1 items" in str(exc_info.value)

def test_subject_update_schema():
    data = {
        "name": "Updated Physics",
        "discipline_ids": [2, 3],
        "topic_ids": [4, 5, 6]
    }
    schema = SubjectUpdateSchema(**data)
    assert schema.name == "Updated Physics"
    assert schema.discipline_ids == [2, 3]
    assert schema.topic_ids == [4, 5, 6]

    # Test partial update
    partial_data = {"name": "Partially Updated Subject"}
    partial_schema = SubjectUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Subject"
    assert partial_schema.discipline_ids is None
    assert partial_schema.topic_ids is None

def test_subject_schema():
    data = {
        "id": 1,
        "name": "Complete Subject",
        "discipline_ids": [1, 2],
        "topic_ids": [3, 4, 5]
    }
    schema = SubjectSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Subject"
    assert schema.discipline_ids == [1, 2]
    assert schema.topic_ids == [3, 4, 5]

def test_subject_schema_from_attributes(db_session, test_subject):
    schema = SubjectSchema.model_validate(test_subject)
    assert schema.id == test_subject.id
    assert schema.name == test_subject.name
    assert set(schema.discipline_ids) == set(d.id for d in test_subject.disciplines)
    assert set(schema.topic_ids) == set(t.id for t in test_subject.topics)

```

## File: test_schemas_subtopics.py
```py
# filename: tests/test_schemas_subtopics.py

import pytest
from pydantic import ValidationError
from app.schemas.subtopics import SubtopicBaseSchema, SubtopicCreateSchema, SubtopicUpdateSchema, SubtopicSchema

def test_subtopic_base_schema_valid():
    data = {
        "name": "Linear Equations"
    }
    schema = SubtopicBaseSchema(**data)
    assert schema.name == "Linear Equations"

def test_subtopic_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        SubtopicBaseSchema(name="")
    assert "Subtopic name cannot be empty or whitespace" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SubtopicBaseSchema(name="a" * 101)
    assert "ensure this value has at most 100 characters" in str(exc_info.value)

def test_subtopic_create_schema():
    data = {
        "name": "Quadratic Equations",
        "topic_ids": [1, 2],
        "concept_ids": [3, 4, 5]
    }
    schema = SubtopicCreateSchema(**data)
    assert schema.name == "Quadratic Equations"
    assert schema.topic_ids == [1, 2]
    assert schema.concept_ids == [3, 4, 5]

def test_subtopic_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        SubtopicCreateSchema(name="Quadratic Equations", topic_ids=[])
    assert "ensure this value has at least 1 items" in str(exc_info.value)

def test_subtopic_update_schema():
    data = {
        "name": "Updated Quadratic Equations",
        "topic_ids": [2, 3],
        "concept_ids": [4, 5, 6]
    }
    schema = SubtopicUpdateSchema(**data)
    assert schema.name == "Updated Quadratic Equations"
    assert schema.topic_ids == [2, 3]
    assert schema.concept_ids == [4, 5, 6]

    # Test partial update
    partial_data = {"name": "Partially Updated Subtopic"}
    partial_schema = SubtopicUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Subtopic"
    assert partial_schema.topic_ids is None
    assert partial_schema.concept_ids is None

def test_subtopic_schema():
    data = {
        "id": 1,
        "name": "Complete Subtopic",
        "topic_ids": [1, 2],
        "concept_ids": [3, 4, 5]
    }
    schema = SubtopicSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Subtopic"
    assert schema.topic_ids == [1, 2]
    assert schema.concept_ids == [3, 4, 5]

def test_subtopic_schema_from_attributes(db_session, test_subtopic):
    schema = SubtopicSchema.model_validate(test_subtopic)
    assert schema.id == test_subtopic.id
    assert schema.name == test_subtopic.name
    assert set(schema.topic_ids) == set(t.id for t in test_subtopic.topics)
    assert set(schema.concept_ids) == set(c.id for c in test_subtopic.concepts)

```

## File: test_schemas_time_period.py
```py
# filename: tests/test_schemas_time_period.py

import pytest
from pydantic import ValidationError
from app.schemas.time_period import TimePeriodSchema

def test_time_period_schema_valid():
    data = {
        "id": 1,
        "name": "daily"
    }
    schema = TimePeriodSchema(**data)
    assert schema.id == 1
    assert schema.name == "daily"

def test_time_period_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        TimePeriodSchema(id=0, name="invalid")
    assert "Input should be greater than 0" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        TimePeriodSchema(id=1, name="")
    assert "ensure this value has at least 1 characters" in str(exc_info.value)

def test_time_period_schema_from_attributes(db_session):
    from app.models.time_period import TimePeriodModel
    
    time_periods = [
        TimePeriodModel.daily(),
        TimePeriodModel.weekly(),
        TimePeriodModel.monthly(),
        TimePeriodModel.yearly()
    ]
    
    for model in time_periods:
        db_session.add(model)
    db_session.commit()

    for model in time_periods:
        schema = TimePeriodSchema.model_validate(model)
        assert schema.id == model.id
        assert schema.name == model.name

def test_time_period_schema_predefined_values():
    daily = TimePeriodSchema(id=1, name="daily")
    assert daily.id == 1
    assert daily.name == "daily"

    weekly = TimePeriodSchema(id=7, name="weekly")
    assert weekly.id == 7
    assert weekly.name == "weekly"

    monthly = TimePeriodSchema(id=30, name="monthly")
    assert monthly.id == 30
    assert monthly.name == "monthly"

    yearly = TimePeriodSchema(id=365, name="yearly")
    assert yearly.id == 365
    assert yearly.name == "yearly"

```

## File: test_schemas_topics.py
```py
# filename: tests/test_schemas_topics.py

import pytest
from pydantic import ValidationError
from app.schemas.topics import TopicBaseSchema, TopicCreateSchema, TopicUpdateSchema, TopicSchema

def test_topic_base_schema_valid():
    data = {
        "name": "Algebra"
    }
    schema = TopicBaseSchema(**data)
    assert schema.name == "Algebra"

def test_topic_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        TopicBaseSchema(name="")
    assert "Topic name cannot be empty or whitespace" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        TopicBaseSchema(name="a" * 101)
    assert "ensure this value has at most 100 characters" in str(exc_info.value)

def test_topic_create_schema():
    data = {
        "name": "Calculus",
        "subject_ids": [1, 2],
        "subtopic_ids": [3, 4, 5]
    }
    schema = TopicCreateSchema(**data)
    assert schema.name == "Calculus"
    assert schema.subject_ids == [1, 2]
    assert schema.subtopic_ids == [3, 4, 5]

def test_topic_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        TopicCreateSchema(name="Calculus", subject_ids=[])
    assert "ensure this value has at least 1 items" in str(exc_info.value)

def test_topic_update_schema():
    data = {
        "name": "Updated Calculus",
        "subject_ids": [2, 3],
        "subtopic_ids": [4, 5, 6]
    }
    schema = TopicUpdateSchema(**data)
    assert schema.name == "Updated Calculus"
    assert schema.subject_ids == [2, 3]
    assert schema.subtopic_ids == [4, 5, 6]

    # Test partial update
    partial_data = {"name": "Partially Updated Topic"}
    partial_schema = TopicUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Topic"
    assert partial_schema.subject_ids is None
    assert partial_schema.subtopic_ids is None

def test_topic_schema():
    data = {
        "id": 1,
        "name": "Complete Topic",
        "subject_ids": [1, 2],
        "subtopic_ids": [3, 4, 5]
    }
    schema = TopicSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Topic"
    assert schema.subject_ids == [1, 2]
    assert schema.subtopic_ids == [3, 4, 5]

def test_topic_schema_from_attributes(db_session, test_topic):
    schema = TopicSchema.model_validate(test_topic)
    assert schema.id == test_topic.id
    assert schema.name == test_topic.name
    assert set(schema.subject_ids) == set(s.id for s in test_topic.subjects)
    assert set(schema.subtopic_ids) == set(st.id for st in test_topic.subtopics)

```

## File: test_schemas_user.py
```py
# filename: tests/test_schemas_user.py

import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreateSchema, UserUpdateSchema, UserSchema
from app.core.security import verify_password

def test_user_create_schema_valid():
    user_data = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.username == "testuser"
    assert verify_password("TestPassword123!", user_schema.password)
    assert user_schema.email == "testuser@example.com"

def test_user_create_schema_password_validation():
    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="weak", email="test@example.com")
    assert "Value should have at least 8 items after validation" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="nodigits!", email="test@example.com")
    assert "Password must contain at least one digit" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="nouppercase123!", email="test@example.com")
    assert "Password must contain at least one uppercase letter" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="NOLOWERCASE123!", email="test@example.com")
    assert "Password must contain at least one lowercase letter" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="NoSpecialChar123", email="test@example.com")
    assert "Password must contain at least one special character" in str(exc_info.value)

def test_user_create_schema_username_validation():
    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="ab", password="ValidPass123!", email="test@example.com")
    assert "String should have at least 3 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="a" * 51, password="ValidPass123!", email="test@example.com")
    assert "String should have at most 50 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="invalid@user", password="ValidPass123!", email="test@example.com")
    assert "Username must contain only alphanumeric characters" in str(exc_info.value)

def test_user_create_schema_email_validation():
    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="ValidPass123!", email="invalidemail")
    assert "value is not a valid email address" in str(exc_info.value)

def test_user_update_schema():
    update_data = {
        "username": "updateduser",
        "email": "updated@example.com",
        "password": "NewPassword123!"
    }
    update_schema = UserUpdateSchema(**update_data)
    assert update_schema.username == "updateduser"
    assert update_schema.email == "updated@example.com"
    assert verify_password("NewPassword123!", update_schema.password)

def test_user_schema(test_user):
    user_schema = UserSchema.model_validate(test_user)
    assert user_schema.id == test_user.id
    assert user_schema.username == test_user.username
    assert user_schema.email == test_user.email
    assert user_schema.is_active == test_user.is_active
    assert user_schema.is_admin == test_user.is_admin
    assert user_schema.groups == test_user.groups
    assert user_schema.created_groups == test_user.created_groups
    assert user_schema.created_question_sets == test_user.created_question_sets
    assert user_schema.responses == test_user.responses
    assert user_schema.leaderboards == test_user.leaderboards

```

## File: test_schemas_user_responses.py
```py
# filename: tests/test_schemas_user_responses.py

import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
from app.schemas.user_responses import UserResponseBaseSchema, UserResponseCreateSchema, UserResponseUpdateSchema, UserResponseSchema

def test_user_response_base_schema_valid():
    data = {
        "user_id": 1,
        "question_id": 1,
        "answer_choice_id": 1,
        "is_correct": True,
        "response_time": 30
    }
    schema = UserResponseBaseSchema(**data)
    assert schema.user_id == 1
    assert schema.question_id == 1
    assert schema.answer_choice_id == 1
    assert schema.is_correct is True
    assert schema.response_time == 30

def test_user_response_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        UserResponseBaseSchema(user_id=0, question_id=1, answer_choice_id=1, is_correct=True)
    assert "Input should be greater than 0" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserResponseBaseSchema(user_id=1, question_id=1, answer_choice_id=1, is_correct=True, response_time=-1)
    assert "Input should be greater than or equal to 0" in str(exc_info.value)

def test_user_response_create_schema():
    data = {
        "user_id": 1,
        "question_id": 1,
        "answer_choice_id": 1,
        "is_correct": True,
        "response_time": 30,
        "timestamp": datetime.now(timezone.utc)
    }
    schema = UserResponseCreateSchema(**data)
    assert schema.user_id == 1
    assert schema.question_id == 1
    assert schema.answer_choice_id == 1
    assert schema.is_correct is True
    assert schema.response_time == 30
    assert isinstance(schema.timestamp, datetime)

def test_user_response_update_schema():
    data = {
        "is_correct": False,
        "response_time": 45
    }
    schema = UserResponseUpdateSchema(**data)
    assert schema.is_correct is False
    assert schema.response_time == 45

    # Test partial update
    partial_data = {"is_correct": True}
    partial_schema = UserResponseUpdateSchema(**partial_data)
    assert partial_schema.is_correct is True
    assert partial_schema.response_time is None

def test_user_response_schema():
    data = {
        "id": 1,
        "user_id": 1,
        "question_id": 1,
        "answer_choice_id": 1,
        "is_correct": True,
        "response_time": 30,
        "timestamp": datetime.now(timezone.utc)
    }
    schema = UserResponseSchema(**data)
    assert schema.id == 1
    assert schema.user_id == 1
    assert schema.question_id == 1
    assert schema.answer_choice_id == 1
    assert schema.is_correct is True
    assert schema.response_time == 30
    assert isinstance(schema.timestamp, datetime)

def test_user_response_schema_from_attributes(db_session, test_user, test_questions, test_answer_choices):
    from app.models.user_responses import UserResponseModel
    
    user_response = UserResponseModel(
        user_id=test_user.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_answer_choices[0].id,
        is_correct=True,
        response_time=30
    )
    db_session.add(user_response)
    db_session.commit()
    db_session.refresh(user_response)

    schema = UserResponseSchema.model_validate(user_response)
    assert schema.id == user_response.id
    assert schema.user_id == test_user.id
    assert schema.question_id == test_questions[0].id
    assert schema.answer_choice_id == test_answer_choices[0].id
    assert schema.is_correct is True
    assert schema.response_time == 30
    assert isinstance(schema.timestamp, datetime)

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
from app.models.domains import DomainModel
from app.models.disciplines import DisciplineModel
from app.models.subjects import SubjectModel
from app.models.topics import TopicModel
from app.models.subtopics import SubtopicModel
from app.models.concepts import ConceptModel
from app.models.question_tags import QuestionTagModel
from app.models.question_sets import QuestionSetModel
from app.models.questions import QuestionModel
from app.crud.crud_questions import read_question
from app.api.endpoints.filters import filter_questions_endpoint


def test_setup_filter_questions_data(db_session, setup_filter_questions_data):
    # Check if the required data is created in the database
    assert db_session.query(DomainModel).filter(DomainModel.name == "Science").first() is not None
    assert db_session.query(DomainModel).filter(DomainModel.name == "Mathematics").first() is not None
    
    assert db_session.query(DisciplineModel).filter(DisciplineModel.name == "Physics").first() is not None
    assert db_session.query(DisciplineModel).filter(DisciplineModel.name == "Pure Mathematics").first() is not None
    
    assert db_session.query(SubjectModel).filter(SubjectModel.name == "Classical Mechanics").first() is not None
    assert db_session.query(SubjectModel).filter(SubjectModel.name == "Algebra").first() is not None
    
    assert db_session.query(TopicModel).filter(TopicModel.name == "Newton's Laws").first() is not None
    assert db_session.query(TopicModel).filter(TopicModel.name == "Linear Algebra").first() is not None
    
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "First Law of Motion").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Second Law of Motion").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Matrices").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Vector Spaces").first() is not None
    
    assert db_session.query(ConceptModel).filter(ConceptModel.name == "Inertia").first() is not None
    assert db_session.query(ConceptModel).filter(ConceptModel.name == "Force and Acceleration").first() is not None
    assert db_session.query(ConceptModel).filter(ConceptModel.name == "Matrix Operations").first() is not None
    assert db_session.query(ConceptModel).filter(ConceptModel.name == "Linear Independence").first() is not None
    
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "physics").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "mathematics").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "mechanics").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "linear algebra").first() is not None
    
    assert db_session.query(QuestionSetModel).filter(QuestionSetModel.name == "Physics Question Set").first() is not None
    assert db_session.query(QuestionSetModel).filter(QuestionSetModel.name == "Math Question Set").first() is not None
    
    assert db_session.query(QuestionModel).count() == 4

    # Check if the topics are correctly associated with their respective subjects
    newtons_laws_topic = db_session.query(TopicModel).filter(TopicModel.name == "Newton's Laws").first()
    assert newtons_laws_topic.subject.name == "Classical Mechanics"

    linear_algebra_topic = db_session.query(TopicModel).filter(TopicModel.name == "Linear Algebra").first()
    assert linear_algebra_topic.subject.name == "Algebra"

    # Check if the subtopics are correctly associated with their respective topics
    first_law_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "First Law of Motion").first()
    assert first_law_subtopic.topic.name == "Newton's Laws"

    second_law_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Second Law of Motion").first()
    assert second_law_subtopic.topic.name == "Newton's Laws"

    matrices_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Matrices").first()
    assert matrices_subtopic.topic.name == "Linear Algebra"

    vector_spaces_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Vector Spaces").first()
    assert vector_spaces_subtopic.topic.name == "Linear Algebra"

    # Check if the concepts are correctly associated with their respective subtopics
    inertia_concept = db_session.query(ConceptModel).filter(ConceptModel.name == "Inertia").first()
    assert inertia_concept.subtopic.name == "First Law of Motion"

    force_acceleration_concept = db_session.query(ConceptModel).filter(ConceptModel.name == "Force and Acceleration").first()
    assert force_acceleration_concept.subtopic.name == "Second Law of Motion"

    matrix_operations_concept = db_session.query(ConceptModel).filter(ConceptModel.name == "Matrix Operations").first()
    assert matrix_operations_concept.subtopic.name == "Matrices"

    linear_independence_concept = db_session.query(ConceptModel).filter(ConceptModel.name == "Linear Independence").first()
    assert linear_independence_concept.subtopic.name == "Vector Spaces"

    # Check if the questions are correctly associated with their respective subjects, topics, subtopics, and concepts
    questions = db_session.query(QuestionModel).all()
    for question in questions:
        assert question.subject is not None
        assert question.topic is not None
        assert question.subtopic is not None
        assert question.concept is not None

    # Check specific questions
    newton_first_law_question = db_session.query(QuestionModel).filter(QuestionModel.text == "What is Newton's First Law of Motion?").first()
    assert newton_first_law_question.subject.name == "Classical Mechanics"
    assert newton_first_law_question.topic.name == "Newton's Laws"
    assert newton_first_law_question.subtopic.name == "First Law of Motion"
    assert newton_first_law_question.concept.name == "Inertia"
    assert set([question_tag.tag for question_tag in newton_first_law_question.question_tags]) == {"physics", "mechanics"}

    linear_independence_question = db_session.query(QuestionModel).filter(QuestionModel.text == "What does it mean for a set of vectors to be linearly independent?").first()
    assert linear_independence_question.subject.name == "Algebra"
    assert linear_independence_question.topic.name == "Linear Algebra"
    assert linear_independence_question.subtopic.name == "Vector Spaces"
    assert linear_independence_question.concept.name == "Linear Independence"
    assert set([question_tag.tag for question_tag in linear_independence_question.question_tags]) == {"mathematics", "linear algebra"}

def test_filter_questions(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "Math",
            "topic": "Algebra",
            "subtopic": "Linear Equations",
            "difficulty": "Easy",
            "question_tags": ["equations", "solving"]
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
            assert "equations" in [tag["tag"] for tag in question["question_tags"]]
            assert "solving" in [tag["tag"] for tag in question["question_tags"]]

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
        params={"question_tags": ["equations"]}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    question_tag = db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "equations").first()
    assert all(question_tag.id in [t.id for t in question["question_tags"]] for question in questions)

def test_filter_questions_by_tags(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"question_tags": ["geometry"]}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    question_tag = db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "geometry").first()
    assert all(question_tag.id in [t.id for t in question["question_tags"]] for question in questions)

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
from app.services.logging_service import logger

def test_create_question_endpoint(logged_in_client, test_subject, test_topic, test_subtopic, test_question_set, test_concept):
    data = {
        "text": "Test Question",
        "subject": test_subject,
        "topic": test_topic,
        "subtopic": test_subtopic,
        "concept": test_concept,
        "difficulty": "Easy",
        "answer_choices": [
            {"text": "Answer 1", "is_correct": True, "explanation": "Answer 1 is correct."},
            {"text": "Answer 2", "is_correct": False, "explanation": "Answer 2 is incorrect."}
        ],
        "question_set_ids": [test_question_set.id]
    }
    response = logged_in_client.post("/questions/", json=data)
    assert response.status_code == 201
    created_question = response.json()
    assert created_question["text"] == "Test Question"
    assert created_question["subject"]["id"] == test_subject.id
    assert created_question["topic"]["id"] == test_topic.id
    assert created_question["subtopic"]["id"] == test_subtopic.id
    assert created_question["concept"]["id"] == test_concept.id
    assert created_question["difficulty"] == "Easy"
    assert len(created_question["answer_choices"]) == 2
    assert len(created_question["question_sets"]) == 1

def test_read_questions_without_token(client, db_session, test_questions):
    with pytest.raises(HTTPException) as exc_info:
        response = client.get("/questions/")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"

def test_read_questions_with_token(
    logged_in_client,
    test_questions,
    test_subject,
    test_topic,
    test_subtopic,
    test_concept
):
    question_id = test_questions[0].id
    response = logged_in_client.get(f"/questions/{question_id}/")
    assert response.status_code == 200
    logger.error("Response: %s", response.json())
    question = response.json()

    # Now we assert that our test question is indeed found and has the correct data
    assert question is not None, "Test question was not found in the response."
    assert question["id"] == test_questions[0].id
    assert question["text"] == test_questions[0].text
    assert question["subject"] == test_subject.name
    assert question["subtopic"] == test_subtopic.name
    assert question["topic"] == test_topic.name
    assert question["concept"] == test_concept.name
    assert question["difficulty"] == test_questions[0].difficulty

def test_update_question_not_found(logged_in_client):
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    response = logged_in_client.put(f"/questions/{question_id}", json=question_update)
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question with ID {question_id} not found"

def test_delete_question_not_found(logged_in_client):
    question_id = 999  # Assuming this ID does not exist
    response = logged_in_client.delete(f"/questions/{question_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question with ID {question_id} not found"

def test_update_question_endpoint(logged_in_client, test_questions):
    data = {
        "text": "Updated Question",
        "difficulty": "Medium"
    }
    response = logged_in_client.put(f"/questions/{test_questions[0].id}", json=data)
    assert response.status_code == 200
    assert response.json()["text"] == "Updated Question"
    assert response.json()["difficulty"] == "Medium"

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
from app.services.logging_service import logger


def test_create_subject(logged_in_client, test_discipline):
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    response = logged_in_client.post("/subjects/", json=subject_data.model_dump())
    assert response.status_code == 201
    assert response.json()["name"] == "Test Subject"

def test_read_subject(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()

    # Read the created subject
    response = logged_in_client.get(f"/subjects/{created_subject['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Subject"

def test_update_subject(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()

    # Update the subject
    updated_data = {"name": "Updated Subject"}
    response = logged_in_client.put(f"/subjects/{created_subject['id']}", json=updated_data)
    logger.debug(response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Subject"

def test_delete_subject(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()

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
from app.schemas.subjects import SubjectCreateSchema
from app.services.logging_service import logger


def test_create_topic(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()
    logger.debug("Created subject: %s", created_subject)

    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    response = logged_in_client.post("/topics/", json=topic_data.model_dump())
    logger.debug("Response: %s", response.json())
    assert response.status_code == 201
    assert response.json()["name"] == "Test Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_read_topic(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()
    logger.debug("Created subject: %s", created_subject)
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.model_dump()).json()

    # Read the created topic
    response = logged_in_client.get(f"/topics/{created_topic['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_update_topic(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()
    logger.debug("Created subject: %s", created_subject)
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.model_dump()).json()

    # Update the topic
    updated_data = {"name": "Updated Topic", "subject_id": created_subject["id"]}
    response = logged_in_client.put(f"/topics/{created_topic['id']}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Topic"
    assert response.json()["subject_id"] == created_subject["id"]

def test_delete_topic(logged_in_client, test_discipline):
    # Create a test subject
    subject_data = SubjectCreateSchema(name="Test Subject", discipline_id=test_discipline.id)
    created_subject = logged_in_client.post("/subjects/", json=subject_data.model_dump()).json()
    logger.debug("Created subject: %s", created_subject)
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=created_subject["id"])
    created_topic = logged_in_client.post("/topics/", json=topic_data.model_dump()).json()

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
# filename: tests/test_services/test_scoring_service.py

import pytest
from app.services.scoring_service import calculate_user_score, calculate_leaderboard_scores
from app.models.time_period import TimePeriodModel
from app.crud.crud_user_responses import create_user_response_crud, get_user_responses_crud
from app.schemas.user_responses import UserResponseCreateSchema
from app.services.logging_service import logger

def test_calculate_user_score(
    db_session,
    test_user,
    test_questions
):
    logger.info(f"Starting test_calculate_user_score with {len(test_questions)} questions")
    
    # Create user responses for multiple questions using CRUD function
    for i, question in enumerate(test_questions):
        is_correct = i != 1  # Make the second answer incorrect, others correct
        user_response_data = UserResponseCreateSchema(
            user_id=test_user.id,
            question_id=question.id,
            answer_choice_id=question.answer_choices[0].id,
            is_correct=is_correct
        )
        created_response = create_user_response_crud(db=db_session, user_response=user_response_data)
        logger.info(f"Created user response: {created_response}")

    # Verify the created responses
    user_responses = get_user_responses_crud(db_session, user_id=test_user.id)
    logger.info(f"Retrieved user responses: {user_responses}")
    
    # Calculate the user's score
    user_score = calculate_user_score(test_user.id, db_session)
    logger.info(f"Calculated user score: {user_score}")
    
    # We expect correct answers for all questions except the second one
    expected_score = len(test_questions) - 1
    assert user_score == expected_score, f"Expected score of {expected_score}, but got {user_score}"
    logger.info(f"Test passed: User score {user_score} matches expected score {expected_score}")

def test_calculate_leaderboard_scores(
    db_session,
    test_user,
    test_questions
):
    # Create user responses for multiple questions using CRUD function
    for i, question in enumerate(test_questions[:2]):  # Use the first two questions
        is_correct = i == 0  # First answer is correct, second is incorrect
        user_response_data = UserResponseCreateSchema(
            user_id=test_user.id,
            question_id=question.id,
            answer_choice_id=question.answer_choices[0].id,
            is_correct=is_correct
        )
        create_user_response_crud(db=db_session, user_response=user_response_data)

    # Test daily leaderboard
    daily_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.DAILY)
    assert daily_scores == {test_user.id: 1}
    logger.debug(f"Daily leaderboard scores: {daily_scores}")

    # Test weekly leaderboard
    weekly_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.WEEKLY)
    assert weekly_scores == {test_user.id: 1}
    logger.debug(f"Weekly leaderboard scores: {weekly_scores}")

    # Test monthly leaderboard
    monthly_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.MONTHLY)
    assert monthly_scores == {test_user.id: 1}
    logger.debug(f"Monthly leaderboard scores: {monthly_scores}")

    # Test yearly leaderboard
    yearly_scores = calculate_leaderboard_scores(db_session, TimePeriodModel.YEARLY)
    assert yearly_scores == {test_user.id: 1}
    logger.debug(f"Yearly leaderboard scores: {yearly_scores}")

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

from app.crud.crud_question_tag_associations import add_tag_to_question, get_question_tags, read_questions_by_tag
from app.crud.crud_role_to_permission_associations import add_permission_to_role, get_role_permissions, get_roles_by_permission


def test_question_tag_association(db_session, test_questions, test_tag):
    add_tag_to_question(db_session, test_questions[0].id, test_tag.id)
    
    question_tags = get_question_tags(db_session, test_questions[0].id)
    assert len(question_tags) == 1
    assert question_tags[0].id == test_tag.id

    questions_with_tag = read_questions_by_tag(db_session, test_tag.id)
    assert len(questions_with_tag) == 1
    assert questions_with_tag[0].id == test_questions[0].id

def test_role_to_permission_association(db_session, test_role, test_permission):
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
        "question_tags": "InvalidTag"  # Invalid type, should be a list of strings
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
        "question_tags": ["InvalidTag"]
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_valid_filters(db_session, test_questions):
    # Test case: Valid filters
    subject = test_questions[0].subject
    topic = test_questions[0].topic
    subtopic = test_questions[0].subtopic
    difficulty = test_questions[0].difficulty
    question_tags = [tag.tag for tag in test_questions[0].question_tags]

    filters = {
        "subject": subject.name,
        "topic": topic.name,
        "subtopic": subtopic.name,
        "difficulty": difficulty,
        "question_tags": question_tags
    }
    result = filter_questions_crud(db=db_session, filters=filters)
    assert len(result) == 1
    assert result[0].id == test_questions[0].id

```

## File: test_crud_question_sets.py
```py
# filename: tests/test_crud_question_sets.py

import pytest
from fastapi import HTTPException
from app.crud.crud_question_sets import create_question_set_crud, delete_question_set_crud, update_question_set_crud
from app.crud.crud_subjects import create_subject
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.question_sets import QuestionSetCreateSchema, QuestionSetUpdateSchema


def test_create_question_set_crud(db_session, test_user, test_questions, test_group):
    question_set_data = QuestionSetCreateSchema(
        db=db_session,
        name="test_create_question_set_crud Question Set",
        is_public=True,
        creator_id=test_user.id,
        question_ids=[test_questions[0].id],
        group_ids=[test_group.id]
    )
    question_set = create_question_set_crud(db=db_session, question_set=question_set_data)

    assert question_set.name == "test_create_question_set_crud Question Set"
    assert question_set.is_public == True
    assert question_set.creator_id == test_user.id
    assert len(question_set.questions) == 1
    assert question_set.questions[0].id == test_questions[0].id
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

def test_update_question_set_crud(db_session, test_question_set, test_questions, test_group):
    update_data = QuestionSetUpdateSchema(
        db = db_session,
        name="Updated Question Set",
        is_public=False,
        question_ids=[test_questions[0].id],
        group_ids=[test_group.id]
    )
    updated_question_set = update_question_set_crud(db_session, test_question_set.id, update_data)

    assert updated_question_set.name == "Updated Question Set"
    assert updated_question_set.is_public == False
    assert len(updated_question_set.questions) == 1
    assert updated_question_set.questions[0].id == test_questions[0].id
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

from app.schemas.questions import QuestionCreateSchema, QuestionUpdateSchema, QuestionWithAnswersCreateSchema
from app.schemas.answer_choices import AnswerChoiceCreateSchema
from app.crud.crud_questions import create_question, read_question, update_question, delete_question, create_question_with_answers


def test_create_question_with_answers(db_session, test_subject, test_topic, test_subtopic, test_concept):
    question_data = QuestionWithAnswersCreateSchema(
        text="Test Question",
        subject_id=test_subject.id,
        topic_id=test_topic.id,
        subtopic_id=test_subtopic.id,
        concept_id=test_concept.id,
        difficulty=DifficultyLevel.EASY,
        answer_choices=[
            AnswerChoiceCreateSchema(text="Answer 1", is_correct=True, explanation="Explanation 1"),
            AnswerChoiceCreateSchema(text="Answer 2", is_correct=False, explanation="Explanation 2"),
        ]
    )
    question = create_question_with_answers(db_session, question_data)
    assert question.text == "Test Question"
    assert question.difficulty == "Easy"
    assert len(question.answer_choices) == 2
    assert question.answer_choices[0].text == "Answer 1"
    assert question.answer_choices[1].text == "Answer 2"

def test_read_question_detailed(db_session, test_questions):
    question = read_question(db_session, test_questions[0].id)
    assert question.text == test_questions[0].text
    assert question.difficulty == test_questions[0].difficulty
    assert question.subject == test_questions[0].subject.name
    assert question.topic == test_questions[0].topic.name
    assert question.subtopic == test_questions[0].subtopic.name
    assert question.concept == test_questions[0].concept.name
    assert len(question.answer_choices) == len(test_questions[0].answer_choices)

def test_update_question_with_answer_choices(db_session, test_questions):
    update_data = QuestionUpdateSchema(
        text="Updated Question",
        difficulty=DifficultyLevel.MEDIUM,
        answer_choice_ids=[test_questions[0].answer_choices[0].id]
    )
    updated_question = update_question(db_session, test_questions[0].id, update_data)
    assert updated_question.text == "Updated Question"
    assert updated_question.difficulty == "Medium"
    assert len(updated_question.answer_choices) == 1

def test_get_nonexistent_question(db_session):
    """Test retrieval of a non-existent question."""
    question = read_question(db_session, question_id=999)
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
from app.crud.crud_subjects import create_subject


def test_create_subject(db_session, test_discipline):
    subject_data = SubjectCreateSchema(
        name="Test Subject",
        discipline_id=test_discipline.id
    )
    created_subject = create_subject(db=db_session, subject=subject_data)
    assert created_subject.name == "Test Subject"
    assert created_subject.discipline_id == test_discipline.id

```

## File: test_crud_user.py
```py
# filename: tests/test_crud_user.py

from app.crud.crud_user import delete_user, create_user_crud, update_user_crud
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.services.authentication_service import authenticate_user
from app.core.security import get_password_hash

def test_remove_user_not_found(db_session):
    user_id = 999  # Assuming this ID does not exist
    removed_user = delete_user(db_session, user_id)
    assert removed_user is None

def test_authenticate_user(db_session, random_username, test_role):
    hashed_password = get_password_hash("AuthPassword123!")
    user_data = UserCreateSchema(
        username=random_username,
        password=hashed_password,
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

## File: test_answer_choice_model.py
```py
# filename: tests/models/test_answer_choice_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.answer_choices import AnswerChoiceModel
from app.models.questions import QuestionModel
from app.models.user_responses import UserResponseModel

def test_answer_choice_creation(db_session):
    answer_choice = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital of France"
    )
    db_session.add(answer_choice)
    db_session.commit()

    assert answer_choice.id is not None
    assert answer_choice.text == "Paris"
    assert answer_choice.is_correct is True
    assert answer_choice.explanation == "Paris is the capital of France"

def test_answer_choice_question_relationship(db_session, test_questions):
    answer_choice = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital of France"
    )
    answer_choice.questions.append(test_questions[0])
    db_session.add(answer_choice)
    db_session.commit()

    assert test_questions[0] in answer_choice.questions
    assert answer_choice in test_questions[0].answer_choices

def test_answer_choice_multiple_questions(db_session, test_questions):
    answer_choice = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital of France"
    )
    
    answer_choice.questions.extend(test_questions[:2])  # Use the first two questions from the fixture
    db_session.add(answer_choice)
    db_session.commit()

    assert len(answer_choice.questions) == 2
    assert test_questions[0] in answer_choice.questions
    assert test_questions[1] in answer_choice.questions

def test_answer_choice_user_response_relationship(db_session, test_questions, test_user):
    answer_choice = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital of France"
    )
    answer_choice.questions.append(test_questions[0])
    db_session.add(answer_choice)
    db_session.commit()

    user_response = UserResponseModel(
        user_id=test_user.id,
        question_id=test_questions[0].id,
        answer_choice_id=answer_choice.id,
        is_correct=True
    )
    db_session.add(user_response)
    db_session.commit()

    assert user_response in answer_choice.user_responses
    assert user_response.answer_choice == answer_choice

def test_answer_choice_required_fields(db_session):
    # Test missing text
    with pytest.raises(IntegrityError):
        answer_choice = AnswerChoiceModel(
            is_correct=True
        )
        db_session.add(answer_choice)
        db_session.commit()
    db_session.rollback()

    # Test missing is_correct
    with pytest.raises(IntegrityError):
        answer_choice = AnswerChoiceModel(
            text="Paris"
        )
        db_session.add(answer_choice)
        db_session.commit()
    db_session.rollback()

def test_answer_choice_repr(db_session):
    answer_choice = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital of France"
    )
    db_session.add(answer_choice)
    db_session.commit()

    expected_repr = f"<AnswerChoiceModel(id={answer_choice.id}, text='Paris...', is_correct=True)>"
    assert repr(answer_choice) == expected_repr

```

## File: test_associations.py
```py
# filename: tests/models/test_associations.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.users import UserModel
from app.models.groups import GroupModel
from app.models.questions import QuestionModel, DifficultyLevel
from app.models.disciplines import DisciplineModel
from app.models.subjects import SubjectModel
from app.models.topics import TopicModel
from app.models.subtopics import SubtopicModel
from app.models.concepts import ConceptModel
from app.models.question_tags import QuestionTagModel
from app.models.question_sets import QuestionSetModel
from app.models.roles import RoleModel
from app.models.permissions import PermissionModel

def test_user_to_group_association(db_session, test_user, test_group):
    test_user.groups.append(test_group)
    db_session.commit()

    assert test_group in test_user.groups
    assert test_user in test_group.users

def test_question_to_subject_association(db_session):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    subject = SubjectModel(name="Test Subject")
    question.subjects.append(subject)
    db_session.add_all([question, subject])
    db_session.commit()

    assert subject in question.subjects
    assert question in subject.questions

def test_question_to_topic_association(db_session):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    topic = TopicModel(name="Test Topic")
    question.topics.append(topic)
    db_session.add_all([question, topic])
    db_session.commit()

    assert topic in question.topics
    assert question in topic.questions

def test_question_to_subtopic_association(db_session):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    subtopic = SubtopicModel(name="Test Subtopic")
    question.subtopics.append(subtopic)
    db_session.add_all([question, subtopic])
    db_session.commit()

    assert subtopic in question.subtopics
    assert question in subtopic.questions

def test_question_to_concept_association(db_session):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    concept = ConceptModel(name="Test Concept")
    question.concepts.append(concept)
    db_session.add_all([question, concept])
    db_session.commit()

    assert concept in question.concepts
    assert question in concept.questions

def test_question_to_tag_association(db_session):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    tag = QuestionTagModel(tag="Test Tag")
    question.question_tags.append(tag)
    db_session.add_all([question, tag])
    db_session.commit()

    assert tag in question.question_tags
    assert question in tag.questions

def test_question_set_to_question_association(db_session, test_user_with_group):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    question_set = QuestionSetModel(name="Test Set", creator_id=test_user_with_group.id)
    question_set.questions.append(question)
    db_session.add_all([question, question_set])
    db_session.commit()

    assert question in question_set.questions
    assert question_set in question.question_sets

def test_question_set_to_group_association(db_session, test_question_set, test_group):
    test_question_set.groups.append(test_group)
    db_session.commit()

    assert test_group in test_question_set.groups
    assert test_question_set in test_group.question_sets

def test_role_to_permission_association(db_session, test_role, test_permission):
    test_role.permissions.append(test_permission)
    db_session.commit()

    assert test_permission in test_role.permissions
    assert test_role in test_permission.roles

def test_discipline_subject_association(db_session):
    discipline = DisciplineModel(name="Science")
    subject = SubjectModel(name="Physics")
    discipline.subjects.append(subject)
    db_session.add_all([discipline, subject])
    db_session.commit()

    assert subject in discipline.subjects
    assert discipline in subject.disciplines

def test_subject_topic_association(db_session):
    subject = SubjectModel(name="Mathematics")
    topic = TopicModel(name="Algebra")
    subject.topics.append(topic)
    db_session.add_all([subject, topic])
    db_session.commit()

    assert topic in subject.topics
    assert subject in topic.subjects

def test_topic_subtopic_association(db_session):
    topic = TopicModel(name="Geometry")
    subtopic = SubtopicModel(name="Triangles")
    topic.subtopics.append(subtopic)
    db_session.add_all([topic, subtopic])
    db_session.commit()

    assert subtopic in topic.subtopics
    assert topic in subtopic.topics

def test_subtopic_concept_association(db_session):
    subtopic = SubtopicModel(name="Calculus")
    concept = ConceptModel(name="Derivatives")
    subtopic.concepts.append(concept)
    db_session.add_all([subtopic, concept])
    db_session.commit()

    assert concept in subtopic.concepts
    assert subtopic in concept.subtopics

def test_question_associations(db_session):
    question = QuestionModel(text="What is 2+2?", difficulty=DifficultyLevel.EASY)
    subject = SubjectModel(name="Math")
    topic = TopicModel(name="Arithmetic")
    subtopic = SubtopicModel(name="Addition")
    concept = ConceptModel(name="Basic Addition")

    question.subjects.append(subject)
    question.topics.append(topic)
    question.subtopics.append(subtopic)
    question.concepts.append(concept)

    db_session.add_all([question, subject, topic, subtopic, concept])
    db_session.commit()

    assert subject in question.subjects
    assert topic in question.topics
    assert subtopic in question.subtopics
    assert concept in question.concepts

    assert question in subject.questions
    assert question in topic.questions
    assert question in subtopic.questions
    assert question in concept.questions

def test_multiple_associations(db_session):
    subject1 = SubjectModel(name="Physics")
    subject2 = SubjectModel(name="Engineering")
    topic = TopicModel(name="Mechanics")

    topic.subjects.extend([subject1, subject2])
    db_session.add_all([subject1, subject2, topic])
    db_session.commit()

    assert subject1 in topic.subjects
    assert subject2 in topic.subjects
    assert topic in subject1.topics
    assert topic in subject2.topics

def test_association_integrity(db_session, test_user, test_group):
    test_user.groups.append(test_group)
    db_session.commit()

    # Try to add the same association again
    with pytest.raises(IntegrityError):
        test_user.groups.append(test_group)
        db_session.commit()

    db_session.rollback()

    # Remove the association
    test_user.groups.remove(test_group)
    db_session.commit()

    assert test_group not in test_user.groups
    assert test_user not in test_group.users

```

## File: test_concept_model.py
```py
# filename: tests/models/test_concept_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.concepts import ConceptModel
from app.models.subtopics import SubtopicModel

def test_concept_creation(db_session):
    concept = ConceptModel(name="Pythagorean Theorem")
    db_session.add(concept)
    db_session.commit()

    assert concept.id is not None
    assert concept.name == "Pythagorean Theorem"

def test_concept_subtopic_relationship(db_session):
    concept = ConceptModel(name="Binomial Theorem")
    subtopic = SubtopicModel(name="Algebraic Theorems")
    concept.subtopics.append(subtopic)
    db_session.add_all([concept, subtopic])
    db_session.commit()

    assert subtopic in concept.subtopics
    assert concept in subtopic.concepts

def test_concept_questions_relationship(db_session, test_questions):
    concept = ConceptModel(name="Logarithms")
    concept.questions.extend(test_questions[:2])
    db_session.add(concept)
    db_session.commit()

    assert len(concept.questions) == 2
    assert test_questions[0] in concept.questions
    assert test_questions[1] in concept.questions

def test_concept_required_fields(db_session):
    # Test missing name
    with pytest.raises(IntegrityError):
        concept = ConceptModel()
        db_session.add(concept)
        db_session.commit()
    db_session.rollback()

def test_concept_repr(db_session):
    concept = ConceptModel(name="Quadratic Formula")
    db_session.add(concept)
    db_session.commit()

    expected_repr = f"<Concept(id={concept.id}, name='Quadratic Formula')>"
    assert repr(concept) == expected_repr

```

## File: test_group_model.py
```py
# filename: tests/models/test_group_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.groups import GroupModel
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.models.question_sets import QuestionSetModel
from app.models.leaderboard import LeaderboardModel
from app.models.time_period import TimePeriodModel

def test_group_model_creation(db_session, test_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    assert group.id is not None
    assert group.name == "Test Group"
    assert group.description == "This is a test group"
    assert group.creator_id == test_user.id

def test_group_model_unique_constraint(db_session, test_user):
    group1 = GroupModel(
        name="Unique Group",
        description="This is a unique group",
        creator_id=test_user.id
    )
    db_session.add(group1)
    db_session.commit()

    # Try to create another group with the same name
    group2 = GroupModel(
        name="Unique Group",
        description="This is another group with the same name",
        creator_id=test_user.id
    )
    db_session.add(group2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()  # Roll back the failed transaction

    # Assert that only one group with this name exists
    groups = db_session.query(GroupModel).filter_by(name="Unique Group").all()
    assert len(groups) == 1
    assert groups[0].description == "This is a unique group"

def test_group_user_relationship(db_session, test_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    group.users.append(test_user)
    db_session.commit()

    assert test_user in group.users
    assert group in test_user.groups

def test_group_creator_relationship(db_session, test_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    assert group.creator == test_user
    assert group in test_user.created_groups

def test_group_question_set_relationship(db_session, test_user, test_question_set):
    group = GroupModel(
        name="test_group_question_set_relationship Test Group",
        description="This is a group for the test_group_question_set_relationship test",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    group.question_sets.append(test_question_set)
    db_session.commit()

    assert test_question_set in group.question_sets
    assert group in test_question_set.groups

def test_group_leaderboard_relationship(db_session, test_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    leaderboard = LeaderboardModel(
        user_id=test_user.id,
        group_id=group.id,
        score=100,
        time_period_id=7
    )
    db_session.add(leaderboard)
    db_session.commit()

    assert leaderboard in group.leaderboards
    assert group == leaderboard.group

def test_group_model_repr(db_session, test_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    assert repr(group) == f"<GroupModel(id={group.id}, name='Test Group', creator_id={test_user.id}, is_active={test_user.is_active})>"
```

## File: test_question_model.py
```py
# filename: tests/models/test_question_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.questions import QuestionModel, DifficultyLevel
from app.models.subjects import SubjectModel
from app.models.topics import TopicModel
from app.models.subtopics import SubtopicModel
from app.models.concepts import ConceptModel
from app.models.question_tags import QuestionTagModel
from app.models.answer_choices import AnswerChoiceModel
from app.models.question_sets import QuestionSetModel
from app.models.user_responses import UserResponseModel
from app.models.associations import QuestionToAnswerAssociation
from app.services.logging_service import logger, sqlalchemy_obj_to_dict
from app.services.validation_service import validate_foreign_keys

def test_question_model_creation(db_session):
    question = QuestionModel(
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY
    )
    db_session.add(question)
    db_session.commit()

    assert question.id is not None
    assert question.text == "What is the capital of France?"
    assert question.difficulty == DifficultyLevel.EASY

def test_question_model_relationships(db_session, test_subject, test_topic, test_subtopic, test_concept):
    question = QuestionModel(
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY
    )
    question.subjects.append(test_subject)
    question.topics.append(test_topic)
    question.subtopics.append(test_subtopic)
    question.concepts.append(test_concept)
    db_session.add(question)
    db_session.commit()

    assert test_subject in question.subjects
    assert test_topic in question.topics
    assert test_subtopic in question.subtopics
    assert test_concept in question.concepts

def test_question_multiple_relationships(db_session, test_subject, test_topic, test_subtopic, test_concept):
    question = QuestionModel(
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY
    )
    question.subjects.extend([test_subject, SubjectModel(name="Another Subject")])
    question.topics.extend([test_topic, TopicModel(name="Another Topic")])
    question.subtopics.extend([test_subtopic, SubtopicModel(name="Another Subtopic")])
    question.concepts.extend([test_concept, ConceptModel(name="Another Concept")])
    db_session.add(question)
    db_session.commit()

    assert len(question.subjects) == 2
    assert len(question.topics) == 2
    assert len(question.subtopics) == 2
    assert len(question.concepts) == 2

def test_question_tag_relationship(db_session, test_tag):
    question = QuestionModel(
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY
    )
    question.question_tags.append(test_tag)
    db_session.add(question)
    db_session.commit()

    assert test_tag in question.question_tags
    assert question in test_tag.questions

# def test_answer_choice_relationship(db_session):
#     question = QuestionModel(
#         text="What is the capital of France?",
#         difficulty=DifficultyLevel.EASY
#     )
#     db_session.add(question)
#     db_session.commit()

#     answer_choice = AnswerChoiceModel(text="Paris", is_correct=True, question_id=question.id)
#     db_session.add(answer_choice)
#     db_session.commit()

#     assert answer_choice in question.answer_choices
#     assert question == answer_choice.question

def test_question_set_relationship(db_session, test_question_set):
    question = QuestionModel(
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY
    )
    question.question_sets.append(test_question_set)
    db_session.add(question)
    db_session.commit()

    assert test_question_set in question.question_sets
    assert question in test_question_set.questions

def test_user_response_relationship(db_session, test_user):
    question = QuestionModel(
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY
    )
    db_session.add(question)
    db_session.commit()

    user_response = UserResponseModel(
        user_id=test_user.id,
        question_id=question.id,
        answer_choice_id=1,  # Assuming an answer choice with id 1 exists
        is_correct=True
    )
    db_session.add(user_response)
    db_session.commit()

    assert user_response in question.user_responses
    assert question == user_response.question

def test_question_model_repr(db_session):
    question = QuestionModel(
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY
    )
    db_session.add(question)
    db_session.commit()

    expected_repr = f"<QuestionModel(id={question.id}, text='What is the capital of France?...', difficulty='DifficultyLevel.EASY')>"
    assert repr(question) == expected_repr

def test_question_model_with_answers(db_session, test_subject, test_topic, test_subtopic):
    question = QuestionModel(text="What is the capital of France?", difficulty=DifficultyLevel.EASY, 
                             subjects=[test_subject], topics=[test_topic], subtopics=[test_subtopic])
    logger.debug("Created question: %s", sqlalchemy_obj_to_dict(question))
    
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    logger.debug("Added and refreshed the question: %s", sqlalchemy_obj_to_dict(question))
    
    answer = AnswerChoiceModel(text="Paris", is_correct=True, explanation="Paris is the capital and largest city of France.")
    
    db_session.add(answer)
    db_session.commit()
    db_session.refresh(answer)
    logger.debug("Added and refreshed answer: %s", sqlalchemy_obj_to_dict(answer))
    
    # Associate the answer with the question
    question.answer_choices.append(answer)
    db_session.commit()
    
    validate_foreign_keys(QuestionModel, db_session.connection(), question)
    validate_foreign_keys(AnswerChoiceModel, db_session.connection(), answer)
    logger.debug("Validated foreign keys")
    
    assert question.id is not None
    assert answer.id is not None
    assert answer in question.answer_choices
    logger.debug("Assertions passed")

def test_question_deletion_removes_association_to_answers(db_session, test_subject, test_topic, test_subtopic):
    question = QuestionModel(text="What is the capital of France?", difficulty=DifficultyLevel.EASY, 
                             subjects=[test_subject], topics=[test_topic], subtopics=[test_subtopic])
    logger.debug("Created question: %s", sqlalchemy_obj_to_dict(question))
    
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    logger.debug("Added and refreshed the question: %s", sqlalchemy_obj_to_dict(question))
    
    answer = AnswerChoiceModel(text="Paris", is_correct=True, explanation="Paris is the capital and largest city of France.")
    
    db_session.add(answer)
    db_session.commit()
    db_session.refresh(answer)
    logger.debug("Added and refreshed answer: %s", sqlalchemy_obj_to_dict(answer))
    
    # Associate the answer with the question
    question.answer_choices.append(answer)
    db_session.commit()
    
    validate_foreign_keys(QuestionModel, db_session.connection(), question)
    validate_foreign_keys(AnswerChoiceModel, db_session.connection(), answer)
    logger.debug("Validated foreign keys")
    
    # Store the answer ID for later checking
    answer_id = answer.id
    
    db_session.delete(question)
    logger.debug("Deleted question: %s", question)
    
    db_session.commit()
    logger.debug("Committed the session after deleting the question")
    
    # Check that the answer still exists
    assert db_session.query(AnswerChoiceModel).filter_by(id=answer_id).first() is not None
    logger.debug("Assertion passed: Answer choice still exists after question deletion")
    
    # Check that the association between the question and answer is removed
    assert db_session.query(QuestionToAnswerAssociation).filter_by(answer_choice_id=answer_id).first() is None
    logger.debug("Assertion passed: Association between question and answer is removed")

```

## File: test_question_set_model.py
```py
# filename: tests/models/test_question_set_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.question_sets import QuestionSetModel

def test_question_set_creation(db_session, test_user):
    question_set = QuestionSetModel(
        name="Geography Quiz",
        is_public=True,
        creator_id=test_user.id
    )
    db_session.add(question_set)
    db_session.commit()

    assert question_set.id is not None
    assert question_set.name == "Geography Quiz"
    assert question_set.is_public is True
    assert question_set.creator_id == test_user.id

def test_question_set_creator_relationship(db_session, test_user):
    question_set = QuestionSetModel(
        name="History Quiz",
        is_public=False,
        creator_id=test_user.id
    )
    db_session.add(question_set)
    db_session.commit()

    assert question_set.creator == test_user
    assert question_set in test_user.created_question_sets

def test_question_set_questions_relationship(db_session, test_user, test_questions):
    question_set = QuestionSetModel(
        name="Science Quiz",
        is_public=True,
        creator_id=test_user.id
    )
    question_set.questions.extend(test_questions[:2])
    db_session.add(question_set)
    db_session.commit()

    assert len(question_set.questions) == 2
    assert test_questions[0] in question_set.questions
    assert test_questions[1] in question_set.questions

def test_question_set_groups_relationship(db_session, test_user, test_group):
    question_set = QuestionSetModel(
        name="Math Quiz",
        is_public=True,
        creator_id=test_user.id
    )
    question_set.groups.append(test_group)
    db_session.add(question_set)
    db_session.commit()

    assert test_group in question_set.groups
    assert question_set in test_group.question_sets

def test_question_set_required_fields(db_session, test_user):
    # Test missing name
    with pytest.raises(IntegrityError):
        question_set = QuestionSetModel(
            is_public=True,
            creator_id=test_user.id
        )
        db_session.add(question_set)
        db_session.commit()
    db_session.rollback()

def test_question_set_repr(db_session, test_user):
    question_set = QuestionSetModel(
        name="Biology Quiz",
        is_public=True,
        creator_id=test_user.id
    )
    db_session.add(question_set)
    db_session.commit()

    expected_repr = f"<QuestionSetModel(id={question_set.id}, name='Biology Quiz', is_public=True, creator_id={test_user.id})>"
    assert repr(question_set) == expected_repr

```

## File: test_question_tag_model.py
```py
# filename: tests/models/test_question_tag_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.question_tags import QuestionTagModel

def test_question_tag_creation(db_session):
    tag = QuestionTagModel(tag="geography")
    db_session.add(tag)
    db_session.commit()

    assert tag.id is not None
    assert tag.tag == "geography"

def test_question_tag_unique_constraint(db_session):
    tag1 = QuestionTagModel(tag="history")
    db_session.add(tag1)
    db_session.commit()

    # Try to create another tag with the same name
    with pytest.raises(IntegrityError):
        tag2 = QuestionTagModel(tag="history")
        db_session.add(tag2)
        db_session.commit()
    
    db_session.rollback()

def test_question_tag_question_relationship(db_session, test_questions):
    tag = QuestionTagModel(tag="science")
    tag.questions.append(test_questions[0])
    db_session.add(tag)
    db_session.commit()

    assert test_questions[0] in tag.questions
    assert tag in test_questions[0].question_tags

def test_question_tag_multiple_questions(db_session, test_questions):
    tag = QuestionTagModel(tag="math")
    tag.questions.extend(test_questions[:2])  # Add the tag to the first two questions
    db_session.add(tag)
    db_session.commit()

    assert len(tag.questions) == 2
    assert test_questions[0] in tag.questions
    assert test_questions[1] in tag.questions

def test_question_tag_required_fields(db_session):
    # Test missing tag
    with pytest.raises(IntegrityError):
        tag = QuestionTagModel()
        db_session.add(tag)
        db_session.commit()
    db_session.rollback()

def test_question_tag_repr(db_session):
    tag = QuestionTagModel(tag="biology")
    db_session.add(tag)
    db_session.commit()

    expected_repr = f"<QuestionTagModel(id={tag.id}, tag='biology')>"
    assert repr(tag) == expected_repr

```

## File: test_role_model.py
```py
# filename: tests/test_models/test_role_model.py

import pytest
from sqlalchemy.exc import SQLAlchemyError
from app.models.permissions import PermissionModel
from app.models.roles import RoleModel
from app.services.logging_service import logger


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
```

## File: test_subject_model.py
```py
# filename: tests/test_models/test_subject_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.subjects import SubjectModel
from app.models.disciplines import DisciplineModel
from app.models.topics import TopicModel

def test_subject_creation(db_session):
    subject = SubjectModel(name="Mathematics")
    db_session.add(subject)
    db_session.commit()

    assert subject.id is not None
    assert subject.name == "Mathematics"

def test_subject_unique_name(db_session):
    subject1 = SubjectModel(name="Physics")
    db_session.add(subject1)
    db_session.commit()

    with pytest.raises(IntegrityError):
        subject2 = SubjectModel(name="Physics")
        db_session.add(subject2)
        db_session.commit()
    db_session.rollback()

def test_subject_discipline_relationship(db_session):
    subject = SubjectModel(name="Chemistry")
    discipline = DisciplineModel(name="Natural Sciences")
    subject.disciplines.append(discipline)
    db_session.add_all([subject, discipline])
    db_session.commit()

    assert discipline in subject.disciplines
    assert subject in discipline.subjects

def test_subject_topics_relationship(db_session):
    subject = SubjectModel(name="Biology")
    topic = TopicModel(name="Genetics")
    subject.topics.append(topic)
    db_session.add_all([subject, topic])
    db_session.commit()

    assert topic in subject.topics
    assert subject in topic.subjects

def test_subject_questions_relationship(db_session, test_questions):
    subject = SubjectModel(name="Geography")
    subject.questions.extend(test_questions[:2])
    db_session.add(subject)
    db_session.commit()

    assert len(subject.questions) == 2
    assert test_questions[0] in subject.questions
    assert test_questions[1] in subject.questions

def test_subject_required_fields(db_session):
    # Test missing name
    with pytest.raises(IntegrityError):
        subject = SubjectModel()
        db_session.add(subject)
        db_session.commit()
    db_session.rollback()

def test_subject_repr(db_session):
    subject = SubjectModel(name="History")
    db_session.add(subject)
    db_session.commit()

    expected_repr = f"<Subject(id={subject.id}, name='History')>"
    assert repr(subject) == expected_repr

```

## File: test_subtopic_model.py
```py
# filename: tests/test_models/test_subtopic_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.subtopics import SubtopicModel
from app.models.topics import TopicModel
from app.models.concepts import ConceptModel

def test_subtopic_creation(db_session):
    subtopic = SubtopicModel(name="Linear Equations")
    db_session.add(subtopic)
    db_session.commit()

    assert subtopic.id is not None
    assert subtopic.name == "Linear Equations"

def test_subtopic_topic_relationship(db_session):
    subtopic = SubtopicModel(name="Quadratic Equations")
    topic = TopicModel(name="Algebra")
    subtopic.topics.append(topic)
    db_session.add_all([subtopic, topic])
    db_session.commit()

    assert topic in subtopic.topics
    assert subtopic in topic.subtopics

def test_subtopic_concepts_relationship(db_session):
    subtopic = SubtopicModel(name="Trigonometric Functions")
    concept = ConceptModel(name="Sine Function")
    subtopic.concepts.append(concept)
    db_session.add_all([subtopic, concept])
    db_session.commit()

    assert concept in subtopic.concepts
    assert subtopic in concept.subtopics

def test_subtopic_questions_relationship(db_session, test_questions):
    subtopic = SubtopicModel(name="Limits")
    subtopic.questions.extend(test_questions[:2])
    db_session.add(subtopic)
    db_session.commit()

    assert len(subtopic.questions) == 2
    assert test_questions[0] in subtopic.questions
    assert test_questions[1] in subtopic.questions

def test_subtopic_required_fields(db_session):
    # Test missing name
    with pytest.raises(IntegrityError):
        subtopic = SubtopicModel()
        db_session.add(subtopic)
        db_session.commit()
    db_session.rollback()

def test_subtopic_repr(db_session):
    subtopic = SubtopicModel(name="Derivatives")
    db_session.add(subtopic)
    db_session.commit()

    expected_repr = f"<Subtopic(id={subtopic.id}, name='Derivatives')>"
    assert repr(subtopic) == expected_repr

```

## File: test_topic_model.py
```py
# filename: tests/test_models/test_topic_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.topics import TopicModel
from app.models.subjects import SubjectModel
from app.models.subtopics import SubtopicModel

def test_topic_creation(db_session):
    topic = TopicModel(name="Algebra")
    db_session.add(topic)
    db_session.commit()

    assert topic.id is not None
    assert topic.name == "Algebra"

def test_topic_subject_relationship(db_session):
    topic = TopicModel(name="Geometry")
    subject = SubjectModel(name="Mathematics")
    topic.subjects.append(subject)
    db_session.add_all([topic, subject])
    db_session.commit()

    assert subject in topic.subjects
    assert topic in subject.topics

def test_topic_subtopics_relationship(db_session):
    topic = TopicModel(name="Calculus")
    subtopic = SubtopicModel(name="Derivatives")
    topic.subtopics.append(subtopic)
    db_session.add_all([topic, subtopic])
    db_session.commit()

    assert subtopic in topic.subtopics
    assert topic in subtopic.topics

def test_topic_questions_relationship(db_session, test_questions):
    topic = TopicModel(name="Statistics")
    topic.questions.extend(test_questions[:2])
    db_session.add(topic)
    db_session.commit()

    assert len(topic.questions) == 2
    assert test_questions[0] in topic.questions
    assert test_questions[1] in topic.questions

def test_topic_required_fields(db_session):
    # Test missing name
    with pytest.raises(IntegrityError):
        topic = TopicModel()
        db_session.add(topic)
        db_session.commit()
    db_session.rollback()

def test_topic_repr(db_session):
    topic = TopicModel(name="Trigonometry")
    db_session.add(topic)
    db_session.commit()

    expected_repr = f"<Topic(id={topic.id}, name='Trigonometry')>"
    assert repr(topic) == expected_repr

```

## File: test_user_model.py
```py
# filename: tests/models/test_user_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.models.groups import GroupModel
from app.models.question_sets import QuestionSetModel

def test_user_model_creation(db_session, test_permissions):
    # Create a role first
    role = RoleModel(name="user", description="Regular user")
    db_session.add(role)
    db_session.commit()

    user = UserModel(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashed_password",
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    assert user.hashed_password == "hashed_password"
    assert user.is_active == True
    assert user.is_admin == False
    assert user.role.name == "user"

def test_user_model_unique_constraints(db_session):
    # Create a role first
    role = RoleModel(name="user", description="Regular user")
    db_session.add(role)
    db_session.commit()

    user1 = UserModel(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashed_password",
        role_id=role.id
    )
    db_session.add(user1)
    db_session.commit()

    # Try to create another user with the same username
    with pytest.raises(IntegrityError):
        user2 = UserModel(
            username="testuser",
            email="testuser2@example.com",
            hashed_password="hashed_password",
            role_id=role.id
        )
        db_session.add(user2)
        db_session.commit()

    db_session.rollback()

    # Try to create another user with the same email
    with pytest.raises(IntegrityError):
        user3 = UserModel(
            username="testuser3",
            email="testuser@example.com",
            hashed_password="hashed_password",
            role_id=role.id
        )
        db_session.add(user3)
        db_session.commit()

def test_user_model_relationships(db_session, test_group, test_question_set):
    # Create a role first
    role = RoleModel(name="user", description="Regular user")
    db_session.add(role)
    db_session.commit()

    user = UserModel(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashed_password",
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()

    # Test group relationship
    user.groups.append(test_group)
    db_session.commit()
    assert test_group in user.groups

    # Test created_groups relationship
    created_group = GroupModel(name="Created Group", creator=user)
    db_session.add(created_group)
    db_session.commit()
    assert created_group in user.created_groups

    # Test created_question_sets relationship
    created_question_set = QuestionSetModel(name="Created Question Set", creator=user)
    db_session.add(created_question_set)
    db_session.commit()
    assert created_question_set in user.created_question_sets

def test_user_model_repr(db_session):
    # Create a role first
    role = RoleModel(name="user", description="Regular user")
    db_session.add(role)
    db_session.commit()

    user = UserModel(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashed_password",
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()

    assert repr(user) == f"<User(id={user.id}, username='testuser', email='testuser@example.com', role_id='1')>"

```

## File: test_user_response_model.py
```py
# filename: tests/models/test_user_response_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user_responses import UserResponseModel

def test_user_response_creation(db_session, test_user, test_questions, test_answer_choices):
    user_response = UserResponseModel(
        user_id=test_user.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_answer_choices[0].id,
        is_correct=True
    )
    db_session.add(user_response)
    db_session.commit()

    assert user_response.id is not None
    assert user_response.user_id == test_user.id
    assert user_response.question_id == test_questions[0].id
    assert user_response.answer_choice_id == test_answer_choices[0].id
    assert user_response.is_correct is True
    assert user_response.timestamp is not None

def test_user_response_relationships(db_session, test_user, test_questions, test_answer_choices):
    user_response = UserResponseModel(
        user_id=test_user.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_answer_choices[0].id,
        is_correct=True
    )
    db_session.add(user_response)
    db_session.commit()

    assert user_response.user == test_user
    assert user_response.question == test_questions[0]
    assert user_response.answer_choice == test_answer_choices[0]
    assert user_response in test_user.responses
    assert user_response in test_questions[0].user_responses
    assert user_response in test_answer_choices[0].user_responses

def test_user_response_required_fields(db_session, test_user, test_questions, test_answer_choices):
    # Test missing user_id
    with pytest.raises(IntegrityError):
        user_response = UserResponseModel(
            question_id=test_questions[0].id,
            answer_choice_id=test_answer_choices[0].id,
            is_correct=True
        )
        db_session.add(user_response)
        db_session.commit()
    db_session.rollback()

    # Test missing question_id
    with pytest.raises(IntegrityError):
        user_response = UserResponseModel(
            user_id=test_user.id,
            answer_choice_id=test_answer_choices[0].id,
            is_correct=True
        )
        db_session.add(user_response)
        db_session.commit()
    db_session.rollback()

    # Test missing answer_choice_id
    with pytest.raises(IntegrityError):
        user_response = UserResponseModel(
            user_id=test_user.id,
            question_id=test_questions[0].id,
            is_correct=True
        )
        db_session.add(user_response)
        db_session.commit()
    db_session.rollback()

    # Test missing is_correct
    with pytest.raises(IntegrityError):
        user_response = UserResponseModel(
            user_id=test_user.id,
            question_id=test_questions[0].id,
            answer_choice_id=test_answer_choices[0].id
        )
        db_session.add(user_response)
        db_session.commit()
    db_session.rollback()

def test_user_response_repr(db_session, test_user, test_questions, test_answer_choices):
    user_response = UserResponseModel(
        user_id=test_user.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_answer_choices[0].id,
        is_correct=True
    )
    db_session.add(user_response)
    db_session.commit()

    expected_repr = f"<UserResponseModel(id={user_response.id}, user_id={test_user.id}, question_id={test_questions[0].id}, is_correct=True)>"
    assert repr(user_response) == expected_repr

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

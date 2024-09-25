
# Directory: /code/quiz-app/backend/

## File: __init__.py
```py

```

# Directory: /code/quiz-app/backend/app

## File: __init__.py
```py

```

## File: main.py
```py
# filename: main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.endpoints import answer_choices as answer_choices_router
from backend.app.api.endpoints import authentication as authentication_router
from backend.app.api.endpoints import concepts as concepts_router
from backend.app.api.endpoints import disciplines as disciplines_router
from backend.app.api.endpoints import domains as domains_router
from backend.app.api.endpoints import filters as filters_router
from backend.app.api.endpoints import groups as groups_router
from backend.app.api.endpoints import leaderboard as leaderboard_router
from backend.app.api.endpoints import question_sets as question_sets_router
from backend.app.api.endpoints import question_tags as question_tags_router
from backend.app.api.endpoints import questions as questions_router
from backend.app.api.endpoints import register as register_router
from backend.app.api.endpoints import subjects as subjects_router
from backend.app.api.endpoints import subtopics as subtopics_router
from backend.app.api.endpoints import topics as topics_router
from backend.app.api.endpoints import user_responses as user_responses_router
from backend.app.api.endpoints import users as users_router
from backend.app.api.endpoints import time_periods as time_periods_router
from backend.app.db.session import get_db
from backend.app.middleware.authorization_middleware import \
    AuthorizationMiddleware
from backend.app.middleware.blacklist_middleware import BlacklistMiddleware
from backend.app.middleware.cors_middleware import add_cors_middleware
from backend.app.services.permission_generator_service import (
    ensure_permissions_in_db, generate_permissions)
from backend.app.services.validation_service import \
    register_validation_listeners
from backend.app.crud.crud_time_period import init_time_periods_in_db

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs when the application starts up
    app.state.db = get_db()
    db = next(app.state.db)
    permissions = generate_permissions(app)
    ensure_permissions_in_db(db, permissions)
    register_validation_listeners()
    init_time_periods_in_db(db)  # Initialize time periods
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
app.include_router(question_tags_router.router, tags=["Question Tags"])
app.include_router(questions_router.router, tags=["Questions"])
app.include_router(subjects_router.router, tags=["Subjects"])
app.include_router(domains_router.router, tags=["Domains"])
app.include_router(disciplines_router.router, tags=["Disciplines"])
app.include_router(concepts_router.router, tags=["Concepts"])
app.include_router(user_responses_router.router, tags=["User Responses"])
app.include_router(users_router.router, tags=["User Management"])
app.include_router(topics_router.router, tags=["Topics"])
app.include_router(subtopics_router.router, tags=["Subtopics"])
app.include_router(time_periods_router.router, tags=["Time Periods"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

```

# Directory: /code/quiz-app/backend/app/schemas

## File: __init__.py
```py

```

## File: answer_choices.py
```py
# filename: backend/app/schemas/answer_choices.py

from typing import Optional, List

from pydantic import BaseModel, Field, validator, field_validator


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
    question_ids: Optional[list[int]] = None

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

class DetailedAnswerChoiceSchema(BaseModel):
    id: int
    text: str = Field(..., min_length=1, max_length=10000, description="The text of the question")
    is_correct: bool = Field(..., description="Whether this answer choice is correct")
    explanation: Optional[str] = Field(None, max_length=10000, description="Explanation for this answer choice")
    questions: List[dict] = Field(..., description="List of questions associated with this answer choice")

    @field_validator('questions', mode='before')
    @classmethod
    def ensure_dict_list(cls, v):
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        elif isinstance(v, list) and all(isinstance(item, str) for item in v):
            return [{"name": item} for item in v]
        elif isinstance(v, list) and all(hasattr(item, 'text') for item in v):
            return [{"id": item.id, "name": item.text} for item in v]
        else:
            raise ValueError("Must be a list of dictionaries, strings, or objects with 'text' attribute")

    class Config:
        from_attributes = True
```

## File: authentication.py
```py
# filename: backend/app/schemas/authentication.py

from pydantic import BaseModel, Field


class LoginFormSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    remember_me: bool = Field(default=False)

class TokenSchema(BaseModel):
    access_token: str = Field(..., min_length=1)
    token_type: str = Field(..., pattern="^bearer$", case_sensitive=False)

```

## File: concepts.py
```py
# filename: backend/app/schemas/concepts.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ConceptBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the concept")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Concept name cannot be empty or whitespace')
        return v

class ConceptCreateSchema(ConceptBaseSchema):
    subtopic_ids: List[int] = Field(..., min_items=1, description="List of subtopic IDs associated with this concept")

    @field_validator('subtopic_ids')
    @classmethod
    def subtopic_ids_must_be_unique(cls, v: List[int]) -> List[int]:
        if len(set(v)) != len(v):
            raise ValueError('Subtopic IDs must be unique')
        return v

class ConceptUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the concept")
    subtopic_ids: Optional[List[int]] = Field(None, min_items=1, description="List of subtopic IDs associated with this concept")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Concept name cannot be empty or whitespace')
        return v

    @field_validator('subtopic_ids')
    @classmethod
    def subtopic_ids_must_be_unique(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None and len(set(v)) != len(v):
            raise ValueError('Subtopic IDs must be unique')
        return v

class ConceptSchema(ConceptBaseSchema):
    id: int
    subtopics: Optional[List[dict]] = Field(None, description="List of subtopics associated with this concept")
    questions: Optional[List[dict]] = Field(None, description="List of questions associated with this concept")

    @field_validator('subtopics', 'questions', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True

```

## File: disciplines.py
```py
# filename: backend/app/schemas/disciplines.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DisciplineBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the discipline")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Discipline name cannot be empty or whitespace')
        return v

class DisciplineCreateSchema(DisciplineBaseSchema):
    domain_ids: List[int] = Field(..., min_items=1, description="List of domain IDs associated with this discipline")
    subject_ids: Optional[List[int]] = Field(None, description="List of subject IDs associated with this discipline")

class DisciplineUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the discipline")
    domain_ids: Optional[List[int]] = Field(None, min_items=1, description="List of domain IDs associated with this discipline")
    subject_ids: Optional[List[int]] = Field(None, description="List of subject IDs associated with this discipline")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Discipline name cannot be empty or whitespace')
        return v

class DisciplineSchema(DisciplineBaseSchema):
    id: int
    domains: Optional[List[dict]] = Field(None, description="List of domains associated with this discipline")
    subjects: Optional[List[dict]] = Field(None, description="List of subjects associated with this discipline")

    @field_validator('domains', 'subjects', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True

```

## File: domains.py
```py
# filename: backend/app/schemas/domains.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DomainBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the domain")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Domain name cannot be empty or whitespace')
        return v

class DomainCreateSchema(DomainBaseSchema):
    discipline_ids: Optional[List[int]] = Field(None, description="List of discipline IDs associated with this domain")

class DomainUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the domain")
    discipline_ids: Optional[List[int]] = Field(None, description="List of discipline IDs associated with this domain")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Domain name cannot be empty or whitespace')
        return v

class DomainSchema(DomainBaseSchema):
    id: Optional[int] = Field(None, description="ID of the domain")
    disciplines: Optional[List[dict]] = Field(None, description="List of disciplines associated with this domain")

    @field_validator('disciplines', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True

```

## File: filters.py
```py
# filename: backend/app/schemas/filters.py

from typing import List, Optional

from pydantic import BaseModel, Field, validator

from backend.app.schemas.questions import DifficultyLevel


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
# filename: backend/app/schemas/groups.py

import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class GroupBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=500, description="Description of the group")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[\w\-\s]+$', v):
            raise ValueError('Group name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class GroupCreateSchema(GroupBaseSchema):
    creator_id: int = Field(..., gt=0, description="ID of the user creating the group")

class GroupUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=500, description="Description of the group")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not re.match(r'^[\w\-\s]+$', v):
            raise ValueError('Group name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class GroupSchema(GroupBaseSchema):
    id: int
    creator_id: int
    users: Optional[List[dict]] = Field(None, description="List of users in this group")
    question_sets: Optional[List[dict]] = Field(None, description="List of question sets associated with this group")

    @field_validator('users', 'question_sets', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": getattr(item, 'name', None)} for item in v]

    class Config:
        from_attributes = True

```

## File: leaderboard.py
```py
# filename: backend/app/schemas/leaderboard.py

from typing import Optional

from pydantic import BaseModel, Field

from backend.app.schemas.time_period import TimePeriodSchema


class LeaderboardBaseSchema(BaseModel):
    user_id: int = Field(..., gt=0)
    score: int = Field(..., ge=0)
    group_id: Optional[int] = Field(None, gt=0)

class LeaderboardCreateSchema(LeaderboardBaseSchema):
    time_period_id: int = Field(..., gt=0)

class LeaderboardUpdateSchema(BaseModel):
    score: int = Field(..., ge=0)

class LeaderboardSchema(LeaderboardBaseSchema):
    id: int
    time_period_id: int
    time_period: TimePeriodSchema

    class Config:
        from_attributes = True

```

## File: permissions.py
```py
# filename: backend/app/schemas/permissions.py

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
# filename: backend/app/schemas/question_sets.py

import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class QuestionSetBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Name of the question set")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the question set")
    is_public: bool = Field(True, description="Whether the question set is public or private")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
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

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not re.match(r'^[\w\-\s]+$', v):
            raise ValueError('Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces')
        return v

class QuestionSetSchema(QuestionSetBaseSchema):
    id: int
    creator_id: int
    questions: Optional[List[dict]] = Field(None, description="List of questions in the set")
    groups: Optional[List[dict]] = Field(None, description="List of groups associated with the set")

    @field_validator('questions', 'groups', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": getattr(item, 'name', None)} for item in v]

    class Config:
        from_attributes = True

```

## File: question_tags.py
```py
# filename: backend/app/schemas/question_tags.py

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
# filename: backend/app/schemas/questions.py

from typing import List, Optional
from pydantic import BaseModel, Field, validator

from backend.app.core.config import DifficultyLevel
from backend.app.schemas.answer_choices import AnswerChoiceCreateSchema, AnswerChoiceSchema
from backend.app.schemas.question_sets import QuestionSetCreateSchema
from backend.app.schemas.question_tags import QuestionTagCreateSchema

class QuestionBaseSchema(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="The text of the question")
    difficulty: DifficultyLevel = Field(..., description="The difficulty level of the question")

    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Question text cannot be empty or only whitespace')
        return v

class QuestionCreateSchema(QuestionBaseSchema):
    subject_ids: List[int] = Field(..., min_items=1, description="IDs of the subjects associated with the question")
    topic_ids: List[int] = Field(..., min_items=1, description="IDs of the topics associated with the question")
    subtopic_ids: List[int] = Field(..., min_items=1, description="IDs of the subtopics associated with the question")
    concept_ids: List[int] = Field(..., min_items=1, description="IDs of the concepts associated with the question")
    answer_choice_ids: Optional[List[int]] = Field(None, description="List of answer choice IDs associated with the question")
    question_tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs associated with the question")
    question_set_ids: Optional[List[int]] = Field(None, description="List of question set IDs the question belongs to")

class QuestionReplaceSchema(QuestionBaseSchema):
    subject_ids: List[int] = Field(..., min_items=1, description="IDs of the subjects associated with the question")
    topic_ids: List[int] = Field(..., min_items=1, description="IDs of the topics associated with the question")
    subtopic_ids: List[int] = Field(..., min_items=1, description="IDs of the subtopics associated with the question")
    concept_ids: List[int] = Field(..., min_items=1, description="IDs of the concepts associated with the question")
    answer_choice_ids: List[int] = Field(..., min_items=1, description="List of answer choice IDs associated with the question")
    question_tag_ids: List[int] = Field(..., description="List of tag IDs associated with the question")
    question_set_ids: List[int] = Field(..., description="List of question set IDs the question belongs to")

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
    subjects: List[int]
    topics: List[int]
    subtopics: List[int]
    concepts: List[int]
    answer_choices: List[int]
    question_tags: List[int]
    question_sets: List[int]

    class Config:
        from_attributes = True

class DetailedQuestionSchema(BaseModel):
    id: int
    text: str = Field(..., min_length=1, max_length=10000, description="The text of the question")
    difficulty: DifficultyLevel
    subjects: List[dict] = Field(..., description="List of subjects associated with this question")
    topics: List[dict] = Field(..., description="List of topics associated with this question")
    subtopics: List[dict] = Field(..., description="List of subtopics associated with this question")
    concepts: List[dict] = Field(..., description="List of concepts associated with this question")
    answer_choices: List[AnswerChoiceSchema] = Field(..., description="List of answer choices for this question")
    question_tags: List[dict] = Field(..., description="List of tags associated with this question")
    question_sets: List[dict] = Field(..., description="List of question sets this question belongs to")

    class Config:
        from_attributes = True

class QuestionWithAnswersCreateSchema(QuestionCreateSchema):
    answer_choices: List[AnswerChoiceCreateSchema]
    question_tags: Optional[List['QuestionTagCreateSchema']] = None
    question_sets: Optional[List['QuestionSetCreateSchema']] = None

class QuestionWithAnswersReplaceSchema(QuestionReplaceSchema):
    answer_choice_ids: List[int] = Field(..., description="IDs of existing answer choices to keep")
    new_answer_choices: Optional[List[AnswerChoiceCreateSchema]] = Field(None, description="New answer choices to create")

```

## File: roles.py
```py
# filename: backend/app/schemas/roles.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class RoleBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Name of the role")
    description: Optional[str] = Field(None, max_length=200, description="Description of the role")
    default: bool = Field(False, description="Whether this is the default role for new users")

class RoleCreateSchema(RoleBaseSchema):
    permissions: List[str] = Field(..., min_items=1, description="List of permission names associated with the role")

    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v):
        return list(set(v))  # Remove duplicates

class RoleUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Name of the role")
    description: Optional[str] = Field(None, max_length=200, description="Description of the role")
    permissions: Optional[List[str]] = Field(None, min_items=1, description="List of permission names associated with the role")
    default: Optional[bool] = Field(None, description="Whether this is the default role for new users")

    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v):
        if v is not None:
            return list(set(v))  # Remove duplicates
        return v

class RoleSchema(RoleBaseSchema):
    id: int
    permissions: List[str] = Field(..., description="List of permission names associated with the role")

    @field_validator('permissions', mode='before')
    @classmethod
    def convert_permissions(cls, v):
        if isinstance(v, list) and all(isinstance(item, str) for item in v):
            return v
        elif isinstance(v, list) and all(hasattr(item, 'name') for item in v):
            return [item.name for item in v]
        else:
            raise ValueError("Permissions must be a list of strings or objects with 'name' attribute")

    class Config:
        from_attributes = True

```

## File: subjects.py
```py
# filename: backend/app/schemas/subjects.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SubjectBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the subject")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Subject name cannot be empty or whitespace')
        return v

class SubjectCreateSchema(SubjectBaseSchema):
    discipline_ids: List[int] = Field(..., min_items=1, description="List of discipline IDs associated with this subject")
    topic_ids: Optional[List[int]] = Field(None, description="List of topic IDs associated with this subject")

class SubjectUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the subject")
    discipline_ids: Optional[List[int]] = Field(None, min_items=1, description="List of discipline IDs associated with this subject")
    topic_ids: Optional[List[int]] = Field(None, description="List of topic IDs associated with this subject")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Subject name cannot be empty or whitespace')
        return v

class SubjectSchema(SubjectBaseSchema):
    id: int
    disciplines: Optional[List[dict]] = Field(None, description="List of disciplines associated with this subject")
    topics: Optional[List[dict]] = Field(None, description="List of topics associated with this subject")
    questions: Optional[List[dict]] = Field(None, description="List of questions associated with this subject")

    @field_validator('disciplines', 'topics', 'questions', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True

```

## File: subtopics.py
```py
# filename: backend/app/schemas/subtopics.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SubtopicBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the subtopic")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Subtopic name cannot be empty or whitespace')
        return v

class SubtopicCreateSchema(SubtopicBaseSchema):
    topic_ids: List[int] = Field(..., min_items=1, description="List of topic IDs associated with this subtopic")
    concept_ids: Optional[List[int]] = Field(None, description="List of concept IDs associated with this subtopic")

class SubtopicUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the subtopic")
    topic_ids: Optional[List[int]] = Field(None, min_items=1, description="List of topic IDs associated with this subtopic")
    concept_ids: Optional[List[int]] = Field(None, description="List of concept IDs associated with this subtopic")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Subtopic name cannot be empty or whitespace')
        return v

class SubtopicSchema(SubtopicBaseSchema):
    id: int
    topics: Optional[List[dict]] = Field(None, description="List of topics associated with this subtopic")
    concepts: Optional[List[dict]] = Field(None, description="List of concepts associated with this subtopic")
    questions: Optional[List[dict]] = Field(None, description="List of questions associated with this subtopic")

    @field_validator('topics', 'concepts', 'questions', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True

```

## File: time_period.py
```py
# filename: backend/app/schemas/time_period.py

from pydantic import BaseModel, Field, field_validator, model_validator


class TimePeriodSchema(BaseModel):
    id: int = Field(..., gt=0, description="ID of the time period")
    name: str = Field(..., min_length=1, max_length=20, description="Name of the time period")

    @field_validator('name')
    @classmethod
    def name_must_be_valid(cls, v):
        valid_names = {"daily", "weekly", "monthly", "yearly"}
        if v not in valid_names:
            raise ValueError(f"Name must be one of: daily, weekly, monthly, yearly")
        return v

    @model_validator(mode='after')
    def check_id_name_combination(self):
        id_name_map = {1: "daily", 7: "weekly", 30: "monthly", 365: "yearly"}
        if self.name != id_name_map.get(self.id):
            raise ValueError(f"Invalid combination of id and name. For id {self.id}, name should be {id_name_map.get(self.id)}")
        return self

    class Config:
        from_attributes = True

```

## File: topics.py
```py
# filename: backend/app/schemas/topics.py

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TopicBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the topic")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Topic name cannot be empty or whitespace')
        return v

class TopicCreateSchema(TopicBaseSchema):
    subject_ids: List[int] = Field(..., min_items=1, description="List of subject IDs associated with this topic")
    subtopic_ids: Optional[List[int]] = Field(None, description="List of subtopic IDs associated with this topic")

class TopicUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Name of the topic")
    subject_ids: Optional[List[int]] = Field(None, min_items=1, description="List of subject IDs associated with this topic")
    subtopic_ids: Optional[List[int]] = Field(None, description="List of subtopic IDs associated with this topic")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Topic name cannot be empty or whitespace')
        return v

class TopicSchema(TopicBaseSchema):
    id: int
    subjects: Optional[List[dict]] = Field(None, description="List of subjects associated with this topic")
    subtopics: Optional[List[dict]] = Field(None, description="List of subtopics associated with this topic")
    questions: Optional[List[dict]] = Field(None, description="List of questions associated with this topic")

    @field_validator('subjects', 'subtopics', 'questions', mode='before')
    @classmethod
    def convert_to_dict(cls, v):
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id, "name": item.name} for item in v]

    class Config:
        from_attributes = True

```

## File: user.py
```py
# filename: backend/app/schemas/user.py

import re
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator

from backend.app.core.security import get_password_hash


class UserBaseSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username of the user")
    email: EmailStr = Field(..., description="Email address of the user")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[\w\-\.]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, hyphens, underscores, and periods')
        return v

class UserCreateSchema(UserBaseSchema):
    password: SecretStr = Field(..., min_length=8, max_length=100, description="Password for the user")
    role_id: Optional[int] = Field(default=None, description="ID of the role for the user")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        password = v.get_secret_value()
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in password):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in password):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char in '!@#$%^&*(),.?":{}|<>' for char in password):
            raise ValueError('Password must contain at least one special character')
        return v

    def create_hashed_password(self):
        return get_password_hash(self.password.get_secret_value())

class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username of the user")
    email: Optional[EmailStr] = Field(None, description="Email address of the user")
    password: Optional[SecretStr] = Field(None, min_length=8, max_length=100, description="Password for the user")
    role_id: Optional[int] = Field(None, description="ID of the role for the user")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v is not None and not re.match(r'^[\w\-\.]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, hyphens, underscores, and periods')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is not None:
            return UserCreateSchema.validate_password(v)
        return v

    def create_hashed_password(self):
        if self.password:
            return get_password_hash(self.password.get_secret_value())
        return None

class UserSchema(UserBaseSchema):
    id: int
    is_active: bool
    is_admin: bool
    role: str
    groups: List[dict] = Field(default_factory=list)
    created_groups: List[dict] = Field(default_factory=list)
    created_question_sets: List[dict] = Field(default_factory=list)
    responses: List[dict] = Field(default_factory=list)
    leaderboards: List[dict] = Field(default_factory=list)

    @field_validator('role', mode='before')
    @classmethod
    def extract_role_name(cls, v):
        if hasattr(v, 'name'):
            return v.name
        return v

    @field_validator('groups', 'created_groups', 'created_question_sets', 'responses', 'leaderboards', mode='before')
    @classmethod
    def ensure_dict_list(cls, v):
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        return [{"id": item.id} for item in v]

    class Config:
        from_attributes = True

```

## File: user_responses.py
```py
# filename: backend/app/schemas/user_responses.py

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, validator


class UserResponseBaseSchema(BaseModel):
    user_id: int = Field(..., gt=0, description="ID of the user who responded")
    question_id: int = Field(..., gt=0, description="ID of the question answered")
    answer_choice_id: int = Field(..., gt=0, description="ID of the chosen answer")
    is_correct: Optional[bool] = Field(None, description="Whether the answer is correct")
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

# Directory: /code/quiz-app/backend/app/services

## File: __init__.py
```py

```

## File: auth_utils.py
```py
# filename: backend/app/services/auth_utils.py

from fastapi import HTTPException, status, Request

from backend.app.services.logging_service import logger

def check_auth_status(request: Request):
    """
    Check the authentication and authorization status from the request state.
    Raise appropriate HTTP exceptions if there are any issues.
    """
    if not hasattr(request.state, 'auth_status'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication status not available"
        )

    auth_status = request.state.auth_status

    if not auth_status["is_authorized"]:
        error = auth_status["error"]
        if error in ["invalid_token", "token_expired", "revoked_token", "user_not_found", "invalid_token_format"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {error}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif error == "insufficient_permissions":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have the required permissions"
            )
        elif error == "missing_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected authentication error: {error}"
            )

def get_current_user_or_error(request: Request):
    """
    Get the current user from the request state or raise an appropriate HTTP exception.
    """
    check_auth_status(request)
    if not hasattr(request.state, 'current_user') or request.state.current_user is None:
        logger.error("No current user found in request state")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request.state.current_user
```

## File: authentication_service.py
```py
# filename: backend/app/services/authentication_service.py

from sqlalchemy.orm import Session

from backend.app.core.security import verify_password
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.models.users import UserModel
from backend.app.crud.authentication import revoke_all_tokens_for_user

def authenticate_user(db: Session, username: str, password: str = None) -> UserModel:
    user = read_user_by_username_from_db(db, username)

    if not user:
        return False

    if password is not None:
        verification_result = verify_password(password, user.hashed_password)
        if not verification_result:
            return False

    if not user.is_active:
        return False

    return user

def revoke_all_user_tokens(db: Session, user_id: int):
    """
    Revoke all tokens for a given user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user whose tokens should be revoked.

    Returns:
        None
    """
    revoke_all_tokens_for_user(db, user_id)

```

## File: authorization_service.py
```py
# filename: backend/app/services/authorization_service.py

from typing import List

from sqlalchemy.orm import Session

from backend.app.crud.crud_roles import read_role_from_db, read_permissions_for_role_from_db

from backend.app.models.groups import GroupModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel


def get_user_permissions(db: Session, user: UserModel) -> List[str]:
    role = db.query(RoleModel).filter(RoleModel.name == user.role).first()
    if role:
        return [permission.name for permission in role.permissions]
    return []

def has_permission(db: Session, user: UserModel, required_permission: str) -> bool:
    # Use the read_role_by_name_from_db function to get the role
    user_role = read_role_from_db(db, user.role_id)
    
    if user_role:
        # Use the read_permissions_for_role_from_db function to get the permissions
        role_permissions = read_permissions_for_role_from_db(db, user_role.id)
        
        user_permissions = [permission.name for permission in role_permissions]
        has_perm = required_permission in user_permissions
        return has_perm
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
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

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

from backend.app.core.config import settings_core
from backend.app.models.permissions import PermissionModel


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

    return permissions

def ensure_permissions_in_db(db, permissions):
    existing_permissions = set(p.name for p in db.query(PermissionModel).all())
    new_permissions = permissions - existing_permissions

    for permission in new_permissions:
        db.add(PermissionModel(name=permission))

    db.commit()

```

## File: randomization_service.py
```py
# filename: backend/app/utils/randomization.py

import random


def randomize_questions(questions):
    return random.sample(questions, len(questions))

def randomize_answer_choices(answer_choices):
    return random.sample(answer_choices, len(answer_choices))

```

## File: scoring_service.py
```py
# filename: backend/app/services/scoring_service.py

from datetime import datetime, timedelta, timezone
from typing import Dict

from sqlalchemy.orm import Session

from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.time_period import TimePeriodModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.users import UserModel
from backend.app.schemas.leaderboard import LeaderboardSchema, TimePeriodSchema
from backend.app.core.config import TimePeriod


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

    if time_period.id == TimePeriod.DAILY.value:
        start_time = datetime.now(timezone.utc) - timedelta(days=1)
    elif time_period.id == TimePeriod.WEEKLY.value:
        start_time = datetime.now(timezone.utc) - timedelta(weeks=1)
    elif time_period.id == TimePeriod.MONTHLY.value:
        start_time = datetime.now(timezone.utc) - timedelta(days=30)
    elif time_period.id == TimePeriod.YEARLY.value:
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
# filename: backend/app/services/user_service.py

from datetime import datetime, timezone

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session

from backend.app.core.jwt import decode_access_token
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            return None, "invalid_token"
        
        user = read_user_by_username_from_db(db, username)
        if user is None:
            return None, "user_not_found"

        return user, "valid"
    except ExpiredSignatureError:
        return None, "token_expired"
    except JWTError:
        return None, "invalid_token"
    except Exception:
        return None, "internal_error"

```

## File: validation_service.py
```py
# filename: backend/app/services/validation_service.py

from fastapi import HTTPException
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from sqlalchemy.orm.base import instance_state

from backend.app.db.base import Base
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.authentication import RevokedTokenModel
from backend.app.models.groups import GroupModel
from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.permissions import PermissionModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import QuestionModel
from backend.app.models.roles import RoleModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.users import UserModel
from backend.app.services.logging_service import sqlalchemy_obj_to_dict


def validate_foreign_keys(mapper, connection, target):
    target_contents = sqlalchemy_obj_to_dict(target)
    db = Session(bind=connection)
    inspector = inspect(target.__class__)

    for relationship in inspector.relationships:
        if relationship.direction.name == 'MANYTOONE':
            validate_single_foreign_key(target, relationship, db)
        elif relationship.direction.name in ['ONETOMANY', 'MANYTOMANY']:
            validate_multiple_foreign_keys(target, relationship, db)

    validate_direct_foreign_keys(target, db)

def validate_single_foreign_key(target, relationship, db):
    foreign_key = relationship.key
    foreign_key_value = getattr(target, foreign_key)

    if foreign_key_value is not None:
        try:
            if isinstance(foreign_key_value, Base):
                foreign_key_value = inspect(foreign_key_value).identity[0]
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid foreign key value") from e
        
        related_class = relationship.entity.class_
        related_object = db.query(related_class).filter(related_class.id == foreign_key_value).first()
        
        if not related_object:
            raise HTTPException(status_code=400, detail=f"Invalid {foreign_key}")

def validate_multiple_foreign_keys(target, relationship, db):
    foreign_key = relationship.key
    foreign_key_values = getattr(target, foreign_key)

    if foreign_key_values:
        for foreign_key_value in foreign_key_values:
            try:
                if isinstance(foreign_key_value, Base):
                    state = instance_state(foreign_key_value)
                    if state.key is None:
                        continue
                    foreign_key_value = state.key[1][0]  # Get the first primary key value

                related_class = relationship.mapper.class_
                related_object = db.query(related_class).filter(related_class.id == foreign_key_value).first()
                
                if not related_object:
                    raise HTTPException(status_code=400, detail=f"Invalid {foreign_key}: {foreign_key_value}")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error validating {foreign_key}: {str(e)}") from e


def validate_direct_foreign_keys(target, db):
    target_contents = sqlalchemy_obj_to_dict(target)

    # Iterate through each attribute in the target object
    for attribute, value in target_contents.items():
        if isinstance(value, int):  # Assuming foreign keys are integers
            related_class = find_related_class(attribute)
            if related_class:
                related_object = db.query(related_class).filter(related_class.id == value).first()
                if not related_object:
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
        model_classes = Base._decl_class_registry.values()
    else:
        model_classes = Base.registry._class_registry.values()

    for model_class in model_classes:
        if hasattr(model_class, '__tablename__'):
            event.listen(model_class, 'before_insert', validate_foreign_keys)
            event.listen(model_class, 'before_update', validate_foreign_keys)

```

# Directory: /code/quiz-app/backend/app/crud

## File: __init__.py
```py

```

## File: authentication.py
```py
# filename: backend/app/crud/authentication.py

from datetime import datetime, timezone
from jose import ExpiredSignatureError

from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.models.authentication import RevokedTokenModel
from backend.app.core.jwt import decode_access_token
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.services.logging_service import logger

def create_revoked_token_in_db(db: Session, jti: str, token: str, user_id: int, expires_at: int) -> RevokedTokenModel:
    # Convert Unix timestamp to datetime object
    expires_at_datetime = datetime.fromtimestamp(expires_at, tz=timezone.utc)
    db_revoked_token = RevokedTokenModel(jti=jti, token=token, user_id=user_id, expires_at=expires_at_datetime, revoked_at=datetime.now(timezone.utc))
    db.add(db_revoked_token)
    db.commit()
    db.refresh(db_revoked_token)
    return db_revoked_token

def read_revoked_token_from_db(db: Session, token: str) -> RevokedTokenModel:
    return db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()

def is_token_revoked(db: Session, token: str) -> bool:
    try:
        decoded_token = decode_access_token(token)
    except ExpiredSignatureError:
        return True  # Consider expired tokens as revoked

    jti = decoded_token.get("jti")
    username = decoded_token.get("sub")
    token_iat = decoded_token.get("iat")

    if not jti or not username or not token_iat:
        logger.warning(f"Invalid token format: jti={jti}, username={username}, iat={token_iat}")
        return True  # Consider invalid tokens as revoked

    user = read_user_by_username_from_db(db, username)
    if not user:
        logger.warning(f"User not found for token: username={username}")
        return True  # Consider tokens for non-existent users as revoked

    # Check if the token is in the revoked tokens table
    revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.jti == jti).first()
    if revoked_token:
        logger.info(f"Token found in revoked tokens table: jti={jti}")
        return True

    # Check if the token was issued before the user's token_blacklist_date
    if user.token_blacklist_date:
        token_iat_datetime = datetime.fromtimestamp(token_iat, tz=timezone.utc)
        if token_iat_datetime < user.token_blacklist_date:
            logger.info(f"Token issued before blacklist date: iat={token_iat_datetime}, blacklist_date={user.token_blacklist_date}")
            return True

    logger.info(f"Token is not revoked: jti={jti}")
    return False

def revoke_all_tokens_for_user(db: Session, user_id: int, active_tokens: list):
    """
    Revoke all tokens for a given user.

    This function creates new revoked token entries for all active tokens of the user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user whose tokens should be revoked.
        active_tokens (list): List of active tokens for the user.

    Returns:
        None
    """
    current_time = datetime.now(timezone.utc)
    
    for token in active_tokens:
        try:
            decoded_token = decode_access_token(token)
        except ExpiredSignatureError:
            continue  # Skip expired tokens

        jti = decoded_token.get("jti")
        expires_at = decoded_token.get("exp")

        if not jti or not expires_at:
            continue  # Skip invalid tokens

        # Check if the token is already revoked
        existing_revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.jti == jti).first()
        if existing_revoked_token:
            existing_revoked_token.revoked_at = current_time
        else:
            create_revoked_token_in_db(db, jti, token, user_id, expires_at)

    db.commit()

def revoke_token(db: Session, token: str):
    """
    Revoke a specific token.

    This function creates a new revoked token entry for the given token if it's not already revoked.
    It also handles expired tokens by considering them as already revoked.

    Args:
        db (Session): The database session.
        token (str): The token to be revoked.

    Returns:
        None
    """
    try:
        decoded_token = decode_access_token(token)
    except ExpiredSignatureError:
        logger.info("Attempted to revoke an expired token")
        return  # Consider expired tokens as already revoked

    jti = decoded_token.get("jti")
    username = decoded_token.get("sub")
    expires_at = decoded_token.get("exp")

    if not jti or not username or not expires_at:
        logger.warning("Invalid token format")
        return

    user = read_user_by_username_from_db(db, username)
    if not user:
        logger.warning(f"User not found for token: username={username}")
        return

    # Check if the token is already revoked
    existing_revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.jti == jti).first()
    if existing_revoked_token:
        logger.info(f"Token already revoked: jti={jti}")
        return

    create_revoked_token_in_db(db, jti, token, user.id, expires_at)

```

## File: crud_answer_choices.py
```py
# filename: backend/app/crud/crud_answer_choices.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.associations import QuestionToAnswerAssociation
from backend.app.models.questions import QuestionModel
from backend.app.services.logging_service import logger


def create_answer_choice_in_db(db: Session, answer_choice_data: Dict) -> AnswerChoiceModel:
    logger.debug("Creating answer choice in DB: %s", answer_choice_data)
    db_answer_choice = AnswerChoiceModel(
        text=answer_choice_data['text'],
        is_correct=answer_choice_data['is_correct'],
        explanation=answer_choice_data.get('explanation')
    )
    logger.debug("DB answer choice before commit: %s", db_answer_choice)
    db.add(db_answer_choice)
    db.commit()
    db.refresh(db_answer_choice)
    
    if 'question_ids' in answer_choice_data and answer_choice_data['question_ids']:
        for question_id in answer_choice_data['question_ids']:
            create_question_to_answer_association_in_db(db, question_id, db_answer_choice.id)
    
    db.refresh(db_answer_choice)
            
    return db_answer_choice

def read_answer_choice_from_db(db: Session, answer_choice_id: int) -> Optional[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id == answer_choice_id).first()

def read_list_of_answer_choices_from_db(db: Session, answer_choice_ids: List[int]) -> List[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id.in_(answer_choice_ids)).all()

def read_answer_choices_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).offset(skip).limit(limit).all()

def update_answer_choice_in_db(db: Session, answer_choice_id: int, answer_choice_data: Dict) -> Optional[AnswerChoiceModel]:
    db_answer_choice = read_answer_choice_from_db(db, answer_choice_id)
    if db_answer_choice:
        for key, value in answer_choice_data.items():
            setattr(db_answer_choice, key, value)
        db.commit()
        db.refresh(db_answer_choice)
    return db_answer_choice

def delete_answer_choice_from_db(db: Session, answer_choice_id: int) -> bool:
    db_answer_choice = read_answer_choice_from_db(db, answer_choice_id)
    if db_answer_choice:
        db.delete(db_answer_choice)
        db.commit()
        return True
    return False

def create_question_to_answer_association_in_db(db: Session, question_id: int, answer_choice_id: int) -> bool:
    association = QuestionToAnswerAssociation(question_id=question_id, answer_choice_id=answer_choice_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_answer_association_from_db(db: Session, question_id: int, answer_choice_id: int) -> bool:
    association = db.query(QuestionToAnswerAssociation).filter_by(
        question_id=question_id, answer_choice_id=answer_choice_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_answer_choices_for_question_from_db(db: Session, question_id: int) -> List[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).join(QuestionToAnswerAssociation).filter(
        QuestionToAnswerAssociation.question_id == question_id
    ).all()

def read_questions_for_answer_choice_from_db(db: Session, answer_choice_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToAnswerAssociation).filter(
        QuestionToAnswerAssociation.answer_choice_id == answer_choice_id
    ).all()

```

## File: crud_concepts.py
```py
# filename: backend/app/crud/crud_concepts.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import (QuestionToConceptAssociation,
                                             SubtopicToConceptAssociation)
from backend.app.models.concepts import ConceptModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subtopics import SubtopicModel


def create_concept_in_db(db: Session, concept_data: Dict) -> ConceptModel:
    db_concept = ConceptModel(name=concept_data['name'])
    db.add(db_concept)
    db.commit()
    db.refresh(db_concept)

    if 'subtopic_ids' in concept_data and concept_data['subtopic_ids']:
        for subtopic_id in concept_data['subtopic_ids']:
            create_subtopic_to_concept_association_in_db(db, subtopic_id, db_concept.id)

    if 'question_ids' in concept_data and concept_data['question_ids']:
        for question_id in concept_data['question_ids']:
            create_question_to_concept_association_in_db(db, question_id, db_concept.id)

    return db_concept

def read_concept_from_db(db: Session, concept_id: int) -> Optional[ConceptModel]:
    return db.query(ConceptModel).filter(ConceptModel.id == concept_id).first()

def read_concept_by_name_from_db(db: Session, name: str) -> Optional[ConceptModel]:
    return db.query(ConceptModel).filter(ConceptModel.name == name).first()

def read_concepts_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[ConceptModel]:
    return db.query(ConceptModel).offset(skip).limit(limit).all()

def update_concept_in_db(db: Session, concept_id: int, concept_data: Dict) -> Optional[ConceptModel]:
    db_concept = read_concept_from_db(db, concept_id)
    if db_concept:
        for key, value in concept_data.items():
            setattr(db_concept, key, value)
        db.commit()
        db.refresh(db_concept)
    return db_concept

def delete_concept_from_db(db: Session, concept_id: int) -> bool:
    db_concept = read_concept_from_db(db, concept_id)
    if db_concept:
        db.delete(db_concept)
        db.commit()
        return True
    return False

def create_subtopic_to_concept_association_in_db(db: Session, subtopic_id: int, concept_id: int) -> bool:
    association = SubtopicToConceptAssociation(subtopic_id=subtopic_id, concept_id=concept_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_subtopic_to_concept_association_from_db(db: Session, subtopic_id: int, concept_id: int) -> bool:
    association = db.query(SubtopicToConceptAssociation).filter_by(
        subtopic_id=subtopic_id, concept_id=concept_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_question_to_concept_association_in_db(db: Session, question_id: int, concept_id: int) -> bool:
    association = QuestionToConceptAssociation(question_id=question_id, concept_id=concept_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_concept_association_from_db(db: Session, question_id: int, concept_id: int) -> bool:
    association = db.query(QuestionToConceptAssociation).filter_by(
        question_id=question_id, concept_id=concept_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_subtopics_for_concept_from_db(db: Session, concept_id: int) -> List[SubtopicModel]:
    return db.query(SubtopicModel).join(SubtopicToConceptAssociation).filter(
        SubtopicToConceptAssociation.concept_id == concept_id
    ).all()

def read_questions_for_concept_from_db(db: Session, concept_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToConceptAssociation).filter(
        QuestionToConceptAssociation.concept_id == concept_id
    ).all()

```

## File: crud_disciplines.py
```py
# filename: backend/app/crud/crud_disciplines.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import (DisciplineToSubjectAssociation,
                                             DomainToDisciplineAssociation)
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.domains import DomainModel
from backend.app.models.subjects import SubjectModel


def create_discipline_in_db(db: Session, discipline_data: Dict) -> DisciplineModel:
    db_discipline = DisciplineModel(name=discipline_data['name'])
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)

    if 'domain_ids' in discipline_data and discipline_data['domain_ids']:
        for domain_id in discipline_data['domain_ids']:
            create_domain_to_discipline_association_in_db(db, domain_id, db_discipline.id)

    if 'subject_ids' in discipline_data and discipline_data['subject_ids']:
        for subject_id in discipline_data['subject_ids']:
            create_discipline_to_subject_association_in_db(db, db_discipline.id, subject_id)

    return db_discipline

def read_discipline_from_db(db: Session, discipline_id: int) -> Optional[DisciplineModel]:
    return db.query(DisciplineModel).filter(DisciplineModel.id == discipline_id).first()

def read_discipline_by_name_from_db(db: Session, name: str) -> Optional[DisciplineModel]:
    return db.query(DisciplineModel).filter(DisciplineModel.name == name).first()

def read_disciplines_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[DisciplineModel]:
    return db.query(DisciplineModel).offset(skip).limit(limit).all()

def update_discipline_in_db(db: Session, discipline_id: int, discipline_data: Dict) -> Optional[DisciplineModel]:
    db_discipline = read_discipline_from_db(db, discipline_id)
    if db_discipline:
        for key, value in discipline_data.items():
            setattr(db_discipline, key, value)
        db.commit()
        db.refresh(db_discipline)
    return db_discipline

def delete_discipline_from_db(db: Session, discipline_id: int) -> bool:
    db_discipline = read_discipline_from_db(db, discipline_id)
    if db_discipline:
        db.delete(db_discipline)
        db.commit()
        return True
    return False

def create_domain_to_discipline_association_in_db(db: Session, domain_id: int, discipline_id: int) -> bool:
    association = DomainToDisciplineAssociation(domain_id=domain_id, discipline_id=discipline_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_domain_to_discipline_association_from_db(db: Session, domain_id: int, discipline_id: int) -> bool:
    association = db.query(DomainToDisciplineAssociation).filter_by(
        domain_id=domain_id, discipline_id=discipline_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_discipline_to_subject_association_in_db(db: Session, discipline_id: int, subject_id: int) -> bool:
    association = DisciplineToSubjectAssociation(discipline_id=discipline_id, subject_id=subject_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_discipline_to_subject_association_from_db(db: Session, discipline_id: int, subject_id: int) -> bool:
    association = db.query(DisciplineToSubjectAssociation).filter_by(
        discipline_id=discipline_id, subject_id=subject_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_domains_for_discipline_from_db(db: Session, discipline_id: int) -> List[DomainModel]:
    return db.query(DomainModel).join(DomainToDisciplineAssociation).filter(
        DomainToDisciplineAssociation.discipline_id == discipline_id
    ).all()

def read_subjects_for_discipline_from_db(db: Session, discipline_id: int) -> List[SubjectModel]:
    return db.query(SubjectModel).join(DisciplineToSubjectAssociation).filter(
        DisciplineToSubjectAssociation.discipline_id == discipline_id
    ).all()

```

## File: crud_domains.py
```py
# filename: backend/app/crud/crud_domains.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import DomainToDisciplineAssociation
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.domains import DomainModel


def create_domain_in_db(db: Session, domain_data: Dict) -> DomainModel:
    db_domain = DomainModel(name=domain_data['name'])
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)

    if 'discipline_ids' in domain_data and domain_data['discipline_ids']:
        for discipline_id in domain_data['discipline_ids']:
            create_domain_to_discipline_association_in_db(db, db_domain.id, discipline_id)

    return db_domain

def read_domain_from_db(db: Session, domain_id: int) -> Optional[DomainModel]:
    return db.query(DomainModel).filter(DomainModel.id == domain_id).first()

def read_domain_by_name_from_db(db: Session, name: str) -> Optional[DomainModel]:
    return db.query(DomainModel).filter(DomainModel.name == name).first()

def read_domains_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[DomainModel]:
    return db.query(DomainModel).offset(skip).limit(limit).all()

def update_domain_in_db(db: Session, domain_id: int, domain_data: Dict) -> Optional[DomainModel]:
    db_domain = read_domain_from_db(db, domain_id)
    if db_domain:
        for key, value in domain_data.items():
            setattr(db_domain, key, value)
        db.commit()
        db.refresh(db_domain)
    return db_domain

def delete_domain_from_db(db: Session, domain_id: int) -> bool:
    db_domain = read_domain_from_db(db, domain_id)
    if db_domain:
        db.delete(db_domain)
        db.commit()
        return True
    return False

def create_domain_to_discipline_association_in_db(db: Session, domain_id: int, discipline_id: int) -> bool:
    association = DomainToDisciplineAssociation(domain_id=domain_id, discipline_id=discipline_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_domain_to_discipline_association_from_db(db: Session, domain_id: int, discipline_id: int) -> bool:
    association = db.query(DomainToDisciplineAssociation).filter_by(
        domain_id=domain_id, discipline_id=discipline_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_disciplines_for_domain_from_db(db: Session, domain_id: int) -> List[DisciplineModel]:
    return db.query(DisciplineModel).join(DomainToDisciplineAssociation).filter(
        DomainToDisciplineAssociation.domain_id == domain_id
    ).all()

```

## File: crud_filters.py
```py
# filename: backend/app/crud/crud_filters.py

from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.core.config import DifficultyLevel


def read_filtered_questions_from_db(
    db: Session,
    filters: Dict,
    skip: int = 0,
    limit: int = 100
) -> List[QuestionModel]:
    query = db.query(QuestionModel).options(
        joinedload(QuestionModel.subjects),
        joinedload(QuestionModel.topics),
        joinedload(QuestionModel.subtopics),
        joinedload(QuestionModel.question_tags)
    )

    if filters.get('subject'):
        query = query.join(QuestionModel.subjects).filter(func.lower(SubjectModel.name) == func.lower(filters['subject']))
    if filters.get('topic'):
        query = query.join(QuestionModel.topics).filter(func.lower(TopicModel.name) == func.lower(filters['topic']))
    if filters.get('subtopic'):
        query = query.join(QuestionModel.subtopics).filter(func.lower(SubtopicModel.name) == func.lower(filters['subtopic']))
    if filters.get('difficulty'):
        query = query.filter(QuestionModel.difficulty == filters['difficulty'])
    if filters.get('question_tags'):
        query = query.join(QuestionModel.question_tags).filter(QuestionTagModel.tag.in_([tag.lower() for tag in filters['question_tags']]))

    return query.offset(skip).limit(limit).all()

```

## File: crud_groups.py
```py
# filename: backend/app/crud/crud_groups.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import (QuestionSetToGroupAssociation,
                                             UserToGroupAssociation)
from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.users import UserModel


def create_group_in_db(db: Session, group_data: Dict) -> GroupModel:
    db_group = GroupModel(
        name=group_data['name'],
        description=group_data.get('description'),
        creator_id=group_data['creator_id'],
        is_active=group_data.get('is_active', True)
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def read_group_from_db(db: Session, group_id: int) -> Optional[GroupModel]:
    return db.query(GroupModel).filter(GroupModel.id == group_id).first()

def read_groups_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[GroupModel]:
    return db.query(GroupModel).offset(skip).limit(limit).all()

def update_group_in_db(db: Session, group_id: int, group_data: Dict) -> Optional[GroupModel]:
    db_group = read_group_from_db(db, group_id)
    if db_group:
        for key, value in group_data.items():
            setattr(db_group, key, value)
        db.commit()
        db.refresh(db_group)
    return db_group

def delete_group_from_db(db: Session, group_id: int) -> bool:
    db_group = read_group_from_db(db, group_id)
    if db_group:
        db.delete(db_group)
        db.commit()
        return True
    return False

def create_user_to_group_association_in_db(db: Session, user_id: int, group_id: int) -> bool:
    association = UserToGroupAssociation(user_id=user_id, group_id=group_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_user_to_group_association_from_db(db: Session, user_id: int, group_id: int) -> bool:
    association = db.query(UserToGroupAssociation).filter_by(
        user_id=user_id, group_id=group_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_question_set_to_group_association_in_db(db: Session, question_set_id: int, group_id: int) -> bool:
    association = QuestionSetToGroupAssociation(question_set_id=question_set_id, group_id=group_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_set_to_group_association_from_db(db: Session, question_set_id: int, group_id: int) -> bool:
    association = db.query(QuestionSetToGroupAssociation).filter_by(
        question_set_id=question_set_id, group_id=group_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_users_for_group_from_db(db: Session, group_id: int) -> List[UserModel]:
    return db.query(UserModel).join(UserToGroupAssociation).filter(
        UserToGroupAssociation.group_id == group_id
    ).all()

def read_question_sets_for_group_from_db(db: Session, group_id: int) -> List[QuestionSetModel]:
    return db.query(QuestionSetModel).join(QuestionSetToGroupAssociation).filter(
        QuestionSetToGroupAssociation.group_id == group_id
    ).all()

```

## File: crud_leaderboard.py
```py
# filename: backend/app/crud/crud_leaderboard.py

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.time_period import TimePeriodModel
from backend.app.core.config import TimePeriod
from backend.app.services.logging_service import logger
from backend.app.crud.crud_time_period import read_time_period_from_db, create_time_period_in_db


def create_leaderboard_entry_in_db(db: Session, leaderboard_data: dict) -> LeaderboardModel:
    try:
        logger.debug(f"Attempting to create leaderboard entry with data: {leaderboard_data}")
        
        # Fetch the TimePeriodModel
        time_period_id = leaderboard_data.pop('time_period_id', None)
        if time_period_id is None:
            raise ValueError("time_period_id is required")
        
        time_period = read_time_period_from_db(db, time_period_id)
        if not time_period:
            raise ValueError(f"TimePeriod with id {time_period_id} not found")
        
        # Create the LeaderboardModel with the time_period relationship
        db_leaderboard_entry = LeaderboardModel(**leaderboard_data, time_period=time_period)
        db.add(db_leaderboard_entry)
        db.commit()
        db.refresh(db_leaderboard_entry)
        logger.debug(f"Successfully created leaderboard entry: {db_leaderboard_entry}")
        return db_leaderboard_entry
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"SQLAlchemy error creating leaderboard entry: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating leaderboard entry: {str(e)}")
        raise

def read_leaderboard_entry_from_db(db: Session, leaderboard_id: int) -> Optional[LeaderboardModel]:
    return db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_id).first()

def read_leaderboard_entries_from_db(
    db: Session,
    time_period_id: int,
    group_id: Optional[int] = None,
    user_id: Optional[int] = None,
    limit: int = 100
) -> List[LeaderboardModel]:
    query = db.query(LeaderboardModel).filter(LeaderboardModel.time_period_id == time_period_id)
    if group_id:
        query = query.filter(LeaderboardModel.group_id == group_id)
    if user_id:
        query = query.filter(LeaderboardModel.user_id == user_id)
    return query.order_by(LeaderboardModel.score.desc()).limit(limit).all()

def read_leaderboard_entries_for_user_from_db(db: Session, user_id: int) -> List[LeaderboardModel]:
    return db.query(LeaderboardModel).filter(LeaderboardModel.user_id == user_id).all()

def read_leaderboard_entries_for_group_from_db(db: Session, group_id: int) -> List[LeaderboardModel]:
    return db.query(LeaderboardModel).filter(LeaderboardModel.group_id == group_id).all()

def update_leaderboard_entry_in_db(db: Session, entry_id: int, update_data: dict) -> Optional[LeaderboardModel]:
    try:
        db_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == entry_id).first()
        if db_entry:
            for key, value in update_data.items():
                setattr(db_entry, key, value)
            db.commit()
            db.refresh(db_entry)
        return db_entry
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating leaderboard entry: {str(e)}")
        raise

def delete_leaderboard_entry_from_db(db: Session, leaderboard_id: int) -> bool:
    try:
        db_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_id).first()
        if db_entry:
            db.delete(db_entry)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting leaderboard entry: {str(e)}")
        raise

def read_or_create_time_period_in_db(db: Session, time_period_id: int) -> TimePeriodModel:
    try:
        time_period = TimePeriod(time_period_id)
    except ValueError:
        logger.error(f"Invalid time period id: {time_period_id}")
        raise ValueError(f"Invalid time period id: {time_period_id}")

    return read_time_period_from_db(db, time_period_id) or create_time_period_in_db(db, time_period)

```

## File: crud_permissions.py
```py
# filename: backend/app/crud/crud_permissions.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import RoleToPermissionAssociation
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel


def create_permission_in_db(db: Session, permission_data: Dict) -> PermissionModel:
    db_permission = PermissionModel(
        name=permission_data['name'],
        description=permission_data.get('description')
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def read_permission_from_db(db: Session, permission_id: int) -> Optional[PermissionModel]:
    return db.query(PermissionModel).filter(PermissionModel.id == permission_id).first()

def read_permission_by_name_from_db(db: Session, name: str) -> Optional[PermissionModel]:
    return db.query(PermissionModel).filter(PermissionModel.name == name).first()

def read_permissions_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[PermissionModel]:
    return db.query(PermissionModel).offset(skip).limit(limit).all()

def update_permission_in_db(db: Session, permission_id: int, permission_data: Dict) -> Optional[PermissionModel]:
    db_permission = read_permission_from_db(db, permission_id)
    if db_permission:
        for key, value in permission_data.items():
            setattr(db_permission, key, value)
        db.commit()
        db.refresh(db_permission)
    return db_permission

def delete_permission_from_db(db: Session, permission_id: int) -> bool:
    db_permission = read_permission_from_db(db, permission_id)
    if db_permission:
        db.delete(db_permission)
        db.commit()
        return True
    return False

def create_role_to_permission_association_in_db(db: Session, role_id: int, permission_id: int) -> bool:
    association = RoleToPermissionAssociation(role_id=role_id, permission_id=permission_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_role_to_permission_association_from_db(db: Session, role_id: int, permission_id: int) -> bool:
    association = db.query(RoleToPermissionAssociation).filter_by(
        role_id=role_id, permission_id=permission_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_roles_for_permission_from_db(db: Session, permission_id: int) -> List[RoleModel]:
    return db.query(RoleModel).join(RoleToPermissionAssociation).filter(
        RoleToPermissionAssociation.permission_id == permission_id
    ).all()

```

## File: crud_question_sets.py
```py
# filename: backend/app/crud/crud_question_sets.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import (QuestionSetToGroupAssociation,
                                             QuestionSetToQuestionAssociation)
from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.questions import QuestionModel
from backend.app.crud.crud_questions import read_question_from_db
from backend.app.crud.crud_groups import read_group_from_db
from backend.app.services.logging_service import logger

def check_existing_question_set(db: Session, name: str, creator_id: int) -> Optional[QuestionSetModel]:
    return db.query(QuestionSetModel).filter(
        QuestionSetModel.name == name,
        QuestionSetModel.creator_id == creator_id
    ).first()

def create_question_set_in_db(db: Session, question_set_data: Dict) -> QuestionSetModel:
    existing_question_set = check_existing_question_set(db, question_set_data['name'], question_set_data['creator_id'])
    if existing_question_set:
        raise ValueError("A question set with this name already exists for this user")

    try:    
        db_question_set = QuestionSetModel(
            name=question_set_data['name'],
            description=question_set_data.get('description'),
            is_public=question_set_data.get('is_public', True),
            creator_id=question_set_data['creator_id']
        )
        db.add(db_question_set)
        db.commit()
        db.refresh(db_question_set)
        if 'question_ids' in question_set_data:
            # Add new associations
            for question_id in question_set_data['question_ids']:
                question = read_question_from_db(db, question_id)
                logger.debug("question: %s", question)
                if question and question is not None:
                    association = QuestionSetToQuestionAssociation(question_set_id=db_question_set.id, question_id=question_id)
                    db.add(association)
                else:
                    raise ValueError(f"Question with id {question_id} does not exist")
        if 'group_ids' in question_set_data:
            # Add new associations
            for group_id in question_set_data['group_ids']:
                group = read_group_from_db(db, group_id)
                if group and group is not None:
                    association = QuestionSetToGroupAssociation(question_set_id=db_question_set.id, group_id=group_id)
                    db.add(association)
                else:
                    raise ValueError(f"Group with id {group_id} does not exist")
        db.commit()
        db.refresh(db_question_set)
        return db_question_set
    
    except ValueError as exc:
        db.rollback()
        raise exc

def read_question_set_from_db(db: Session, question_set_id: int) -> Optional[QuestionSetModel]:
    return db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()

def read_question_sets_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSetModel]:
    return db.query(QuestionSetModel).offset(skip).limit(limit).all()

def update_question_set_in_db(db: Session, question_set_id: int, question_set_data: Dict) -> Optional[QuestionSetModel]:
    try:
        db_question_set = read_question_set_from_db(db, question_set_id)
        if db_question_set and db_question_set is not None:
            for key, value in question_set_data.items():
                if key not in ['question_ids', 'group_ids'] and value is not None:
                    setattr(db_question_set, key, value)
            
            if 'question_ids' in question_set_data:
                # Remove existing associations
                db.query(QuestionSetToQuestionAssociation).filter_by(question_set_id=question_set_id).delete()

                # Add new associations
                for question_id in question_set_data['question_ids']:
                    question = read_question_from_db(db, question_id)
                    logger.debug("question: %s", question)
                    if question and question is not None:
                        association = QuestionSetToQuestionAssociation(question_set_id=db_question_set.id, question_id=question_id)
                        db.add(association)
                    else:
                        raise ValueError(f"Question with id {question_id} does not exist")
            if 'group_ids' in question_set_data:
                # Remove existing associations
                db.query(QuestionSetToGroupAssociation).filter_by(question_set_id=question_set_id).delete()

                # Add new associations
                for group_id in question_set_data['group_ids']:
                    group = read_group_from_db(db, group_id)
                    if group and group is not None:
                        association = QuestionSetToGroupAssociation(question_set_id=db_question_set.id, group_id=group_id)
                        db.add(association)
                    else:
                        raise ValueError(f"Group with id {group_id} does not exist")
            db.commit()
            db.refresh(db_question_set)
            return db_question_set
        else:
            raise ValueError(f"Question set with id {question_set_id} does not exist")
    except ValueError as exc:
        db.rollback()
        raise exc

def delete_question_set_from_db(db: Session, question_set_id: int) -> bool:
    db_question_set = read_question_set_from_db(db, question_set_id)
    if db_question_set:
        db.delete(db_question_set)
        db.commit()
        return True
    return False

def create_question_set_to_question_association_in_db(db: Session, question_set_id: int, question_id: int) -> bool:
    association = QuestionSetToQuestionAssociation(question_set_id=question_set_id, question_id=question_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_set_to_question_association_from_db(db: Session, question_set_id: int, question_id: int) -> bool:
    association = db.query(QuestionSetToQuestionAssociation).filter_by(
        question_set_id=question_set_id, question_id=question_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_question_set_to_group_association_in_db(db: Session, question_set_id: int, group_id: int) -> bool:
    association = QuestionSetToGroupAssociation(question_set_id=question_set_id, group_id=group_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_set_to_group_association_from_db(db: Session, question_set_id: int, group_id: int) -> bool:
    association = db.query(QuestionSetToGroupAssociation).filter_by(
        question_set_id=question_set_id, group_id=group_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_questions_for_question_set_from_db(db: Session, question_set_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionSetToQuestionAssociation).filter(
        QuestionSetToQuestionAssociation.question_set_id == question_set_id
    ).all()

def read_groups_for_question_set_from_db(db: Session, question_set_id: int) -> List[GroupModel]:
    return db.query(GroupModel).join(QuestionSetToGroupAssociation).filter(
        QuestionSetToGroupAssociation.question_set_id == question_set_id
    ).all()

```

## File: crud_question_tags.py
```py
# filename: backend/app/crud/crud_question_tags.py

from typing import Dict, List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.associations import QuestionToTagAssociation
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import QuestionModel


def create_question_tag_in_db(db: Session, question_tag_data: Dict) -> QuestionTagModel:
    # Check if the tag already exists
    existing_tag = read_question_tag_by_tag_from_db(db, question_tag_data['tag'])
    if existing_tag:
        raise IntegrityError("Tag already exists", params=question_tag_data, orig=None)
    if question_tag_data['tag'] is not None and question_tag_data['tag'] != "":
        db_question_tag = QuestionTagModel(
            tag=question_tag_data['tag'],
            description=question_tag_data.get('description')
        )
        db.add(db_question_tag)
    else:
        raise ValueError("Tag cannot be None or empty")
    try:
        db.commit()
        db.refresh(db_question_tag)
        return db_question_tag
    except IntegrityError as e:
        db.rollback()
        raise e
    except ValueError as e:
        db.rollback()
        raise e

def read_question_tag_from_db(db: Session, question_tag_id: int) -> Optional[QuestionTagModel]:
    return db.query(QuestionTagModel).filter(QuestionTagModel.id == question_tag_id).first()

def read_question_tag_by_tag_from_db(db: Session, tag: str) -> Optional[QuestionTagModel]:
    return db.query(QuestionTagModel).filter(QuestionTagModel.tag == tag.lower()).first()

def read_question_tags_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionTagModel]:
    return db.query(QuestionTagModel).offset(skip).limit(limit).all()

def update_question_tag_in_db(db: Session, question_tag_id: int, question_tag_data: Dict) -> Optional[QuestionTagModel]:
    try:
        db_question_tag = read_question_tag_from_db(db, question_tag_id)
        if db_question_tag:
            for key, value in question_tag_data.items():
                if key == 'tag':
                    existing_tag = read_question_tag_by_tag_from_db(db, value)
                    if existing_tag:
                        raise IntegrityError("Tag already exists", params=question_tag_data, orig=None)
                    if value is not None and value != "":
                        setattr(db_question_tag, key, value)
                    else:
                        raise ValueError("Tag cannot be None or empty")
                setattr(db_question_tag, key, value)
            db.commit()
            db.refresh(db_question_tag)
        return db_question_tag
    except IntegrityError as e:
        db.rollback()
        raise e
    except ValueError as e:
        db.rollback()
        raise e

def delete_question_tag_from_db(db: Session, question_tag_id: int) -> bool:
    db_question_tag = read_question_tag_from_db(db, question_tag_id)
    if db_question_tag:
        db.delete(db_question_tag)
        db.commit()
        return True
    return False

def create_question_to_tag_association_in_db(db: Session, question_id: int, tag_id: int) -> bool:
    association = QuestionToTagAssociation(question_id=question_id, question_tag_id=tag_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_tag_association_from_db(db: Session, question_id: int, tag_id: int) -> bool:
    association = db.query(QuestionToTagAssociation).filter_by(
        question_id=question_id, question_tag_id=tag_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_tags_for_question_from_db(db: Session, question_id: int) -> List[QuestionTagModel]:
    return db.query(QuestionTagModel).join(QuestionToTagAssociation).filter(
        QuestionToTagAssociation.question_id == question_id
    ).all()

def read_questions_for_tag_from_db(db: Session, tag_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToTagAssociation).filter(
        QuestionToTagAssociation.question_tag_id == tag_id
    ).all()

```

## File: crud_questions.py
```py
# filename: backend/app/crud/crud_questions.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.crud.crud_answer_choices import create_answer_choice_in_db, read_list_of_answer_choices_from_db
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.concepts import ConceptModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import DifficultyLevel, QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.services.logging_service import logger

ASSOCIATED_FIELDS = ['answer_choices', 'question_tag_ids', 'question_set_ids',
                     'subject_ids', 'topic_ids', 'subtopic_ids',
                     'answer_choice_ids', 'concept_ids']

def associate_question_related_models(db: Session, db_question: QuestionModel, question_data: Dict) -> None:
    """Helper function to associate related models with the question."""
    for key, value in question_data.items():
        if not value:
            continue

        if key in ['answer_choices', 'new_answer_choices']:
            logger.debug("Creating answer choices: %s", value)
            for answer_choice_data in value:
                if 'question_ids' not in answer_choice_data or answer_choice_data['question_ids'] is None:
                    answer_choice_data['question_ids'] = [db_question.id]
                else:
                    answer_choice_data['question_ids'].append(db_question.id)
                logger.debug("Creating answer choice: %s", answer_choice_data)
                db_answer_choice = create_answer_choice_in_db(db, answer_choice_data)
                db_question.answer_choices.append(db_answer_choice)

        elif key == 'answer_choice_ids':
            existing_answer_choices = read_list_of_answer_choices_from_db(db, value)
            db_question.answer_choices = existing_answer_choices

        elif key in ['question_tag_ids', 'question_set_ids', 'subject_ids', 'topic_ids', 'subtopic_ids', 'concept_ids']:
            model_map = {
                'question_tag_ids': QuestionTagModel,
                'question_set_ids': QuestionSetModel,
                'subject_ids': SubjectModel,
                'topic_ids': TopicModel,
                'subtopic_ids': SubtopicModel,
                'concept_ids': ConceptModel,
            }
            related_items = db.query(model_map[key]).filter(model_map[key].id.in_(value)).all()
            current_items = getattr(db_question, key.replace('_ids', 's'))
            setattr(db_question, key.replace('_ids', 's'), list(set(current_items + related_items)))
        
        else:
            setattr(db_question, key, value)

def update_associations_to_question_related_models(db: Session, db_question: QuestionModel, question_data: Dict) -> None:
    """Helper function to update associations to models related to the question."""
    for key, value in question_data.items():
        if key not in ASSOCIATED_FIELDS or value is None:
            continue

        if key == 'answer_choice_ids':
            if value:
                existing_answer_choices = db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id.in_(value)).all()
                db_question.answer_choices = existing_answer_choices
            else:
                db_question.answer_choices = []
        elif key in ['question_tag_ids', 'question_set_ids', 'subject_ids', 'topic_ids', 'subtopic_ids', 'concept_ids']:
            model_map = {
                'question_tag_ids': QuestionTagModel,
                'question_set_ids': QuestionSetModel,
                'subject_ids': SubjectModel,
                'topic_ids': TopicModel,
                'subtopic_ids': SubtopicModel,
                'concept_ids': ConceptModel,
            }
            attr_name = key.replace('_ids', 's')
            current_items = getattr(db_question, attr_name)
            if value:
                new_items = db.query(model_map[key]).filter(model_map[key].id.in_(value)).all()
                setattr(db_question, attr_name, list(set(current_items + new_items)))
            else:
                setattr(db_question, attr_name, [])

def create_question_in_db(db: Session, question_data: Dict) -> QuestionModel:
    """Creates a new question in the database."""
    try:
        if question_data['text'] is None or question_data['text'] == "":
            raise ValueError("Question text cannot be None or empty")
        db_question = QuestionModel(
            text=question_data['text'],
            difficulty=DifficultyLevel(question_data['difficulty'])
            if isinstance(question_data['difficulty'], str)
            else question_data['difficulty']
        )
        db.add(db_question)
        db.flush()

        # Associate related models
        associate_question_related_models(db, db_question, question_data)

        db.commit()
        db.refresh(db_question)
        return db_question

    except ValueError as e:
        db.rollback()
        raise e

def read_question_from_db(db: Session, question_id: int) -> Optional[QuestionModel]:
    return db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

def read_questions_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionModel]:
    return db.query(QuestionModel).offset(skip).limit(limit).all()

def replace_question_in_db(db: Session, question_id: int, replace_data: Dict) -> Optional[QuestionModel]:
    """Replaces an existing question in the database."""
    db_question = read_question_from_db(db, question_id)
    if db_question is None:
        return None

    try:
        # Update simple fields
        for key, value in replace_data.items():
            if key not in ASSOCIATED_FIELDS and key != 'new_answer_choices':
                setattr(db_question, key, value)

        # Clear existing associations
        db_question.subjects = []
        db_question.topics = []
        db_question.subtopics = []
        db_question.concepts = []
        db_question.question_tags = []
        db_question.question_sets = []
        db_question.answer_choices = []

        # Set new associations
        associate_question_related_models(db, db_question, replace_data)

        db.commit()
        db.refresh(db_question)
        return db_question
    except Exception as e:
        db.rollback()
        logger.error("Error replacing question: %s", str(e))
        raise

def update_question_in_db(db: Session, question_id: int, update_data: Dict) -> Optional[QuestionModel]:
    """Updates an existing question in the database."""
    db_question = read_question_from_db(db, question_id)
    if db_question is None:
        return None

    try:
        # Handle answer choices separately
        existing_answer_choices = update_data.pop('answer_choice_ids', None)
        new_answer_choices = update_data.pop('new_answer_choices', None)

        # Update simple fields
        for key, value in update_data.items():
            if key not in ASSOCIATED_FIELDS:
                if value is not None:
                    setattr(db_question, key, value)

        # Update associations
        update_associations_to_question_related_models(db, db_question, update_data)

        # Handle answer choices
        if existing_answer_choices is not None:
            db_question.answer_choices = db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id.in_(existing_answer_choices)).all()

        if new_answer_choices:
            for answer_choice_data in new_answer_choices:
                db_answer_choice = AnswerChoiceModel(**answer_choice_data)
                db.add(db_answer_choice)
                db_question.answer_choices.append(db_answer_choice)

        db.commit()
        db.refresh(db_question)
        return db_question
    except Exception as e:
        db.rollback()
        logger.error("Error updating question: %s", str(e))
        raise

def delete_question_from_db(db: Session, question_id: int) -> bool:
    db_question = read_question_from_db(db, question_id)
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False

```

## File: crud_roles.py
```py
# filename: backend/app/crud/crud_roles.py

from typing import Dict, List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.associations import RoleToPermissionAssociation
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel


def create_role_in_db(db: Session, role_data: Dict) -> RoleModel:
    is_default = role_data.get('default', False)
    if is_default:
        existing_default = db.query(RoleModel).filter(RoleModel.default == True).first()
        if existing_default:
            raise IntegrityError("A default role already exists", params=None, orig=None)

    db_role = RoleModel(
        name=role_data['name'],
        description=role_data.get('description'),
        default=is_default
    )
    db.add(db_role)
    db.flush()  # Flush to get the role ID

    # Handle permissions
    if 'permissions' in role_data:
        for permission_name in role_data['permissions']:
            permission = db.query(PermissionModel).filter(PermissionModel.name == permission_name).first()
            if permission:
                association = RoleToPermissionAssociation(role_id=db_role.id, permission_id=permission.id)
                db.add(association)

    db.commit()
    db.refresh(db_role)
    return db_role

def read_role_from_db(db: Session, role_id: int) -> Optional[RoleModel]:
    return db.query(RoleModel).filter(RoleModel.id == role_id).first()

def read_role_by_name_from_db(db: Session, name: str) -> Optional[RoleModel]:
    return db.query(RoleModel).filter(RoleModel.name == name).first()

def read_roles_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[RoleModel]:
    return db.query(RoleModel).offset(skip).limit(limit).all()

def update_role_in_db(db: Session, role_id: int, role_data: Dict) -> Optional[RoleModel]:
    db_role = read_role_from_db(db, role_id)
    if db_role:
        if 'default' in role_data and role_data['default']:
            existing_default = db.query(RoleModel).filter(RoleModel.default == True, RoleModel.id != role_id).first()
            if existing_default:
                raise IntegrityError("A default role already exists", params=None, orig=None)
        
        for key, value in role_data.items():
            if key != 'permissions':
                setattr(db_role, key, value)

        # Handle permissions
        if 'permissions' in role_data:
            # Remove existing permissions
            db.query(RoleToPermissionAssociation).filter(RoleToPermissionAssociation.role_id == role_id).delete()
            
            # Add new permissions
            for permission_name in role_data['permissions']:
                permission = db.query(PermissionModel).filter(PermissionModel.name == permission_name).first()
                if permission:
                    association = RoleToPermissionAssociation(role_id=db_role.id, permission_id=permission.id)
                    db.add(association)

        db.commit()
        db.refresh(db_role)
    return db_role

def delete_role_from_db(db: Session, role_id: int) -> bool:
    db_role = read_role_from_db(db, role_id)
    if db_role:
        # Find a default role to reassign users
        default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
        if not default_role:
            raise ValueError("No default role found to reassign users")

        # Reassign users to the default role
        db.query(UserModel).filter(UserModel.role_id == role_id).update({UserModel.role_id: default_role.id})

        # Delete the role
        db.delete(db_role)
        db.commit()
        return True
    return False

def create_role_to_permission_association_in_db(db: Session, role_id: int, permission_id: int) -> bool:
    association = RoleToPermissionAssociation(role_id=role_id, permission_id=permission_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_role_to_permission_association_from_db(db: Session, role_id: int, permission_id: int) -> bool:
    association = db.query(RoleToPermissionAssociation).filter_by(
        role_id=role_id, permission_id=permission_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_permissions_for_role_from_db(db: Session, role_id: int) -> List[PermissionModel]:
    return db.query(PermissionModel).join(RoleToPermissionAssociation).filter(
        RoleToPermissionAssociation.role_id == role_id
    ).all()

def read_users_for_role_from_db(db: Session, role_id: int) -> List[UserModel]:
    return db.query(UserModel).filter(UserModel.role_id == role_id).all()

def read_default_role_from_db(db: Session) -> Optional[RoleModel]:
    return db.query(RoleModel).filter(RoleModel.default == True).first()

def read_role_by_name_from_db(db: Session, name: str) -> Optional[RoleModel]:
    return db.query(RoleModel).filter(RoleModel.name == name).first()

def read_roles_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[RoleModel]:
    return db.query(RoleModel).offset(skip).limit(limit).all()

```

## File: crud_subjects.py
```py
# filename: backend/app/crud/crud_subjects.py

from typing import Dict, List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.associations import (DisciplineToSubjectAssociation,
                                             QuestionToSubjectAssociation,
                                             SubjectToTopicAssociation)
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.topics import TopicModel
from backend.app.services.logging_service import logger


def create_subject_in_db(db: Session, subject_data: Dict) -> SubjectModel:
    # Validate discipline IDs before creating the subject
    if 'discipline_ids' in subject_data and subject_data['discipline_ids']:
        for discipline_id in subject_data['discipline_ids']:
            discipline = db.query(DisciplineModel).filter(DisciplineModel.id == discipline_id).first()
            if not discipline:
                raise HTTPException(status_code=400, detail=f"Invalid discipline_id: {discipline_id}")

    db_subject = SubjectModel(name=subject_data['name'])
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)

    if 'discipline_ids' in subject_data and subject_data['discipline_ids']:
        for discipline_id in subject_data['discipline_ids']:
            create_discipline_to_subject_association_in_db(db, discipline_id, db_subject.id)

    if 'topic_ids' in subject_data and subject_data['topic_ids']:
        for topic_id in subject_data['topic_ids']:
            create_subject_to_topic_association_in_db(db, db_subject.id, topic_id)

    if 'question_ids' in subject_data and subject_data['question_ids']:
        for question_id in subject_data['question_ids']:
            create_question_to_subject_association_in_db(db, question_id, db_subject.id)

    return db_subject

def read_subject_from_db(db: Session, subject_id: int) -> Optional[SubjectModel]:
    return db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()

def read_subject_by_name_from_db(db: Session, name: str) -> Optional[SubjectModel]:
    return db.query(SubjectModel).filter(SubjectModel.name == name).first()

def read_subjects_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[SubjectModel]:
    return db.query(SubjectModel).offset(skip).limit(limit).all()

def update_subject_in_db(db: Session, subject_id: int, subject_data: Dict) -> Optional[SubjectModel]:
    logger.debug(f"Updating subject with id {subject_id}. Data: {subject_data}")
    db_subject = read_subject_from_db(db, subject_id)
    if db_subject:
        logger.debug(f"Found subject: {db_subject}")
        if 'name' in subject_data:
            db_subject.name = subject_data['name']

        if 'discipline_ids' in subject_data:
            logger.debug(f"Updating disciplines for subject {subject_id}")
            # Validate discipline IDs before updating
            for discipline_id in subject_data['discipline_ids']:
                discipline = db.query(DisciplineModel).filter(DisciplineModel.id == discipline_id).first()
                if not discipline:
                    logger.error(f"Discipline not found: {discipline_id}")
                    raise HTTPException(status_code=404, detail=f"Discipline not found: {discipline_id}")

            # Remove all existing associations
            db.query(DisciplineToSubjectAssociation).filter(DisciplineToSubjectAssociation.subject_id == subject_id).delete()

            # Create new associations
            for discipline_id in subject_data['discipline_ids']:
                create_discipline_to_subject_association_in_db(db, discipline_id, subject_id)

        try:
            db.commit()
            logger.debug(f"Successfully updated subject {subject_id}")
        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError while updating subject {subject_id}: {str(e)}")
            raise HTTPException(status_code=400, detail="Subject with this name already exists")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while updating subject {subject_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        db.refresh(db_subject)
    else:
        logger.error(f"Subject not found: {subject_id}")
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject

def delete_subject_from_db(db: Session, subject_id: int) -> bool:
    db_subject = read_subject_from_db(db, subject_id)
    if db_subject:
        db.delete(db_subject)
        db.commit()
        return True
    return False

def create_discipline_to_subject_association_in_db(db: Session, discipline_id: int, subject_id: int) -> bool:
    association = DisciplineToSubjectAssociation(discipline_id=discipline_id, subject_id=subject_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_discipline_to_subject_association_from_db(db: Session, discipline_id: int, subject_id: int) -> bool:
    association = db.query(DisciplineToSubjectAssociation).filter_by(
        discipline_id=discipline_id, subject_id=subject_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_subject_to_topic_association_in_db(db: Session, subject_id: int, topic_id: int) -> bool:
    association = SubjectToTopicAssociation(subject_id=subject_id, topic_id=topic_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_subject_to_topic_association_from_db(db: Session, subject_id: int, topic_id: int) -> bool:
    association = db.query(SubjectToTopicAssociation).filter_by(
        subject_id=subject_id, topic_id=topic_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_question_to_subject_association_in_db(db: Session, question_id: int, subject_id: int) -> bool:
    association = QuestionToSubjectAssociation(question_id=question_id, subject_id=subject_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_subject_association_from_db(db: Session, question_id: int, subject_id: int) -> bool:
    association = db.query(QuestionToSubjectAssociation).filter_by(
        question_id=question_id, subject_id=subject_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_disciplines_for_subject_from_db(db: Session, subject_id: int) -> List[DisciplineModel]:
    return db.query(DisciplineModel).join(DisciplineToSubjectAssociation).filter(
        DisciplineToSubjectAssociation.subject_id == subject_id
    ).all()

def read_topics_for_subject_from_db(db: Session, subject_id: int) -> List[TopicModel]:
    return db.query(TopicModel).join(SubjectToTopicAssociation).filter(
        SubjectToTopicAssociation.subject_id == subject_id
    ).all()

def read_questions_for_subject_from_db(db: Session, subject_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToSubjectAssociation).filter(
        QuestionToSubjectAssociation.subject_id == subject_id
    ).all()

```

## File: crud_subtopics.py
```py
# filename: backend/app/crud/crud_subtopics.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import (QuestionToSubtopicAssociation,
                                             SubtopicToConceptAssociation,
                                             TopicToSubtopicAssociation)
from backend.app.models.concepts import ConceptModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def create_subtopic_in_db(db: Session, subtopic_data: Dict) -> SubtopicModel:
    db_subtopic = SubtopicModel(name=subtopic_data['name'])
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)

    if 'topic_ids' in subtopic_data and subtopic_data['topic_ids']:
        for topic_id in subtopic_data['topic_ids']:
            create_topic_to_subtopic_association_in_db(db, topic_id, db_subtopic.id)

    if 'concept_ids' in subtopic_data and subtopic_data['concept_ids']:
        for concept_id in subtopic_data['concept_ids']:
            create_subtopic_to_concept_association_in_db(db, db_subtopic.id, concept_id)

    if 'question_ids' in subtopic_data and subtopic_data['question_ids']:
        for question_id in subtopic_data['question_ids']:
            create_question_to_subtopic_association_in_db(db, question_id, db_subtopic.id)

    return db_subtopic

def read_subtopic_from_db(db: Session, subtopic_id: int) -> Optional[SubtopicModel]:
    return db.query(SubtopicModel).filter(SubtopicModel.id == subtopic_id).first()

def read_subtopic_by_name_from_db(db: Session, name: str) -> Optional[SubtopicModel]:
    return db.query(SubtopicModel).filter(SubtopicModel.name == name).first()

def read_subtopics_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[SubtopicModel]:
    return db.query(SubtopicModel).offset(skip).limit(limit).all()

def update_subtopic_in_db(db: Session, subtopic_id: int, subtopic_data: Dict) -> Optional[SubtopicModel]:
    db_subtopic = read_subtopic_from_db(db, subtopic_id)
    if db_subtopic:
        for key, value in subtopic_data.items():
            setattr(db_subtopic, key, value)
        db.commit()
        db.refresh(db_subtopic)
    return db_subtopic

def delete_subtopic_from_db(db: Session, subtopic_id: int) -> bool:
    db_subtopic = read_subtopic_from_db(db, subtopic_id)
    if db_subtopic:
        db.delete(db_subtopic)
        db.commit()
        return True
    return False

def create_topic_to_subtopic_association_in_db(db: Session, topic_id: int, subtopic_id: int) -> bool:
    association = TopicToSubtopicAssociation(topic_id=topic_id, subtopic_id=subtopic_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_topic_to_subtopic_association_from_db(db: Session, topic_id: int, subtopic_id: int) -> bool:
    association = db.query(TopicToSubtopicAssociation).filter_by(
        topic_id=topic_id, subtopic_id=subtopic_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_subtopic_to_concept_association_in_db(db: Session, subtopic_id: int, concept_id: int) -> bool:
    association = SubtopicToConceptAssociation(subtopic_id=subtopic_id, concept_id=concept_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_subtopic_to_concept_association_from_db(db: Session, subtopic_id: int, concept_id: int) -> bool:
    association = db.query(SubtopicToConceptAssociation).filter_by(
        subtopic_id=subtopic_id, concept_id=concept_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_question_to_subtopic_association_in_db(db: Session, question_id: int, subtopic_id: int) -> bool:
    association = QuestionToSubtopicAssociation(question_id=question_id, subtopic_id=subtopic_id)
    db.add(association)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_subtopic_association_from_db(db: Session, question_id: int, subtopic_id: int) -> bool:
    association = db.query(QuestionToSubtopicAssociation).filter_by(
        question_id=question_id, subtopic_id=subtopic_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_topics_for_subtopic_from_db(db: Session, subtopic_id: int) -> List[TopicModel]:
    return db.query(TopicModel).join(TopicToSubtopicAssociation).filter(
        TopicToSubtopicAssociation.subtopic_id == subtopic_id
    ).all()

def read_concepts_for_subtopic_from_db(db: Session, subtopic_id: int) -> List[ConceptModel]:
    return db.query(ConceptModel).join(SubtopicToConceptAssociation).filter(
        SubtopicToConceptAssociation.subtopic_id == subtopic_id
    ).all()

def read_questions_for_subtopic_from_db(db: Session, subtopic_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToSubtopicAssociation).filter(
        QuestionToSubtopicAssociation.subtopic_id == subtopic_id
    ).all()

```

## File: crud_time_period.py
```py
# filename: backend/app/crud/crud_time_period.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.models.time_period import TimePeriodModel
from backend.app.core.config import TimePeriod
from backend.app.services.logging_service import logger

def create_time_period_in_db(db: Session, time_period: TimePeriod) -> TimePeriodModel:
    try:
        db_time_period = TimePeriodModel(id=time_period.value, name=time_period.name.lower())
        db.add(db_time_period)
        db.commit()
        db.refresh(db_time_period)
        return db_time_period
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating time period: {str(e)}")
        raise

def read_time_period_from_db(db: Session, time_period_id: int) -> Optional[TimePeriodModel]:
    return db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period_id).first()

def read_all_time_periods_from_db(db: Session) -> List[TimePeriodModel]:
    return db.query(TimePeriodModel).all()

def update_time_period_in_db(db: Session, time_period_id: int, new_name: str) -> Optional[TimePeriodModel]:
    try:
        db_time_period = db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period_id).first()
        if db_time_period:
            db_time_period.name = new_name
            db.commit()
            db.refresh(db_time_period)
        return db_time_period
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating time period: {str(e)}")
        raise

def delete_time_period_from_db(db: Session, time_period_id: int) -> bool:
    try:
        db_time_period = db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period_id).first()
        if db_time_period:
            db.delete(db_time_period)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting time period: {str(e)}")
        raise

def init_time_periods_in_db(db: Session) -> None:
    try:
        existing_periods = read_all_time_periods_from_db(db)
        existing_ids = {period.id for period in existing_periods}

        for time_period in TimePeriod:
            if time_period.value not in existing_ids:
                create_time_period_in_db(db, time_period)
        
        logger.info("Time periods initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing time periods: {str(e)}")
        raise
```

## File: crud_topics.py
```py
# filename: backend/app/crud/crud_topics.py

from typing import Dict, List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from backend.app.models.associations import (QuestionToTopicAssociation,
                                             SubjectToTopicAssociation,
                                             TopicToSubtopicAssociation)
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.services.logging_service import logger


def create_topic_in_db(db: Session, topic_data: Dict) -> Optional[TopicModel]:
    # Validate subject IDs before creating the topic
    if 'subject_ids' in topic_data and topic_data['subject_ids']:
        for subject_id in topic_data['subject_ids']:
            subject = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
            if not subject:
                raise HTTPException(status_code=400, detail=f"Invalid subject_id: {subject_id}")

    db_topic = TopicModel(name=topic_data['name'])
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    
    if 'subject_ids' in topic_data and topic_data['subject_ids']:
        for subject_id in topic_data['subject_ids']:
            create_subject_to_topic_association_in_db(db, subject_id, db_topic.id)

    if 'subtopic_ids' in topic_data and topic_data['subtopic_ids']:
        for subtopic_id in topic_data['subtopic_ids']:
            create_topic_to_subtopic_association_in_db(db, db_topic.id, subtopic_id)

    if 'question_ids' in topic_data and topic_data['question_ids']:
        for question_id in topic_data['question_ids']:
            create_question_to_topic_association_in_db(db, question_id, db_topic.id)

    return db_topic

def read_topic_from_db(db: Session, topic_id: int) -> Optional[TopicModel]:
    topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
    if topic:
        # Manually load the subjects
        topic.subjects = read_subjects_for_topic_from_db(db, topic_id)
        logger.debug(f"Loaded subjects for topic: {topic.subjects}")
    return topic

def read_topic_by_name_from_db(db: Session, name: str) -> Optional[TopicModel]:
    return db.query(TopicModel).filter(TopicModel.name == name).first()

def read_topics_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[TopicModel]:
    return db.query(TopicModel).offset(skip).limit(limit).all()

def update_topic_in_db(db: Session, topic_id: int, topic_data: Dict) -> Optional[TopicModel]:
    db_topic = read_topic_from_db(db, topic_id)
    if db_topic:
        if 'name' in topic_data:
            db_topic.name = topic_data['name']

        if 'subject_ids' in topic_data:
            # Remove all existing associations
            db.query(SubjectToTopicAssociation).filter(SubjectToTopicAssociation.topic_id == topic_id).delete()

            # Create new associations
            for subject_id in topic_data['subject_ids']:
                if not db.query(SubjectModel).filter(SubjectModel.id == subject_id).first():
                    db.rollback()
                    return None
                create_subject_to_topic_association_in_db(db, subject_id, topic_id)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise
        db.refresh(db_topic)
    return db_topic

def delete_topic_from_db(db: Session, topic_id: int) -> bool:
    db_topic = read_topic_from_db(db, topic_id)
    if db_topic:
        db.delete(db_topic)
        db.commit()
        return True
    return False

def create_subject_to_topic_association_in_db(db: Session, subject_id: int, topic_id: int) -> bool:
    association = SubjectToTopicAssociation(subject_id=subject_id, topic_id=topic_id)
    db.add(association)
    try:
        db.flush()
        logger.debug(f"Created association: subject_id={subject_id}, topic_id={topic_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create association: subject_id={subject_id}, topic_id={topic_id}. Error: {str(e)}")
        return False

def delete_subject_to_topic_association_from_db(db: Session, subject_id: int, topic_id: int) -> bool:
    association = db.query(SubjectToTopicAssociation).filter_by(
        subject_id=subject_id, topic_id=topic_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_topic_to_subtopic_association_in_db(db: Session, topic_id: int, subtopic_id: int) -> bool:
    association = TopicToSubtopicAssociation(topic_id=topic_id, subtopic_id=subtopic_id)
    db.add(association)
    try:
        db.flush()
        return True
    except:
        db.rollback()
        return False

def delete_topic_to_subtopic_association_from_db(db: Session, topic_id: int, subtopic_id: int) -> bool:
    association = db.query(TopicToSubtopicAssociation).filter_by(
        topic_id=topic_id, subtopic_id=subtopic_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def create_question_to_topic_association_in_db(db: Session, question_id: int, topic_id: int) -> bool:
    association = QuestionToTopicAssociation(question_id=question_id, topic_id=topic_id)
    db.add(association)
    try:
        db.flush()
        return True
    except:
        db.rollback()
        return False

def delete_question_to_topic_association_from_db(db: Session, question_id: int, topic_id: int) -> bool:
    association = db.query(QuestionToTopicAssociation).filter_by(
        question_id=question_id, topic_id=topic_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_subjects_for_topic_from_db(db: Session, topic_id: int) -> List[SubjectModel]:
    logger.debug(f"Querying subjects for topic_id: {topic_id}")
    subjects = db.query(SubjectModel).join(SubjectToTopicAssociation).filter(
        SubjectToTopicAssociation.topic_id == topic_id
    ).all()
    logger.debug(f"Found subjects: {subjects}")
    
    # Additional debug: Check the SubjectToTopicAssociation table directly
    associations = db.query(SubjectToTopicAssociation).filter(
        SubjectToTopicAssociation.topic_id == topic_id
    ).all()
    logger.debug(f"SubjectToTopicAssociations for topic_id {topic_id}: {associations}")
    
    return subjects

def read_subtopics_for_topic_from_db(db: Session, topic_id: int) -> List[SubtopicModel]:
    return db.query(SubtopicModel).join(TopicToSubtopicAssociation).filter(
        TopicToSubtopicAssociation.topic_id == topic_id
    ).all()

def read_questions_for_topic_from_db(db: Session, topic_id: int) -> List[QuestionModel]:
    return db.query(QuestionModel).join(QuestionToTopicAssociation).filter(
        QuestionToTopicAssociation.topic_id == topic_id
    ).all()

```

## File: crud_user.py
```py
# filename: backend/app/crud/crud_user.py

from typing import Dict, List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import func

from backend.app.core.security import get_password_hash
from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel
from backend.app.services.logging_service import logger


def create_user_in_db(db: Session, user_data: Dict) -> UserModel:
    db_user = UserModel(
        username=user_data['username'].lower(),  # Store username in lowercase
        email=user_data['email'],
        hashed_password=user_data['hashed_password'],
        is_active=user_data.get('is_active', True),
        is_admin=user_data.get('is_admin', False),
        role_id=user_data.get('role_id')
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as exc:
        db.rollback()
        error_info = str(exc.orig)
        if "role_id" in error_info:
            raise ValueError("Role is required for user creation") from exc
        elif "username" in error_info:
            raise ValueError("Username already exists") from exc
        elif "email" in error_info:
            raise ValueError("Email already exists") from exc
        else:
            raise ValueError("Username or email already exists") from exc
    except Exception as exc:
        db.rollback()
        logger.error("Error creating user: %s", exc)
        raise ValueError(f"Error creating user: {str(exc)}") from exc

def read_user_from_db(db: Session, user_id: int) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def read_user_by_username_from_db(db: Session, username: str) -> Optional[UserModel]:
    user = db.query(UserModel).filter(func.lower(UserModel.username) == username.lower()).first()
    if user and user.token_blacklist_date:
        # Ensure token_blacklist_date is timezone-aware
        if user.token_blacklist_date.tzinfo is None:
            user.token_blacklist_date = user.token_blacklist_date.replace(tzinfo=timezone.utc)
    return user

def read_user_by_email_from_db(db: Session, email: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.email == email).first()

def read_users_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    return db.query(UserModel).offset(skip).limit(limit).all()

def update_user_in_db(db: Session, user_id: int, user_data: Dict) -> Optional[UserModel]:
    db_user = read_user_from_db(db, user_id)
    if db_user:
        try:
            for key, value in user_data.items():
                if key == 'password':
                    db_user.hashed_password = get_password_hash(value)
                elif key == 'role_id':
                    role = db.query(RoleModel).filter(RoleModel.id == value).first()
                    if not role:
                        raise ValueError("Invalid role_id")
                    db_user.role_id = value
                elif key == 'username':
                    db_user.username = value.lower()  # Store username in lowercase when updating
                else:
                    setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as exc:
            db.rollback()
            error_info = str(exc.orig)
            if "username" in error_info:
                raise ValueError("Username already exists") from exc
            elif "email" in error_info:
                raise ValueError("Email already exists") from exc
            else:
                raise ValueError("Error updating user") from exc
        except ValueError:
            db.rollback()
            raise
    return None

def delete_user_from_db(db: Session, user_id: int) -> bool:
    db_user = read_user_from_db(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def create_user_to_group_association_in_db(db: Session, user_id: int, group_id: int) -> bool:
    association = UserToGroupAssociation(user_id=user_id, group_id=group_id)
    db.add(association)
    try:
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False

def delete_user_to_group_association_from_db(db: Session, user_id: int, group_id: int) -> bool:
    association = db.query(UserToGroupAssociation).filter_by(
        user_id=user_id, group_id=group_id
    ).first()
    if association:
        db.delete(association)
        db.commit()
        return True
    return False

def read_groups_for_user_from_db(db: Session, user_id: int) -> List[GroupModel]:
    return db.query(GroupModel).join(UserToGroupAssociation).filter(
        UserToGroupAssociation.user_id == user_id
    ).all()

def read_role_for_user_from_db(db: Session, user_id: int) -> Optional[RoleModel]:
    user = read_user_from_db(db, user_id)
    return user.role if user else None

def read_created_question_sets_for_user_from_db(db: Session, user_id: int) -> List[QuestionSetModel]:
    return db.query(QuestionSetModel).filter(QuestionSetModel.creator_id == user_id).all()

def update_user_token_blacklist_date(db: Session, user_id: int, new_date: Optional[datetime]) -> Optional[UserModel]:
    db_user = read_user_from_db(db, user_id)
    if db_user:
        if new_date is not None:
            # Ensure new_date is timezone-aware
            if new_date.tzinfo is None:
                new_date = new_date.replace(tzinfo=timezone.utc)
        db_user.token_blacklist_date = new_date
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

```

## File: crud_user_responses.py
```py
# filename: backend/app/crud/crud_user_responses.py

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.user_responses import UserResponseModel


def create_user_response_in_db(db: Session, user_response_data: Dict) -> UserResponseModel:
    db_user_response = UserResponseModel(
        user_id=user_response_data['user_id'],
        question_id=user_response_data['question_id'],
        answer_choice_id=user_response_data['answer_choice_id'],
        is_correct=user_response_data['is_correct'],
        response_time=user_response_data.get('response_time'),
        timestamp=user_response_data.get('timestamp', datetime.now(timezone.utc))
    )
    db.add(db_user_response)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

def read_user_response_from_db(db: Session, user_response_id: int) -> Optional[UserResponseModel]:
    return db.query(UserResponseModel).filter(UserResponseModel.id == user_response_id).first()

def read_user_responses_from_db(
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
    return query.offset(skip).limit(limit).all()

def update_user_response_in_db(db: Session, user_response_id: int, user_response_data: Dict) -> Optional[UserResponseModel]:
    db_user_response = read_user_response_from_db(db, user_response_id)
    if db_user_response:
        for key, value in user_response_data.items():
            if key != 'is_correct' or value is not None:  # Only update is_correct if it's explicitly set
                setattr(db_user_response, key, value)
        db.commit()
        db.refresh(db_user_response)
    return db_user_response

def delete_user_response_from_db(db: Session, user_response_id: int) -> bool:
    db_user_response = read_user_response_from_db(db, user_response_id)
    if db_user_response:
        db.delete(db_user_response)
        db.commit()
        return True
    return False

def read_user_responses_for_user_from_db(db: Session, user_id: int) -> List[UserResponseModel]:
    return db.query(UserResponseModel).filter(UserResponseModel.user_id == user_id).all()

def read_user_responses_for_question_from_db(db: Session, question_id: int) -> List[UserResponseModel]:
    return db.query(UserResponseModel).filter(UserResponseModel.question_id == question_id).all()

```

# Directory: /code/quiz-app/backend/app/db

## File: __init__.py
```py

```

## File: base.py
```py
# filename: backend/app/db/base.py

from sqlalchemy.orm import declarative_base

Base = declarative_base()

```

## File: session.py
```py
# filename: backend/app/db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, NullPool

from backend.app.core.config import settings_core
from backend.app.db.base import Base
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.services.logging_service import logger

# Determine the environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

# Set pool settings based on the environment
if ENVIRONMENT == "test":
    # For SQLite (testing), use a smaller pool
    pool_settings = {
        "poolclass": QueuePool,
        "pool_size": 30,
        "max_overflow": 40,
        "pool_recycle": 3600,
        "pool_pre_ping": True
    }
elif ENVIRONMENT in ["dev", "prod"]:
    # For MariaDB (production), use a larger pool
    pool_settings = {
        "poolclass": QueuePool,
        "pool_size": 50,
        "max_overflow": 100,
        "pool_recycle": 3600,
        "pool_pre_ping": True
    }
else:
    # For unknown environments, use NullPool as a safe default
    pool_settings = {"poolclass": NullPool}

# Create the engine with the appropriate pool settings
engine = create_engine(settings_core.DATABASE_URL, **pool_settings)

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

# Add logging for connection pool statistics
def log_pool_info():
    if hasattr(engine.pool, "size"):
        logger.info(f"Database connection pool status:")
        logger.info(f"  Pool size: {engine.pool.size()}")
        logger.info(f"  Connections in use: {engine.pool.checkedin()}")
        logger.info(f"  Connections available: {engine.pool.checkedout()}")
    else:
        logger.info("Database is not using a connection pool.")

# You can call this function periodically or in strategic places in your application
# For example, you might want to add it to your main FastAPI app startup event
# @app.on_event("startup")
# async def startup_event():
#     log_pool_info()

```

# Directory: /code/quiz-app/backend/app/api

## File: __init__.py
```py

```

# Directory: /code/quiz-app/backend/app/api/endpoints

## File: __init__.py
```py

```

## File: answer_choices.py
```py
# filename: backend/app/api/endpoints/answer_choices.py

"""
Answer Choices Management API

This module provides API endpoints for managing answer choices in the quiz application.
It includes operations for creating, reading, updating, and deleting answer choices.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_answer_choices module.

Endpoints:
- POST /answer-choices/: Create a new answer choice
- GET /answer-choices/: Retrieve a list of answer choices
- GET /answer-choices/{answer_choice_id}: Retrieve a specific answer choice by ID
- PUT /answer-choices/{answer_choice_id}: Update a specific answer choice
- DELETE /answer-choices/{answer_choice_id}: Delete a specific answer choice

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_answer_choices import (create_answer_choice_in_db,
                                                  delete_answer_choice_from_db,
                                                  read_answer_choice_from_db,
                                                  read_answer_choices_from_db,
                                                  update_answer_choice_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.answer_choices import (AnswerChoiceCreateSchema,
                                                AnswerChoiceSchema, DetailedAnswerChoiceSchema,
                                                AnswerChoiceUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.services.logging_service import logger

router = APIRouter()

@router.post("/answer-choices/", response_model=AnswerChoiceSchema, status_code=status.HTTP_201_CREATED)
def post_answer_choice(
    request: Request,
    answer_choice: AnswerChoiceCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new answer choice.

    This endpoint allows authenticated users to create a new answer choice in the database.
    The answer choice data is validated using the AnswerChoiceCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        answer_choice (AnswerChoiceCreateSchema): The answer choice data to be created.
        db (Session): The database session.

    Returns:
        AnswerChoiceSchema: The created answer choice data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_answer_choice = AnswerChoiceCreateSchema(**answer_choice.model_dump())
    logger.debug("Validated answer choice in API endpoint: %s", validated_answer_choice)
    answer_choice_data = validated_answer_choice.model_dump()
    logger.debug("Answer choice data in API endpoint: %s", answer_choice_data)
    created_answer_choice = create_answer_choice_in_db(db=db, answer_choice_data=answer_choice_data)
    logger.debug("Created answer choice in API endpoint: %s", created_answer_choice)
    return AnswerChoiceSchema.model_validate(created_answer_choice)

@router.post("/answer-choices/with-question", response_model=DetailedAnswerChoiceSchema, status_code=status.HTTP_201_CREATED)
def post_answer_choice_with_question(
    request: Request,
    answer_choice: AnswerChoiceCreateSchema,
    db: Session = Depends(get_db)
):
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_answer_choice = AnswerChoiceCreateSchema(**answer_choice.model_dump())
    answer_choice_data = validated_answer_choice.model_dump()
    created_answer_choice = create_answer_choice_in_db(db=db, answer_choice_data=answer_choice_data)
    return DetailedAnswerChoiceSchema.model_validate(created_answer_choice)

@router.get("/answer-choices/", response_model=List[AnswerChoiceSchema])
def get_answer_choices(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of answer choices.

    This endpoint allows authenticated users to retrieve a paginated list of answer choices from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of answer choices to skip. Defaults to 0.
        limit (int, optional): The maximum number of answer choices to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[AnswerChoiceSchema]: A list of answer choices.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    answer_choices = read_answer_choices_from_db(db, skip=skip, limit=limit)
    return [AnswerChoiceSchema.model_validate(ac) for ac in answer_choices]

@router.get("/answer-choices/{answer_choice_id}", response_model=AnswerChoiceSchema)
def get_answer_choice(
    request: Request,
    answer_choice_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific answer choice by ID.

    This endpoint allows authenticated users to retrieve a single answer choice by its ID.

    Args:
        request (Request): The FastAPI request object.
        answer_choice_id (int): The ID of the answer choice to retrieve.
        db (Session): The database session.

    Returns:
        AnswerChoiceSchema: The answer choice data.

    Raises:
        HTTPException: If the answer choice with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_answer_choice = read_answer_choice_from_db(db, answer_choice_id=answer_choice_id)
    if db_answer_choice is None:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return AnswerChoiceSchema.model_validate(db_answer_choice)

@router.put("/answer-choices/{answer_choice_id}", response_model=AnswerChoiceSchema)
def put_answer_choice(
    request: Request,
    answer_choice_id: int,
    answer_choice: AnswerChoiceUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific answer choice.

    This endpoint allows authenticated users to update an existing answer choice by its ID.

    Args:
        request (Request): The FastAPI request object.
        answer_choice_id (int): The ID of the answer choice to update.
        answer_choice (AnswerChoiceUpdateSchema): The updated answer choice data.
        db (Session): The database session.

    Returns:
        AnswerChoiceSchema: The updated answer choice data.

    Raises:
        HTTPException: If the answer choice with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_answer_choice = AnswerChoiceUpdateSchema(**answer_choice.model_dump())
    answer_choice_data = validated_answer_choice.model_dump()
    updated_answer_choice = update_answer_choice_in_db(db, answer_choice_id, answer_choice_data)
    
    if updated_answer_choice is None:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    
    return AnswerChoiceSchema.model_validate(updated_answer_choice)

@router.delete("/answer-choices/{answer_choice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_answer_choice(
    request: Request,
    answer_choice_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific answer choice.

    This endpoint allows authenticated users to delete an existing answer choice by its ID.

    Args:
        request (Request): The FastAPI request object.
        answer_choice_id (int): The ID of the answer choice to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the answer choice with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_answer_choice_from_db(db, answer_choice_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return None

```

## File: authentication.py
```py
# filename: backend/app/api/endpoints/authentication.py

"""
Authentication API

This module provides API endpoints for user authentication in the quiz application.
It includes operations for user login, logout, and logging out all sessions.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations and uses JWT for token-based authentication.

Endpoints:
- POST /login: Authenticate a user and return an access token
- POST /logout: Logout a user by revoking their access token
- POST /logout/all: Logout all sessions for a user by revoking all their access tokens

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency for the logout endpoints.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.app.core.jwt import create_access_token, decode_access_token
from backend.app.db.session import get_db
from backend.app.schemas.authentication import TokenSchema, LoginFormSchema
from backend.app.services.authentication_service import authenticate_user
from backend.app.services.user_service import oauth2_scheme
from backend.app.services.auth_utils import check_auth_status
from backend.app.crud.authentication import is_token_revoked, revoke_token
from backend.app.crud.crud_user import update_user_token_blacklist_date, read_user_by_username_from_db
from backend.app.services.logging_service import logger

router = APIRouter()

@router.post("/login", response_model=TokenSchema)
async def login_endpoint(
    form_data: LoginFormSchema,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token.

    This endpoint allows users to login by providing their username and password.
    If credentials are valid, returns an access token for use in subsequent authenticated requests.

    Args:
        form_data (LoginFormSchema): The login form data containing username, password, and remember_me flag.
        db (Session): The database session.

    Returns:
        TokenSchema: An object containing the access token and token type.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the provided credentials are invalid or the user is inactive.
    """
    logger.debug("Login attempt for user: %s", form_data.username)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user or not user.is_active:
        logger.warning(f"Login failed for user: {form_data.username}. User not found or inactive.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("User authenticated successfully: %s", user.username)
    
    # Check if the user's token_blacklist_date is in the past
    current_time = datetime.now(timezone.utc)
    if user.token_blacklist_date:
        logger.debug(f"User {user.username} has token_blacklist_date: {user.token_blacklist_date}")
        if user.token_blacklist_date > current_time:
            logger.warning(f"Login attempt for user with active token blacklist: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="All sessions have been logged out. Please try again later.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            logger.debug(f"Clearing token_blacklist_date for user: {user.username}")
            update_user_token_blacklist_date(db, user.id, None)

    # Set expiration time based on remember_me flag
    # For remember_me tokens, set expiration to 30 days; otherwise, use the default expiration time
    expires_delta = timedelta(days=30) if form_data.remember_me else None
    access_token = create_access_token(data={"sub": user.username, "remember_me": form_data.remember_me}, expires_delta=expires_delta)
    logger.debug("Access token created for user: %s (remember_me: %s)", user.username, form_data.remember_me)
    response = {"access_token": access_token, "token_type": "bearer"}
    logger.debug("Login response: %s", response)
    return response

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_endpoint(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout a user by revoking their access token.

    This endpoint allows authenticated users to logout by revoking their current access token.
    Once revoked, the token can no longer be used for authentication.
    This handles both regular and remember me tokens.

    Args:
        request (Request): The FastAPI request object.
        token (str): The access token to be revoked.
        db (Session): The database session.

    Returns:
        dict: A message indicating successful logout.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the token is invalid or expired.
            - 403 Forbidden: If the user doesn't have sufficient permissions.
            - 500 Internal Server Error: If there's an error during the logout process.
    """
    check_auth_status(request)

    try:
        decoded_token = decode_access_token(token)
        jti = decoded_token.get("jti")
        if not jti:
            raise ValueError("Token does not contain a JTI")

        if is_token_revoked(db, token):
            return {"message": "Token already revoked"}
        
        revoke_token(db, token)
        is_remember_me = decoded_token.get("remember_me", False)
        logger.debug(f"Token revoked for user: {decoded_token.get('sub')} (remember_me: {is_remember_me})")
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout user"
        ) from e

@router.post("/logout/all", status_code=status.HTTP_200_OK)
async def logout_all_sessions_endpoint(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout all sessions for a user by updating their token_blacklist_date.

    This endpoint allows authenticated users to logout from all their active sessions
    by updating their token_blacklist_date, which invalidates all previously issued tokens,
    including remember me tokens.

    Args:
        request (Request): The FastAPI request object.
        token (str): The current access token.
        db (Session): The database session.

    Returns:
        dict: A message indicating successful logout from all sessions.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the token is invalid or expired.
            - 403 Forbidden: If the user doesn't have sufficient permissions.
            - 500 Internal Server Error: If there's an error during the logout process.
    """
    check_auth_status(request)

    try:
        decoded_token = decode_access_token(token)
        username = decoded_token.get("sub")
        if not username:
            raise ValueError("Token does not contain a subject (username)")

        user = read_user_by_username_from_db(db, username)
        if not user:
            raise ValueError("User not found")

        # Update the user's token_blacklist_date to the current time
        current_time = datetime.now(timezone.utc)
        update_user_token_blacklist_date(db, user.id, current_time)
        logger.debug(f"Updated token_blacklist_date for user {username} to {current_time} (all sessions, including remember me)")

        return {"message": "Successfully logged out from all sessions"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout user from all sessions: {str(e)}"
        ) from e

```

## File: concepts.py
```py
# filename: backend/app/api/endpoints/concepts.py

"""
Concepts Management API

This module provides API endpoints for managing concepts in the quiz application.
It includes operations for creating, reading, updating, and deleting concepts.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_concepts module.

Endpoints:
- POST /concepts/: Create a new concept
- GET /concepts/: Retrieve a list of concepts
- GET /concepts/{concept_id}: Retrieve a specific concept by ID
- PUT /concepts/{concept_id}: Update a specific concept
- DELETE /concepts/{concept_id}: Delete a specific concept

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_concepts import (create_concept_in_db,
                                            delete_concept_from_db,
                                            read_concept_from_db,
                                            read_concepts_from_db,
                                            update_concept_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.concepts import (ConceptCreateSchema, ConceptSchema,
                                          ConceptUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()

@router.post("/concepts/", response_model=ConceptSchema, status_code=201)
def post_concept(
    request: Request,
    concept: ConceptCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new concept.

    This endpoint allows authenticated users to create a new concept in the database.
    The concept data is validated using the ConceptCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        concept (ConceptCreateSchema): The concept data to be created.
        db (Session): The database session.

    Returns:
        ConceptSchema: The created concept data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_concept = ConceptCreateSchema(**concept.model_dump())
    concept_data = validated_concept.model_dump()
    created_concept = create_concept_in_db(db=db, concept_data=concept_data)
    return ConceptSchema.model_validate(created_concept)

@router.get("/concepts/", response_model=List[ConceptSchema])
def get_concepts(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of concepts.

    This endpoint allows authenticated users to retrieve a paginated list of concepts from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of concepts to skip. Defaults to 0.
        limit (int, optional): The maximum number of concepts to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[ConceptSchema]: A list of concepts.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    concepts = read_concepts_from_db(db, skip=skip, limit=limit)
    return [ConceptSchema.model_validate(c) for c in concepts]

@router.get("/concepts/{concept_id}", response_model=ConceptSchema)
def get_concept(
    request: Request,
    concept_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific concept by ID.

    This endpoint allows authenticated users to retrieve a single concept by its ID.

    Args:
        request (Request): The FastAPI request object.
        concept_id (int): The ID of the concept to retrieve.
        db (Session): The database session.

    Returns:
        ConceptSchema: The concept data.

    Raises:
        HTTPException: If the concept with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_concept = read_concept_from_db(db, concept_id=concept_id)
    if db_concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return ConceptSchema.model_validate(db_concept)

@router.put("/concepts/{concept_id}", response_model=ConceptSchema)
def put_concept(
    request: Request,
    concept_id: int,
    concept: ConceptUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific concept.

    This endpoint allows authenticated users to update an existing concept by its ID.

    Args:
        request (Request): The FastAPI request object.
        concept_id (int): The ID of the concept to update.
        concept (ConceptUpdateSchema): The updated concept data.
        db (Session): The database session.

    Returns:
        ConceptSchema: The updated concept data.

    Raises:
        HTTPException: If the concept with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_concept = ConceptUpdateSchema(**concept.model_dump())
    concept_data = validated_concept.model_dump()
    updated_concept = update_concept_in_db(db, concept_id, concept_data)
    
    if updated_concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    return ConceptSchema.model_validate(updated_concept)

@router.delete("/concepts/{concept_id}", status_code=204)
def delete_concept(
    request: Request,
    concept_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific concept.

    This endpoint allows authenticated users to delete an existing concept by its ID.

    Args:
        request (Request): The FastAPI request object.
        concept_id (int): The ID of the concept to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the concept with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_concept_from_db(db, concept_id)
    if not success:
        raise HTTPException(status_code=404, detail="Concept not found")
    return None

```

## File: disciplines.py
```py
# filename: backend/app/api/endpoints/disciplines.py

"""
Disciplines Management API

This module provides API endpoints for managing disciplines in the quiz application.
It includes operations for creating, reading, updating, and deleting disciplines.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_disciplines module.

Endpoints:
- POST /disciplines/: Create a new discipline
- GET /disciplines/: Retrieve a list of disciplines
- GET /disciplines/{discipline_id}: Retrieve a specific discipline by ID
- PUT /disciplines/{discipline_id}: Update a specific discipline
- DELETE /disciplines/{discipline_id}: Delete a specific discipline

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_disciplines import (create_discipline_in_db,
                                               delete_discipline_from_db,
                                               read_discipline_from_db,
                                               read_disciplines_from_db,
                                               update_discipline_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.disciplines import (DisciplineCreateSchema,
                                             DisciplineSchema,
                                             DisciplineUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()

@router.post("/disciplines/", response_model=DisciplineSchema, status_code=201)
def post_discipline(
    request: Request,
    discipline: DisciplineCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new discipline.

    This endpoint allows authenticated users to create a new discipline in the database.
    The discipline data is validated using the DisciplineCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        discipline (DisciplineCreateSchema): The discipline data to be created.
        db (Session): The database session.

    Returns:
        DisciplineSchema: The created discipline data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_discipline = DisciplineCreateSchema(**discipline.model_dump())
    discipline_data = validated_discipline.model_dump()
    created_discipline = create_discipline_in_db(db=db, discipline_data=discipline_data)
    return DisciplineSchema.model_validate(created_discipline)

@router.get("/disciplines/", response_model=List[DisciplineSchema])
def get_disciplines(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of disciplines.

    This endpoint allows authenticated users to retrieve a paginated list of disciplines from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of disciplines to skip. Defaults to 0.
        limit (int, optional): The maximum number of disciplines to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[DisciplineSchema]: A list of disciplines.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    disciplines = read_disciplines_from_db(db, skip=skip, limit=limit)
    return [DisciplineSchema.model_validate(d) for d in disciplines]

@router.get("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def get_discipline(
    request: Request,
    discipline_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific discipline by ID.

    This endpoint allows authenticated users to retrieve a single discipline by its ID.

    Args:
        request (Request): The FastAPI request object.
        discipline_id (int): The ID of the discipline to retrieve.
        db (Session): The database session.

    Returns:
        DisciplineSchema: The discipline data.

    Raises:
        HTTPException: If the discipline with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_discipline = read_discipline_from_db(db, discipline_id=discipline_id)
    if db_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return DisciplineSchema.model_validate(db_discipline)

@router.put("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def put_discipline(
    request: Request,
    discipline_id: int,
    discipline: DisciplineUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific discipline.

    This endpoint allows authenticated users to update an existing discipline by its ID.

    Args:
        request (Request): The FastAPI request object.
        discipline_id (int): The ID of the discipline to update.
        discipline (DisciplineUpdateSchema): The updated discipline data.
        db (Session): The database session.

    Returns:
        DisciplineSchema: The updated discipline data.

    Raises:
        HTTPException: If the discipline with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_discipline = DisciplineUpdateSchema(**discipline.model_dump())
    discipline_data = validated_discipline.model_dump()
    updated_discipline = update_discipline_in_db(db, discipline_id, discipline_data)
    if updated_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return DisciplineSchema.model_validate(updated_discipline)

@router.delete("/disciplines/{discipline_id}", status_code=204)
def delete_discipline(
    request: Request,
    discipline_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific discipline.

    This endpoint allows authenticated users to delete an existing discipline by its ID.

    Args:
        request (Request): The FastAPI request object.
        discipline_id (int): The ID of the discipline to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the discipline with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_discipline_from_db(db, discipline_id)
    if not success:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return None

```

## File: domains.py
```py
# filename: backend/app/api/endpoints/domains.py

"""
Domains Management API

This module provides API endpoints for managing domains in the quiz application.
It includes operations for creating, reading, updating, and deleting domains.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_domains module.

Endpoints:
- POST /domains/: Create a new domain
- GET /domains/: Retrieve a list of domains
- GET /domains/{domain_id}: Retrieve a specific domain by ID
- PUT /domains/{domain_id}: Update a specific domain
- DELETE /domains/{domain_id}: Delete a specific domain

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_domains import (create_domain_in_db,
                                           delete_domain_from_db,
                                           read_domain_from_db,
                                           read_domains_from_db,
                                           update_domain_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.domains import (DomainCreateSchema, DomainSchema,
                                         DomainUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()

@router.post("/domains/", response_model=DomainSchema, status_code=201)
def post_domain(
    request: Request,
    domain: DomainCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new domain.

    This endpoint allows authenticated users to create a new domain in the database.
    The domain data is validated using the DomainCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        domain (DomainCreateSchema): The domain data to be created.
        db (Session): The database session.

    Returns:
        DomainSchema: The created domain data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_domain = DomainCreateSchema(**domain.model_dump())
    domain_data = validated_domain.model_dump()
    created_domain = create_domain_in_db(db=db, domain_data=domain_data)
    return DomainSchema.model_validate(created_domain)

@router.get("/domains/", response_model=List[DomainSchema])
def get_domains(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of domains.

    This endpoint allows authenticated users to retrieve a paginated list of domains from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of domains to skip. Defaults to 0.
        limit (int, optional): The maximum number of domains to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[DomainSchema]: A list of domains.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    domains = read_domains_from_db(db, skip=skip, limit=limit)
    return [DomainSchema.model_validate(d) for d in domains]

@router.get("/domains/{domain_id}", response_model=DomainSchema)
def get_domain(
    request: Request,
    domain_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific domain by ID.

    This endpoint allows authenticated users to retrieve a single domain by its ID.

    Args:
        request (Request): The FastAPI request object.
        domain_id (int): The ID of the domain to retrieve.
        db (Session): The database session.

    Returns:
        DomainSchema: The domain data.

    Raises:
        HTTPException: If the domain with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_domain = read_domain_from_db(db, domain_id=domain_id)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainSchema.model_validate(db_domain)

@router.put("/domains/{domain_id}", response_model=DomainSchema)
def put_domain(
    request: Request,
    domain_id: int,
    domain: DomainUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific domain.

    This endpoint allows authenticated users to update an existing domain by its ID.

    Args:
        request (Request): The FastAPI request object.
        domain_id (int): The ID of the domain to update.
        domain (DomainUpdateSchema): The updated domain data.
        db (Session): The database session.

    Returns:
        DomainSchema: The updated domain data.

    Raises:
        HTTPException: If the domain with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    validated_domain = DomainUpdateSchema(**domain.model_dump())
    domain_data = validated_domain.model_dump()
    updated_domain = update_domain_in_db(db, domain_id, domain_data)
    if updated_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainSchema.model_validate(updated_domain)

@router.delete("/domains/{domain_id}", status_code=204)
def delete_domain(
    request: Request,
    domain_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific domain.

    This endpoint allows authenticated users to delete an existing domain by its ID.

    Args:
        request (Request): The FastAPI request object.
        domain_id (int): The ID of the domain to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the domain with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_domain_from_db(db, domain_id)
    if not success:
        raise HTTPException(status_code=404, detail="Domain not found")
    return None

```

## File: filters.py
```py
# filename: backend/app/api/endpoints/filters.py

"""
Filters API

This module provides API endpoints for filtering questions in the quiz application.
It includes an operation for retrieving filtered questions based on various criteria.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_filters module.

Endpoints:
- GET /questions/filter: Retrieve a list of filtered questions

The endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_filters import read_filtered_questions_from_db
from backend.app.db.session import get_db
from backend.app.schemas.filters import FilterParamsSchema
from backend.app.schemas.questions import QuestionSchema
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.core.config import DifficultyLevel

router = APIRouter()

async def forbid_extra_params(request: Request):
    """
    Check for unexpected query parameters in the request.

    This function ensures that only allowed query parameters are present in the request.

    Args:
        request (Request): The incoming request object.

    Raises:
        HTTPException: If unexpected parameters are found in the request.
    """
    allowed_params = {'subject', 'topic', 'subtopic', 'difficulty', 'question_tags', 'skip', 'limit'}
    actual_params = set(request.query_params.keys())
    extra_params = actual_params - allowed_params
    if extra_params:
        raise HTTPException(status_code=422, detail=f"Unexpected parameters provided: {extra_params}")

@router.get("/questions/filter", response_model=List[QuestionSchema], status_code=200)
async def filter_questions(
    request: Request,
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    subtopic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    question_tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve a list of filtered questions.

    This endpoint allows authenticated users to retrieve a list of questions
    filtered by various criteria such as subject, topic, subtopic, difficulty, and tags.

    Args:
        request (Request): The incoming request object.
        subject (Optional[str]): The subject to filter by.
        topic (Optional[str]): The topic to filter by.
        subtopic (Optional[str]): The subtopic to filter by.
        difficulty (Optional[str]): The difficulty level to filter by.
        question_tags (Optional[List[str]]): A list of tags to filter by.
        db (Session): The database session.
        skip (int): The number of questions to skip (for pagination).
        limit (int): The maximum number of questions to return (for pagination).

    Returns:
        List[QuestionSchema]: A list of filtered questions.

    Raises:
        HTTPException: If unexpected parameters are provided in the request, if an invalid difficulty level is specified,
                       or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    await forbid_extra_params(request)
    
    # Convert difficulty string to DifficultyLevel enum
    difficulty_enum = None
    if difficulty:
        try:
            difficulty_enum = DifficultyLevel[difficulty.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty level: {difficulty}")
    
    filters = FilterParamsSchema(
        subject=subject,
        topic=topic,
        subtopic=subtopic,
        difficulty=difficulty_enum,
        question_tags=question_tags
    )
    
    questions = read_filtered_questions_from_db(
        db=db,
        filters=filters.model_dump(),
        skip=skip,
        limit=limit
    )
    
    return [QuestionSchema.model_validate(q) for q in questions] if questions else []

```

## File: groups.py
```py
# filename: backend/app/api/endpoints/groups.py

"""
Groups Management API

This module provides API endpoints for managing groups in the quiz application.
It includes operations for creating, reading, updating, and deleting groups.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_groups module.

Endpoints:
- POST /groups: Create a new group
- GET /groups/{group_id}: Retrieve a specific group by ID
- PUT /groups/{group_id}: Update a specific group
- DELETE /groups/{group_id}: Delete a specific group

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import ValidationError

from backend.app.crud.crud_groups import (create_group_in_db,
                                          delete_group_from_db,
                                          read_group_from_db,
                                          update_group_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.groups import (GroupCreateSchema, GroupSchema,
                                        GroupUpdateSchema, GroupBaseSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()

@router.post("/groups", response_model=GroupSchema)
def post_group(
    request: Request,
    group: GroupBaseSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new group.

    This endpoint allows authenticated users to create a new group in the database.
    The group data is validated using the GroupCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        group (GroupBaseSchema): The group data to be created.
        db (Session): The database session.

    Returns:
        GroupSchema: The created group data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    current_user = get_current_user_or_error(request)

    try:
        group_data = group.model_dump()
        group_data["creator_id"] = current_user.id
        validated_group = GroupCreateSchema(**group_data)
        created_group = create_group_in_db(db=db, group_data=validated_group.model_dump())
        return GroupSchema.model_validate(created_group)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred while creating the group: {str(e)}"
                            ) from e

@router.get("/groups/{group_id}", response_model=GroupSchema)
def get_group(
    request: Request,
    group_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific group by ID.

    This endpoint allows authenticated users to retrieve a single group by its ID.

    Args:
        request (Request): The FastAPI request object.
        group_id (int): The ID of the group to retrieve.
        db (Session): The database session.

    Returns:
        GroupSchema: The group data.

    Raises:
        HTTPException: If the group with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_group = read_group_from_db(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return GroupSchema.model_validate(db_group)

@router.put("/groups/{group_id}", response_model=GroupSchema)
def put_group(
    request: Request,
    group_id: int, 
    group: GroupUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific group.

    This endpoint allows authenticated users to update an existing group by its ID.
    Only the group creator can update the group.

    Args:
        request (Request): The FastAPI request object.
        group_id (int): The ID of the group to update.
        group (GroupUpdateSchema): The updated group data.
        db (Session): The database session.

    Returns:
        GroupSchema: The updated group data.

    Raises:
        HTTPException: 
            - 404: If the group with the given ID is not found.
            - 403: If the current user is not the creator of the group.
            - 401: If the user is not authenticated.
    """
    check_auth_status(request)
    current_user = get_current_user_or_error(request)

    db_group = read_group_from_db(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if db_group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group creator can update the group")
    
    group_data = group.model_dump(exclude_unset=True)
    updated_group = update_group_in_db(db=db, group_id=group_id, group_data=group_data)
    return GroupSchema.model_validate(updated_group)

@router.delete("/groups/{group_id}", status_code=204)
def delete_group(
    request: Request,
    group_id: int, 
    db: Session = Depends(get_db)
):
    """
    Delete a specific group.

    This endpoint allows authenticated users to delete an existing group by its ID.
    Only the group creator can delete the group.

    Args:
        request (Request): The FastAPI request object.
        group_id (int): The ID of the group to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: 
            - 404: If the group with the given ID is not found.
            - 403: If the current user is not the creator of the group.
            - 401: If the user is not authenticated.
    """
    check_auth_status(request)
    current_user = get_current_user_or_error(request)

    db_group = read_group_from_db(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if db_group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group creator can delete the group")
    delete_group_from_db(db=db, group_id=group_id)
    return None

```

## File: leaderboard.py
```py
# filename: backend/app/api/endpoints/leaderboard.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.crud.crud_groups import read_group_from_db
from backend.app.crud.crud_leaderboard import (
    create_leaderboard_entry_in_db, delete_leaderboard_entry_from_db,
    read_leaderboard_entries_for_group_from_db,
    read_leaderboard_entries_for_user_from_db,
    read_leaderboard_entries_from_db,
    read_or_create_time_period_in_db, update_leaderboard_entry_in_db)
from backend.app.crud.crud_user import read_user_from_db
from backend.app.db.session import get_db
from backend.app.schemas.leaderboard import (LeaderboardCreateSchema,
                                             LeaderboardSchema,
                                             LeaderboardUpdateSchema)
from backend.app.services.scoring_service import (calculate_leaderboard_scores,
                                                  time_period_to_schema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.core.config import TimePeriod
from backend.app.services.logging_service import logger

router = APIRouter()

@router.get("/leaderboard/", response_model=List[LeaderboardSchema])
def get_leaderboard(
    request: Request,
    time_period: TimePeriod = Query(..., description="Time period for the leaderboard"),
    group_id: Optional[int] = None,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Retrieve leaderboard entries.

    This endpoint allows authenticated users to retrieve leaderboard entries for a specific time period and optionally for a specific group.

    Args:
        request (Request): The FastAPI request object.
        time_period (TimePeriod): The time period for the leaderboard (DAILY, WEEKLY, MONTHLY, YEARLY).
        group_id (Optional[int]): The ID of the group to filter leaderboard entries (if applicable).
        db (Session): The database session.
        limit (int): The maximum number of entries to return (default: 10, min: 1, max: 100).

    Returns:
        List[LeaderboardSchema]: A list of leaderboard entries.

    Raises:
        HTTPException: If the specified time period is invalid or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        time_period_model = read_or_create_time_period_in_db(db, time_period.value)
        if not time_period_model:
            raise HTTPException(status_code=400, detail="Invalid time period")

        leaderboard_scores = calculate_leaderboard_scores(db, time_period_model, group_id)
        
        for user_id, score in leaderboard_scores.items():
            entries = read_leaderboard_entries_from_db(db, time_period_id=time_period_model.id, user_id=user_id, group_id=group_id)
            if entries:
                entry = entries[0]
                update_leaderboard_entry_in_db(db, entry.id, {"score": score})
            else:
                create_leaderboard_entry_in_db(db, {
                    "user_id": user_id,
                    "score": score,
                    "time_period_id": time_period_model.id,
                    "group_id": group_id
                })

        leaderboard_entries = read_leaderboard_entries_from_db(
            db, time_period_id=time_period_model.id, group_id=group_id, limit=limit
        )

        return [
            LeaderboardSchema(
                id=entry.id,
                user_id=entry.user_id,
                score=entry.score,
                time_period_id=entry.time_period_id,
                time_period=time_period_to_schema(time_period_model),
                group_id=entry.group_id
            )
            for entry in leaderboard_entries
        ]
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/leaderboard/user/{user_id}", response_model=List[LeaderboardSchema])
def get_user_leaderboard(
    request: Request,
    user_id: int = Path(..., description="The ID of the user to get leaderboard entries for"),
    db: Session = Depends(get_db)
):
    """
    Retrieve leaderboard entries for a specific user.

    This endpoint allows authenticated users to retrieve all leaderboard entries for a specific user.

    Args:
        request (Request): The FastAPI request object.
        user_id (int): The ID of the user to retrieve leaderboard entries for.
        db (Session): The database session.

    Returns:
        List[LeaderboardSchema]: A list of leaderboard entries for the specified user.

    Raises:
        HTTPException: If the user is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        # Check if the user exists
        user = read_user_from_db(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

        # Retrieve leaderboard entries for the user
        entries = read_leaderboard_entries_for_user_from_db(db, user_id)

        # Return an empty list if there are no leaderboard entries
        return [LeaderboardSchema.model_validate(entry) for entry in entries] or []
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/leaderboard/group/{group_id}", response_model=List[LeaderboardSchema])
def get_group_leaderboard(
    request: Request,
    group_id: int = Path(..., description="The ID of the group to get leaderboard entries for"),
    db: Session = Depends(get_db)
):
    """
    Retrieve leaderboard entries for a specific group.

    Args:
        request (Request): The FastAPI request object.
        group_id (int): The ID of the group to retrieve leaderboard entries for.
        db (Session): The database session.

    Returns:
        List[LeaderboardSchema]: A list of leaderboard entries for the specified group.

    Raises:
        HTTPException: If the group is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        # Check if the group exists
        group = read_group_from_db(db, group_id)
        if not group:
            raise HTTPException(status_code=404, detail=f"Group with ID {group_id} not found")

        # Retrieve leaderboard entries for the group
        db_leaderboard_entries = read_leaderboard_entries_for_group_from_db(db, group_id)
        
        # Return an empty list if there are no leaderboard entries
        return [LeaderboardSchema.model_validate(entry) for entry in db_leaderboard_entries] or []
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_group_leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/leaderboard/", response_model=LeaderboardSchema)
def post_leaderboard_entry(
    request: Request,
    entry: LeaderboardCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new leaderboard entry.

    This endpoint allows authenticated users to create a new leaderboard entry.

    Args:
        request (Request): The FastAPI request object.
        entry (LeaderboardCreateSchema): The leaderboard entry data to be created.
        db (Session): The database session.

    Returns:
        LeaderboardSchema: The created leaderboard entry.

    Raises:
        HTTPException: If the user is not authenticated or if there's an error creating the entry.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    logger.debug(f"Received leaderboard entry data: {entry.model_dump()}")

    try:
        created_entry = create_leaderboard_entry_in_db(db, entry.model_dump())
        logger.debug(f"Created leaderboard entry: {created_entry}")
        return LeaderboardSchema.model_validate(created_entry)
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error in post_leaderboard_entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating leaderboard entry: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in post_leaderboard_entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/leaderboard/{entry_id}", response_model=LeaderboardSchema)
def put_leaderboard_entry(
    request: Request,
    entry_id: int,
    entry: LeaderboardUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific leaderboard entry.

    This endpoint allows authenticated users to update an existing leaderboard entry.

    Args:
        request (Request): The FastAPI request object.
        entry_id (int): The ID of the leaderboard entry to update.
        entry (LeaderboardUpdateSchema): The updated leaderboard entry data.
        db (Session): The database session.

    Returns:
        LeaderboardSchema: The updated leaderboard entry.

    Raises:
        HTTPException: If the leaderboard entry with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        updated_entry = update_leaderboard_entry_in_db(db, entry_id, entry.model_dump())
        if not updated_entry:
            raise HTTPException(status_code=404, detail="Leaderboard entry not found")
        return LeaderboardSchema.model_validate(updated_entry)
    except SQLAlchemyError as e:
        logger.error(f"Database error in put_leaderboard_entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating leaderboard entry")

@router.delete("/leaderboard/{entry_id}", status_code=204)
def delete_leaderboard_entry(
    request: Request,
    entry_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific leaderboard entry.

    This endpoint allows authenticated users to delete an existing leaderboard entry.

    Args:
        request (Request): The FastAPI request object.
        entry_id (int): The ID of the leaderboard entry to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the leaderboard entry with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        success = delete_leaderboard_entry_from_db(db, entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Leaderboard entry not found")
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_leaderboard_entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting leaderboard entry")

```

## File: question_sets.py
```py
# filename: backend/app/api/endpoints/question_sets.py

"""
Question Sets Management API

This module provides API endpoints for managing question sets in the quiz application.
It includes operations for creating, reading, updating, and deleting question sets,
as well as uploading question sets from files.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_question_sets module.

Endpoints:
- POST /upload-questions/: Upload a question set from a file
- GET /question-sets/: Retrieve a list of question sets
- POST /question-sets/: Create a new question set
- GET /question-sets/{question_set_id}: Retrieve a specific question set by ID
- PUT /question-sets/{question_set_id}: Update a specific question set
- DELETE /question-sets/{question_set_id}: Delete a specific question set

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

import json
from typing import List

from fastapi import (APIRouter, Depends, File, Form, HTTPException, Response,
                     UploadFile, status, Request)
from sqlalchemy.orm import Session

from backend.app.crud.crud_question_sets import (create_question_set_in_db,
                                                 delete_question_set_from_db,
                                                 read_question_set_from_db,
                                                 read_question_sets_from_db,
                                                 update_question_set_in_db)
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.db.session import get_db
from backend.app.schemas.question_sets import (QuestionSetCreateSchema,
                                               QuestionSetSchema,
                                               QuestionSetUpdateSchema,
                                               QuestionSetBaseSchema)
from backend.app.schemas.questions import QuestionCreateSchema
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()

@router.post("/upload-questions/")
async def upload_question_set(
    request: Request,
    file: UploadFile = File(...),
    question_set_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a question set from a file.

    This endpoint allows admin users to upload a question set from a JSON file.

    Args:
        request (Request): The FastAPI request object.
        file (UploadFile): The JSON file containing the question set data.
        question_set_name (str): The name for the new question set.
        db (Session): The database session.

    Returns:
        dict: A message indicating successful upload.

    Raises:
        HTTPException: 
            - 403: If the user is not an admin.
            - 400: If the JSON data is invalid.
            - 500: If there's an error during the upload process.
    """
    check_auth_status(request)
    current_user = get_current_user_or_error(request)

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin users can upload question sets")

    try:
        content = await file.read()
        question_data = json.loads(content.decode('utf-8'))

        for question in question_data:
            QuestionCreateSchema(**question)

        question_set = QuestionSetCreateSchema(name=question_set_name, creator_id=current_user.id)
        question_set_created = create_question_set_in_db(db, question_set.model_dump())

        for question in question_data:
            question['question_set_id'] = question_set_created.id
            create_question_in_db(db, QuestionCreateSchema(**question).model_dump())

        return {"message": "Question set uploaded successfully"}

    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON data: {str(exc)}"
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading question set: {str(exc)}"
        ) from exc

@router.get("/question-sets/", response_model=List[QuestionSetSchema])
def get_question_sets(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of question sets.

    This endpoint allows authenticated users to retrieve a paginated list of question sets.

    Args:
        request (Request): The FastAPI request object.
        skip (int): The number of question sets to skip (for pagination).
        limit (int): The maximum number of question sets to return (for pagination).
        db (Session): The database session.

    Returns:
        List[QuestionSetSchema]: A list of question sets.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    question_sets = read_question_sets_from_db(db, skip=skip, limit=limit)
    return [QuestionSetSchema.model_validate(qs) for qs in question_sets]

@router.post("/question-sets/", response_model=QuestionSetSchema, status_code=201)
def post_question_set(
    request: Request,
    question_set: QuestionSetBaseSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new question set.

    This endpoint allows authenticated users to create a new question set.

    Args:
        request (Request): The FastAPI request object.
        question_set (QuestionSetBaseSchema): The question set data to be created.
        db (Session): The database session.

    Returns:
        QuestionSetSchema: The created question set.

    Raises:
        HTTPException: If a question set with the same name already exists for the user or if the user is not authenticated.
    """
    check_auth_status(request)
    current_user = get_current_user_or_error(request)

    question_set_data = question_set.model_dump()
    question_set_data['creator_id'] = current_user.id
    validated_question_set = QuestionSetCreateSchema(**question_set_data)
    try:
        created_question_set = create_question_set_in_db(db=db, question_set_data=validated_question_set.model_dump())
        return QuestionSetSchema.model_validate(created_question_set)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.get("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def get_question_set(
    request: Request,
    question_set_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific question set by ID.

    This endpoint allows authenticated users to retrieve a single question set by its ID.

    Args:
        request (Request): The FastAPI request object.
        question_set_id (int): The ID of the question set to retrieve.
        db (Session): The database session.

    Returns:
        QuestionSetSchema: The question set data.

    Raises:
        HTTPException: If the question set with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    question_set = read_question_set_from_db(db, question_set_id=question_set_id)
    if not question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found")
    return QuestionSetSchema.model_validate(question_set)

@router.put("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def put_question_set(
    request: Request,
    question_set_id: int,
    question_set: QuestionSetUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific question set.

    This endpoint allows authenticated users to update an existing question set by its ID.

    Args:
        request (Request): The FastAPI request object.
        question_set_id (int): The ID of the question set to update.
        question_set (QuestionSetUpdateSchema): The updated question set data.
        db (Session): The database session.

    Returns:
        QuestionSetSchema: The updated question set data.

    Raises:
        HTTPException: If the question set with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    question_set_data = question_set.model_dump()
    updated_question_set = update_question_set_in_db(db, question_set_id, question_set_data)
    if updated_question_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found")
    return QuestionSetSchema.model_validate(updated_question_set)

@router.delete("/question-sets/{question_set_id}", status_code=204)
def delete_question_set(
    request: Request,
    question_set_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific question set.

    This endpoint allows authenticated users to delete an existing question set by its ID.

    Args:
        request (Request): The FastAPI request object.
        question_set_id (int): The ID of the question set to delete.
        db (Session): The database session.

    Returns:
        Response: An empty response with a 204 status code.

    Raises:
        HTTPException: If the question set with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    deleted = delete_question_set_from_db(db, question_set_id=question_set_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question set not found")
    return Response(status_code=204)

```

## File: question_tags.py
```py
# filename: backend/app/api/endpoints/question_tags.py

"""
Question Tags Management API

This module provides API endpoints for managing question tags in the quiz application.
It includes operations for creating, reading, updating, and deleting question tags.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_question_tags module.

Endpoints:
- POST /question-tags/: Create a new question tag
- GET /question-tags/: Retrieve a list of question tags
- GET /question-tags/{tag_id}: Retrieve a specific question tag by ID
- PUT /question-tags/{tag_id}: Update a specific question tag
- DELETE /question-tags/{tag_id}: Delete a specific question tag

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.crud.crud_question_tags import (create_question_tag_in_db,
                                                 delete_question_tag_from_db,
                                                 read_question_tag_from_db,
                                                 read_question_tags_from_db,
                                                 update_question_tag_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.question_tags import (QuestionTagCreateSchema,
                                               QuestionTagSchema,
                                               QuestionTagUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error


router = APIRouter()

@router.post("/question-tags/", response_model=QuestionTagSchema, status_code=status.HTTP_201_CREATED)
def post_question_tag(
    request: Request,
    question_tag: QuestionTagCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new question tag.

    This endpoint allows authenticated users to create a new question tag in the database.
    The question tag data is validated using the QuestionTagCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        question_tag (QuestionTagCreateSchema): The question tag data to be created.
        db (Session): The database session.

    Returns:
        QuestionTagSchema: The created question tag data.

    Raises:
        HTTPException: If a duplicate tag is attempted or the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    question_tag_data = question_tag.model_dump()

    try:
        created_tag = create_question_tag_in_db(db=db, question_tag_data=question_tag_data)
    except IntegrityError as exc:
        db.rollback()  # Rollback the session to avoid transaction issues
        raise HTTPException(status_code=400, detail="Tag already exists") from exc
    except Exception as e:
        raise

    return QuestionTagSchema.model_validate(created_tag)


@router.get("/question-tags/", response_model=List[QuestionTagSchema])
def get_question_tags(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of question tags.

    This endpoint allows authenticated users to retrieve a paginated list of question tags from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of question tags to skip. Defaults to 0.
        limit (int, optional): The maximum number of question tags to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[QuestionTagSchema]: A list of question tags.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    question_tags = read_question_tags_from_db(db, skip=skip, limit=limit)
    return [QuestionTagSchema.model_validate(tag) for tag in question_tags]

@router.get("/question-tags/{tag_id}", response_model=QuestionTagSchema)
def get_question_tag(
    request: Request,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific question tag by ID.

    This endpoint allows authenticated users to retrieve a single question tag by its ID.

    Args:
        request (Request): The FastAPI request object.
        tag_id (int): The ID of the question tag to retrieve.
        db (Session): The database session.

    Returns:
        QuestionTagSchema: The question tag data.

    Raises:
        HTTPException: If the question tag with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_question_tag = read_question_tag_from_db(db, question_tag_id=tag_id)
    if db_question_tag is None:
        raise HTTPException(status_code=404, detail="Question tag not found")
    return QuestionTagSchema.model_validate(db_question_tag)

@router.put("/question-tags/{tag_id}", response_model=QuestionTagSchema)
def put_question_tag(
    request: Request,
    tag_id: int,
    question_tag: QuestionTagUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific question tag.

    This endpoint allows authenticated users to update an existing question tag by its ID.

    Args:
        request (Request): The FastAPI request object.
        tag_id (int): The ID of the question tag to update.
        question_tag (QuestionTagUpdateSchema): The updated question tag data.
        db (Session): The database session.

    Returns:
        QuestionTagSchema: The updated question tag data.

    Raises:
        HTTPException: If the question tag with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    question_tag_data = question_tag.model_dump()
    updated_tag = update_question_tag_in_db(db, tag_id, question_tag_data)
    if updated_tag is None:
        raise HTTPException(status_code=404, detail="Question tag not found")
    return QuestionTagSchema.model_validate(updated_tag)

@router.delete("/question-tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question_tag(
    request: Request,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific question tag.

    This endpoint allows authenticated users to delete an existing question tag by its ID.

    Args:
        request (Request): The FastAPI request object.
        tag_id (int): The ID of the question tag to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the question tag with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_question_tag_from_db(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question tag not found")
    return None
```

## File: questions.py
```py
# filename: backend/app/api/endpoints/questions.py

"""
Question Management API

This module provides API endpoints for managing questions in the quiz application.
It includes operations for creating, reading, updating, and deleting questions,
as well as specialized endpoints for creating questions with associated answers.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_questions module.

Endpoints:
- POST /questions/: Create a new question
- POST /questions/with-answers/: Create a new question with associated answers
- GET /questions/: Retrieve a list of questions
- GET /questions/{question_id}: Retrieve a specific question by ID
- PUT /questions/{question_id}: Update a specific question
- DELETE /questions/{question_id}: Delete a specific question

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_questions import (create_question_in_db,
                                             delete_question_from_db,
                                             read_question_from_db,
                                             read_questions_from_db,
                                             replace_question_in_db,
                                             update_question_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.questions import (DetailedQuestionSchema,
                                           QuestionCreateSchema,
                                           QuestionUpdateSchema,
                                           QuestionWithAnswersReplaceSchema,
                                           QuestionWithAnswersCreateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()

@router.post("/questions/", response_model=DetailedQuestionSchema, status_code=status.HTTP_201_CREATED)
async def post_question(
    request: Request,
    question: QuestionCreateSchema,
    db: Session = Depends(get_db)
) -> DetailedQuestionSchema:
    """
    Create a new question.

    This endpoint allows authenticated users to create a new question in the database.
    The question data is validated using the QuestionCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        question (QuestionCreateSchema): The question data to be created.
        db (Session): The database session.

    Returns:
        QuestionSchema: The created question data.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the user is not authenticated.
            - 422 Unprocessable Entity: If the question data is invalid.
            - 500 Internal Server Error: If an unexpected error occurs during question creation.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        validated_question = QuestionCreateSchema(**question.model_dump())
        question_data = validated_question.model_dump()
        created_question = create_question_in_db(db=db, question_data=question_data)
        return DetailedQuestionSchema.model_validate(created_question)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(ve)
                        ) from ve
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while creating the question"
                        ) from e

@router.post("/questions/with-answers/",
             response_model=DetailedQuestionSchema,
             status_code=status.HTTP_201_CREATED)
async def post_question_with_answers(
    request: Request,
    question: QuestionWithAnswersCreateSchema,
    db: Session = Depends(get_db)
) -> DetailedQuestionSchema:
    """
    Create a new question with associated answers.

    This endpoint allows authenticated users to create a new question along with its answer choices
    in a single operation.
    The question and answer data are validated using the QuestionWithAnswersCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        question (QuestionWithAnswersCreateSchema): The question and answer data to be created.
        db (Session): The database session.

    Returns:
        DetailedQuestionSchema: The created question data including associated answers.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the user is not authenticated.
            - 422 Unprocessable Entity: If the question or answer data is invalid.
            - 500 Internal Server Error: If an unexpected error occurs during question creation.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        validated_question = QuestionWithAnswersCreateSchema(**question.model_dump())
        question_data = validated_question.model_dump()
        created_question = create_question_in_db(db=db, question_data=question_data)
        return DetailedQuestionSchema.model_validate(created_question)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(ve)
                        ) from ve
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error occurred while creating the question with answers: {e}"
                        ) from e

@router.get("/questions/", response_model=List[DetailedQuestionSchema])
async def get_questions(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[DetailedQuestionSchema]:
    """
    Retrieve a list of questions.

    This endpoint allows authenticated users to retrieve a
    paginated list of questions from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of questions to skip. Defaults to 0.
        limit (int, optional): The maximum number of questions to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[DetailedQuestionSchema]: A list of questions with their details.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the user is not authenticated.
            - 500 Internal Server Error: If an unexpected error occurs during retrieval.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        questions = read_questions_from_db(db, skip=skip, limit=limit)
        return [DetailedQuestionSchema.model_validate(q) for q in questions]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while retrieving questions"
                        ) from e

@router.get("/questions/{question_id}", response_model=DetailedQuestionSchema)
async def get_question(
    request: Request,
    question_id: int,
    db: Session = Depends(get_db)
) -> DetailedQuestionSchema:
    """
    Retrieve a specific question by ID.

    This endpoint allows authenticated users to retrieve a single question by its ID.

    Args:
        request (Request): The FastAPI request object.
        question_id (int): The ID of the question to retrieve.
        db (Session): The database session.

    Returns:
        DetailedQuestionSchema: The detailed question data.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the user is not authenticated.
            - 404 Not Found: If the question with the given ID does not exist.
            - 500 Internal Server Error: If an unexpected error occurs during retrieval.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        db_question = read_question_from_db(db, question_id=question_id)
        if db_question is None:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        return DetailedQuestionSchema.model_validate(db_question)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while retrieving the question"
                        ) from e

@router.put("/questions/{question_id}", response_model=DetailedQuestionSchema)
async def put_question(
    request: Request,
    question_id: int,
    question: QuestionWithAnswersReplaceSchema,
    db: Session = Depends(get_db)
) -> DetailedQuestionSchema:
    """
    Replace a specific question with its answer choices.

    This endpoint allows authenticated users to replace an existing question by its ID,
    including its associated answer choices. It can handle both existing and new answer choices.

    Args:
        request (Request): The FastAPI request object.
        question_id (int): The ID of the question to replace.
        question (QuestionWithAnswersReplaceSchema): The new question data to replace the existing question.
        db (Session): The database session.

    Returns:
        DetailedQuestionSchema: The replaced question data.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the user is not authenticated.
            - 404 Not Found: If the question with the given ID does not exist.
            - 422 Unprocessable Entity: If the replace data is invalid.
            - 500 Internal Server Error: If an unexpected error occurs during the replacement.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        question_data = question.model_dump()
        replaced_question = replace_question_in_db(db, question_id, question_data)
        if replaced_question is None:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        return DetailedQuestionSchema.model_validate(replaced_question)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)) from ve
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An unexpected error occurred while replacing the question: {str(e)}") from e

@router.patch("/questions/{question_id}", response_model=DetailedQuestionSchema)
async def patch_question(
    request: Request,
    question_id: int,
    question: QuestionUpdateSchema,
    db: Session = Depends(get_db)
) -> DetailedQuestionSchema:
    """
    Partially update a specific question.

    This endpoint allows authenticated users to partially update an existing question by its ID.
    Only the provided fields will be updated.

    Args:
        request (Request): The FastAPI request object.
        question_id (int): The ID of the question to update.
        question (QuestionUpdateSchema): The partial question data to update.
        db (Session): The database session.

    Returns:
        DetailedQuestionSchema: The updated question data.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the user is not authenticated.
            - 404 Not Found: If the question with the given ID does not exist.
            - 422 Unprocessable Entity: If the update data is invalid.
            - 500 Internal Server Error: If an unexpected error occurs during the update.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        question_data = question.model_dump(exclude_unset=True)
        updated_question = update_question_in_db(db, question_id, question_data)
        if updated_question is None:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        return DetailedQuestionSchema.model_validate(updated_question)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)) from ve
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An unexpected error occurred while updating the question: {str(e)}") from e

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    request: Request,
    question_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific question.

    This endpoint allows authenticated users to delete an existing question by its ID.

    Args:
        request (Request): The FastAPI request object.
        question_id (int): The ID of the question to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the user is not authenticated.
            - 404 Not Found: If the question with the given ID does not exist.
            - 500 Internal Server Error: If an unexpected error occurs during the deletion.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        success = delete_question_from_db(db, question_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while deleting the question"
                        ) from e

```

## File: register.py
```py
# filename: backend/app/api/endpoints/register.py

"""
User Registration API

This module provides an API endpoint for user registration in the quiz application.
It includes an operation for creating a new user account.

The module uses FastAPI for defining the API endpoint and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_user module.

Endpoints:
- POST /register: Register a new user

This endpoint does not require authentication as it's used for creating new user accounts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import ValidationError

from backend.app.core.security import get_password_hash
from backend.app.crud.crud_user import (create_user_in_db,
                                        read_user_by_email_from_db,
                                        read_user_by_username_from_db)
from backend.app.db.session import get_db
from backend.app.models.roles import RoleModel
from backend.app.schemas.user import UserCreateSchema, UserSchema
from backend.app.services.logging_service import logger

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    """
    Register a new user.

    This endpoint allows new users to create an account in the application.
    It checks if the username and email are unique, hashes the password,
    and assigns a default role if one is not specified.

    Args:
        user (UserCreateSchema): The user data for registration.
        db (Session): The database session.

    Returns:
        UserSchema: The created user data.

    Raises:
        HTTPException: 
            - 400 Bad Request: If the username or email is already registered.
            - 400 Bad Request: If the specified role_id does not exist.
            - 400 Bad Request: If no role is available (neither specified nor default).
            - 500 Internal Server Error: For any other unexpected errors.
    """
    try:
        logger.debug(f"Attempting to register user: {user.username}")
        
        db_user = read_user_by_username_from_db(db, username=user.username)
        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
        
        db_email = read_user_by_email_from_db(db, email=user.email)
        if db_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        logger.debug("Hashing password")
        hashed_password = get_password_hash(user.password.get_secret_value())
        logger.debug("Password hashed successfully")
        
        if user.role_id is not None:
            logger.debug(f"Checking for role with id: {user.role_id}")
            role = db.query(RoleModel).filter(RoleModel.id == user.role_id).first()
            if not role:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role_id: {user.role_id}")
        else:
            logger.debug("No role_id provided, looking for default role")
            default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
            if default_role:
                user.role_id = default_role.id
                logger.debug(f"Assigned default role with id: {user.role_id}")
            else:
                logger.debug("No default role found")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No role available for user creation")
        
        user_data = user.model_dump()
        user_data['hashed_password'] = hashed_password
        del user_data['password']
        
        logger.debug("Creating user in database")
        created_user = create_user_in_db(db=db, user_data=user_data)
        logger.debug(f"User created successfully with id: {created_user.id}")
        
        return UserSchema.model_validate(created_user)
    except ValidationError as exc:
        logger.error(f"Validation error during user registration: {exc}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Validation error: {exc}") from exc
    except ValueError as exc:
        logger.error(f"Error during user registration: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error during user registration: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating user: {exc}") from exc

```

## File: subjects.py
```py
# filepath: backend/app/api/endpoints/subjects.py

"""
Subjects Management API

This module provides API endpoints for managing subjects in the quiz application.
It includes operations for creating, reading, updating, and deleting subjects.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_subjects module.

Endpoints:
- POST /subjects/: Create a new subject
- GET /subjects/: Retrieve a list of subjects
- GET /subjects/{subject_id}: Retrieve a specific subject by ID
- PUT /subjects/{subject_id}: Update a specific subject
- DELETE /subjects/{subject_id}: Delete a specific subject

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.crud.crud_subjects import (create_subject_in_db,
                                            delete_subject_from_db,
                                            read_subject_from_db,
                                            read_subjects_from_db,
                                            update_subject_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.subjects import (SubjectCreateSchema, SubjectSchema,
                                          SubjectUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.services.logging_service import logger

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
def post_subject(
    request: Request,
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new subject.

    This endpoint allows authenticated users to create a new subject in the database.
    The subject data is validated using the SubjectCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        subject (SubjectCreateSchema): The subject data to be created.
        db (Session): The database session.

    Returns:
        SubjectSchema: The created subject data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    subject_data = subject.model_dump()
    try:
        created_subject = create_subject_in_db(db=db, subject_data=subject_data)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Subject with this name already exists")
    except HTTPException as e:
        # Re-raise the HTTPException from create_subject_in_db
        raise e
    return SubjectSchema.model_validate(created_subject)

@router.get("/subjects/", response_model=List[SubjectSchema])
def get_subjects(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of subjects.

    This endpoint allows authenticated users to retrieve a paginated list of subjects from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of subjects to skip. Defaults to 0.
        limit (int, optional): The maximum number of subjects to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[SubjectSchema]: A list of subjects.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    subjects = read_subjects_from_db(db, skip=skip, limit=limit)
    return [SubjectSchema.model_validate(s) for s in subjects]

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
def get_subject(
    request: Request,
    subject_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific subject by ID.

    This endpoint allows authenticated users to retrieve a single subject by its ID.

    Args:
        request (Request): The FastAPI request object.
        subject_id (int): The ID of the subject to retrieve.
        db (Session): The database session.

    Returns:
        SubjectSchema: The subject data.

    Raises:
        HTTPException: If the subject with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_subject = read_subject_from_db(db, subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectSchema.model_validate(db_subject)

@router.put("/subjects/{subject_id}", response_model=SubjectSchema)
def put_subject(
    request: Request,
    subject_id: int,
    subject: SubjectUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific subject.

    This endpoint allows authenticated users to update an existing subject by its ID.

    Args:
        request (Request): The FastAPI request object.
        subject_id (int): The ID of the subject to update.
        subject (SubjectUpdateSchema): The updated subject data.
        db (Session): The database session.

    Returns:
        SubjectSchema: The updated subject data.

    Raises:
        HTTPException: If the subject with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    subject_data = subject.model_dump(exclude_unset=True)
    logger.debug(f"Updating subject {subject_id} with data: {subject_data}")
    try:
        db_subject = update_subject_in_db(db, subject_id, subject_data)
        if db_subject is None:
            raise HTTPException(status_code=404, detail="Subject not found")
    except HTTPException as e:
        # Re-raise the HTTPException from update_subject_in_db
        logger.error(f"Error updating subject {subject_id}: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating subject {subject_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
    logger.debug(f"Successfully updated subject {subject_id}")
    return SubjectSchema.model_validate(db_subject)

@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(
    request: Request,
    subject_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific subject.

    This endpoint allows authenticated users to delete an existing subject by its ID.

    Args:
        request (Request): The FastAPI request object.
        subject_id (int): The ID of the subject to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the subject with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_subject_from_db(db, subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return None

```

## File: subtopics.py
```py
# filename: backend/app/api/endpoints/subtopics.py

"""
Subtopics Management API

This module provides API endpoints for managing subtopics in the quiz application.
It includes operations for creating, reading, updating, and deleting subtopics.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_subtopics module.

Endpoints:
- POST /subtopics/: Create a new subtopic
- GET /subtopics/: Retrieve a list of subtopics
- GET /subtopics/{subtopic_id}: Retrieve a specific subtopic by ID
- PUT /subtopics/{subtopic_id}: Update a specific subtopic
- DELETE /subtopics/{subtopic_id}: Delete a specific subtopic

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_subtopics import (create_subtopic_in_db,
                                             delete_subtopic_from_db,
                                             read_subtopic_from_db,
                                             read_subtopics_from_db,
                                             update_subtopic_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.subtopics import (SubtopicCreateSchema,
                                           SubtopicSchema,
                                           SubtopicUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()

@router.post("/subtopics/", response_model=SubtopicSchema, status_code=201)
def post_subtopic(
    request: Request,
    subtopic: SubtopicCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new subtopic.

    This endpoint allows authenticated users to create a new subtopic in the database.
    The subtopic data is validated using the SubtopicCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        subtopic (SubtopicCreateSchema): The subtopic data to be created.
        db (Session): The database session.

    Returns:
        SubtopicSchema: The created subtopic data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    subtopic_data = subtopic.model_dump()
    created_subtopic = create_subtopic_in_db(db=db, subtopic_data=subtopic_data)
    return SubtopicSchema.model_validate(created_subtopic)

@router.get("/subtopics/", response_model=List[SubtopicSchema])
def get_subtopics(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of subtopics.

    This endpoint allows authenticated users to retrieve a paginated list of subtopics from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of subtopics to skip. Defaults to 0.
        limit (int, optional): The maximum number of subtopics to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[SubtopicSchema]: A list of subtopics.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    subtopics = read_subtopics_from_db(db, skip=skip, limit=limit)
    return [SubtopicSchema.model_validate(s) for s in subtopics]

@router.get("/subtopics/{subtopic_id}", response_model=SubtopicSchema)
def get_subtopic(
    request: Request,
    subtopic_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific subtopic by ID.

    This endpoint allows authenticated users to retrieve a single subtopic by its ID.

    Args:
        request (Request): The FastAPI request object.
        subtopic_id (int): The ID of the subtopic to retrieve.
        db (Session): The database session.

    Returns:
        SubtopicSchema: The subtopic data.

    Raises:
        HTTPException: If the subtopic with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_subtopic = read_subtopic_from_db(db, subtopic_id=subtopic_id)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return SubtopicSchema.model_validate(db_subtopic)

@router.put("/subtopics/{subtopic_id}", response_model=SubtopicSchema)
def put_subtopic(
    request: Request,
    subtopic_id: int,
    subtopic: SubtopicUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific subtopic.

    This endpoint allows authenticated users to update an existing subtopic by its ID.

    Args:
        request (Request): The FastAPI request object.
        subtopic_id (int): The ID of the subtopic to update.
        subtopic (SubtopicUpdateSchema): The updated subtopic data.
        db (Session): The database session.

    Returns:
        SubtopicSchema: The updated subtopic data.

    Raises:
        HTTPException: If the subtopic with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    subtopic_data = subtopic.model_dump()
    db_subtopic = update_subtopic_in_db(db, subtopic_id, subtopic_data)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return SubtopicSchema.model_validate(db_subtopic)

@router.delete("/subtopics/{subtopic_id}", status_code=204)
def delete_subtopic(
    request: Request,
    subtopic_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific subtopic.

    This endpoint allows authenticated users to delete an existing subtopic by its ID.

    Args:
        request (Request): The FastAPI request object.
        subtopic_id (int): The ID of the subtopic to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the subtopic with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_subtopic_from_db(db, subtopic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return None

```

## File: time_periods.py
```py
# filename: backend/app/api/endpoints/time_periods.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud import crud_time_period
from backend.app.schemas.time_period import TimePeriodSchema
from backend.app.db.session import get_db
from backend.app.core.config import TimePeriod

router = APIRouter()

@router.get("/time-periods/", response_model=List[TimePeriodSchema])
def read_time_periods(db: Session = Depends(get_db)):
    return crud_time_period.read_all_time_periods_from_db(db)

@router.get("/time-periods/{time_period_id}", response_model=TimePeriodSchema)
def read_time_period(time_period_id: int, db: Session = Depends(get_db)):
    db_time_period = crud_time_period.read_time_period_from_db(db, time_period_id)
    if db_time_period is None:
        raise HTTPException(status_code=404, detail="Time period not found")
    return db_time_period

@router.post("/time-periods/", response_model=TimePeriodSchema)
def create_time_period(time_period: TimePeriod, db: Session = Depends(get_db)):
    return crud_time_period.create_time_period_in_db(db, time_period)

@router.put("/time-periods/{time_period_id}", response_model=TimePeriodSchema)
def update_time_period(time_period_id: int, new_name: str, db: Session = Depends(get_db)):
    db_time_period = crud_time_period.update_time_period_in_db(db, time_period_id, new_name)
    if db_time_period is None:
        raise HTTPException(status_code=404, detail="Time period not found")
    return db_time_period

@router.delete("/time-periods/{time_period_id}", response_model=bool)
def delete_time_period(time_period_id: int, db: Session = Depends(get_db)):
    success = crud_time_period.delete_time_period_from_db(db, time_period_id)
    if not success:
        raise HTTPException(status_code=404, detail="Time period not found")
    return success
```

## File: topics.py
```py
# filename: backend/app/api/endpoints/topics.py

"""
Topics Management API

This module provides API endpoints for managing topics in the quiz application.
It includes operations for creating, reading, updating, and deleting topics.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_topics module.

Endpoints:
- POST /topics/: Create a new topic
- GET /topics/: Retrieve a list of topics
- GET /topics/{topic_id}: Retrieve a specific topic by ID
- PUT /topics/{topic_id}: Update a specific topic
- DELETE /topics/{topic_id}: Delete a specific topic

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.crud.crud_topics import (create_topic_in_db,
                                          delete_topic_from_db,
                                          read_topic_from_db,
                                          read_topics_from_db,
                                          update_topic_in_db)
from backend.app.db.session import get_db
from backend.app.schemas.topics import (TopicCreateSchema, TopicSchema,
                                        TopicUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.services.logging_service import logger

router = APIRouter()

@router.post("/topics/", response_model=TopicSchema, status_code=201)
def post_topic(
    request: Request,
    topic: TopicCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new topic.

    This endpoint allows authenticated users to create a new topic in the database.
    The topic data is validated using the TopicCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        topic (TopicCreateSchema): The topic data to be created.
        db (Session): The database session.

    Returns:
        TopicSchema: The created topic data.

    Raises:
        HTTPException: If there's an error during the creation process or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    topic_data = topic.model_dump()
    try:
        created_topic = create_topic_in_db(db=db, topic_data=topic_data)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Topic with this name already exists")
    except HTTPException as e:
        # Re-raise the HTTPException from create_topic_in_db
        raise e
    return TopicSchema.model_validate(created_topic)

@router.get("/topics/", response_model=List[TopicSchema])
def get_topics(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of topics.

    This endpoint allows authenticated users to retrieve a paginated list of topics from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of topics to skip. Defaults to 0.
        limit (int, optional): The maximum number of topics to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[TopicSchema]: A list of topics.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    topics = read_topics_from_db(db, skip=skip, limit=limit)
    return [TopicSchema.model_validate(t) for t in topics]

@router.get("/topics/{topic_id}", response_model=TopicSchema)
def get_topic(
    request: Request,
    topic_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific topic by ID.

    This endpoint allows authenticated users to retrieve a single topic by its ID.

    Args:
        request (Request): The FastAPI request object.
        topic_id (int): The ID of the topic to retrieve.
        db (Session): The database session.

    Returns:
        TopicSchema: The topic data.

    Raises:
        HTTPException: If the topic with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    db_topic = read_topic_from_db(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Debug logging
    logger.debug(f"Raw db_topic: {db_topic}")
    logger.debug(f"db_topic subjects: {db_topic.subjects}")
    
    topic_schema = TopicSchema.model_validate(db_topic)
    
    # More debug logging
    logger.debug(f"Converted topic_schema: {topic_schema}")
    logger.debug(f"topic_schema subjects: {topic_schema.subjects}")
    
    return topic_schema

@router.put("/topics/{topic_id}", response_model=TopicSchema)
def put_topic(
    request: Request,
    topic_id: int,
    topic: TopicUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific topic.

    This endpoint allows authenticated users to update an existing topic by its ID.

    Args:
        request (Request): The FastAPI request object.
        topic_id (int): The ID of the topic to update.
        topic (TopicUpdateSchema): The updated topic data.
        db (Session): The database session.

    Returns:
        TopicSchema: The updated topic data.

    Raises:
        HTTPException: If the topic with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    topic_data = topic.model_dump(exclude_unset=True)
    try:
        db_topic = update_topic_in_db(db, topic_id, topic_data)
        if db_topic is None:
            raise HTTPException(status_code=404, detail="Topic not found or one or more subjects do not exist")
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Topic with this name already exists")
    return TopicSchema.model_validate(db_topic)

@router.delete("/topics/{topic_id}", status_code=204)
def delete_topic(
    request: Request,
    topic_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific topic.

    This endpoint allows authenticated users to delete an existing topic by its ID.

    Args:
        request (Request): The FastAPI request object.
        topic_id (int): The ID of the topic to delete.
        db (Session): The database session.

    Returns:
        None

    Raises:
        HTTPException: If the topic with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_topic_from_db(db, topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return None

```

## File: user_responses.py
```py
# filename: backend/app/api/endpoints/user_responses.py

"""
User Responses Management API

This module provides API endpoints for managing user responses in the quiz application.
It includes operations for creating, reading, updating, and deleting user responses.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_user_responses module.

Endpoints:
- POST /user-responses/: Create a new user response
- GET /user-responses/{user_response_id}: Retrieve a specific user response by ID
- GET /user-responses/: Retrieve a list of user responses
- PUT /user-responses/{user_response_id}: Update a specific user response
- DELETE /user-responses/{user_response_id}: Delete a specific user response

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_user_responses import (create_user_response_in_db,
                                                  delete_user_response_from_db,
                                                  read_user_response_from_db,
                                                  read_user_responses_from_db,
                                                  update_user_response_in_db)
from backend.app.crud.crud_questions import read_question_from_db
from backend.app.crud.crud_answer_choices import read_answer_choice_from_db
from backend.app.db.session import get_db
from backend.app.schemas.user_responses import (UserResponseCreateSchema,
                                                UserResponseSchema,
                                                UserResponseUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()

def score_user_response(db: Session, user_response_data: dict) -> bool:
    """
    Score the user response by checking if the selected answer is correct.

    Args:
        db (Session): The database session.
        user_response_data (dict): The user response data.

    Returns:
        bool: True if the answer is correct, False otherwise.

    Raises:
        HTTPException: If the question or answer choice is not found.
    """
    question = read_question_from_db(db, user_response_data['question_id'])
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    answer_choice = read_answer_choice_from_db(db, user_response_data['answer_choice_id'])
    if not answer_choice:
        raise HTTPException(status_code=404, detail="Answer choice not found")

    return answer_choice.is_correct

@router.post(
    "/user-responses/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED
)
def post_user_response(
    request: Request,
    user_response: UserResponseCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new user response and score it.

    This endpoint allows authenticated users to create a new user response in the database.
    The user response data is validated using the UserResponseCreateSchema.
    After creation, the response is immediately scored.

    Args:
        request (Request): The FastAPI request object.
        user_response (UserResponseCreateSchema): The user response data to be created.
        db (Session): The database session.

    Returns:
        UserResponseSchema: The created and scored user response data.

    Raises:
        HTTPException: If there's an error during the creation or scoring process, or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    user_response_data = user_response.model_dump()
    
    try:
        is_correct = score_user_response(db, user_response_data)
        user_response_data['is_correct'] = is_correct
    except HTTPException as e:
        # If scoring fails, we still create the response but set is_correct to None
        user_response_data['is_correct'] = None
    
    created_response = create_user_response_in_db(db=db, user_response_data=user_response_data)
    return UserResponseSchema.model_validate(created_response)

@router.get("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def get_user_response(
    request: Request,
    user_response_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific user response by ID.

    This endpoint allows authenticated users to retrieve a single user response by its ID.

    Args:
        request (Request): The FastAPI request object.
        user_response_id (int): The ID of the user response to retrieve.
        db (Session): The database session.

    Returns:
        UserResponseSchema: The user response data.

    Raises:
        HTTPException: If the user response with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    user_response = read_user_response_from_db(db, user_response_id)
    if not user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    return UserResponseSchema.model_validate(user_response)

@router.get("/user-responses/", response_model=List[UserResponseSchema])
def get_user_responses(
    request: Request,
    user_id: Optional[int] = None,
    question_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of user responses.

    This endpoint allows authenticated users to retrieve a list of user responses from the database.
    The responses can be filtered by user_id, question_id, and time range.

    Args:
        request (Request): The FastAPI request object.
        user_id (Optional[int]): Filter responses by user ID.
        question_id (Optional[int]): Filter responses by question ID.
        start_time (Optional[datetime]): Filter responses after this time.
        end_time (Optional[datetime]): Filter responses before this time.
        skip (int): The number of responses to skip (for pagination).
        limit (int): The maximum number of responses to return (for pagination).
        db (Session): The database session.

    Returns:
        List[UserResponseSchema]: A list of user responses.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    user_responses = read_user_responses_from_db(
        db,
        user_id=user_id,
        question_id=question_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )
    return [UserResponseSchema.model_validate(ur) for ur in user_responses]

@router.put("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def put_user_response(
    request: Request,
    user_response_id: int,
    user_response: UserResponseUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific user response.

    This endpoint allows authenticated users to update an existing user response by its ID.

    Args:
        request (Request): The FastAPI request object.
        user_response_id (int): The ID of the user response to update.
        user_response (UserResponseUpdateSchema): The updated user response data.
        db (Session): The database session.

    Returns:
        UserResponseSchema: The updated user response data.

    Raises:
        HTTPException: If the user response with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    user_response_data = user_response.model_dump()
    updated_user_response = update_user_response_in_db(db, user_response_id, user_response_data)
    if not updated_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    return UserResponseSchema.model_validate(updated_user_response)

@router.delete("/user-responses/{user_response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_response(
    request: Request,
    user_response_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific user response.

    This endpoint allows authenticated users to delete an existing user response by its ID.

    Args:
        request (Request): The FastAPI request object.
        user_response_id (int): The ID of the user response to delete.
        db (Session): The database session.

    Returns:
        Response: An empty response with a 204 status code.

    Raises:
        HTTPException: If the user response with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_user_response_from_db(db, user_response_id)
    if not success:
        raise HTTPException(status_code=404, detail="User response not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

```

## File: users.py
```py
# filename: backend/app/api/endpoints/users.py

"""
Users Management API

This module provides API endpoints for managing users in the quiz application.
It includes operations for creating, reading, and updating user information.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_user module.

Endpoints:
- POST /users/: Create a new user
- GET /users/: Retrieve a list of users
- GET /users/me: Retrieve the current user's information
- PUT /users/me: Update the current user's information

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import ValidationError

from backend.app.crud.crud_user import (create_user_in_db, read_users_from_db,
                                        update_user_in_db)
from backend.app.crud.crud_roles import read_role_from_db
from backend.app.db.session import get_db
from backend.app.schemas.user import (UserCreateSchema, UserSchema,
                                      UserUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.core.security import get_password_hash

router = APIRouter()

@router.post("/users/", response_model=UserSchema, status_code=201)
def post_user(
    request: Request,
    user: UserCreateSchema, 
    db: Session = Depends(get_db)
):
    """
    Create a new user.

    This endpoint allows authenticated users to create a new user in the database.
    The user data is validated using the UserCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        user (UserCreateSchema): The user data to be created.
        db (Session): The database session.

    Returns:
        UserSchema: The created user data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        user_data = user.model_dump()
        user_data['hashed_password'] = get_password_hash(user_data.pop('password'))
        new_user = create_user_in_db(db=db, user_data=user_data)
        return UserSchema.model_validate(new_user)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        ) from e
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            ) from e
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
        ) from e

@router.get("/users/", response_model=List[UserSchema])
def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of users.

    This endpoint allows authenticated users to retrieve a paginated list of users from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of users to skip. Defaults to 0.
        limit (int, optional): The maximum number of users to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[UserSchema]: A list of users.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    users = read_users_from_db(db, skip=skip, limit=limit)
    return [UserSchema.model_validate(user) for user in users]

@router.get("/users/me", response_model=UserSchema)
def get_user_me(request: Request):
    """
    Retrieve the current user's information.

    This endpoint allows authenticated users to retrieve their own user information.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        UserSchema: The current user's data.
    """
    check_auth_status(request)
    current_user = get_current_user_or_error(request)
    return UserSchema.model_validate(current_user)

@router.put("/users/me", response_model=UserSchema)
def put_user_me(
    request: Request,
    user: UserUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update the current user's information.

    This endpoint allows authenticated users to update their own user information.

    Args:
        request (Request): The FastAPI request object.
        user (UserUpdateSchema): The updated user data.
        db (Session): The database session.

    Returns:
        UserSchema: The updated user data.

    Raises:
        HTTPException: 
            - 422 Unprocessable Entity: If there's a validation error or invalid role_id.
            - 400 Bad Request: If there's an unexpected error during the update process.
    """
    check_auth_status(request)
    current_user = get_current_user_or_error(request)

    try:
        user_data = user.model_dump(exclude_unset=True)
        if 'password' in user_data:
            user_data['hashed_password'] = get_password_hash(user_data.pop('password'))
        if 'role_id' in user_data:
            role = read_role_from_db(db, user_data['role_id'])
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid role_id"
                )
        
        updated_user = update_user_in_db(db=db, user_id=current_user.id, user_data=user_data)
        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserSchema.model_validate(updated_user)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to update user. ' + str(e)
        ) from e

```

# Directory: /code/quiz-app/backend/app/models

## File: __init__.py
```py

```

## File: answer_choices.py
```py
# filename: backend/app/models/answer_choices.py

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


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
# filename: backend/app/models/associations.py

from sqlalchemy import Column, ForeignKey, Integer

from backend.app.db.base import Base


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
# filename: backend/app/models/authentication.py

from sqlalchemy import Column, DateTime, Integer, String
from datetime import datetime, timezone

from backend.app.db.base import Base


class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    jti = Column(String(36), primary_key=True, unique=True, nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<RevokedTokenModel(jti='{self.jti}', user_id='{self.user_id}', revoked_at='{self.revoked_at}')>"

```

## File: concepts.py
```py
# filename: backend/app/models/concepts.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


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
# filename: backend/app/models/disciplines.py

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


class DisciplineModel(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    domains = relationship("DomainModel", secondary="domain_to_discipline_association", back_populates="disciplines")
    subjects = relationship("SubjectModel", secondary="discipline_to_subject_association", back_populates="disciplines")

    def __repr__(self):
        return f"<Discipline(id={self.id}, name='{self.name}')>"

```

## File: domains.py
```py
# filename: backend/app/models/domains.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


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
# filename: backend/app/models/groups.py

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


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
# filename: backend/app/models/leaderboard.py

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


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
# filename: backend/app/models/permissions.py

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base
from backend.app.models.associations import RoleToPermissionAssociation


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
# filename: backend/app/models/question_sets.py

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


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
# filename: backend/app/models/question_tags.py

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


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
# filename: backend/app/models/questions.py

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.core.config import DifficultyLevel
from backend.app.db.base import Base


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
# filename: backend/app/models/roles.py

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base
from backend.app.models.associations import RoleToPermissionAssociation


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
# filename: backend/app/models/subjects.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


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
# filename: backend/app/models/subtopics.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


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
# filename: backend/app/models/time_period.py

from sqlalchemy import Column, Integer, String

from backend.app.db.base import Base
from backend.app.core.config import TimePeriod


class TimePeriodModel(Base):
    __tablename__ = "time_periods"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(20), unique=True, nullable=False)

    @classmethod
    def create(cls, time_period: TimePeriod):
        return cls(id=time_period.value, name=time_period.get_name(time_period.value))

    def __repr__(self):
        return f"<TimePeriodModel(id={self.id}, name='{self.name}')"

```

## File: topics.py
```py
# filename: backend/app/models/topics.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


class TopicModel(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    subjects = relationship("SubjectModel", secondary="subject_to_topic_association", back_populates="topics")
    subtopics = relationship("SubtopicModel", secondary="topic_to_subtopic_association", back_populates="topics")
    questions = relationship("QuestionModel", secondary="question_to_topic_association", back_populates="topics")

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}')>"

```

## File: user_responses.py
```py
# filename: backend/app/models/user_responses.py

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


class UserResponseModel(Base):
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_choice_id = Column(Integer, ForeignKey("answer_choices.id", ondelete="SET NULL"), nullable=False)
    is_correct = Column(Boolean, nullable=True)  # Changed to nullable=True
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
# filename: backend/app/models/users.py

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    token_blacklist_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    role = relationship("RoleModel", back_populates="users")
    responses = relationship("UserResponseModel", back_populates="user", cascade="all, delete-orphan")
    groups = relationship("GroupModel", secondary="user_to_group_association", back_populates="users")
    leaderboards = relationship("LeaderboardModel", back_populates="user", cascade="all, delete-orphan")
    created_groups = relationship("GroupModel", back_populates="creator", cascade="all, delete-orphan")
    created_question_sets = relationship("QuestionSetModel", back_populates="creator", cascade="all, delete-orphan")
    created_questions = relationship("QuestionModel", back_populates="creator")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role_id='{self.role_id}')>"

```

# Directory: /code/quiz-app/backend/app/middleware

## File: __init__.py
```py

```

## File: authorization_middleware.py
```py
# backend/app/middleware/authorization_middleware.py

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError, ExpiredSignatureError

from backend.app.core.config import settings_core
from backend.app.db.session import get_db
from backend.app.models.permissions import PermissionModel
from backend.app.services.authorization_service import has_permission
from backend.app.services.user_service import get_current_user, oauth2_scheme


class AuthorizationMiddleware(BaseHTTPMiddleware):
    method_map = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "DELETE": "delete",
    }

    async def dispatch(self, request: Request, call_next):
        request.state.auth_status = {"is_authorized": True, "error": None}
        request.state.current_user = None

        if request.url.path in settings_core.UNPROTECTED_ENDPOINTS:
            return await call_next(request)

        token = await oauth2_scheme(request)
        if not token:
            request.state.auth_status = {"is_authorized": False, "error": "missing_token"}
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

        try:
            db = next(get_db())
            
            # Check if the token has been invalidated by the BlacklistMiddleware
            if hasattr(request.state, 'auth_status') and not request.state.auth_status["is_authorized"]:
                error = request.state.auth_status.get("error", "Unknown error")
                return JSONResponse(status_code=401, content={"detail": f"Authentication failed: {error}"})
            
            current_user, user_status = await get_current_user(token, db)

            if user_status != "valid":
                request.state.auth_status = {"is_authorized": False, "error": user_status}
                return JSONResponse(status_code=401, content={"detail": f"Authentication failed: {user_status}"})

            request.state.current_user = current_user

            route = request.url.path
            crud_verb = self.method_map.get(request.method)

            if crud_verb:
                required_permission = db.query(PermissionModel).filter(
                    PermissionModel.name == f"{crud_verb}_{route.replace('/', '_')}"
                ).first()

                if required_permission:
                    if not has_permission(db, current_user, required_permission.name):
                        request.state.auth_status = {"is_authorized": False, "error": "insufficient_permissions"}
                        return JSONResponse(status_code=403, content={"detail": "User does not have the required permission"})

            return await call_next(request)
        except Exception as e:
            request.state.auth_status = {"is_authorized": False, "error": "internal_error"}
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})
        finally:
            db.close()

```

## File: blacklist_middleware.py
```py
# filename: backend/app/middleware/blacklist_middleware.py

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from backend.app.core.jwt import decode_access_token
from backend.app.crud.authentication import is_token_revoked
from backend.app.db.session import get_db
from backend.app.services.logging_service import logger
from backend.app.core.config import settings_core

class BlacklistMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug(f"BlacklistMiddleware: Processing request to {request.url.path}")

        # Allow unprotected endpoints to pass through without token validation
        if request.url.path in settings_core.UNPROTECTED_ENDPOINTS:
            logger.debug(f"BlacklistMiddleware: Allowing unprotected endpoint {request.url.path} to pass through")
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if authorization:
            try:
                scheme, token = authorization.split()
                if scheme.lower() != "bearer":
                    logger.warning("BlacklistMiddleware: Invalid authentication scheme")
                    raise HTTPException(status_code=401, detail="Invalid authentication scheme")

                db = next(get_db())
                if is_token_revoked(db, token):
                    logger.warning("BlacklistMiddleware: Token has been revoked")
                    raise HTTPException(status_code=401, detail="Token has been revoked")

                logger.debug("BlacklistMiddleware: Token is valid")
            except HTTPException as e:
                logger.error(f"BlacklistMiddleware: HTTPException - {e.detail}")
                return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
            except Exception as e:
                logger.error(f"BlacklistMiddleware: Unexpected error - {str(e)}")
                return JSONResponse(status_code=401, content={"detail": str(e)})
        else:
            logger.debug("BlacklistMiddleware: No Authorization header present")

        response = await call_next(request)
        return response

```

## File: cors_middleware.py
```py
# filename: backend/app/middleware/cors_middleware.py

from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings_core

def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings_core.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

```

# Directory: /code/quiz-app/backend/app/core

## File: __init__.py
```py

```

## File: config.py
```py
# filename: backend/app/core/config.py

import os
from enum import Enum as PyEnum
from typing import List
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings

import dotenv
import toml

from backend.app.services.logging_service import logger


class DifficultyLevel(str, PyEnum):
    BEGINNER = "Beginner"
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"


class TimePeriod(int, PyEnum):
    DAILY = 1
    WEEKLY = 7
    MONTHLY = 30
    YEARLY = 365

    @classmethod
    def get_name(cls, value):
        return cls(value).name.lower()


class SettingsCore(BaseSettings):
    PROJECT_NAME: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    UNPROTECTED_ENDPOINTS: List[str]
    CORS_ORIGINS: List[str]
    ENVIRONMENT: str
    SENTRY_DSN: str = ""  # Optional, empty string as default

    class Config:
        # Define the path to the .env file relative to the location of config.py
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")
        logger.debug("Looking for .env file at: %s", env_file)


def load_config_from_toml() -> dict:
    # Adjust path to find pyproject.toml in the quiz-app directory
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "pyproject.toml")
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
        # Load SECRET_KEY from .env using the path defined in Config
        env_file = SettingsCore.Config.env_file
        logger.debug(f"Loading SECRET_KEY from .env file at {env_file}")
        env_settings = dotenv.dotenv_values(env_file)
        secret_key = env_settings.get("SECRET_KEY")
        if not secret_key:
            raise ValueError(f"SECRET_KEY not found in .env file at {env_file}")
        logger.debug("SECRET_KEY loaded from .env")
    except Exception as e:
        raise ValueError(f"Error loading .env file at {env_file}: {e}")
    
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
            PROJECT_NAME=toml_config["project_name"],
            SECRET_KEY=secret_key,
            ACCESS_TOKEN_EXPIRE_MINUTES=toml_config["access_token_expire_minutes"],
            DATABASE_URL=database_url,
            UNPROTECTED_ENDPOINTS=toml_config["unprotected_endpoints"],
            CORS_ORIGINS=toml_config["cors_origins"],
            ENVIRONMENT=environment,
            SENTRY_DSN=toml_config.get("sentry_dsn", ""),  # Optional
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

# Add a Pydantic model for JSON serialization
class DifficultyLevelModel(BaseModel):
    difficulty: DifficultyLevel

class TimePeriodModel(BaseModel):
    time_period: TimePeriod

```

## File: jwt.py
```py
# filename: backend/app/core/jwt.py

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, ExpiredSignatureError, jwt

from backend.app.core.config import settings_core
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.db.session import get_db

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings_core.ACCESS_TOKEN_EXPIRE_MINUTES)

    db = next(get_db())
    user = read_user_by_username_from_db(db, to_encode["sub"])
    if not user:
        raise ValueError("User not found")

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),  # Add a unique JWT ID
        "iat": datetime.now(timezone.utc)  # Add issued at time
    })
    encoded_jwt = jwt.encode(to_encode, settings_core.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token,
                             settings_core.SECRET_KEY,
                             algorithms=["HS256"],
                             options={"verify_exp": True})

        db = next(get_db())
        user = read_user_by_username_from_db(db, payload['sub'])
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User not found")

        # Check if the token was issued before the user's current token_blacklist_date
        if user and user.token_blacklist_date:
            token_issued_at = datetime.fromtimestamp(payload['iat'], tz=timezone.utc)
            if token_issued_at < user.token_blacklist_date:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Token has been revoked")

        return payload
    except ExpiredSignatureError:
        # Allow ExpiredSignatureError to propagate
        raise
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Could not validate credentials: {str(e)}") from e
    except HTTPException as e:
        # Re-raise HTTP exceptions (including our custom "Token has been revoked" exception)
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}") from e

```

## File: security.py
```py
# filename: backend/app/core/security.py

from passlib.context import CryptContext
from pydantic import SecretStr

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    result = pwd_context.verify(plain_password, hashed_password)

    return result

def get_password_hash(password):
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    hashed = pwd_context.hash(password)

    return hashed

```

# Directory: /code/quiz-app/backend/tests

## File: conftest.py
```py
# filename: backend/tests/conftest.py

import os
import sys

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import random
import string
from datetime import datetime, timezone

import pytest
import toml
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.jwt import create_access_token
from backend.app.core.security import get_password_hash
from backend.app.crud.crud_answer_choices import create_answer_choice_in_db
from backend.app.crud.crud_concepts import create_concept_in_db
from backend.app.crud.crud_disciplines import create_discipline_in_db
from backend.app.crud.crud_domains import create_domain_in_db
from backend.app.crud.crud_groups import create_group_in_db, read_group_from_db
from backend.app.crud.crud_question_sets import create_question_set_in_db
from backend.app.crud.crud_question_tags import (create_question_tag_in_db,
                                                 delete_question_tag_from_db)
from backend.app.crud.crud_questions import \
    create_question_in_db  # , create_question_with_answers
from backend.app.crud.crud_roles import create_role_in_db, delete_role_from_db
from backend.app.crud.crud_subjects import create_subject_in_db
from backend.app.crud.crud_subtopics import create_subtopic_in_db
from backend.app.crud.crud_topics import create_topic_in_db
from backend.app.crud.crud_user import create_user_in_db, read_user_by_username_from_db
from backend.app.db.base import Base
from backend.app.db.session import get_db, init_db
from backend.app.main import app
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.authentication import RevokedTokenModel
from backend.app.models.concepts import ConceptModel
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.domains import DomainModel
from backend.app.models.groups import GroupModel
from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.permissions import PermissionModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import DifficultyLevel, QuestionModel
from backend.app.models.roles import RoleModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.time_period import TimePeriodModel
from backend.app.models.topics import TopicModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.users import UserModel
from backend.app.schemas.answer_choices import AnswerChoiceCreateSchema
from backend.app.schemas.concepts import ConceptCreateSchema
from backend.app.schemas.disciplines import DisciplineCreateSchema
from backend.app.schemas.domains import DomainCreateSchema
from backend.app.schemas.groups import GroupCreateSchema
from backend.app.schemas.leaderboard import LeaderboardCreateSchema
from backend.app.schemas.permissions import PermissionCreateSchema
from backend.app.schemas.question_sets import QuestionSetCreateSchema
from backend.app.schemas.question_tags import QuestionTagCreateSchema
from backend.app.schemas.questions import (QuestionCreateSchema,
                                           QuestionWithAnswersCreateSchema)
from backend.app.schemas.roles import RoleCreateSchema
from backend.app.schemas.subjects import SubjectCreateSchema
from backend.app.schemas.subtopics import SubtopicCreateSchema
from backend.app.schemas.topics import TopicCreateSchema
from backend.app.schemas.user import UserCreateSchema
from backend.app.schemas.user_responses import UserResponseCreateSchema
from backend.app.services.permission_generator_service import \
    generate_permissions
from backend.app.services.logging_service import logger

# Set the environment to test for pytest
os.environ["ENVIRONMENT"] = "test"

# Load the test database URL from pyproject.toml (now two levels above the current directory)
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pyproject.toml")
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
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    reset_database(SQLALCHEMY_TEST_DATABASE_URL)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        reset_database(SQLALCHEMY_TEST_DATABASE_URL)

@pytest.fixture(scope='function')
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[override_get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope='function')
def test_permission(db_session):
    from backend.app.models.permissions import PermissionModel
    permission = PermissionModel(name="test_permission", description="A test permission")
    db_session.add(permission)
    db_session.commit()
    return permission

@pytest.fixture(scope="function")
def test_model_permissions(db_session):
    from backend.app.main import app  # Import the actual FastAPI app instance
    from backend.app.services.permission_generator_service import (
        ensure_permissions_in_db, generate_permissions)

    # Generate permissions
    permissions = generate_permissions(app)
    
    # Ensure permissions are in the database
    ensure_permissions_in_db(db_session, permissions)

    # Fetch and return the permissions from the database
    db_permissions = db_session.query(PermissionModel).all()
    
    yield db_permissions

    # Clean up (optional, depending on your test isolation needs)
    try:
        for permission in db_permissions:
            db_session.delete(permission)
        db_session.commit()
    except Exception as e:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_model_role(db_session, test_model_permissions):
    try:
        # Create a test role with all permissions
        role = RoleModel(
            name="test_role",
            description="Test Role",
            default=False
        )
        role.permissions.extend(test_model_permissions)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        yield role
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_model_default_role(db_session, test_model_permissions):
    try:
        # Create a test role with all permissions
        role = RoleModel(
            name="test_default_role",
            description="Test Default Role",
            default=True
        )
        role.permissions.extend(test_model_permissions)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        yield role
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_random_username():
    random_username = "test.user_" + "".join(random.choices(string.ascii_letters + string.digits, k=5))
    random_username = random_username.lower()
    yield random_username

@pytest.fixture(scope="function")
def test_model_user(db_session, test_random_username, test_model_role):
    try:
        email = f"{test_random_username}@example.com"
        hashed_password = get_password_hash("TestPassword123!")
        
        user = UserModel(
            username=test_random_username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
            role_id=test_model_role.id
        )
        

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)


        created_user = read_user_by_username_from_db(db_session, user.username)
        if not created_user:
            raise Exception(f"User not found after creation: {created_user.username}")

        yield user
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_model_group(db_session, test_model_user):
    try:
        group = GroupModel(
            name="Test Group",
            description="This is a test group",
            creator_id=test_model_user.id
        )
        db_session.add(group)
        db_session.commit()
        db_session.refresh(group)
        yield group
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_model_user_with_group(db_session, test_model_user, test_model_group):
    try:
        association = UserToGroupAssociation(user_id=test_model_user.id, group_id=test_model_group.id)
        db_session.add(association)
        db_session.commit()
        yield test_model_user
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_model_tag(db_session):
    tag = QuestionTagModel(tag="Test Tag")
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    yield tag

@pytest.fixture(scope='function')
def test_model_question_set(db_session, test_model_user_with_group):
    try:
        question_set = QuestionSetModel(
            name = "Test Question Set",
            is_public= True,
            creator_id = test_model_user_with_group.id
        )
        db_session.add(question_set)
        db_session.commit()
        db_session.refresh(question_set)
        return question_set
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_model_answer_choices(db_session):
    answer_choices = [
        AnswerChoiceModel(text="Answer 1 for Q1", is_correct=True, explanation="Explanation 1 for Q1"),
        AnswerChoiceModel(text="Answer 2 for Q1", is_correct=False, explanation="Explanation 2 for Q1"),
        AnswerChoiceModel(text="Answer 1 for Q2", is_correct=True, explanation="Explanation 1 for Q2"),
        AnswerChoiceModel(text="Answer 2 for Q2", is_correct=False, explanation="Explanation 2 for Q2")
    ]
    
    for answer_choice in answer_choices:
        db_session.add(answer_choice)
    db_session.commit()
    
    yield answer_choices

@pytest.fixture(scope="function")
def test_model_domain(db_session):
    domain = DomainModel(name="Test Domain")
    db_session.add(domain)
    db_session.commit()
    yield domain


@pytest.fixture(scope="function")
def test_model_discipline(db_session, test_model_domain):
    discipline = DisciplineModel(name="Test Discipline")
    discipline.domains.append(test_model_domain)
    db_session.add(discipline)
    db_session.commit()
    yield discipline


@pytest.fixture(scope="function")
def test_model_subject(db_session, test_model_discipline):
    subject = SubjectModel(name="Test Subject")
    subject.disciplines.append(test_model_discipline)
    db_session.add(subject)
    db_session.commit()
    yield subject


@pytest.fixture(scope="function")
def test_model_topic(db_session, test_model_subject):
    topic = TopicModel(name="Test Topic")
    topic.subjects.append(test_model_subject)
    db_session.add(topic)
    db_session.commit()
    yield topic


@pytest.fixture(scope="function")
def test_model_subtopic(db_session, test_model_topic):
    subtopic = SubtopicModel(name="Test Subtopic")
    subtopic.topics.append(test_model_topic)
    db_session.add(subtopic)
    db_session.commit()
    yield subtopic


@pytest.fixture(scope="function")
def test_model_concept(db_session, test_model_subtopic):
    concept = ConceptModel(name="Test Concept")
    concept.subtopics.append(test_model_subtopic)
    db_session.add(concept)
    db_session.commit()
    yield concept

@pytest.fixture(scope="function")
def test_model_questions(db_session, test_model_subject, test_model_topic, test_model_subtopic, test_model_concept, test_model_answer_choices):
    try:
        questions = []
        for i in range(2):
            question = QuestionModel(
                text=f"Test Question {i+1}",
                difficulty="EASY",
                subjects=[test_model_subject],
                topics=[test_model_topic],
                subtopics=[test_model_subtopic],
                concepts=[test_model_concept]
            )
            db_session.add(question)
            db_session.flush()  # Flush to get the question ID

            # Associate answer choices with the question
            question.answer_choices.extend(test_model_answer_choices[i*2:(i+1)*2])
            questions.append(question)

        db_session.commit()
        yield questions
    except Exception as e:
        raise
    finally:
        db_session.rollback()

@pytest.fixture(scope="function")
def test_token(test_model_user):
    try:
        access_token = create_access_token(data={"sub": test_model_user.username})
        yield access_token
    except Exception as e:
        raise

@pytest.fixture(scope="function")
def logged_in_client(client, test_model_user_with_group):
    try:
        login_data = {"username": test_model_user_with_group.username, "password": "TestPassword123!"}
        response = client.post("/login", json=login_data)
        logger.debug(response.json())
        access_token = response.json()["access_token"]
        assert response.status_code == 200, "Authentication failed."
        
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        yield client
    except Exception as e:
        raise

@pytest.fixture(scope="function")
def setup_filter_questions_data(db_session, test_model_user_with_group):
    try:
        # Create Domains
        domain1 = create_domain_in_db(db_session, DomainCreateSchema(name="Science").model_dump())
        domain2 = create_domain_in_db(db_session, DomainCreateSchema(name="Mathematics").model_dump())

        # Create Disciplines
        discipline1 = create_discipline_in_db(db_session, DisciplineCreateSchema(name="Physics", domain_ids=[domain1.id]).model_dump())
        discipline2 = create_discipline_in_db(db_session, DisciplineCreateSchema(name="Pure Mathematics", domain_ids=[domain2.id]).model_dump())

        # Create Subjects
        subject1 = create_subject_in_db(db_session, SubjectCreateSchema(name="Classical Mechanics", discipline_ids=[discipline1.id]).model_dump())
        subject2 = create_subject_in_db(db_session, SubjectCreateSchema(name="Algebra", discipline_ids=[discipline2.id]).model_dump())

        # Create Topics
        topic1 = create_topic_in_db(db_session, TopicCreateSchema(name="Newton's Laws", subject_ids=[subject1.id]).model_dump())
        topic2 = create_topic_in_db(db_session, TopicCreateSchema(name="Linear Algebra", subject_ids=[subject2.id]).model_dump())

        # Create Subtopics
        subtopic1 = create_subtopic_in_db(db_session, SubtopicCreateSchema(name="First Law of Motion", topic_ids=[topic1.id]).model_dump())
        subtopic2 = create_subtopic_in_db(db_session, SubtopicCreateSchema(name="Second Law of Motion", topic_ids=[topic1.id]).model_dump())
        subtopic3 = create_subtopic_in_db(db_session, SubtopicCreateSchema(name="Matrices", topic_ids=[topic2.id]).model_dump())
        subtopic4 = create_subtopic_in_db(db_session, SubtopicCreateSchema(name="Vector Spaces", topic_ids=[topic2.id]).model_dump())

        # Create Concepts
        concept1 = create_concept_in_db(db_session, ConceptCreateSchema(name="Inertia", subtopic_ids=[subtopic1.id]).model_dump())
        concept2 = create_concept_in_db(db_session, ConceptCreateSchema(name="Force and Acceleration", subtopic_ids=[subtopic2.id]).model_dump())
        concept3 = create_concept_in_db(db_session, ConceptCreateSchema(name="Matrix Operations", subtopic_ids=[subtopic3.id]).model_dump())
        concept4 = create_concept_in_db(db_session, ConceptCreateSchema(name="Linear Independence", subtopic_ids=[subtopic4.id]).model_dump())

        # Create Tags
        tag1 = create_question_tag_in_db(db_session, QuestionTagCreateSchema(tag="physics").model_dump())
        tag2 = create_question_tag_in_db(db_session, QuestionTagCreateSchema(tag="mathematics").model_dump())
        tag3 = create_question_tag_in_db(db_session, QuestionTagCreateSchema(tag="mechanics").model_dump())
        tag4 = create_question_tag_in_db(db_session, QuestionTagCreateSchema(tag="linear algebra").model_dump())

        # Create Question Sets
        question_set1 = create_question_set_in_db(db_session,
                                                  QuestionSetCreateSchema(name="Physics Question Set",
                                                                          is_public=True,
                                                                          creator_id=test_model_user_with_group.id).model_dump())
        question_set2 = create_question_set_in_db(db_session,
                                                  QuestionSetCreateSchema(name="Math Question Set",
                                                                          is_public=True,
                                                                          creator_id=test_model_user_with_group.id).model_dump())

        # Create Questions
        question1 = create_question_in_db(db_session, QuestionCreateSchema(
            text="What is Newton's First Law of Motion?",
            subject_ids=[subject1.id],
            topic_ids=[topic1.id],
            subtopic_ids=[subtopic1.id],
            concept_ids=[concept1.id],
            difficulty=DifficultyLevel.EASY,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id]
        ).model_dump())
        question2 = create_question_in_db(db_session, QuestionCreateSchema(
            text="How does force relate to acceleration according to Newton's Second Law?",
            subject_ids=[subject1.id],
            topic_ids=[topic1.id],
            subtopic_ids=[subtopic2.id],
            concept_ids=[concept2.id],
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id]
        ).model_dump())
        question3 = create_question_in_db(db_session, QuestionCreateSchema(
            text="What is the result of multiplying a 2x2 identity matrix with any 2x2 matrix?",
            subject_ids=[subject2.id],
            topic_ids=[topic2.id],
            subtopic_ids=[subtopic3.id],
            concept_ids=[concept3.id],
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id]
        ).model_dump())
        question4 = create_question_in_db(db_session, QuestionCreateSchema(
            text="What does it mean for a set of vectors to be linearly independent?",
            subject_ids=[subject2.id],
            topic_ids=[topic2.id],
            subtopic_ids=[subtopic4.id],
            concept_ids=[concept4.id],
            difficulty=DifficultyLevel.HARD,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id]
        ).model_dump())

    except Exception as e:
        raise e


@pytest.fixture(scope="function")
def filter_test_data(db_session, test_schema_question, test_schema_subject, test_schema_topic, test_schema_subtopic, test_schema_question_tag):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())

    question_data = test_schema_question.model_dump()
    question_data.update({
        "subject_ids": [subject.id],
        "topic_ids": [topic.id],
        "subtopic_ids": [subtopic.id],
        "question_tag_ids": [tag.id],
        "difficulty": DifficultyLevel.MEDIUM
    })
    question = create_question_in_db(db_session, question_data)

    return {
        "subject": subject,
        "topic": topic,
        "subtopic": subtopic,
        "tag": tag,
        "question": question
    }

@pytest.fixture(scope="function")
def test_schema_answer_choice():
    return AnswerChoiceCreateSchema(
        text="test_schema answer choice",
        is_correct=True,
        explanation="This is a test explanation"
    )

@pytest.fixture(scope="function")
def test_schema_domain():
    domain = DomainCreateSchema(name="test_schema Domain")
    yield domain

@pytest.fixture(scope="function")
def test_schema_discipline(test_model_domain):
    discipline = DisciplineCreateSchema(
        name="test_schema Discipline",
        domain_ids=[test_model_domain.id]
    )
    yield discipline

@pytest.fixture(scope="function")
def test_schema_subject(test_model_discipline):
    return SubjectCreateSchema(
        name="test_schema Subject",
        discipline_ids=[test_model_discipline.id]
    )

@pytest.fixture(scope="function")
def test_schema_topic(test_model_subject):
    return TopicCreateSchema(
        name="test_schema Topic",
        subject_ids=[test_model_subject.id]
    )

@pytest.fixture(scope="function")
def test_schema_subtopic(test_model_topic):
    return SubtopicCreateSchema(
        name="test_schema Subtopic",
        topic_ids=[test_model_topic.id]
    )

@pytest.fixture(scope="function")
def test_schema_concept(test_model_subtopic):
    return ConceptCreateSchema(
        name="test_schema Concept",
        subtopic_ids=[test_model_subtopic.id]
    )

@pytest.fixture(scope="function")
def test_schema_question(test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
    question_schema = QuestionCreateSchema(
        text="test_schema question",
        difficulty="Medium",
        subject_ids=[test_model_subject.id],
        topic_ids=[test_model_topic.id],
        subtopic_ids=[test_model_subtopic.id],
        concept_ids=[test_model_concept.id]
    )
    
    yield question_schema

@pytest.fixture(scope="function")
def test_schema_question_with_answers(test_schema_question, test_schema_answer_choice):
    question_with_answers = test_schema_question.model_dump()
    question_with_answers['answer_choices'] = [test_schema_answer_choice]
    question_with_answers_schema = QuestionWithAnswersCreateSchema(**question_with_answers)
    
    yield question_with_answers_schema

@pytest.fixture(scope="function")
def test_schema_question_set(test_model_user):
    return QuestionSetCreateSchema(
        name="test_schema Question Set",
        description="This is a test question set",
        is_public=True,
        creator_id=test_model_user.id
    )

@pytest.fixture(scope="function")
def test_schema_question_tag():
    return QuestionTagCreateSchema(
        tag="test-tag"
    )

@pytest.fixture(scope="function")
def test_schema_user(test_model_role):
    return UserCreateSchema(
        username="testuser",
        email="testuser@example.com",
        password="TestPassword123!",
        role_id=test_model_role.id
    )

@pytest.fixture(scope="function")
def test_schema_group(test_model_user):
    return GroupCreateSchema(
        name="test_schema Group",
        description="This is a test group",
        creator_id=test_model_user.id
    )

@pytest.fixture(scope="function")
def test_schema_role(test_model_permissions):
    role_data = {
        "name": "test_schema Role",
        "description":"This is a test role",
        "permissions": []
    }
    role_data['permissions'].extend(permission.name for permission in test_model_permissions)
    role = RoleCreateSchema(**role_data)

    yield role

@pytest.fixture(scope="function")
def test_schema_permission():
    return PermissionCreateSchema(
        name="test_schema_permission",
        description="This is a test permission"
    )

@pytest.fixture(scope="function")
def test_schema_leaderboard(test_model_user, client):
    return LeaderboardCreateSchema(
        user_id=test_model_user.id,
        score=100,
        time_period_id=1
    )

@pytest.fixture(scope="function")
def test_schema_user_response(test_model_user, test_model_questions, test_model_answer_choices):
    return UserResponseCreateSchema(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True,
        response_time=10,
        timestamp=datetime.now(timezone.utc)
    )

```

# Directory: /code/quiz-app/backend/tests/test_crud

## File: conftest.py
```py
# filename: backend/tests/test_crud/conftest.py

import pytest

from backend.app.core.security import get_password_hash
from backend.app.services.logging_service import logger

@pytest.fixture(scope="function")
def test_user_data(test_schema_user):
    user_data = test_schema_user.model_dump()
    logger.debug("test_user_data: %s", user_data)
    user_data["hashed_password"] = get_password_hash(user_data["password"])
    return user_data

@pytest.fixture(scope="function")
def test_group_data(test_schema_group):
    logger.debug("test_group_data: %s", test_schema_group.model_dump())
    return test_schema_group.model_dump()

@pytest.fixture(scope="function")
def test_role_data(test_schema_role):
    logger.debug("test_role_data: %s", test_schema_role.model_dump())
    return test_schema_role.model_dump()

@pytest.fixture(scope="function")
def test_question_set_data(test_schema_question_set):
    logger.debug("test_question_set_data: %s", test_schema_question_set.model_dump())
    return test_schema_question_set.model_dump()

```

## File: test_crud_answer_choices.py
```py
# filename: backend/tests/crud/test_crud_answer_choices.py

from backend.app.crud.crud_answer_choices import (
    create_answer_choice_in_db, create_question_to_answer_association_in_db,
    delete_answer_choice_from_db,
    delete_question_to_answer_association_from_db, read_answer_choice_from_db,
    read_answer_choices_for_question_from_db, read_answer_choices_from_db,
    read_questions_for_answer_choice_from_db, update_answer_choice_in_db)
from backend.app.crud.crud_questions import create_question_in_db


def test_create_answer_choice(db_session, test_schema_answer_choice):
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    assert answer_choice.text == test_schema_answer_choice.text
    assert answer_choice.is_correct == test_schema_answer_choice.is_correct
    assert answer_choice.explanation == test_schema_answer_choice.explanation

def test_read_answer_choice(db_session, test_schema_answer_choice):
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    read_choice = read_answer_choice_from_db(db_session, answer_choice.id)
    assert read_choice.id == answer_choice.id
    assert read_choice.text == answer_choice.text

def test_read_answer_choices(db_session, test_schema_answer_choice):
    create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    choices = read_answer_choices_from_db(db_session)
    assert len(choices) > 0

def test_update_answer_choice(db_session, test_schema_answer_choice):
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    updated_data = {"text": "Updated text"}
    updated_choice = update_answer_choice_in_db(db_session, answer_choice.id, updated_data)
    assert updated_choice.text == "Updated text"

def test_delete_answer_choice(db_session, test_schema_answer_choice):
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    assert delete_answer_choice_from_db(db_session, answer_choice.id) is True
    assert read_answer_choice_from_db(db_session, answer_choice.id) is None

def test_create_question_to_answer_association(db_session, test_schema_question, test_schema_answer_choice):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    assert create_question_to_answer_association_in_db(db_session, question.id, answer_choice.id) is True

def test_delete_question_to_answer_association(db_session, test_schema_question, test_schema_answer_choice):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    create_question_to_answer_association_in_db(db_session, question.id, answer_choice.id)
    assert delete_question_to_answer_association_from_db(db_session, question.id, answer_choice.id) is True

def test_read_answer_choices_for_question(db_session, test_schema_question, test_schema_answer_choice):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    create_question_to_answer_association_in_db(db_session, question.id, answer_choice.id)
    choices = read_answer_choices_for_question_from_db(db_session, question.id)
    assert len(choices) == 1
    assert choices[0].id == answer_choice.id

def test_read_questions_for_answer_choice(db_session, test_schema_question, test_schema_answer_choice):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    create_question_to_answer_association_in_db(db_session, question.id, answer_choice.id)
    questions = read_questions_for_answer_choice_from_db(db_session, answer_choice.id)
    assert len(questions) == 1
    assert questions[0].id == question.id

```

## File: test_crud_authentication.py
```py
# filename: backend/tests/test_crud/test_crud_authentication.py

from datetime import datetime, timezone, timedelta

import pytest
from fastapi import HTTPException
from jose import ExpiredSignatureError

from backend.app.crud.authentication import (
    create_revoked_token_in_db,
    read_revoked_token_from_db,
    is_token_revoked,
    revoke_all_tokens_for_user,
    revoke_token
)
from backend.app.core.jwt import create_access_token, decode_access_token
from backend.app.models.authentication import RevokedTokenModel
from backend.app.services.logging_service import logger

def test_create_revoked_token_in_db(db_session, test_model_user):
    jti = "test_jti"
    token = "test_token"
    expires_at = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
    
    revoked_token = create_revoked_token_in_db(db_session, jti, token, test_model_user.id, expires_at)
    
    assert revoked_token.jti == jti
    assert revoked_token.token == token
    assert revoked_token.user_id == test_model_user.id
    assert revoked_token.expires_at.replace(tzinfo=timezone.utc) == datetime.fromtimestamp(expires_at, tz=timezone.utc)

def test_read_revoked_token_from_db(db_session, test_model_user):
    jti = "test_jti"
    token = "test_token"
    expires_at = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
    
    create_revoked_token_in_db(db_session, jti, token, test_model_user.id, expires_at)
    
    retrieved_token = read_revoked_token_from_db(db_session, token)
    assert retrieved_token is not None
    assert retrieved_token.token == token

def test_is_token_revoked(db_session, test_model_user):
    access_token = create_access_token({"sub": test_model_user.username})
    
    # Token should not be revoked initially
    assert not is_token_revoked(db_session, access_token)
    
    # Revoke the token
    revoke_token(db_session, access_token)
    
    # Token should now be revoked
    assert is_token_revoked(db_session, access_token)

def test_revoke_all_tokens_for_user(db_session, test_model_user):
    # Create some active tokens for the user
    token1 = create_access_token({"sub": test_model_user.username})
    token2 = create_access_token({"sub": test_model_user.username})
    
    active_tokens = [token1, token2]
    
    # Revoke all tokens for the user
    revoke_all_tokens_for_user(db_session, test_model_user.id, active_tokens)
    
    # Check if all tokens are revoked
    assert is_token_revoked(db_session, token1)
    assert is_token_revoked(db_session, token2)

def test_revoke_token(db_session, test_model_user):
    access_token = create_access_token({"sub": test_model_user.username})
    
    # Token should not be revoked initially
    assert not is_token_revoked(db_session, access_token)
    
    # Revoke the token
    revoke_token(db_session, access_token)
    
    # Token should now be revoked
    assert is_token_revoked(db_session, access_token)

def test_revoke_token_twice(db_session, test_model_user):
    access_token = create_access_token({"sub": test_model_user.username})
    
    # Revoke the token
    revoke_token(db_session, access_token)
    
    # Attempt to revoke the same token again (should not raise an error)
    revoke_token(db_session, access_token)
    
    # Token should still be revoked
    assert is_token_revoked(db_session, access_token)

def test_revoke_expired_token(db_session, test_model_user):
    # Create an expired token
    expired_token = create_access_token({"sub": test_model_user.username}, expires_delta=timedelta(seconds=-1))
    
    # Attempt to revoke the expired token (should not raise an error)
    revoke_token(db_session, expired_token)
    
    # The token should be considered revoked (due to expiration)
    assert is_token_revoked(db_session, expired_token)

def test_create_token_with_nonexistent_user(db_session):
    with pytest.raises(ValueError):
        create_access_token({"sub": "nonexistent_user"})

def test_is_token_revoked_with_invalid_token(db_session):
    # Create an invalid token
    invalid_token = "invalid.token.format"
    
    # The invalid token should fail the check
    with pytest.raises(HTTPException) as exc_info:
        is_token_revoked(db_session, invalid_token)
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail

def test_revoke_all_tokens_for_user_with_no_active_tokens(db_session, test_model_user):
    # Attempt to revoke all tokens when there are no active tokens
    revoke_all_tokens_for_user(db_session, test_model_user.id, [])
    
    # No error should be raised, and no new tokens should be in the revoked_tokens table
    assert db_session.query(RevokedTokenModel).filter_by(user_id=test_model_user.id).count() == 0

def test_is_token_revoked_with_old_token(db_session, test_model_user):
    # Create a token with expiration date in the past
    old_token = create_access_token({"sub": test_model_user.username}, expires_delta=timedelta(days=-7))
    with pytest.raises(ExpiredSignatureError) as exc_info:
        decode_access_token(old_token)
    assert "Signature has expired" in str(exc_info.value)

    # The old token should be considered revoked
    is_old_token_revoked = is_token_revoked(db_session, old_token)
    logger.debug("is_old_token_revoked: %s", is_old_token_revoked)
    assert is_old_token_revoked is True

    # Create a new token
    new_token = create_access_token({"sub": test_model_user.username})

    # The new token should not be revoked
    assert not is_token_revoked(db_session, new_token)

```

## File: test_crud_concepts.py
```py
# filename: backend/tests/crud/test_crud_concepts.py

from backend.app.crud.crud_concepts import (
    create_concept_in_db, create_question_to_concept_association_in_db,
    create_subtopic_to_concept_association_in_db, delete_concept_from_db,
    delete_question_to_concept_association_from_db,
    delete_subtopic_to_concept_association_from_db,
    read_concept_by_name_from_db, read_concept_from_db, read_concepts_from_db,
    read_questions_for_concept_from_db, read_subtopics_for_concept_from_db,
    update_concept_in_db)
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subtopics import create_subtopic_in_db


def test_create_concept(db_session, test_schema_concept):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    assert concept.name == test_schema_concept.name

def test_read_concept(db_session, test_schema_concept):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    read_concept = read_concept_from_db(db_session, concept.id)
    assert read_concept.id == concept.id
    assert read_concept.name == concept.name

def test_read_concept_by_name(db_session, test_schema_concept):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    read_concept = read_concept_by_name_from_db(db_session, concept.name)
    assert read_concept.id == concept.id
    assert read_concept.name == concept.name

def test_read_concepts(db_session, test_schema_concept):
    create_concept_in_db(db_session, test_schema_concept.model_dump())
    concepts = read_concepts_from_db(db_session)
    assert len(concepts) > 0

def test_update_concept(db_session, test_schema_concept):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    updated_data = {"name": "Updated Concept"}
    updated_concept = update_concept_in_db(db_session, concept.id, updated_data)
    assert updated_concept.name == "Updated Concept"

def test_delete_concept(db_session, test_schema_concept):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    assert delete_concept_from_db(db_session, concept.id) is True
    assert read_concept_from_db(db_session, concept.id) is None

def test_create_subtopic_to_concept_association(db_session, test_schema_concept, test_schema_subtopic):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    assert create_subtopic_to_concept_association_in_db(db_session, subtopic.id, concept.id) is True

def test_delete_subtopic_to_concept_association(db_session, test_schema_concept, test_schema_subtopic):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    create_subtopic_to_concept_association_in_db(db_session, subtopic.id, concept.id)
    assert delete_subtopic_to_concept_association_from_db(db_session, subtopic.id, concept.id) is True

def test_create_question_to_concept_association(db_session, test_schema_concept, test_schema_question):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_to_concept_association_in_db(db_session, question.id, concept.id) is True

def test_delete_question_to_concept_association(db_session, test_schema_concept, test_schema_question):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_concept_association_in_db(db_session, question.id, concept.id)
    assert delete_question_to_concept_association_from_db(db_session, question.id, concept.id) is True

def test_read_subtopics_for_concept(db_session, test_schema_concept, test_schema_subtopic):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    created_subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    create_subtopic_to_concept_association_in_db(db_session, created_subtopic.id, concept.id)
    subtopics = read_subtopics_for_concept_from_db(db_session, concept.id)
    assert len(subtopics) == 2
    assert created_subtopic.id in [subtopic.id for subtopic in subtopics]

def test_read_questions_for_concept(db_session, test_schema_concept, test_schema_question):
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_concept_association_in_db(db_session, question.id, concept.id)
    questions = read_questions_for_concept_from_db(db_session, concept.id)
    assert len(questions) == 1
    assert questions[0].id == question.id

```

## File: test_crud_disciplines.py
```py
# filename: backend/tests/crud/test_crud_disciplines.py

import pytest

from backend.app.crud.crud_disciplines import (
    create_discipline_in_db, create_discipline_to_subject_association_in_db,
    create_domain_to_discipline_association_in_db, delete_discipline_from_db,
    delete_discipline_to_subject_association_from_db,
    delete_domain_to_discipline_association_from_db,
    read_discipline_by_name_from_db, read_discipline_from_db,
    read_disciplines_from_db, read_domains_for_discipline_from_db,
    read_subjects_for_discipline_from_db, update_discipline_in_db)
from backend.app.crud.crud_domains import create_domain_in_db
from backend.app.crud.crud_subjects import create_subject_in_db


def test_create_discipline(db_session, test_schema_discipline):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    assert discipline.name == test_schema_discipline.name

def test_read_discipline(db_session, test_schema_discipline):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    read_discipline = read_discipline_from_db(db_session, discipline.id)
    assert read_discipline.id == discipline.id
    assert read_discipline.name == discipline.name

def test_read_discipline_by_name(db_session, test_schema_discipline):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    read_discipline = read_discipline_by_name_from_db(db_session, discipline.name)
    assert read_discipline.id == discipline.id
    assert read_discipline.name == discipline.name

def test_read_disciplines(db_session, test_schema_discipline):
    create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    disciplines = read_disciplines_from_db(db_session)
    assert len(disciplines) > 0

def test_update_discipline(db_session, test_schema_discipline):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    updated_data = {"name": "Updated Discipline"}
    updated_discipline = update_discipline_in_db(db_session, discipline.id, updated_data)
    assert updated_discipline.name == "Updated Discipline"

def test_delete_discipline(db_session, test_schema_discipline):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    assert delete_discipline_from_db(db_session, discipline.id) is True
    assert read_discipline_from_db(db_session, discipline.id) is None

def test_create_domain_to_discipline_association(db_session, test_schema_discipline, test_schema_domain):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    assert create_domain_to_discipline_association_in_db(db_session, domain.id, discipline.id) is True

def test_delete_domain_to_discipline_association(db_session, test_schema_discipline, test_schema_domain):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    create_domain_to_discipline_association_in_db(db_session, domain.id, discipline.id)
    assert delete_domain_to_discipline_association_from_db(db_session, domain.id, discipline.id) is True

def test_create_discipline_to_subject_association(db_session, test_schema_discipline, test_schema_subject):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    assert create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id) is True

def test_delete_discipline_to_subject_association(db_session, test_schema_discipline, test_schema_subject):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id)
    assert delete_discipline_to_subject_association_from_db(db_session, discipline.id, subject.id) is True

def test_read_domains_for_discipline(db_session, test_schema_discipline, test_schema_domain):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    created_domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    create_domain_to_discipline_association_in_db(db_session, created_domain.id, discipline.id)
    domains = read_domains_for_discipline_from_db(db_session, discipline.id)
    assert len(domains) == 2
    assert created_domain.id in [domain.id for domain in domains]

def test_read_subjects_for_discipline(db_session, test_schema_discipline, test_schema_subject):
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id)
    subjects = read_subjects_for_discipline_from_db(db_session, discipline.id)
    assert len(subjects) == 1
    assert subjects[0].id == subject.id

```

## File: test_crud_domains.py
```py
# filename: backend/tests/crud/test_crud_domains.py

import pytest

from backend.app.crud.crud_disciplines import create_discipline_in_db
from backend.app.crud.crud_domains import (
    create_domain_in_db, create_domain_to_discipline_association_in_db,
    delete_domain_from_db, delete_domain_to_discipline_association_from_db,
    read_disciplines_for_domain_from_db, read_domain_by_name_from_db,
    read_domain_from_db, read_domains_from_db, update_domain_in_db)


def test_create_domain(db_session, test_schema_domain):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    assert domain.name == test_schema_domain.name

def test_read_domain(db_session, test_schema_domain):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    read_domain = read_domain_from_db(db_session, domain.id)
    assert read_domain.id == domain.id
    assert read_domain.name == domain.name

def test_read_domain_by_name(db_session, test_schema_domain):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    read_domain = read_domain_by_name_from_db(db_session, domain.name)
    assert read_domain.id == domain.id
    assert read_domain.name == domain.name

def test_read_domains(db_session, test_schema_domain):
    create_domain_in_db(db_session, test_schema_domain.model_dump())
    domains = read_domains_from_db(db_session)
    assert len(domains) > 0

def test_update_domain(db_session, test_schema_domain):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    updated_data = {"name": "Updated Domain"}
    updated_domain = update_domain_in_db(db_session, domain.id, updated_data)
    assert updated_domain.name == "Updated Domain"

def test_delete_domain(db_session, test_schema_domain):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    assert delete_domain_from_db(db_session, domain.id) is True
    assert read_domain_from_db(db_session, domain.id) is None

def test_create_domain_to_discipline_association(db_session, test_schema_domain, test_schema_discipline):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    assert create_domain_to_discipline_association_in_db(db_session, domain.id, discipline.id) is True

def test_delete_domain_to_discipline_association(db_session, test_schema_domain, test_schema_discipline):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    create_domain_to_discipline_association_in_db(db_session, domain.id, discipline.id)
    assert delete_domain_to_discipline_association_from_db(db_session, domain.id, discipline.id) is True

def test_read_disciplines_for_domain(db_session, test_schema_domain, test_schema_discipline):
    domain = create_domain_in_db(db_session, test_schema_domain.model_dump())
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    create_domain_to_discipline_association_in_db(db_session, domain.id, discipline.id)
    disciplines = read_disciplines_for_domain_from_db(db_session, domain.id)
    assert len(disciplines) == 1
    assert disciplines[0].id == discipline.id

```

## File: test_crud_filters.py
```py
# filename: backend/tests/test_crud/test_crud_filters.py

import pytest
from backend.app.crud.crud_filters import read_filtered_questions_from_db
from backend.app.models.questions import DifficultyLevel
from backend.app.crud.crud_question_tags import create_question_tag_in_db, create_question_to_tag_association_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subjects import create_question_to_subject_association_in_db
from backend.app.services.logging_service import logger

def test_read_filtered_questions_no_filter(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_by_subject(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"subject": filter_test_data["subject"].name})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_by_topic(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"topic": filter_test_data["topic"].name})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_by_subtopic(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"subtopic": filter_test_data["subtopic"].name})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_by_difficulty(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"difficulty": DifficultyLevel.MEDIUM.value})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_by_tag(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"question_tags": [filter_test_data["tag"].tag]})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_multiple_filters(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {
        "subject": filter_test_data["subject"].name,
        "topic": filter_test_data["topic"].name,
        "subtopic": filter_test_data["subtopic"].name,
        "difficulty": DifficultyLevel.MEDIUM.value,
        "question_tags": [filter_test_data["tag"].tag]
    })
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_non_matching_filter(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"subject": "Non-existent Subject"})
    assert len(results) == 0



def test_read_filtered_questions_case_insensitive(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"subject": filter_test_data["subject"].name.upper()})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_partial_tag_match(db_session, filter_test_data):
    partial_tag = filter_test_data["tag"].tag[:3]  # Take first 3 characters of the tag
    results = read_filtered_questions_from_db(db_session, {"question_tags": [partial_tag]})
    assert len(results) == 0

def test_read_filtered_questions_multiple_tags(db_session, filter_test_data, test_schema_question_tag):
    # Create a new tag and associate it with the existing question
    new_tag_data = {"tag": "New Tag"}
    new_tag = create_question_tag_in_db(db_session, new_tag_data)
    logger.debug("New tag: %s", new_tag)
    assert new_tag.id is not None
    assert new_tag.tag == new_tag_data["tag"]
    create_question_to_tag_association_in_db(db_session, filter_test_data["question"].id, new_tag.id)

    results = read_filtered_questions_from_db(db_session, {"question_tags": [filter_test_data["tag"].tag, new_tag.tag]})
    logger.debug("Results: %s", results)
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

def test_read_filtered_questions_pagination(db_session, filter_test_data, test_schema_question):
    # Create additional questions
    for i in range(5):
        new_question_data = test_schema_question.model_dump()
        new_question_data['text'] = f"Additional Question {i}"
        new_question = create_question_in_db(db_session, new_question_data)
        create_question_to_subject_association_in_db(db_session, new_question.id, filter_test_data["subject"].id)

    # Test pagination
    results_page1 = read_filtered_questions_from_db(db_session, {"subject": filter_test_data["subject"].name}, skip=0, limit=3)
    results_page2 = read_filtered_questions_from_db(db_session, {"subject": filter_test_data["subject"].name}, skip=3, limit=3)

    assert len(results_page1) == 3
    assert len(results_page2) == 3
    assert set(q.id for q in results_page1).isdisjoint(set(q.id for q in results_page2))

def test_read_filtered_questions_no_results(db_session):
    results = read_filtered_questions_from_db(db_session, {
        "subject": "Non-existent Subject",
        "topic": "Non-existent Topic",
        "subtopic": "Non-existent Subtopic",
        "difficulty": DifficultyLevel.EXPERT.value,
        "question_tags": ["non-existent-tag"]
    })
    assert len(results) == 0

def test_read_filtered_questions_empty_tag_list(db_session, filter_test_data):
    results = read_filtered_questions_from_db(db_session, {"question_tags": []})
    assert len(results) == 1
    assert results[0].id == filter_test_data["question"].id

```

## File: test_crud_groups.py
```py
# filename: backend/tests/crud/test_crud_groups.py

import pytest

from backend.app.crud.crud_groups import (
    create_group_in_db, create_question_set_to_group_association_in_db,
    create_user_to_group_association_in_db, delete_group_from_db,
    delete_question_set_to_group_association_from_db,
    delete_user_to_group_association_from_db, read_group_from_db,
    read_groups_from_db, read_question_sets_for_group_from_db,
    read_users_for_group_from_db, update_group_in_db)
from backend.app.crud.crud_question_sets import create_question_set_in_db
from backend.app.crud.crud_user import create_user_in_db


def test_create_group(db_session, test_group_data):
    group = create_group_in_db(db_session, test_group_data)
    assert group.name == test_group_data["name"]
    assert group.description == test_group_data["description"]
    assert group.creator_id == test_group_data["creator_id"]

def test_read_group(db_session, test_group_data):
    group = create_group_in_db(db_session, test_group_data)
    read_group = read_group_from_db(db_session, group.id)
    assert read_group.id == group.id
    assert read_group.name == group.name

def test_read_groups(db_session, test_group_data):
    create_group_in_db(db_session, test_group_data)
    groups = read_groups_from_db(db_session)
    assert len(groups) > 0

def test_update_group(db_session, test_group_data):
    group = create_group_in_db(db_session, test_group_data)
    updated_data = {"name": "Updated Group", "description": "Updated description"}
    updated_group = update_group_in_db(db_session, group.id, updated_data)
    assert updated_group.name == "Updated Group"
    assert updated_group.description == "Updated description"

def test_delete_group(db_session, test_group_data):
    group = create_group_in_db(db_session, test_group_data)
    assert delete_group_from_db(db_session, group.id) is True
    assert read_group_from_db(db_session, group.id) is None

def test_create_user_to_group_association(db_session, test_group_data, test_user_data):
    group = create_group_in_db(db_session, test_group_data)
    user = create_user_in_db(db_session, test_user_data)
    assert create_user_to_group_association_in_db(db_session, user.id, group.id) is True

def test_delete_user_to_group_association(db_session, test_group_data, test_user_data):
    group = create_group_in_db(db_session, test_group_data)
    user = create_user_in_db(db_session, test_user_data)
    create_user_to_group_association_in_db(db_session, user.id, group.id)
    assert delete_user_to_group_association_from_db(db_session, user.id, group.id) is True

def test_create_question_set_to_group_association(db_session, test_group_data, test_schema_question_set):
    group = create_group_in_db(db_session, test_group_data)
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    assert create_question_set_to_group_association_in_db(db_session, question_set.id, group.id) is True

def test_delete_question_set_to_group_association(db_session, test_group_data, test_schema_question_set):
    group = create_group_in_db(db_session, test_group_data)
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    create_question_set_to_group_association_in_db(db_session, question_set.id, group.id)
    assert delete_question_set_to_group_association_from_db(db_session, question_set.id, group.id) is True

def test_read_users_for_group(db_session, test_group_data, test_user_data):
    group = create_group_in_db(db_session, test_group_data)
    user = create_user_in_db(db_session, test_user_data)
    create_user_to_group_association_in_db(db_session, user.id, group.id)
    users = read_users_for_group_from_db(db_session, group.id)
    assert len(users) == 1
    assert users[0].id == user.id

def test_read_question_sets_for_group(db_session, test_group_data, test_schema_question_set):
    group = create_group_in_db(db_session, test_group_data)
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    create_question_set_to_group_association_in_db(db_session, question_set.id, group.id)
    question_sets = read_question_sets_for_group_from_db(db_session, group.id)
    assert len(question_sets) == 1
    assert question_sets[0].id == question_set.id

```

## File: test_crud_leaderboard.py
```py
# filename: backend/tests/test_crud/test_crud_leaderboard.py

from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.app.crud.crud_groups import create_group_in_db
from backend.app.crud.crud_leaderboard import (
    create_leaderboard_entry_in_db,
    delete_leaderboard_entry_from_db,
    read_leaderboard_entries_for_group_from_db,
    read_leaderboard_entries_for_user_from_db,
    read_leaderboard_entries_from_db,
    read_leaderboard_entry_from_db,
    read_or_create_time_period_in_db,
    update_leaderboard_entry_in_db
)
from backend.app.crud.crud_user import create_user_in_db
from backend.app.core.config import TimePeriod
from backend.app.services.logging_service import logger

def test_create_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    assert entry.user_id == test_schema_leaderboard.user_id
    assert entry.score == test_schema_leaderboard.score
    assert entry.time_period_id == test_schema_leaderboard.time_period_id

def test_read_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    read_entry = read_leaderboard_entry_from_db(db_session, entry.id)
    assert read_entry.id == entry.id
    assert read_entry.user_id == entry.user_id
    assert read_entry.score == entry.score

def test_read_leaderboard_entries(db_session, test_schema_leaderboard):
    create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    entries = read_leaderboard_entries_from_db(db_session, test_schema_leaderboard.time_period_id)
    assert len(entries) > 0

def test_update_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    updated_data = {"score": 200}
    updated_entry = update_leaderboard_entry_in_db(db_session, entry.id, updated_data)
    assert updated_entry.score == 200

def test_delete_leaderboard_entry(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    assert delete_leaderboard_entry_from_db(db_session, entry.id) is True
    assert read_leaderboard_entry_from_db(db_session, entry.id) is None

def test_read_or_create_time_period(db_session):
    time_period = read_or_create_time_period_in_db(db_session, time_period_id=1)
    assert time_period.id == 1
    assert time_period.name == "daily"

def test_read_leaderboard_entries_for_user(db_session, test_schema_leaderboard, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    leaderboard_data = test_schema_leaderboard.model_dump()
    leaderboard_data["user_id"] = user.id
    create_leaderboard_entry_in_db(db_session, leaderboard_data)
    entries = read_leaderboard_entries_for_user_from_db(db_session, user.id)
    assert len(entries) == 1
    assert entries[0].user_id == user.id

def test_read_leaderboard_entries_for_group(db_session, test_schema_leaderboard, test_schema_group):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    leaderboard_data = test_schema_leaderboard.model_dump()
    leaderboard_data["group_id"] = group.id
    create_leaderboard_entry_in_db(db_session, leaderboard_data)
    entries = read_leaderboard_entries_for_group_from_db(db_session, group.id)
    assert len(entries) == 1
    assert entries[0].group_id == group.id

def test_create_leaderboard_entry_with_invalid_time_period(db_session, test_schema_leaderboard):
    invalid_data = test_schema_leaderboard.model_dump()
    invalid_data['time_period_id'] = 9999  # Invalid time period ID
    with pytest.raises(ValueError):
        create_leaderboard_entry_in_db(db_session, invalid_data)

def test_read_leaderboard_entries_with_filters(db_session, test_schema_leaderboard, test_user_data, test_group_data):
    user = create_user_in_db(db_session, test_user_data)
    group = create_group_in_db(db_session, test_group_data)
    
    leaderboard_data = test_schema_leaderboard.model_dump()
    leaderboard_data['user_id'] = user.id
    leaderboard_data['group_id'] = group.id
    
    time_period_id = leaderboard_data['time_period_id']
    
    created_leaderboard_entry = create_leaderboard_entry_in_db(db_session, leaderboard_data)
    
    entries = read_leaderboard_entries_from_db(db_session, time_period_id=time_period_id, group_id=group.id, user_id=user.id)
    assert len(entries) == 1
    assert entries[0].user_id == user.id
    assert entries[0].group_id == group.id

def test_update_nonexistent_leaderboard_entry(db_session):
    non_existent_id = 9999
    updated_data = {"score": 200}
    result = update_leaderboard_entry_in_db(db_session, non_existent_id, updated_data)
    assert result is None

def test_delete_nonexistent_leaderboard_entry(db_session):
    non_existent_id = 9999
    result = delete_leaderboard_entry_from_db(db_session, non_existent_id)
    assert result is False

@pytest.mark.parametrize("time_period_id", [tp.value for tp in TimePeriod])
def test_read_or_create_all_time_periods(db_session, time_period_id):
    time_period = read_or_create_time_period_in_db(db_session, time_period_id)
    assert time_period.id == time_period_id
    assert time_period.name == TimePeriod(time_period_id).name.lower()

def test_read_leaderboard_entries_empty_result(db_session):
    entries = read_leaderboard_entries_from_db(db_session, time_period_id=1, group_id=9999, user_id=9999)
    assert len(entries) == 0

# Note: The following test assumes that SQLAlchemyError can be triggered by passing invalid data.
# You might need to adjust this based on your actual database constraints.
def test_create_leaderboard_entry_sql_error(db_session, test_schema_leaderboard):
    invalid_data = test_schema_leaderboard.model_dump()
    invalid_data['user_id'] = None  # Assuming user_id is non-nullable
    with pytest.raises(SQLAlchemyError):
        create_leaderboard_entry_in_db(db_session, invalid_data)



def test_create_multiple_leaderboard_entries(db_session, test_schema_leaderboard, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    leaderboard_data = test_schema_leaderboard.model_dump()
    leaderboard_data["user_id"] = user.id

    # Create entries for different time periods
    for time_period in TimePeriod:
        leaderboard_data["time_period_id"] = time_period.value
        create_leaderboard_entry_in_db(db_session, leaderboard_data)

    entries = read_leaderboard_entries_for_user_from_db(db_session, user.id)
    assert len(entries) == len(TimePeriod)

def test_update_leaderboard_entry_score(db_session, test_schema_leaderboard):
    entry = create_leaderboard_entry_in_db(db_session, test_schema_leaderboard.model_dump())
    new_score = entry.score + 100
    updated_entry = update_leaderboard_entry_in_db(db_session, entry.id, {"score": new_score})
    assert updated_entry.score == new_score

def test_read_leaderboard_entries_ordering(db_session, test_schema_leaderboard, test_user_data):
    user1 = create_user_in_db(db_session, test_user_data)
    user2 = create_user_in_db(db_session, {**test_user_data, "username": "testuser2", "email": "testuser2@example.com"})

    leaderboard_data1 = test_schema_leaderboard.model_dump()
    leaderboard_data1["user_id"] = user1.id
    leaderboard_data1["score"] = 100

    leaderboard_data2 = test_schema_leaderboard.model_dump()
    leaderboard_data2["user_id"] = user2.id
    leaderboard_data2["score"] = 200

    create_leaderboard_entry_in_db(db_session, leaderboard_data1)
    create_leaderboard_entry_in_db(db_session, leaderboard_data2)

    entries = read_leaderboard_entries_from_db(db_session, time_period_id=test_schema_leaderboard.time_period_id)
    assert len(entries) == 2
    assert entries[0].score > entries[1].score

def test_read_leaderboard_entries_with_limit(db_session, test_schema_leaderboard, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    leaderboard_data = test_schema_leaderboard.model_dump()
    logger.debug("test_user_data: %s", test_user_data)
    leaderboard_data["user_id"] = user.id
    logger.debug("leaderboard_data: %s", leaderboard_data)

    for i in range(5):
        leaderboard_data["score"] = i * 100
        leaderboard_data["time_period_id"] = test_schema_leaderboard.time_period_id
        logger.debug("leaderboard_data for i=%s: %s", i, leaderboard_data)
        create_leaderboard_entry_in_db(db_session, leaderboard_data)

    entries_without_limit = read_leaderboard_entries_from_db(db_session, time_period_id=test_schema_leaderboard.time_period_id)
    assert len(entries_without_limit) == 5

    entries_with_limit = read_leaderboard_entries_from_db(db_session, time_period_id=test_schema_leaderboard.time_period_id, limit=3)
    assert len(entries_with_limit) == 3

def test_read_leaderboard_entries_for_nonexistent_group(db_session):
    entries = read_leaderboard_entries_for_group_from_db(db_session, group_id=9999)
    assert len(entries) == 0

def test_read_leaderboard_entries_for_nonexistent_user(db_session):
    entries = read_leaderboard_entries_for_user_from_db(db_session, user_id=9999)
    assert len(entries) == 0

```

## File: test_crud_permissions.py
```py
# filename: backend/tests/test_crud/test_crud_permissions.py

import pytest

from backend.app.crud.crud_permissions import (
    create_permission_in_db,
    create_role_to_permission_association_in_db,
    delete_permission_from_db,
    delete_role_to_permission_association_from_db,
    read_permission_by_name_from_db,
    read_permission_from_db,
    read_permissions_from_db,
    read_roles_for_permission_from_db,
    update_permission_in_db
)
from backend.app.crud.crud_roles import create_role_in_db


def test_create_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    assert permission.name == test_schema_permission.name
    assert permission.description == test_schema_permission.description

def test_read_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    read_permission = read_permission_from_db(db_session, permission.id)
    assert read_permission.id == permission.id
    assert read_permission.name == permission.name

def test_read_permission_by_name(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    read_permission = read_permission_by_name_from_db(db_session, permission.name)
    assert read_permission.id == permission.id
    assert read_permission.name == permission.name

def test_read_permissions(db_session, test_schema_permission):
    create_permission_in_db(db_session, test_schema_permission.model_dump())
    permissions = read_permissions_from_db(db_session)
    assert len(permissions) > 0

def test_update_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    updated_data = {"description": "Updated description"}
    updated_permission = update_permission_in_db(db_session, permission.id, updated_data)
    assert updated_permission.description == "Updated description"

def test_delete_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    assert delete_permission_from_db(db_session, permission.id) is True
    assert read_permission_from_db(db_session, permission.id) is None

def test_create_role_to_permission_association(db_session, test_schema_permission, test_schema_role):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    assert create_role_to_permission_association_in_db(db_session, role.id, permission.id) is True

def test_delete_role_to_permission_association(db_session, test_schema_permission, test_schema_role):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    assert delete_role_to_permission_association_from_db(db_session, role.id, permission.id) is True

def test_read_roles_for_permission(db_session, test_schema_permission, test_schema_role):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    roles = read_roles_for_permission_from_db(db_session, permission.id)
    assert len(roles) == 1
    assert roles[0].id == role.id



def test_create_duplicate_permission(db_session, test_schema_permission):
    create_permission_in_db(db_session, test_schema_permission.model_dump())
    with pytest.raises(Exception):  # Adjust the exception type if needed
        create_permission_in_db(db_session, test_schema_permission.model_dump())

def test_read_nonexistent_permission(db_session):
    nonexistent_id = 9999
    assert read_permission_from_db(db_session, nonexistent_id) is None

def test_read_nonexistent_permission_by_name(db_session):
    nonexistent_name = "nonexistent_permission"
    assert read_permission_by_name_from_db(db_session, nonexistent_name) is None

def test_update_nonexistent_permission(db_session):
    nonexistent_id = 9999
    updated_data = {"description": "Updated description"}
    assert update_permission_in_db(db_session, nonexistent_id, updated_data) is None

def test_delete_nonexistent_permission(db_session):
    nonexistent_id = 9999
    assert delete_permission_from_db(db_session, nonexistent_id) is False

def test_create_multiple_permissions(db_session, test_schema_permission):
    permission1 = create_permission_in_db(db_session, test_schema_permission.model_dump())
    permission2 = create_permission_in_db(db_session, {**test_schema_permission.model_dump(), "name": "another_permission"})
    permissions = read_permissions_from_db(db_session)
    assert len(permissions) == 2
    assert {p.id for p in permissions} == {permission1.id, permission2.id}

def test_update_permission_name(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    new_name = "updated_permission_name"
    updated_permission = update_permission_in_db(db_session, permission.id, {"name": new_name})
    assert updated_permission.name == new_name
    assert read_permission_by_name_from_db(db_session, new_name) is not None

def test_delete_permission_cascade(db_session, test_schema_permission, test_schema_role):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    
    delete_permission_from_db(db_session, permission.id)
    
    assert read_permission_from_db(db_session, permission.id) is None
    assert read_roles_for_permission_from_db(db_session, permission.id) == []

def test_read_permissions_pagination(db_session, test_schema_permission):
    for i in range(5):
        create_permission_in_db(db_session, {**test_schema_permission.model_dump(), "name": f"permission_{i}"})
    
    permissions_page1 = read_permissions_from_db(db_session, skip=0, limit=2)
    permissions_page2 = read_permissions_from_db(db_session, skip=2, limit=2)
    
    assert len(permissions_page1) == 2
    assert len(permissions_page2) == 2
    assert permissions_page1[0].id != permissions_page2[0].id

def test_create_role_to_permission_association_idempotent(db_session, test_schema_permission, test_schema_role):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    
    first_association = create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    assert first_association is True
    second_association = create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    assert second_association is False
    
    roles = read_roles_for_permission_from_db(db_session, permission.id)
    assert len(roles) == 1

```

## File: test_crud_question_sets.py
```py
# filename: backend/tests/test_crud/test_crud_question_sets.py

import pytest

from backend.app.crud.crud_groups import create_group_in_db
from backend.app.crud.crud_question_sets import (
    create_question_set_in_db,
    create_question_set_to_group_association_in_db,
    create_question_set_to_question_association_in_db,
    delete_question_set_from_db,
    delete_question_set_to_group_association_from_db,
    delete_question_set_to_question_association_from_db,
    read_groups_for_question_set_from_db,
    read_question_set_from_db,
    read_question_sets_from_db,
    read_questions_for_question_set_from_db,
    update_question_set_in_db
)
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.services.logging_service import logger


def test_create_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    assert question_set.name == test_schema_question_set.name
    assert question_set.description == test_schema_question_set.description
    assert question_set.is_public == test_schema_question_set.is_public

def test_read_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    read_set = read_question_set_from_db(db_session, question_set.id)
    assert read_set.id == question_set.id
    assert read_set.name == question_set.name

def test_read_question_sets(db_session, test_schema_question_set):
    create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question_sets = read_question_sets_from_db(db_session)
    assert len(question_sets) > 0

def test_update_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    updated_data = {"name": "Updated Question Set", "description": "Updated description"}
    updated_set = update_question_set_in_db(db_session, question_set.id, updated_data)
    assert updated_set.name == "Updated Question Set"
    assert updated_set.description == "Updated description"

def test_delete_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    assert delete_question_set_from_db(db_session, question_set.id) is True
    assert read_question_set_from_db(db_session, question_set.id) is None

def test_create_question_set_to_question_association(db_session, test_schema_question_set, test_schema_question):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_set_to_question_association_in_db(db_session, question_set.id, question.id) is True

def test_delete_question_set_to_question_association(db_session, test_schema_question_set, test_schema_question):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_set_to_question_association_in_db(db_session, question_set.id, question.id)
    assert delete_question_set_to_question_association_from_db(db_session, question_set.id, question.id) is True

def test_create_question_set_to_group_association(db_session, test_schema_question_set, test_schema_group):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    assert create_question_set_to_group_association_in_db(db_session, question_set.id, group.id) is True

def test_delete_question_set_to_group_association(db_session, test_schema_question_set, test_schema_group):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    create_question_set_to_group_association_in_db(db_session, question_set.id, group.id)
    assert delete_question_set_to_group_association_from_db(db_session, question_set.id, group.id) is True

def test_read_questions_for_question_set(db_session, test_schema_question_set, test_schema_question):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_set_to_question_association_in_db(db_session, question_set.id, question.id)
    questions = read_questions_for_question_set_from_db(db_session, question_set.id)
    assert len(questions) == 1
    assert questions[0].id == question.id

def test_read_groups_for_question_set(db_session, test_schema_question_set, test_schema_group):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    create_question_set_to_group_association_in_db(db_session, question_set.id, group.id)
    groups = read_groups_for_question_set_from_db(db_session, question_set.id)
    assert len(groups) == 1
    assert groups[0].id == group.id



def test_create_question_set_with_duplicate_name(db_session, test_schema_question_set):
    create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    with pytest.raises(ValueError, match="A question set with this name already exists for this user"):
        create_question_set_in_db(db_session, test_schema_question_set.model_dump())

def test_read_nonexistent_question_set(db_session):
    nonexistent_id = 9999
    assert read_question_set_from_db(db_session, nonexistent_id) is None

def test_update_nonexistent_question_set(db_session):
    nonexistent_id = 9999
    updated_data = {"name": "Updated Question Set"}
    with pytest.raises(ValueError, match="Question set with id 9999 does not exist"):
        update_question_set_in_db(db_session, nonexistent_id, updated_data)

def test_delete_nonexistent_question_set(db_session):
    nonexistent_id = 9999
    assert delete_question_set_from_db(db_session, nonexistent_id) is False

def test_create_question_set_with_questions(db_session, test_schema_question_set, test_schema_question):
    question1 = create_question_in_db(db_session, test_schema_question.model_dump())
    logger.debug("question1: %s", question1)
    question2 = create_question_in_db(db_session, {**test_schema_question.model_dump(), "text": "Another question"})
    logger.debug("question2: %s", question2)
    
    question_set_data = test_schema_question_set.model_dump()
    question_set_data["question_ids"] = [question1.id, question2.id]
    logger.debug("question_set_data: %s", question_set_data)
    
    question_set = create_question_set_in_db(db_session, question_set_data)
    logger.debug("question_set: %s", question_set)
    
    questions = read_questions_for_question_set_from_db(db_session, question_set.id)
    logger.debug("questions: %s", questions)
    assert len(questions) == 2
    assert {q.id for q in questions} == {question1.id, question2.id}

def test_update_question_set_questions(db_session, test_schema_question_set, test_schema_question):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question1 = create_question_in_db(db_session, test_schema_question.model_dump())
    question2 = create_question_in_db(db_session, {**test_schema_question.model_dump(), "text": "Another question"})
    
    update_data = {"question_ids": [question1.id, question2.id]}
    updated_set = update_question_set_in_db(db_session, question_set.id, update_data)
    
    questions = read_questions_for_question_set_from_db(db_session, updated_set.id)
    assert len(questions) == 2
    assert {q.id for q in questions} == {question1.id, question2.id}

def test_read_question_sets_pagination(db_session, test_schema_question_set):
    for i in range(5):
        create_question_set_in_db(db_session, {**test_schema_question_set.model_dump(), "name": f"Question Set {i}"})
    
    page1 = read_question_sets_from_db(db_session, skip=0, limit=2)
    page2 = read_question_sets_from_db(db_session, skip=2, limit=2)
    
    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id

def test_delete_question_set_cascading(db_session, test_schema_question_set, test_schema_question, test_schema_group):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    
    create_question_set_to_question_association_in_db(db_session, question_set.id, question.id)
    create_question_set_to_group_association_in_db(db_session, question_set.id, group.id)
    
    delete_question_set_from_db(db_session, question_set.id)
    
    assert read_question_set_from_db(db_session, question_set.id) is None
    assert read_questions_for_question_set_from_db(db_session, question_set.id) == []
    assert read_groups_for_question_set_from_db(db_session, question_set.id) == []

def test_create_question_set_with_invalid_question_id(db_session, test_schema_question_set):
    question_set_data = test_schema_question_set.model_dump()
    question_set_data["question_ids"] = [9999]  # Non-existent question ID
    logger.debug("question_set_data: %s", question_set_data)
    
    with pytest.raises(ValueError) as exc_info:
        created_question_set = create_question_set_in_db(db_session, question_set_data)
        logger.debug("created_question_set: %s", created_question_set)
    assert "Question with id 9999 does not exist" in str(exc_info.value)

def test_create_question_set_with_invalid_group_id(db_session, test_schema_question_set):
    question_set_data = test_schema_question_set.model_dump()
    question_set_data["group_ids"] = [9999]  # Non-existent group ID
    logger.debug("question_set_data: %s", question_set_data)
    
    with pytest.raises(ValueError) as exc_info:
        created_question_set = create_question_set_in_db(db_session, question_set_data)
        logger.debug("created_question_set: %s", created_question_set)
    assert "Group with id 9999 does not exist" in str(exc_info.value)

def test_update_question_set_toggle_public(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    original_is_public = question_set.is_public
    
    update_data = {"is_public": not original_is_public}
    updated_set = update_question_set_in_db(db_session, question_set.id, update_data)
    
    assert updated_set.is_public != original_is_public

```

## File: test_crud_question_tags.py
```py
# filename: backend/tests/test_crud/test_crud_question_tags.py

from backend.app.crud.crud_question_tags import (
    create_question_tag_in_db,
    create_question_to_tag_association_in_db,
    delete_question_tag_from_db,
    delete_question_to_tag_association_from_db,
    read_question_tag_by_tag_from_db,
    read_question_tag_from_db,
    read_question_tags_from_db,
    read_questions_for_tag_from_db,
    read_tags_for_question_from_db,
    update_question_tag_in_db
)
from backend.app.crud.crud_questions import create_question_in_db
import pytest
from sqlalchemy.exc import IntegrityError

def test_create_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    assert tag.tag == test_schema_question_tag.tag

def test_read_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    read_tag = read_question_tag_from_db(db_session, tag.id)
    assert read_tag.id == tag.id
    assert read_tag.tag == tag.tag

def test_read_question_tag_by_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    read_tag = read_question_tag_by_tag_from_db(db_session, tag.tag)
    assert read_tag.id == tag.id
    assert read_tag.tag == tag.tag

def test_read_question_tags(db_session, test_schema_question_tag):
    create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    tags = read_question_tags_from_db(db_session)
    assert len(tags) > 0

def test_update_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    updated_data = {"tag": "updated-tag"}
    updated_tag = update_question_tag_in_db(db_session, tag.id, updated_data)
    assert updated_tag.tag == "updated-tag"

def test_delete_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    assert delete_question_tag_from_db(db_session, tag.id) is True
    assert read_question_tag_from_db(db_session, tag.id) is None

def test_create_question_to_tag_association(db_session, test_schema_question_tag, test_schema_question):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_to_tag_association_in_db(db_session, question.id, tag.id) is True

def test_delete_question_to_tag_association(db_session, test_schema_question_tag, test_schema_question):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)
    assert delete_question_to_tag_association_from_db(db_session, question.id, tag.id) is True

def test_read_tags_for_question(db_session, test_schema_question_tag, test_schema_question):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)
    tags = read_tags_for_question_from_db(db_session, question.id)
    assert len(tags) == 1
    assert tags[0].id == tag.id

def test_read_questions_for_tag(db_session, test_schema_question_tag, test_schema_question):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)
    questions = read_questions_for_tag_from_db(db_session, tag.id)
    assert len(questions) == 1
    assert questions[0].id == question.id



def test_create_duplicate_tag(db_session, test_schema_question_tag):
    create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    with pytest.raises(IntegrityError):
        create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())

def test_read_nonexistent_tag(db_session):
    nonexistent_id = 9999
    assert read_question_tag_from_db(db_session, nonexistent_id) is None

def test_read_nonexistent_tag_by_tag(db_session):
    nonexistent_tag = "nonexistent-tag"
    assert read_question_tag_by_tag_from_db(db_session, nonexistent_tag) is None

def test_update_nonexistent_tag(db_session):
    nonexistent_id = 9999
    updated_data = {"tag": "updated-tag"}
    assert update_question_tag_in_db(db_session, nonexistent_id, updated_data) is None

def test_delete_nonexistent_tag(db_session):
    nonexistent_id = 9999
    assert delete_question_tag_from_db(db_session, nonexistent_id) is False

def test_create_multiple_tags(db_session, test_schema_question_tag):
    tag1 = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    tag2 = create_question_tag_in_db(db_session, {**test_schema_question_tag.model_dump(), "tag": "another-tag"})
    tags = read_question_tags_from_db(db_session)
    assert len(tags) == 2
    assert {t.id for t in tags} == {tag1.id, tag2.id}

def test_update_tag_to_existing_name(db_session, test_schema_question_tag):
    tag1 = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    tag2 = create_question_tag_in_db(db_session, {**test_schema_question_tag.model_dump(), "tag": "another-tag"})
    with pytest.raises(IntegrityError):
        update_question_tag_in_db(db_session, tag2.id, {"tag": tag1.tag})

def test_read_tags_pagination(db_session, test_schema_question_tag):
    for i in range(5):
        create_question_tag_in_db(db_session, {**test_schema_question_tag.model_dump(), "tag": f"tag-{i}"})
    
    page1 = read_question_tags_from_db(db_session, skip=0, limit=2)
    page2 = read_question_tags_from_db(db_session, skip=2, limit=2)
    
    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id

def test_delete_tag_cascading(db_session, test_schema_question_tag, test_schema_question):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)
    
    delete_question_tag_from_db(db_session, tag.id)
    
    assert read_question_tag_from_db(db_session, tag.id) is None
    assert read_tags_for_question_from_db(db_session, question.id) == []

def test_create_tag_with_description(db_session, test_schema_question_tag):
    tag_data = test_schema_question_tag.model_dump()
    tag_data["description"] = "This is a test tag description"
    tag = create_question_tag_in_db(db_session, tag_data)
    assert tag.description == "This is a test tag description"

def test_update_tag_description(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    updated_data = {"description": "Updated description"}
    updated_tag = update_question_tag_in_db(db_session, tag.id, updated_data)
    assert updated_tag.description == "Updated description"

def test_create_tag_with_empty_string(db_session, test_schema_question_tag):
    tag_data = test_schema_question_tag.model_dump()
    tag_data["tag"] = ""
    with pytest.raises(ValueError):
        create_question_tag_in_db(db_session, tag_data)

def test_update_tag_to_empty_string(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    with pytest.raises(ValueError):
        update_question_tag_in_db(db_session, tag.id, {"tag": ""})

def test_create_tag_case_insensitive(db_session, test_schema_question_tag):
    create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    with pytest.raises(IntegrityError):
        create_question_tag_in_db(db_session, {**test_schema_question_tag.model_dump(), "tag": test_schema_question_tag.tag.upper()})

```

## File: test_crud_questions.py
```py
# filename: backend/tests/test_crud/test_crud_questions.py

import pytest

from backend.app.crud.crud_questions import (
    create_question_in_db,
    delete_question_from_db,
    read_question_from_db,
    read_questions_from_db,
    update_question_in_db,
    replace_question_in_db
)
from backend.app.models.questions import DifficultyLevel
from backend.app.crud.crud_question_tags import create_question_tag_in_db
from backend.app.crud.crud_answer_choices import create_answer_choice_in_db, read_answer_choices_from_db
from backend.app.crud.crud_subjects import create_subject_in_db
from backend.app.services.logging_service import logger

def test_create_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert question.text == test_schema_question.text
    assert question.difficulty == test_schema_question.difficulty

def test_create_question_with_answers(db_session, test_schema_question_with_answers):
    # Ensure no questions exist before creating a new one
    existing_questions = read_questions_from_db(db_session)
    logger.debug("test_create_question_with_answers: existing_questions: %s", existing_questions)
    assert len(existing_questions) == 0
    
    # Ensure no answer choices exist before creating a new question
    existing_answer_choices = read_answer_choices_from_db(db_session)
    logger.debug("test_create_question_with_answers: existing_answer_choices: %s", existing_answer_choices)
    assert len(existing_answer_choices) == 0
    
    question_data = test_schema_question_with_answers.model_dump()
    logger.debug("test_create_question_with_answers before ac: question_data: %s", question_data)
    question_data['answer_choices'] = [ac for ac in question_data['answer_choices']]
    logger.debug("test_create_question_with_answers after ac: question_data: %s", question_data)
    question = create_question_in_db(db_session, question_data)
    assert question.text == test_schema_question_with_answers.text
    assert question.difficulty == test_schema_question_with_answers.difficulty
    assert len(question.answer_choices) == len(test_schema_question_with_answers.answer_choices)

def test_read_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    read_question = read_question_from_db(db_session, question.id)
    assert read_question.id == question.id
    assert read_question.text == question.text

def test_read_questions(db_session, test_schema_question):
    create_question_in_db(db_session, test_schema_question.model_dump())
    questions = read_questions_from_db(db_session)
    assert len(questions) > 0

def test_update_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    updated_data = {"text": "Updated question text", "difficulty": DifficultyLevel.HARD}
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert updated_question.text == "Updated question text"
    assert updated_question.difficulty == DifficultyLevel.HARD

def test_delete_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert delete_question_from_db(db_session, question.id) is True
    assert read_question_from_db(db_session, question.id) is None

def test_create_question_with_associations(db_session, test_schema_question, test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
    question_data = test_schema_question.model_dump()
    question_data.update({
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id]
    })
    question = create_question_in_db(db_session, question_data)
    assert len(question.subjects) == 1
    assert len(question.topics) == 1
    assert len(question.subtopics) == 1
    assert len(question.concepts) == 1

def test_update_question_associations(db_session, test_schema_question, test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    updated_data = {
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id]
    }
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert len(updated_question.subjects) == 1
    assert len(updated_question.topics) == 1
    assert len(updated_question.subtopics) == 1
    assert len(updated_question.concepts) == 1

def test_create_question_with_invalid_difficulty(db_session, test_schema_question):
    invalid_question_data = test_schema_question.model_dump()
    invalid_question_data['difficulty'] = 'INVALID_DIFFICULTY'
    with pytest.raises(ValueError):
        create_question_in_db(db_session, invalid_question_data)

def test_create_question_with_empty_text(db_session, test_schema_question):
    invalid_question_data = test_schema_question.model_dump()
    invalid_question_data['text'] = ''
    with pytest.raises(ValueError):
        create_question_in_db(db_session, invalid_question_data)

def test_read_nonexistent_question(db_session):
    nonexistent_id = 9999
    assert read_question_from_db(db_session, nonexistent_id) is None

def test_update_nonexistent_question(db_session):
    nonexistent_id = 9999
    updated_data = {"text": "Updated question text"}
    assert update_question_in_db(db_session, nonexistent_id, updated_data) is None

def test_delete_nonexistent_question(db_session):
    nonexistent_id = 9999
    assert delete_question_from_db(db_session, nonexistent_id) is False

def test_create_question_with_multiple_subjects(db_session, test_schema_question, test_model_subject):
    new_subject = create_subject_in_db(db_session, {"name": "New Subject"})
    question_data = test_schema_question.model_dump()
    question_data['subject_ids'] = [test_model_subject.id, new_subject.id]
    question = create_question_in_db(db_session, question_data)
    assert len(question.subjects) == 2
    assert test_model_subject.id in [subject.id for subject in question.subjects]
    assert new_subject.id in [subject.id for subject in question.subjects]

def test_update_question_remove_associations(db_session, test_schema_question, test_model_subject, test_model_topic):
    question_data = test_schema_question.model_dump()
    question_data.update({
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id]
    })
    question = create_question_in_db(db_session, question_data)
    
    updated_data = {
        "subject_ids": [],
        "topic_ids": []
    }
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert len(updated_question.subjects) == 0
    assert len(updated_question.topics) == 0

def test_create_question_with_tags(db_session, test_schema_question, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question_data = test_schema_question.model_dump()
    question_data['question_tag_ids'] = [tag.id]
    question = create_question_in_db(db_session, question_data)
    assert len(question.question_tags) == 1
    assert question.question_tags[0].id == tag.id

def test_update_question_tags(db_session, test_schema_question, test_schema_question_tag):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    
    updated_data = {"question_tag_ids": [tag.id]}
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert len(updated_question.question_tags) == 1
    assert updated_question.question_tags[0].id == tag.id

def test_create_question_with_answer_choices(db_session, test_schema_question, test_schema_answer_choice):
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    question_data = test_schema_question.model_dump()
    question_data['answer_choice_ids'] = [answer_choice.id]
    question = create_question_in_db(db_session, question_data)
    assert len(question.answer_choices) == 1
    assert question.answer_choices[0].id == answer_choice.id

def test_update_question_answer_choices(db_session, test_schema_question, test_schema_answer_choice):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    logger.debug("test_update_question_answer_choices: question.answer_choices: %s", question.answer_choices)
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    logger.debug("test_update_question_answer_choices: answer_choice: %s", answer_choice)
    
    updated_data = {"answer_choice_ids": [answer_choice.id]}
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert len(updated_question.answer_choices) == 1
    assert updated_question.answer_choices[0].id == answer_choice.id

def test_read_questions_pagination(db_session, test_schema_question):
    for i in range(5):
        create_question_in_db(db_session, {**test_schema_question.model_dump(), "text": f"Question {i}"})
    
    page1 = read_questions_from_db(db_session, skip=0, limit=2)
    page2 = read_questions_from_db(db_session, skip=2, limit=2)
    
    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id

def test_create_question_with_creator(db_session, test_schema_question, test_model_user):
    question_data = test_schema_question.model_dump()
    question_data['creator_id'] = test_model_user.id
    question = create_question_in_db(db_session, question_data)
    assert question.creator_id == test_model_user.id

def test_update_question_creator(db_session, test_schema_question, test_model_user):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    updated_data = {"creator_id": test_model_user.id}
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert updated_question.creator_id == test_model_user.id

def test_replace_question(db_session, test_schema_question, test_model_subject, test_model_topic):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    replace_data = {
        "text": "Replaced question text",
        "difficulty": DifficultyLevel.EXPERT,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [],
        "concept_ids": [],
        "answer_choice_ids": [],
        "question_tag_ids": [],
        "question_set_ids": []
    }
    replaced_question = replace_question_in_db(db_session, question.id, replace_data)
    assert replaced_question.text == "Replaced question text"
    assert replaced_question.difficulty == DifficultyLevel.EXPERT
    assert len(replaced_question.subjects) == 1
    assert len(replaced_question.topics) == 1
    assert len(replaced_question.subtopics) == 0
    assert len(replaced_question.concepts) == 0
    assert len(replaced_question.answer_choices) == 0
    assert len(replaced_question.question_tags) == 0
    assert len(replaced_question.question_sets) == 0

def test_replace_question_with_new_answer_choices(db_session, test_schema_question, test_schema_answer_choice):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    new_answer_choice_data = test_schema_answer_choice.model_dump()
    replace_data = {
        "text": "Replaced question with new answers",
        "difficulty": DifficultyLevel.MEDIUM,
        "subject_ids": [],
        "topic_ids": [],
        "subtopic_ids": [],
        "concept_ids": [],
        "new_answer_choices": [new_answer_choice_data],
        "question_tag_ids": [],
        "question_set_ids": []
    }
    replaced_question = replace_question_in_db(db_session, question.id, replace_data)
    assert replaced_question.text == "Replaced question with new answers"
    assert len(replaced_question.answer_choices) == 1
    assert replaced_question.answer_choices[0].text == new_answer_choice_data["text"]

def test_replace_nonexistent_question(db_session):
    nonexistent_id = 9999
    replace_data = {"text": "Replaced question text", "difficulty": DifficultyLevel.EASY}
    assert replace_question_in_db(db_session, nonexistent_id, replace_data) is None

# Update existing test to cover more partial update scenarios
def test_update_question_partial(db_session, test_schema_question, test_model_subject, test_model_topic):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    initial_difficulty = question.difficulty
    initial_subject_count = len(question.subjects)
    new_subject = create_subject_in_db(db_session, {"name": "New Subject"})
    
    # Partial update: only change text and add a subject
    partial_update_data = {
        "text": "Partially updated question text",
        "subject_ids": [new_subject.id]
    }
    updated_question = update_question_in_db(db_session, question.id, partial_update_data)
    
    assert updated_question.text == "Partially updated question text"
    assert updated_question.difficulty == initial_difficulty  # Should remain unchanged
    assert len(updated_question.subjects) == initial_subject_count + 1
    assert new_subject.id in [subject.id for subject in updated_question.subjects]
    assert test_model_subject.id in [subject.id for subject in updated_question.subjects]
    
    # Another partial update: change difficulty and add a topic
    another_partial_update = {
        "difficulty": DifficultyLevel.HARD,
        "topic_ids": [test_model_topic.id]
    }
    updated_question = update_question_in_db(db_session, question.id, another_partial_update)
    
    assert updated_question.text == "Partially updated question text"  # Should remain from previous update
    assert updated_question.difficulty == DifficultyLevel.HARD
    assert len(updated_question.topics) == 1

def test_update_question_mixed_answer_choices(db_session, test_schema_question, test_schema_answer_choice):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    existing_answer = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    update_data = {
        "answer_choice_ids": [existing_answer.id],
        "new_answer_choices": [{"text": "New answer", "is_correct": False}]
    }
    
    updated_question = update_question_in_db(db_session, question.id, update_data)
    assert len(updated_question.answer_choices) == 2
    assert any(ac.id == existing_answer.id for ac in updated_question.answer_choices)
    assert any(ac.text == "New answer" for ac in updated_question.answer_choices)

```

## File: test_crud_roles.py
```py
# filename: backend/tests/test_crud/test_crud_roles.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.crud.crud_permissions import create_permission_in_db
from backend.app.crud.crud_roles import (
    create_role_in_db,
    create_role_to_permission_association_in_db,
    delete_role_from_db,
    delete_role_to_permission_association_from_db,
    read_permissions_for_role_from_db,
    read_role_by_name_from_db,
    read_role_from_db,
    read_roles_from_db,
    read_users_for_role_from_db,
    update_role_in_db,
    read_default_role_from_db
)
from backend.app.crud.crud_user import create_user_in_db


def test_create_role(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    assert role.name == test_role_data["name"]
    assert role.description == test_role_data["description"]

def test_read_role(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    read_role = read_role_from_db(db_session, role.id)
    assert read_role.id == role.id
    assert read_role.name == role.name

def test_read_role_by_name(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    read_role = read_role_by_name_from_db(db_session, role.name)
    assert read_role.id == role.id
    assert read_role.name == role.name

def test_read_roles(db_session, test_role_data):
    create_role_in_db(db_session, test_role_data)
    roles = read_roles_from_db(db_session)
    assert len(roles) > 0

def test_update_role(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    updated_data = {"description": "Updated description"}
    updated_role = update_role_in_db(db_session, role.id, updated_data)
    assert updated_role.description == "Updated description"

def test_delete_role(db_session, test_role_data):
    # Create a default role first
    default_role_data = {**test_role_data, "name": "Default Role", "default": True}
    create_role_in_db(db_session, default_role_data)

    # Now create and delete the test role
    role = create_role_in_db(db_session, test_role_data)
    assert delete_role_from_db(db_session, role.id) is True
    assert read_role_from_db(db_session, role.id) is None

def test_create_role_to_permission_association(db_session, test_role_data, test_schema_permission):
    role = create_role_in_db(db_session, test_role_data)
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    assert create_role_to_permission_association_in_db(db_session, role.id, permission.id) is True

def test_delete_role_to_permission_association(db_session, test_role_data, test_schema_permission):
    role = create_role_in_db(db_session, test_role_data)
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    assert delete_role_to_permission_association_from_db(db_session, role.id, permission.id) is True

def test_read_permissions_for_role(db_session, test_role_data, test_schema_permission):
    role = create_role_in_db(db_session, test_role_data)
    initial_permissions = read_permissions_for_role_from_db(db_session, role.id)
    
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    
    updated_permissions = read_permissions_for_role_from_db(db_session, role.id)
    assert len(updated_permissions) == len(initial_permissions) + 1
    assert permission.id in [p.id for p in updated_permissions]

def test_read_users_for_role(db_session, test_role_data, test_user_data):
    role = create_role_in_db(db_session, test_role_data)
    user_data = test_user_data
    user_data['role_id'] = role.id
    user = create_user_in_db(db_session, user_data)
    users = read_users_for_role_from_db(db_session, role.id)
    assert len(users) == 1
    assert users[0].id == user.id

def test_create_duplicate_role(db_session, test_role_data):
    create_role_in_db(db_session, test_role_data)
    with pytest.raises(IntegrityError):
        create_role_in_db(db_session, test_role_data)

def test_read_nonexistent_role(db_session):
    nonexistent_id = 9999
    assert read_role_from_db(db_session, nonexistent_id) is None

def test_update_nonexistent_role(db_session):
    nonexistent_id = 9999
    updated_data = {"description": "Updated description"}
    assert update_role_in_db(db_session, nonexistent_id, updated_data) is None

def test_delete_nonexistent_role(db_session):
    nonexistent_id = 9999
    assert delete_role_from_db(db_session, nonexistent_id) is False

def test_create_role_with_default_true(db_session, test_role_data):
    role_data = {**test_role_data, "default": True}
    role = create_role_in_db(db_session, role_data)
    assert role.default is True

def test_update_role_default_status(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    updated_data = {"default": True}
    updated_role = update_role_in_db(db_session, role.id, updated_data)
    assert updated_role.default is True

def test_read_default_role(db_session, test_role_data):
    role_data = {**test_role_data, "default": True}
    create_role_in_db(db_session, role_data)
    default_role = read_default_role_from_db(db_session)
    assert default_role is not None
    assert default_role.default is True

def test_create_multiple_default_roles(db_session, test_role_data):
    role_data1 = {**test_role_data, "name": "Default Role 1", "default": True}
    role_data2 = {**test_role_data, "name": "Default Role 2", "default": True}
    create_role_in_db(db_session, role_data1)
    with pytest.raises(IntegrityError):
        create_role_in_db(db_session, role_data2)

def test_update_role_name(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    new_name = "Updated Role Name"
    updated_data = {"name": new_name}
    updated_role = update_role_in_db(db_session, role.id, updated_data)
    assert updated_role.name == new_name

def test_read_roles_pagination(db_session, test_role_data):
    for i in range(5):
        create_role_in_db(db_session, {**test_role_data, "name": f"Role {i}"})
    
    page1 = read_roles_from_db(db_session, skip=0, limit=2)
    page2 = read_roles_from_db(db_session, skip=2, limit=2)
    
    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id

def test_delete_role_cascade(db_session, test_role_data, test_schema_permission, test_user_data):
    # Create a default role first
    default_role_data = {**test_role_data, "name": "Default Role", "default": True}
    create_role_in_db(db_session, default_role_data)

    role = create_role_in_db(db_session, test_role_data)
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    
    user_data = {**test_user_data, "role_id": role.id}
    create_user_in_db(db_session, user_data)
    
    delete_role_from_db(db_session, role.id)
    
    assert read_role_from_db(db_session, role.id) is None
    assert read_permissions_for_role_from_db(db_session, role.id) == []
    assert read_users_for_role_from_db(db_session, role.id) == []

def test_create_role_with_permissions(db_session, test_role_data, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    role_data = {**test_role_data, "permissions": [permission.name]}
    role = create_role_in_db(db_session, role_data)
    
    role_permissions = read_permissions_for_role_from_db(db_session, role.id)
    assert len(role_permissions) == 1
    assert role_permissions[0].id == permission.id

def test_update_role_permissions(db_session, test_role_data, test_schema_permission):
    role = create_role_in_db(db_session, test_role_data)
    permission1 = create_permission_in_db(db_session, test_schema_permission.model_dump())
    permission2 = create_permission_in_db(db_session, {**test_schema_permission.model_dump(), "name": "another_permission"})
    
    updated_data = {"permissions": [permission1.name, permission2.name]}
    updated_role = update_role_in_db(db_session, role.id, updated_data)
    
    role_permissions = read_permissions_for_role_from_db(db_session, updated_role.id)
    assert len(role_permissions) == 2
    assert {p.id for p in role_permissions} == {permission1.id, permission2.id}

```

## File: test_crud_subjects.py
```py
# filename: backend/tests/crud/test_crud_subjects.py

import pytest

from backend.app.crud.crud_disciplines import create_discipline_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subjects import (
    create_discipline_to_subject_association_in_db,
    create_question_to_subject_association_in_db, create_subject_in_db,
    create_subject_to_topic_association_in_db,
    delete_discipline_to_subject_association_from_db,
    delete_question_to_subject_association_from_db, delete_subject_from_db,
    delete_subject_to_topic_association_from_db,
    read_disciplines_for_subject_from_db, read_questions_for_subject_from_db,
    read_subject_by_name_from_db, read_subject_from_db, read_subjects_from_db,
    read_topics_for_subject_from_db, update_subject_in_db)
from backend.app.crud.crud_topics import create_topic_in_db


def test_create_subject(db_session, test_schema_subject):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    assert subject.name == test_schema_subject.name

def test_read_subject(db_session, test_schema_subject):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    read_subject = read_subject_from_db(db_session, subject.id)
    assert read_subject.id == subject.id
    assert read_subject.name == subject.name

def test_read_subject_by_name(db_session, test_schema_subject):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    read_subject = read_subject_by_name_from_db(db_session, subject.name)
    assert read_subject.id == subject.id
    assert read_subject.name == subject.name

def test_read_subjects(db_session, test_schema_subject):
    create_subject_in_db(db_session, test_schema_subject.model_dump())
    subjects = read_subjects_from_db(db_session)
    assert len(subjects) > 0

def test_update_subject(db_session, test_schema_subject):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    updated_data = {"name": "Updated Subject"}
    updated_subject = update_subject_in_db(db_session, subject.id, updated_data)
    assert updated_subject.name == "Updated Subject"

def test_delete_subject(db_session, test_schema_subject):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    assert delete_subject_from_db(db_session, subject.id) is True
    assert read_subject_from_db(db_session, subject.id) is None

def test_create_discipline_to_subject_association(db_session, test_schema_subject, test_schema_discipline):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    assert create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id) is True

def test_delete_discipline_to_subject_association(db_session, test_schema_subject, test_schema_discipline):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id)
    assert delete_discipline_to_subject_association_from_db(db_session, discipline.id, subject.id) is True

def test_create_subject_to_topic_association(db_session, test_schema_subject, test_schema_topic):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    assert create_subject_to_topic_association_in_db(db_session, subject.id, topic.id) is True

def test_delete_subject_to_topic_association(db_session, test_schema_subject, test_schema_topic):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    create_subject_to_topic_association_in_db(db_session, subject.id, topic.id)
    assert delete_subject_to_topic_association_from_db(db_session, subject.id, topic.id) is True

def test_create_question_to_subject_association(db_session, test_schema_subject, test_schema_question):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_to_subject_association_in_db(db_session, question.id, subject.id) is True

def test_delete_question_to_subject_association(db_session, test_schema_subject, test_schema_question):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_subject_association_in_db(db_session, question.id, subject.id)
    assert delete_question_to_subject_association_from_db(db_session, question.id, subject.id) is True

def test_read_disciplines_for_subject(db_session, test_schema_subject, test_schema_discipline):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    created_discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    create_discipline_to_subject_association_in_db(db_session, created_discipline.id, subject.id)
    disciplines = read_disciplines_for_subject_from_db(db_session, subject.id)
    assert len(disciplines) == 2
    assert created_discipline.id in [discipline.id for discipline in disciplines]

def test_read_topics_for_subject(db_session, test_schema_subject, test_schema_topic):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    create_subject_to_topic_association_in_db(db_session, subject.id, topic.id)
    topics = read_topics_for_subject_from_db(db_session, subject.id)
    assert len(topics) == 1
    assert topics[0].id == topic.id

def test_read_questions_for_subject(db_session, test_schema_subject, test_schema_question):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_subject_association_in_db(db_session, question.id, subject.id)
    questions = read_questions_for_subject_from_db(db_session, subject.id)
    assert len(questions) == 1
    assert questions[0].id == question.id

```

## File: test_crud_subtopics.py
```py
# filename: backend/tests/crud/test_crud_subtopics.py

import pytest

from backend.app.crud.crud_concepts import create_concept_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subtopics import (
    create_question_to_subtopic_association_in_db, create_subtopic_in_db,
    create_subtopic_to_concept_association_in_db,
    create_topic_to_subtopic_association_in_db,
    delete_question_to_subtopic_association_from_db, delete_subtopic_from_db,
    delete_subtopic_to_concept_association_from_db,
    delete_topic_to_subtopic_association_from_db,
    read_concepts_for_subtopic_from_db, read_questions_for_subtopic_from_db,
    read_subtopic_by_name_from_db, read_subtopic_from_db,
    read_subtopics_from_db, read_topics_for_subtopic_from_db,
    update_subtopic_in_db)
from backend.app.crud.crud_topics import create_topic_in_db


def test_create_subtopic(db_session, test_schema_subtopic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    assert subtopic.name == test_schema_subtopic.name

def test_read_subtopic(db_session, test_schema_subtopic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    read_subtopic = read_subtopic_from_db(db_session, subtopic.id)
    assert read_subtopic.id == subtopic.id
    assert read_subtopic.name == subtopic.name

def test_read_subtopic_by_name(db_session, test_schema_subtopic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    read_subtopic = read_subtopic_by_name_from_db(db_session, subtopic.name)
    assert read_subtopic.id == subtopic.id
    assert read_subtopic.name == subtopic.name

def test_read_subtopics(db_session, test_schema_subtopic):
    create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    subtopics = read_subtopics_from_db(db_session)
    assert len(subtopics) > 0

def test_update_subtopic(db_session, test_schema_subtopic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    updated_data = {"name": "Updated Subtopic"}
    updated_subtopic = update_subtopic_in_db(db_session, subtopic.id, updated_data)
    assert updated_subtopic.name == "Updated Subtopic"

def test_delete_subtopic(db_session, test_schema_subtopic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    assert delete_subtopic_from_db(db_session, subtopic.id) is True
    assert read_subtopic_from_db(db_session, subtopic.id) is None

def test_create_topic_to_subtopic_association(db_session, test_schema_subtopic, test_schema_topic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    assert create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id) is True

def test_delete_topic_to_subtopic_association(db_session, test_schema_subtopic, test_schema_topic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id)
    assert delete_topic_to_subtopic_association_from_db(db_session, topic.id, subtopic.id) is True

def test_create_subtopic_to_concept_association(db_session, test_schema_subtopic, test_schema_concept):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    assert create_subtopic_to_concept_association_in_db(db_session, subtopic.id, concept.id) is True

def test_delete_subtopic_to_concept_association(db_session, test_schema_subtopic, test_schema_concept):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    create_subtopic_to_concept_association_in_db(db_session, subtopic.id, concept.id)
    assert delete_subtopic_to_concept_association_from_db(db_session, subtopic.id, concept.id) is True

def test_create_question_to_subtopic_association(db_session, test_schema_subtopic, test_schema_question):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_to_subtopic_association_in_db(db_session, question.id, subtopic.id) is True

def test_delete_question_to_subtopic_association(db_session, test_schema_subtopic, test_schema_question):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_subtopic_association_in_db(db_session, question.id, subtopic.id)
    assert delete_question_to_subtopic_association_from_db(db_session, question.id, subtopic.id) is True

def test_read_topics_for_subtopic(db_session, test_schema_subtopic, test_schema_topic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    created_topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    create_topic_to_subtopic_association_in_db(db_session, created_topic.id, subtopic.id)
    topics = read_topics_for_subtopic_from_db(db_session, subtopic.id)
    assert len(topics) == 2
    assert created_topic.id in [topic.id for topic in topics]

def test_read_concepts_for_subtopic(db_session, test_schema_subtopic, test_schema_concept):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    create_subtopic_to_concept_association_in_db(db_session, subtopic.id, concept.id)
    concepts = read_concepts_for_subtopic_from_db(db_session, subtopic.id)
    assert len(concepts) == 1
    assert concepts[0].id == concept.id

def test_read_questions_for_subtopic(db_session, test_schema_subtopic, test_schema_question):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_subtopic_association_in_db(db_session, question.id, subtopic.id)
    questions = read_questions_for_subtopic_from_db(db_session, subtopic.id)
    assert len(questions) == 1
    assert questions[0].id == question.id

```

## File: test_crud_topics.py
```py
# filename: backend/tests/crud/test_crud_topics.py

import pytest

from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subjects import create_subject_in_db
from backend.app.crud.crud_subtopics import create_subtopic_in_db
from backend.app.crud.crud_topics import (
    create_question_to_topic_association_in_db,
    create_subject_to_topic_association_in_db, create_topic_in_db,
    create_topic_to_subtopic_association_in_db,
    delete_question_to_topic_association_from_db,
    delete_subject_to_topic_association_from_db, delete_topic_from_db,
    delete_topic_to_subtopic_association_from_db,
    read_questions_for_topic_from_db, read_subjects_for_topic_from_db,
    read_subtopics_for_topic_from_db, read_topic_by_name_from_db,
    read_topic_from_db, read_topics_from_db, update_topic_in_db)


def test_create_topic(db_session, test_schema_topic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    assert topic.name == test_schema_topic.name

def test_read_topic(db_session, test_schema_topic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    read_topic = read_topic_from_db(db_session, topic.id)
    assert read_topic.id == topic.id
    assert read_topic.name == topic.name

def test_read_topic_by_name(db_session, test_schema_topic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    read_topic = read_topic_by_name_from_db(db_session, topic.name)
    assert read_topic.id == topic.id
    assert read_topic.name == topic.name

def test_read_topics(db_session, test_schema_topic):
    create_topic_in_db(db_session, test_schema_topic.model_dump())
    topics = read_topics_from_db(db_session)
    assert len(topics) > 0

def test_update_topic(db_session, test_schema_topic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    updated_data = {"name": "Updated Topic"}
    updated_topic = update_topic_in_db(db_session, topic.id, updated_data)
    assert updated_topic.name == "Updated Topic"

def test_delete_topic(db_session, test_schema_topic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    assert delete_topic_from_db(db_session, topic.id) is True
    assert read_topic_from_db(db_session, topic.id) is None

def test_create_subject_to_topic_association(db_session, test_schema_topic, test_schema_subject):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    assert create_subject_to_topic_association_in_db(db_session, subject.id, topic.id) is True

def test_delete_subject_to_topic_association(db_session, test_schema_topic, test_schema_subject):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    create_subject_to_topic_association_in_db(db_session, subject.id, topic.id)
    assert delete_subject_to_topic_association_from_db(db_session, subject.id, topic.id) is True

def test_create_topic_to_subtopic_association(db_session, test_schema_topic, test_schema_subtopic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    assert create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id) is True

def test_delete_topic_to_subtopic_association(db_session, test_schema_topic, test_schema_subtopic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id)
    assert delete_topic_to_subtopic_association_from_db(db_session, topic.id, subtopic.id) is True

def test_create_question_to_topic_association(db_session, test_schema_topic, test_schema_question):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_to_topic_association_in_db(db_session, question.id, topic.id) is True

def test_delete_question_to_topic_association(db_session, test_schema_topic, test_schema_question):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_topic_association_in_db(db_session, question.id, topic.id)
    assert delete_question_to_topic_association_from_db(db_session, question.id, topic.id) is True

def test_read_subjects_for_topic(db_session, test_schema_topic, test_schema_subject):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    created_subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    create_subject_to_topic_association_in_db(db_session, created_subject.id, topic.id)
    subjects = read_subjects_for_topic_from_db(db_session, topic.id)
    assert len(subjects) == 2
    assert created_subject.id in [subject.id for subject in subjects]

def test_read_subtopics_for_topic(db_session, test_schema_topic, test_schema_subtopic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id)
    subtopics = read_subtopics_for_topic_from_db(db_session, topic.id)
    assert len(subtopics) == 1
    assert subtopics[0].id == subtopic.id

def test_read_questions_for_topic(db_session, test_schema_topic, test_schema_question):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_topic_association_in_db(db_session, question.id, topic.id)
    questions = read_questions_for_topic_from_db(db_session, topic.id)
    assert len(questions) == 1
    assert questions[0].id == question.id
    
```

## File: test_crud_user.py
```py
# filename: backend/tests/crud/test_crud_user.py

from backend.app.crud.crud_groups import create_group_in_db
from backend.app.crud.crud_question_sets import create_question_set_in_db
from backend.app.crud.crud_roles import create_role_in_db
from backend.app.crud.crud_user import (
    create_user_in_db, create_user_to_group_association_in_db,
    delete_user_from_db, delete_user_to_group_association_from_db,
    read_created_question_sets_for_user_from_db, read_groups_for_user_from_db,
    read_role_for_user_from_db, read_user_by_email_from_db,
    read_user_by_username_from_db, read_user_from_db, read_users_from_db,
    update_user_in_db)


def test_create_user(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    assert user.username == test_user_data["username"]
    assert user.email == test_user_data["email"]

def test_read_user(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    read_user = read_user_from_db(db_session, user.id)
    assert read_user.id == user.id
    assert read_user.username == user.username

def test_read_user_by_username(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    read_user = read_user_by_username_from_db(db_session, user.username)
    assert read_user.id == user.id
    assert read_user.username == user.username

def test_read_user_by_email(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    read_user = read_user_by_email_from_db(db_session, user.email)
    assert read_user.id == user.id
    assert read_user.email == user.email

def test_read_users(db_session, test_user_data):
    create_user_in_db(db_session, test_user_data)
    users = read_users_from_db(db_session)
    assert len(users) > 0

def test_update_user(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    updated_data = {"email": "updated@example.com"}
    updated_user = update_user_in_db(db_session, user.id, updated_data)
    assert updated_user.email == "updated@example.com"

def test_delete_user(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    assert delete_user_from_db(db_session, user.id) is True
    assert read_user_from_db(db_session, user.id) is None

def test_create_user_to_group_association(db_session, test_user_data, test_group_data):
    user = create_user_in_db(db_session, test_user_data)
    group = create_group_in_db(db_session, test_group_data)
    assert create_user_to_group_association_in_db(db_session, user.id, group.id) is True

def test_delete_user_to_group_association(db_session, test_user_data, test_group_data):
    user = create_user_in_db(db_session, test_user_data)
    group = create_group_in_db(db_session, test_group_data)
    create_user_to_group_association_in_db(db_session, user.id, group.id)
    assert delete_user_to_group_association_from_db(db_session, user.id, group.id) is True

def test_read_groups_for_user(db_session, test_user_data, test_group_data):
    user = create_user_in_db(db_session, test_user_data)
    group = create_group_in_db(db_session, test_group_data)
    create_user_to_group_association_in_db(db_session, user.id, group.id)
    groups = read_groups_for_user_from_db(db_session, user.id)
    assert len(groups) == 1
    assert groups[0].id == group.id

def test_read_role_for_user(db_session, test_user_data, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    user_data = test_user_data
    user_data['role_id'] = role.id
    user = create_user_in_db(db_session, user_data)
    user_role = read_role_for_user_from_db(db_session, user.id)
    assert user_role.id == role.id

def test_read_created_question_sets_for_user(db_session, test_user_data, test_question_set_data):
    user = create_user_in_db(db_session, test_user_data)
    question_set_data = test_question_set_data
    question_set_data['creator_id'] = user.id
    question_set = create_question_set_in_db(db_session, question_set_data)
    created_sets = read_created_question_sets_for_user_from_db(db_session, user.id)
    assert len(created_sets) == 1
    assert created_sets[0].id == question_set.id

```

## File: test_crud_user_responses.py
```py
# filename: backend/tests/crud/test_crud_user_responses.py

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.crud.crud_answer_choices import create_answer_choice_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_user import create_user_in_db
from backend.app.crud.crud_user_responses import (
    create_user_response_in_db, delete_user_response_from_db,
    read_user_response_from_db, read_user_responses_for_question_from_db,
    read_user_responses_for_user_from_db, read_user_responses_from_db,
    update_user_response_in_db)


def test_create_user_response(db_session, test_schema_user_response, test_user_data, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_user_data)
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    user_response = create_user_response_in_db(db_session, user_response_data)
    assert user_response.user_id == user.id
    assert user_response.question_id == question.id
    assert user_response.answer_choice_id == answer_choice.id
    assert user_response.is_correct == user_response_data["is_correct"]

def test_read_user_response(db_session, test_schema_user_response, test_user_data, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_user_data)
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    user_response = create_user_response_in_db(db_session, user_response_data)
    read_response = read_user_response_from_db(db_session, user_response.id)
    assert read_response.id == user_response.id
    assert read_response.user_id == user_response.user_id
    assert read_response.question_id == user_response.question_id

def test_read_user_responses(db_session, test_schema_user_response, test_user_data, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_user_data)
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    create_user_response_in_db(db_session, user_response_data)
    responses = read_user_responses_from_db(db_session)
    assert len(responses) > 0

def test_update_user_response(db_session, test_schema_user_response, test_user_data, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_user_data)
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    user_response = create_user_response_in_db(db_session, user_response_data)
    
    # Store the original is_correct value
    original_is_correct = user_response.is_correct
    
    updated_data = {"is_correct": not original_is_correct}
    
    updated_response = update_user_response_in_db(db_session, user_response.id, updated_data)
    
    # Fetch the response from the database again to ensure it's updated
    fetched_response = read_user_response_from_db(db_session, user_response.id)
    
    assert updated_response.is_correct != original_is_correct, f"Updated response is_correct ({updated_response.is_correct}) should not equal original is_correct ({original_is_correct})"
    assert fetched_response.is_correct != original_is_correct, f"Fetched response is_correct ({fetched_response.is_correct}) should not equal original is_correct ({original_is_correct})"

def test_delete_user_response(db_session, test_schema_user_response, test_user_data, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_user_data)
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    user_response = create_user_response_in_db(db_session, user_response_data)
    assert delete_user_response_from_db(db_session, user_response.id) is True
    assert read_user_response_from_db(db_session, user_response.id) is None

def test_read_user_responses_for_user(db_session, test_schema_user_response, test_user_data, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_user_data)
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    create_user_response_in_db(db_session, user_response_data)
    user_responses = read_user_responses_for_user_from_db(db_session, user.id)
    assert len(user_responses) == 1
    assert user_responses[0].user_id == user.id

def test_read_user_responses_for_question(db_session, test_schema_user_response, test_user_data, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_user_data)
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    create_user_response_in_db(db_session, user_response_data)
    question_responses = read_user_responses_for_question_from_db(db_session, question.id)
    assert len(question_responses) == 1
    assert question_responses[0].question_id == question.id

def test_read_user_responses_with_time_range(db_session, test_schema_user_response, test_user_data, test_schema_question, test_schema_answer_choice):
    user = create_user_in_db(db_session, test_user_data)
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    answer_choice = create_answer_choice_in_db(db_session, test_schema_answer_choice.model_dump())
    
    user_response_data = test_schema_user_response.model_dump()
    user_response_data.update({
        "user_id": user.id,
        "question_id": question.id,
        "answer_choice_id": answer_choice.id
    })
    
    create_user_response_in_db(db_session, user_response_data)
    
    start_time = datetime.now(timezone.utc) - timedelta(hours=1)
    end_time = datetime.now(timezone.utc) + timedelta(hours=1)
    
    responses = read_user_responses_from_db(db_session, start_time=start_time, end_time=end_time)
    assert len(responses) == 1
    
    past_start_time = datetime.now(timezone.utc) - timedelta(days=2)
    past_end_time = datetime.now(timezone.utc) - timedelta(days=1)
    
    past_responses = read_user_responses_from_db(db_session, start_time=past_start_time, end_time=past_end_time)
    assert len(past_responses) == 0

```

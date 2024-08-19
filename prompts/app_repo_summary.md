
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
from backend.app.api.endpoints import questions as questions_router
from backend.app.api.endpoints import register as register_router
from backend.app.api.endpoints import subjects as subjects_router
from backend.app.api.endpoints import subtopics as subtopics_router
from backend.app.api.endpoints import topics as topics_router
from backend.app.api.endpoints import user_responses as user_responses_router
from backend.app.api.endpoints import users as users_router
from backend.app.db.session import get_db
from backend.app.middleware.authorization_middleware import \
    AuthorizationMiddleware
from backend.app.middleware.blacklist_middleware import BlacklistMiddleware
from backend.app.middleware.cors_middleware import add_cors_middleware
from backend.app.services.permission_generator_service import (
    ensure_permissions_in_db, generate_permissions)
from backend.app.services.validation_service import \
    register_validation_listeners

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
# filename: /code/quiz-app/backend/app/validate_openapi.py

from fastapi.openapi.utils import get_openapi

from backend.app.main import \
    app  # Adjust the import based on your actual app file and instance


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

# Directory: /code/quiz-app/backend/app/schemas

## File: __init__.py
```py

```

## File: answer_choices.py
```py
# filename: backend/app/schemas/answer_choices.py

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
# filename: backend/app/schemas/authentication.py

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

from pydantic import BaseModel, Field, field_validator, validator

from backend.app.core.config import DifficultyLevel
from backend.app.schemas.answer_choices import (AnswerChoiceCreateSchema,
                                                AnswerChoiceSchema)
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

    @field_validator('subjects', 'topics', 'subtopics', 'concepts', 'question_tags', 'question_sets', mode='before')
    @classmethod
    def ensure_dict_list(cls, v):
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        elif isinstance(v, list) and all(isinstance(item, str) for item in v):
            return [{"name": item} for item in v]
        elif isinstance(v, list) and all(hasattr(item, 'name') for item in v):
            return [{"id": item.id, "name": item.name} for item in v]
        else:
            raise ValueError("Must be a list of dictionaries, strings, or objects with 'name' attribute")

    class Config:
        from_attributes = True

class QuestionWithAnswersCreateSchema(QuestionCreateSchema):
    answer_choices: List['AnswerChoiceCreateSchema']
    question_tags: Optional[List['QuestionTagCreateSchema']] = None
    question_sets: Optional[List['QuestionSetCreateSchema']] = None

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
    role_id: int = Field(..., description="ID of the role for the user")

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

# Directory: /code/quiz-app/backend/app/services

## File: __init__.py
```py

```

## File: authentication_service.py
```py
# filename: backend/app/services/authentication_service.py

from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash, verify_password
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.models.users import UserModel


def authenticate_user(db: Session, username: str, password: str) -> UserModel:
    user = read_user_by_username_from_db(db, username)
    if not user:
        return False
    
    # Add this line to log the result of verify_password
    verification_result = verify_password(password, user.hashed_password)
    
    if not verification_result:
        hashed_attempt = get_password_hash(password)
        return False
    if not user.is_active:
        return False
    return user

```

## File: authorization_service.py
```py
# filename: backend/app/services/authorization_service.py

from typing import List

from sqlalchemy.orm import Session

from backend.app.models.groups import GroupModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel
from backend.app.services.logging_service import logger


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
# filename: backend/app/services/user_service.py

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from backend.app.core.jwt import decode_access_token
from backend.app.crud.crud_user import read_user_by_username_from_db
from backend.app.db.session import get_db
from backend.app.models.authentication import RevokedTokenModel
from backend.app.services.logging_service import logger

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
        user = read_user_by_username_from_db(db, username=username)
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

```

## File: validation_service.py
```py
# filename: backend/app/services/validation_service.py

from fastapi import HTTPException
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import instance_dict
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
from backend.app.services.logging_service import logger, sqlalchemy_obj_to_dict


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

# Directory: /code/quiz-app/backend/app/crud

## File: __init__.py
```py

```

## File: crud_answer_choices.py
```py
# filename: backend/app/crud/crud_answer_choices.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.associations import QuestionToAnswerAssociation
from backend.app.models.questions import QuestionModel


def create_answer_choice_in_db(db: Session, answer_choice_data: Dict) -> AnswerChoiceModel:
    db_answer_choice = AnswerChoiceModel(
        text=answer_choice_data['text'],
        is_correct=answer_choice_data['is_correct'],
        explanation=answer_choice_data.get('explanation')
    )
    db.add(db_answer_choice)
    db.commit()
    db.refresh(db_answer_choice)
    return db_answer_choice

def read_answer_choice_from_db(db: Session, answer_choice_id: int) -> Optional[AnswerChoiceModel]:
    return db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id == answer_choice_id).first()

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
        query = query.filter(func.lower(QuestionModel.difficulty) == func.lower(filters['difficulty']))
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

from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.time_period import TimePeriodModel


def create_leaderboard_entry_in_db(db: Session, leaderboard_data: dict) -> LeaderboardModel:
    db_leaderboard_entry = LeaderboardModel(**leaderboard_data)
    db.add(db_leaderboard_entry)
    db.commit()
    db.refresh(db_leaderboard_entry)
    return db_leaderboard_entry

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
    db_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == entry_id).first()
    if db_entry:
        for key, value in update_data.items():
            setattr(db_entry, key, value)
        db.commit()
        db.refresh(db_entry)
    return db_entry

def delete_leaderboard_entry_from_db(db: Session, leaderboard_id: int) -> bool:
    db_entry = db.query(LeaderboardModel).filter(LeaderboardModel.id == leaderboard_id).first()
    if db_entry:
        db.delete(db_entry)
        db.commit()
        return True
    return False

def read_or_create_time_period_in_db(db: Session, time_period_data: dict) -> TimePeriodModel:
    db_time_period = db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period_data['id']).first()
    if not db_time_period:
        db_time_period = TimePeriodModel(**time_period_data)
        db.add(db_time_period)
        db.commit()
        db.refresh(db_time_period)
    return db_time_period

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


def create_question_set_in_db(db: Session, question_set_data: Dict) -> QuestionSetModel:
    db_question_set = QuestionSetModel(
        name=question_set_data['name'],
        description=question_set_data.get('description'),
        is_public=question_set_data.get('is_public', True),
        creator_id=question_set_data['creator_id']
    )
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set

def read_question_set_from_db(db: Session, question_set_id: int) -> Optional[QuestionSetModel]:
    return db.query(QuestionSetModel).filter(QuestionSetModel.id == question_set_id).first()

def read_question_sets_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSetModel]:
    return db.query(QuestionSetModel).offset(skip).limit(limit).all()

def update_question_set_in_db(db: Session, question_set_id: int, question_set_data: Dict) -> Optional[QuestionSetModel]:
    db_question_set = read_question_set_from_db(db, question_set_id)
    if db_question_set:
        for key, value in question_set_data.items():
            if key not in ['question_ids', 'group_ids']:
                setattr(db_question_set, key, value)
        db.commit()
        db.refresh(db_question_set)
    return db_question_set

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

from sqlalchemy.orm import Session

from backend.app.models.associations import QuestionToTagAssociation
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import QuestionModel


def create_question_tag_in_db(db: Session, question_tag_data: Dict) -> QuestionTagModel:
    db_question_tag = QuestionTagModel(
        tag=question_tag_data['tag'],
        description=question_tag_data.get('description')
    )
    db.add(db_question_tag)
    db.commit()
    db.refresh(db_question_tag)
    return db_question_tag

def read_question_tag_from_db(db: Session, question_tag_id: int) -> Optional[QuestionTagModel]:
    return db.query(QuestionTagModel).filter(QuestionTagModel.id == question_tag_id).first()

def read_question_tag_by_tag_from_db(db: Session, tag: str) -> Optional[QuestionTagModel]:
    return db.query(QuestionTagModel).filter(QuestionTagModel.tag == tag).first()

def read_question_tags_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionTagModel]:
    return db.query(QuestionTagModel).offset(skip).limit(limit).all()

def update_question_tag_in_db(db: Session, question_tag_id: int, question_tag_data: Dict) -> Optional[QuestionTagModel]:
    db_question_tag = read_question_tag_from_db(db, question_tag_id)
    if db_question_tag:
        for key, value in question_tag_data.items():
            setattr(db_question_tag, key, value)
        db.commit()
        db.refresh(db_question_tag)
    return db_question_tag

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

from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.concepts import ConceptModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import DifficultyLevel, QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def associate_related_models(db: Session, db_question: QuestionModel, question_data: Dict) -> None:
    """Helper function to associate related models with the question."""

    # Iterate over keys
    for key, value in question_data.items():
        if not value:
            continue

        if key == 'answer_choices':
            for answer_choice_data in value:
                db_answer_choice = AnswerChoiceModel(**answer_choice_data)
                db.add(db_answer_choice)
                db_question.answer_choices.append(db_answer_choice)

        elif key == 'answer_choice_ids':
            existing_answer_choices = db.query(AnswerChoiceModel).filter(AnswerChoiceModel.id.in_(value)).all()
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
            setattr(db_question, key.replace('_ids', 's'), related_items)
        
        else:
            setattr(db_question, key, value)


def create_question_in_db(db: Session, question_data: Dict) -> QuestionModel:
    """Creates a new question in the database."""
    db_question = QuestionModel(
        text=question_data['text'],
        difficulty=DifficultyLevel(question_data['difficulty'])
        if isinstance(question_data['difficulty'], str)
        else question_data['difficulty']
    )
    db.add(db_question)
    db.flush()

    # Associate related models
    associate_related_models(db, db_question, question_data)

    db.commit()
    db.refresh(db_question)
    return db_question

def read_question_from_db(db: Session, question_id: int) -> Optional[QuestionModel]:
    return db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

def read_questions_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionModel]:
    return db.query(QuestionModel).offset(skip).limit(limit).all()

def update_question_in_db(db: Session, question_id: int, update_data: Dict) -> Optional[QuestionModel]:
    """Updates an existing question in the database."""
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

    if db_question is None:
        return None

    # Update simple fields
    for key, value in update_data.items():
        if key not in ['answer_choices', 'question_tag_ids', 'question_set_ids', 'subject_ids', 'topic_ids', 'subtopic_ids', 'concept_ids']:
            setattr(db_question, key, value)

    # Update associations
    associate_related_models(db, db_question, update_data)

    db.commit()
    db.refresh(db_question)
    return db_question

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

from sqlalchemy.orm import Session

from backend.app.models.associations import RoleToPermissionAssociation
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel


def create_role_in_db(db: Session, role_data: Dict) -> RoleModel:
    db_role = RoleModel(
        name=role_data['name'],
        description=role_data.get('description'),
        default=role_data.get('default', False)
    )
    db.add(db_role)
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
        for key, value in role_data.items():
            setattr(db_role, key, value)
        db.commit()
        db.refresh(db_role)
    return db_role

def delete_role_from_db(db: Session, role_id: int) -> bool:
    db_role = read_role_from_db(db, role_id)
    if db_role:
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

```

## File: crud_subjects.py
```py
# filename: backend/app/crud/crud_subjects.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import (DisciplineToSubjectAssociation,
                                             QuestionToSubjectAssociation,
                                             SubjectToTopicAssociation)
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.topics import TopicModel


def create_subject_in_db(db: Session, subject_data: Dict) -> SubjectModel:
    db_subject = SubjectModel(name=subject_data['name'])
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def read_subject_from_db(db: Session, subject_id: int) -> Optional[SubjectModel]:
    return db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()

def read_subject_by_name_from_db(db: Session, name: str) -> Optional[SubjectModel]:
    return db.query(SubjectModel).filter(SubjectModel.name == name).first()

def read_subjects_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[SubjectModel]:
    return db.query(SubjectModel).offset(skip).limit(limit).all()

def update_subject_in_db(db: Session, subject_id: int, subject_data: Dict) -> Optional[SubjectModel]:
    db_subject = read_subject_from_db(db, subject_id)
    if db_subject:
        for key, value in subject_data.items():
            setattr(db_subject, key, value)
        db.commit()
        db.refresh(db_subject)
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

## File: crud_topics.py
```py
# filename: backend/app/crud/crud_topics.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.associations import (QuestionToTopicAssociation,
                                             SubjectToTopicAssociation,
                                             TopicToSubtopicAssociation)
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def create_topic_in_db(db: Session, topic_data: Dict) -> TopicModel:
    db_topic = TopicModel(name=topic_data['name'])
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def read_topic_from_db(db: Session, topic_id: int) -> Optional[TopicModel]:
    return db.query(TopicModel).filter(TopicModel.id == topic_id).first()

def read_topic_by_name_from_db(db: Session, name: str) -> Optional[TopicModel]:
    return db.query(TopicModel).filter(TopicModel.name == name).first()

def read_topics_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[TopicModel]:
    return db.query(TopicModel).offset(skip).limit(limit).all()

def update_topic_in_db(db: Session, topic_id: int, topic_data: Dict) -> Optional[TopicModel]:
    db_topic = read_topic_from_db(db, topic_id)
    if db_topic:
        for key, value in topic_data.items():
            setattr(db_topic, key, value)
        db.commit()
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

def create_question_to_topic_association_in_db(db: Session, question_id: int, topic_id: int) -> bool:
    association = QuestionToTopicAssociation(question_id=question_id, topic_id=topic_id)
    db.add(association)
    try:
        db.commit()
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
    return db.query(SubjectModel).join(SubjectToTopicAssociation).filter(
        SubjectToTopicAssociation.topic_id == topic_id
    ).all()

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
# filename: backend/app/crud/crud_users.py

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.models.associations import UserToGroupAssociation
from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel


def create_user_in_db(db: Session, user_data: Dict) -> UserModel:
    hashed_password = get_password_hash(user_data['password'])
    db_user = UserModel(
        username=user_data['username'],
        email=user_data['email'],
        hashed_password=hashed_password,
        is_active=user_data.get('is_active', True),
        is_admin=user_data.get('is_admin', False),
        role_id=user_data['role_id']
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def read_user_from_db(db: Session, user_id: int) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def read_user_by_username_from_db(db: Session, username: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.username == username).first()

def read_user_by_email_from_db(db: Session, email: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.email == email).first()

def read_users_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    return db.query(UserModel).offset(skip).limit(limit).all()

def update_user_in_db(db: Session, user_id: int, user_data: Dict) -> Optional[UserModel]:
    db_user = read_user_from_db(db, user_id)
    if db_user:
        for key, value in user_data.items():
            if key == 'password':
                db_user.hashed_password = get_password_hash(value)
            else:
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

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

def read_groups_for_user_from_db(db: Session, user_id: int) -> List[GroupModel]:
    return db.query(GroupModel).join(UserToGroupAssociation).filter(
        UserToGroupAssociation.user_id == user_id
    ).all()

def read_role_for_user_from_db(db: Session, user_id: int) -> Optional[RoleModel]:
    user = read_user_from_db(db, user_id)
    return user.role if user else None

def read_created_question_sets_for_user_from_db(db: Session, user_id: int) -> List[QuestionSetModel]:
    return db.query(QuestionSetModel).filter(QuestionSetModel.creator_id == user_id).all()

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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings_core
from backend.app.db.base import Base
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.services.logging_service import logger

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

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.crud.crud_answer_choices import (create_answer_choice_in_db,
                                                  delete_answer_choice_from_db,
                                                  read_answer_choice_from_db,
                                                  read_answer_choices_from_db,
                                                  update_answer_choice_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.answer_choices import (AnswerChoiceCreateSchema,
                                                AnswerChoiceSchema,
                                                AnswerChoiceUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/answer-choices/", response_model=AnswerChoiceSchema, status_code=status.HTTP_201_CREATED)
def create_answer_choice(
    answer_choice: AnswerChoiceCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Validate incoming data using Pydantic schema
    validated_answer_choice = AnswerChoiceCreateSchema(**answer_choice.model_dump())
    
    # Convert to dict for CRUD function
    answer_choice_data = validated_answer_choice.model_dump()
    
    # Call CRUD function
    created_answer_choice = create_answer_choice_in_db(db=db, answer_choice_data=answer_choice_data)
    
    # Convert back to Pydantic schema for response
    return AnswerChoiceSchema.model_validate(created_answer_choice)

@router.get("/answer-choices/", response_model=List[AnswerChoiceSchema])
def get_answer_choices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    answer_choices = read_answer_choices_from_db(db, skip=skip, limit=limit)
    return [AnswerChoiceSchema.model_validate(ac) for ac in answer_choices]

@router.get("/answer-choices/{answer_choice_id}", response_model=AnswerChoiceSchema)
def get_answer_choice(
    answer_choice_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_answer_choice = read_answer_choice_from_db(db, answer_choice_id=answer_choice_id)
    if db_answer_choice is None:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return AnswerChoiceSchema.model_validate(db_answer_choice)

@router.put("/answer-choices/{answer_choice_id}", response_model=AnswerChoiceSchema)
def update_answer_choice(
    answer_choice_id: int,
    answer_choice: AnswerChoiceUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Validate incoming data using Pydantic schema
    validated_answer_choice = AnswerChoiceUpdateSchema(**answer_choice.model_dump())
    
    # Convert to dict for CRUD function
    answer_choice_data = validated_answer_choice.model_dump()
    
    # Call CRUD function
    updated_answer_choice = update_answer_choice_in_db(db, answer_choice_id, answer_choice_data)
    
    if updated_answer_choice is None:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    
    # Convert back to Pydantic schema for response
    return AnswerChoiceSchema.model_validate(updated_answer_choice)

@router.delete("/answer-choices/{answer_choice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_answer_choice(
    answer_choice_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_answer_choice_from_db(db, answer_choice_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Answer choice with ID {answer_choice_id} not found")
    return None

```

## File: authentication.py
```py
# filename: backend/app/api/endpoints/authentication.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.core.jwt import create_access_token
from backend.app.db.session import get_db
from backend.app.models.authentication import RevokedTokenModel
from backend.app.models.users import UserModel
from backend.app.schemas.authentication import TokenSchema
from backend.app.services.authentication_service import authenticate_user
from backend.app.services.logging_service import logger
from backend.app.services.user_service import get_current_user, oauth2_scheme

router = APIRouter()

@router.post("/login", response_model=TokenSchema)
async def login_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    logger.debug(f"User {form_data.username} is trying to log in")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user or not user.is_active:
        logger.error(f"User {form_data.username} failed to log in")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    logger.debug(f"User {form_data.username} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_endpoint(
    current_user: UserModel = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
    if not revoked_token:
        try:
            revoked_token = RevokedTokenModel(token=token)
            db.add(revoked_token)
            db.commit()
            logger.info(f"User {current_user.username} logged out successfully")
            return {"message": "Successfully logged out"}
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to logout user {current_user.username}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to logout user"
            ) from e
    else:
        logger.warning(f"Attempt to logout with already revoked token by user {current_user.username}")
        return {"message": "Token already revoked"}

```

## File: concepts.py
```py
# filename: backend/app/api/endpoints/concepts.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_concepts import (create_concept_in_db,
                                            delete_concept_from_db,
                                            read_concept_from_db,
                                            read_concepts_from_db,
                                            update_concept_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.concepts import (ConceptCreateSchema, ConceptSchema,
                                          ConceptUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/concepts/", response_model=ConceptSchema, status_code=201)
def post_concept(
    concept: ConceptCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Validate incoming data using Pydantic schema
    validated_concept = ConceptCreateSchema(**concept.model_dump())
    
    # Convert to dict for CRUD function
    concept_data = validated_concept.model_dump()
    
    # Call CRUD function
    created_concept = create_concept_in_db(db=db, concept_data=concept_data)
    
    # Convert back to Pydantic schema for response
    return ConceptSchema.model_validate(created_concept)

@router.get("/concepts/", response_model=List[ConceptSchema])
def get_concepts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    concepts = read_concepts_from_db(db, skip=skip, limit=limit)
    return [ConceptSchema.model_validate(c) for c in concepts]

@router.get("/concepts/{concept_id}", response_model=ConceptSchema)
def get_concept(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_concept = read_concept_from_db(db, concept_id=concept_id)
    if db_concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return ConceptSchema.model_validate(db_concept)

@router.put("/concepts/{concept_id}", response_model=ConceptSchema)
def put_concept(
    concept_id: int,
    concept: ConceptUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Validate incoming data using Pydantic schema
    validated_concept = ConceptUpdateSchema(**concept.model_dump())
    
    # Convert to dict for CRUD function
    concept_data = validated_concept.model_dump()
    
    # Call CRUD function
    updated_concept = update_concept_in_db(db, concept_id, concept_data)
    
    if updated_concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    # Convert back to Pydantic schema for response
    return ConceptSchema.model_validate(updated_concept)

@router.delete("/concepts/{concept_id}", status_code=204)
def delete_concept_endpoint(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_concept_from_db(db, concept_id)
    if not success:
        raise HTTPException(status_code=404, detail="Concept not found")
    return None

```

## File: disciplines.py
```py
# filename: backend/app/api/endpoints/disciplines.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_disciplines import (create_discipline_in_db,
                                               delete_discipline_from_db,
                                               read_discipline_from_db,
                                               read_disciplines_from_db,
                                               update_discipline_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.disciplines import (DisciplineCreateSchema,
                                             DisciplineSchema,
                                             DisciplineUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/disciplines/", response_model=DisciplineSchema, status_code=201)
def post_discipline(
    discipline: DisciplineCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    validated_discipline = DisciplineCreateSchema(**discipline.model_dump())
    discipline_data = validated_discipline.model_dump()
    created_discipline = create_discipline_in_db(db=db, discipline_data=discipline_data)
    return DisciplineSchema.model_validate(created_discipline)

@router.get("/disciplines/", response_model=List[DisciplineSchema])
def get_disciplines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    disciplines = read_disciplines_from_db(db, skip=skip, limit=limit)
    return [DisciplineSchema.model_validate(d) for d in disciplines]

@router.get("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def get_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_discipline = read_discipline_from_db(db, discipline_id=discipline_id)
    if db_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return DisciplineSchema.model_validate(db_discipline)

@router.put("/disciplines/{discipline_id}", response_model=DisciplineSchema)
def put_discipline(
    discipline_id: int,
    discipline: DisciplineUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    validated_discipline = DisciplineUpdateSchema(**discipline.model_dump())
    discipline_data = validated_discipline.model_dump()
    updated_discipline = update_discipline_in_db(db, discipline_id, discipline_data)
    if updated_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return DisciplineSchema.model_validate(updated_discipline)

@router.delete("/disciplines/{discipline_id}", status_code=204)
def delete_discipline_endpoint(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_discipline_from_db(db, discipline_id)
    if not success:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return None

```

## File: domains.py
```py
# filename: backend/app/api/endpoints/domains.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_domains import (create_domain_in_db,
                                           delete_domain_from_db,
                                           read_domain_from_db,
                                           read_domains_from_db,
                                           update_domain_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.domains import (DomainCreateSchema, DomainSchema,
                                         DomainUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/domains/", response_model=DomainSchema, status_code=201)
def post_domain(
    domain: DomainCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    validated_domain = DomainCreateSchema(**domain.model_dump())
    domain_data = validated_domain.model_dump()
    created_domain = create_domain_in_db(db=db, domain_data=domain_data)
    return DomainSchema.model_validate(created_domain)

@router.get("/domains/", response_model=List[DomainSchema])
def get_domains(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    domains = read_domains_from_db(db, skip=skip, limit=limit)
    return [DomainSchema.model_validate(d) for d in domains]

@router.get("/domains/{domain_id}", response_model=DomainSchema)
def get_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_domain = read_domain_from_db(db, domain_id=domain_id)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainSchema.model_validate(db_domain)

@router.put("/domains/{domain_id}", response_model=DomainSchema)
def put_domain(
    domain_id: int,
    domain: DomainUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    validated_domain = DomainUpdateSchema(**domain.model_dump())
    domain_data = validated_domain.model_dump()
    updated_domain = update_domain_in_db(db, domain_id, domain_data)
    if updated_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainSchema.model_validate(updated_domain)

@router.delete("/domains/{domain_id}", status_code=204)
def delete_domain_endpoint(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_domain_from_db(db, domain_id)
    if not success:
        raise HTTPException(status_code=404, detail="Domain not found")
    return None

```

## File: filters.py
```py
# filename: backend/app/api/endpoints/filters.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_filters import read_filtered_questions_from_db
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.filters import FilterParamsSchema
from backend.app.schemas.questions import QuestionSchema
from backend.app.services.user_service import get_current_user

router = APIRouter()

async def forbid_extra_params(request: Request):
    allowed_params = {'subject', 'topic', 'subtopic', 'difficulty', 'question_tags', 'skip', 'limit'}
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
    question_tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user)
):
    await forbid_extra_params(request)
    
    filters = FilterParamsSchema(
        subject=subject,
        topic=topic,
        subtopic=subtopic,
        difficulty=difficulty,
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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_groups import (create_group_in_db,
                                          delete_group_from_db,
                                          read_group_from_db,
                                          update_group_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.groups import (GroupCreateSchema, GroupSchema,
                                        GroupUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/groups", response_model=GroupSchema)
def create_group_endpoint(
    group: GroupCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    validated_group = GroupCreateSchema(**group.model_dump())
    group_data = validated_group.model_dump()
    group_data["creator_id"] = current_user.id
    created_group = create_group_in_db(db=db, group_data=group_data)
    return GroupSchema.model_validate(created_group)

@router.get("/groups/{group_id}", response_model=GroupSchema)
def get_group_endpoint(
    group_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_group = read_group_from_db(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return GroupSchema.model_validate(db_group)

@router.put("/groups/{group_id}", response_model=GroupSchema)
def update_group_endpoint(
    group_id: int, 
    group: GroupUpdateSchema,
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    db_group = read_group_from_db(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if db_group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group creator can update the group")
    
    validated_group = GroupUpdateSchema(**group.model_dump())
    group_data = validated_group.model_dump()
    updated_group = update_group_in_db(db=db, group_id=group_id, group_data=group_data)
    return GroupSchema.model_validate(updated_group)

@router.delete("/groups/{group_id}", status_code=204)
def delete_group_endpoint(
    group_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
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

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from backend.app.crud.crud_leaderboard import (
    create_leaderboard_entry_in_db, delete_leaderboard_entry_from_db,
    read_leaderboard_entries_for_group_from_db,
    read_leaderboard_entries_for_user_from_db,
    read_leaderboard_entries_from_db, read_leaderboard_entry_from_db,
    read_or_create_time_period_in_db, update_leaderboard_entry_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.leaderboard import (LeaderboardCreateSchema,
                                             LeaderboardSchema,
                                             LeaderboardUpdateSchema)
from backend.app.services.scoring_service import (calculate_leaderboard_scores,
                                                  time_period_to_schema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.get("/leaderboard/", response_model=List[LeaderboardSchema])
def get_leaderboard(
    time_period: int = Query(..., description="Time period ID (1: daily, 7: weekly, 30: monthly, 365: yearly)"),
    group_id: Optional[int] = None,
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user: UserModel = Depends(get_current_user)
):
    time_period_model = read_or_create_time_period_in_db(db, {"id": time_period})
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
            time_period=time_period_to_schema(time_period_model),
            group_id=entry.group_id
        )
        for entry in leaderboard_entries
    ]

@router.get("/leaderboard/user/{user_id}", response_model=List[LeaderboardSchema])
def get_user_leaderboard(
    user_id: int = Path(..., description="The ID of the user to get leaderboard entries for"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    entries = read_leaderboard_entries_for_user_from_db(db, user_id)
    return [LeaderboardSchema.model_validate(entry) for entry in entries]

@router.get("/leaderboard/group/{group_id}", response_model=List[LeaderboardSchema])
def get_group_leaderboard(
    group_id: int = Path(..., description="The ID of the group to get leaderboard entries for"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    entries = read_leaderboard_entries_for_group_from_db(db, group_id)
    return [LeaderboardSchema.model_validate(entry) for entry in entries]

@router.post("/leaderboard/", response_model=LeaderboardSchema)
def create_leaderboard_entry(
    entry: LeaderboardCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return create_leaderboard_entry_in_db(db, entry.model_dump())

@router.put("/leaderboard/{entry_id}", response_model=LeaderboardSchema)
def update_leaderboard_entry(
    entry_id: int,
    entry: LeaderboardUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    updated_entry = update_leaderboard_entry_in_db(db, entry_id, entry.model_dump())
    if not updated_entry:
        raise HTTPException(status_code=404, detail="Leaderboard entry not found")
    return LeaderboardSchema.model_validate(updated_entry)

@router.delete("/leaderboard/{entry_id}", status_code=204)
def delete_leaderboard_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_leaderboard_entry_from_db(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Leaderboard entry not found")
    return None

```

## File: question_sets.py
```py
# filename: backend/app/api/endpoints/question_sets.py

import json
from typing import List

from fastapi import (APIRouter, Depends, File, Form, HTTPException, Response,
                     UploadFile, status)
from sqlalchemy.orm import Session

from backend.app.crud.crud_question_sets import (create_question_set_in_db,
                                                 delete_question_set_from_db,
                                                 read_question_set_from_db,
                                                 read_question_sets_from_db,
                                                 update_question_set_in_db)
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.question_sets import (QuestionSetCreateSchema,
                                               QuestionSetSchema,
                                               QuestionSetUpdateSchema)
from backend.app.schemas.questions import QuestionCreateSchema
from backend.app.services.logging_service import logger
from backend.app.services.user_service import get_current_user

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
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading question set: {str(exc)}"
        )

@router.get("/question-sets/", response_model=List[QuestionSetSchema])
def read_question_sets_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question_sets = read_question_sets_from_db(db, skip=skip, limit=limit)
    return [QuestionSetSchema.model_validate(qs) for qs in question_sets]

@router.post("/question-sets/", response_model=QuestionSetSchema, status_code=201)
def create_question_set_endpoint(
    question_set: QuestionSetCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Received question set data: %s", question_set)
    question_set_data = question_set.model_dump()
    question_set_data['creator_id'] = current_user.id
    created_question_set = create_question_set_in_db(db=db, question_set_data=question_set_data)
    logger.debug("Question set created successfully: %s", created_question_set)
    return QuestionSetSchema.model_validate(created_question_set)

@router.get("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def get_question_set_endpoint(
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    question_set = read_question_set_from_db(db, question_set_id=question_set_id)
    if not question_set:
        raise HTTPException(status_code=404, detail=f"Question set with ID {question_set_id} not found")
    return QuestionSetSchema.model_validate(question_set)

@router.put("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
def update_question_set_endpoint(
    question_set_id: int,
    question_set: QuestionSetUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Received update data for question set %d: %s", question_set_id, question_set)
    question_set_data = question_set.model_dump()
    updated_question_set = update_question_set_in_db(db, question_set_id, question_set_data)
    if updated_question_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found")
    logger.debug("Question set updated successfully: %s", updated_question_set)
    return QuestionSetSchema.model_validate(updated_question_set)

@router.delete("/question-sets/{question_set_id}", status_code=204)
def delete_question_set_endpoint(
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    deleted = delete_question_set_from_db(db, question_set_id=question_set_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question set not found")
    return Response(status_code=204)

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
which is handled by the get_current_user dependency.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.crud.crud_questions import (create_question_in_db,
                                             delete_question_from_db,
                                             read_question_from_db,
                                             read_questions_from_db,
                                             update_question_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.questions import (DetailedQuestionSchema,
                                           QuestionCreateSchema,
                                           QuestionSchema,
                                           QuestionUpdateSchema,
                                           QuestionWithAnswersCreateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/questions/", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
async def create_question_endpoint(
    question: QuestionCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> QuestionSchema:
    """
    Create a new question.

    This endpoint allows authenticated users to create a new question in the database.
    The question data is validated using the QuestionCreateSchema.

    Args:
        question (QuestionCreateSchema): The question data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        QuestionSchema: The created question data.

    Raises:
        HTTPException: 
            - 422 Unprocessable Entity: If the question data is invalid.
            - 500 Internal Server Error: If an unexpected error occurs during question creation.
    """
    try:
        validated_question = QuestionCreateSchema(**question.model_dump())
        question_data = validated_question.model_dump()
        created_question = create_question_in_db(db=db, question_data=question_data)
        return QuestionSchema.model_validate(created_question)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)) from ve
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An unexpected error occurred while creating the question") from e

@router.post("/questions/with-answers/", response_model=DetailedQuestionSchema, status_code=status.HTTP_201_CREATED)
async def create_question_with_answers_endpoint(
    question: QuestionWithAnswersCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> DetailedQuestionSchema:
    """
    Create a new question with associated answers.

    This endpoint allows authenticated users to create a new question along with its answer choices
    in a single operation. The question and answer data are validated using the QuestionWithAnswersCreateSchema.

    Args:
        question (QuestionWithAnswersCreateSchema): The question and answer data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        DetailedQuestionSchema: The created question data including associated answers.

    Raises:
        HTTPException: 
            - 422 Unprocessable Entity: If the question or answer data is invalid.
            - 500 Internal Server Error: If an unexpected error occurs during question creation.
    """
    try:
        validated_question = QuestionWithAnswersCreateSchema(**question.model_dump())
        question_data = validated_question.model_dump()
        created_question = create_question_in_db(db=db, question_data=question_data)
        return DetailedQuestionSchema.model_validate(created_question)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)) from ve
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An unexpected error occurred while creating the question with answers") from e

@router.get("/questions/", response_model=List[DetailedQuestionSchema])
async def get_questions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> List[DetailedQuestionSchema]:
    """
    Retrieve a list of questions.

    This endpoint allows authenticated users to retrieve a paginated list of questions from the database.

    Args:
        skip (int, optional): The number of questions to skip. Defaults to 0.
        limit (int, optional): The maximum number of questions to return. Defaults to 100.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[DetailedQuestionSchema]: A list of questions with their details.

    Raises:
        HTTPException: 500 Internal Server Error if an unexpected error occurs during retrieval.
    """
    try:
        questions = read_questions_from_db(db, skip=skip, limit=limit)
        return [DetailedQuestionSchema.model_validate(q) for q in questions]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An unexpected error occurred while retrieving questions") from e

@router.get("/questions/{question_id}", response_model=DetailedQuestionSchema)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> DetailedQuestionSchema:
    """
    Retrieve a specific question by ID.

    This endpoint allows authenticated users to retrieve a single question by its ID.

    Args:
        question_id (int): The ID of the question to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        DetailedQuestionSchema: The detailed question data.

    Raises:
        HTTPException: 
            - 404 Not Found: If the question with the given ID does not exist.
            - 500 Internal Server Error: If an unexpected error occurs during retrieval.
    """
    try:
        db_question = read_question_from_db(db, question_id=question_id)
        if db_question is None:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        return DetailedQuestionSchema.model_validate(db_question)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An unexpected error occurred while retrieving the question") from e

@router.put("/questions/{question_id}", response_model=DetailedQuestionSchema)
async def update_question_endpoint(
    question_id: int,
    question: QuestionUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> DetailedQuestionSchema:
    """
    Update a specific question.

    This endpoint allows authenticated users to update an existing question by its ID.

    Args:
        question_id (int): The ID of the question to update.
        question (QuestionUpdateSchema): The updated question data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        DetailedQuestionSchema: The updated question data.

    Raises:
        HTTPException: 
            - 404 Not Found: If the question with the given ID does not exist.
            - 422 Unprocessable Entity: If the update data is invalid.
            - 500 Internal Server Error: If an unexpected error occurs during the update.
    """
    try:
        validated_question = QuestionUpdateSchema(**question.model_dump())
        question_data = validated_question.model_dump()
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
                            detail="An unexpected error occurred while updating the question") from e

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_endpoint(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific question.

    This endpoint allows authenticated users to delete an existing question by its ID.

    Args:
        question_id (int): The ID of the question to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        None

    Raises:
        HTTPException: 
            - 404 Not Found: If the question with the given ID does not exist.
            - 500 Internal Server Error: If an unexpected error occurs during the deletion.
    """
    try:
        success = delete_question_from_db(db, question_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An unexpected error occurred while deleting the question") from e

```

## File: register.py
```py
# filename: backend/app/api/endpoints/register.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.crud.crud_user import (create_user_in_db,
                                        read_user_by_email_from_db,
                                        read_user_by_username_from_db)
from backend.app.db.session import get_db
from backend.app.models.roles import RoleModel
from backend.app.schemas.user import UserCreateSchema, UserSchema

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    db_user = read_user_by_username_from_db(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    db_email = read_user_by_email_from_db(db, email=user.email)
    if db_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password.get_secret_value())
    
    if not user.role_id:
        default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
        user.role_id = default_role.id if default_role else None
    
    user_data = user.model_dump()
    user_data['hashed_password'] = hashed_password
    del user_data['password']
    
    created_user = create_user_in_db(db=db, user_data=user_data)
    return UserSchema.model_validate(created_user)

```

## File: subjects.py
```py
# filename: backend/app/api/endpoints/subjects.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_subjects import (create_subject_in_db,
                                            delete_subject_from_db,
                                            read_subject_from_db,
                                            read_subjects_from_db,
                                            update_subject_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.subjects import (SubjectCreateSchema, SubjectSchema,
                                          SubjectUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/subjects/", response_model=SubjectSchema, status_code=201)
def post_subject(
    subject: SubjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subject_data = subject.model_dump()
    created_subject = create_subject_in_db(db=db, subject_data=subject_data)
    return SubjectSchema.model_validate(created_subject)

@router.get("/subjects/", response_model=List[SubjectSchema])
def get_subjects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subjects = read_subjects_from_db(db, skip=skip, limit=limit)
    return [SubjectSchema.model_validate(s) for s in subjects]

@router.get("/subjects/{subject_id}", response_model=SubjectSchema)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subject = read_subject_from_db(db, subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectSchema.model_validate(db_subject)

@router.put("/subjects/{subject_id}", response_model=SubjectSchema)
def put_subject(
    subject_id: int,
    subject: SubjectUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subject_data = subject.model_dump()
    db_subject = update_subject_in_db(db, subject_id, subject_data)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectSchema.model_validate(db_subject)

@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_subject_from_db(db, subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return None

```

## File: subtopics.py
```py
# filename: backend/app/api/endpoints/subtopics.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_subtopics import (create_subtopic_in_db,
                                             delete_subtopic_from_db,
                                             read_subtopic_from_db,
                                             read_subtopics_from_db,
                                             update_subtopic_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.subtopics import (SubtopicCreateSchema,
                                           SubtopicSchema,
                                           SubtopicUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/subtopics/", response_model=SubtopicSchema, status_code=201)
def post_subtopic(
    subtopic: SubtopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subtopic_data = subtopic.model_dump()
    created_subtopic = create_subtopic_in_db(db=db, subtopic_data=subtopic_data)
    return SubtopicSchema.model_validate(created_subtopic)

@router.get("/subtopics/", response_model=List[SubtopicSchema])
def get_subtopics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subtopics = read_subtopics_from_db(db, skip=skip, limit=limit)
    return [SubtopicSchema.model_validate(s) for s in subtopics]

@router.get("/subtopics/{subtopic_id}", response_model=SubtopicSchema)
def get_subtopic(
    subtopic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_subtopic = read_subtopic_from_db(db, subtopic_id=subtopic_id)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return SubtopicSchema.model_validate(db_subtopic)

@router.put("/subtopics/{subtopic_id}", response_model=SubtopicSchema)
def put_subtopic(
    subtopic_id: int,
    subtopic: SubtopicUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subtopic_data = subtopic.model_dump()
    db_subtopic = update_subtopic_in_db(db, subtopic_id, subtopic_data)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return SubtopicSchema.model_validate(db_subtopic)

@router.delete("/subtopics/{subtopic_id}", status_code=204)
def delete_subtopic_endpoint(
    subtopic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_subtopic_from_db(db, subtopic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return None

```

## File: topics.py
```py
# filename: backend/app/api/endpoints/topics.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud.crud_topics import (create_topic_in_db,
                                          delete_topic_from_db,
                                          read_topic_from_db,
                                          read_topics_from_db,
                                          update_topic_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.topics import (TopicCreateSchema, TopicSchema,
                                        TopicUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/topics/", response_model=TopicSchema, status_code=201)
def post_topic(
    topic: TopicCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    topic_data = topic.model_dump()
    created_topic = create_topic_in_db(db=db, topic_data=topic_data)
    return TopicSchema.model_validate(created_topic)

@router.get("/topics/", response_model=List[TopicSchema])
def get_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    topics = read_topics_from_db(db, skip=skip, limit=limit)
    return [TopicSchema.model_validate(t) for t in topics]

@router.get("/topics/{topic_id}", response_model=TopicSchema)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_topic = read_topic_from_db(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return TopicSchema.model_validate(db_topic)

@router.put("/topics/{topic_id}", response_model=TopicSchema)
def put_topic(
    topic_id: int,
    topic: TopicUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    topic_data = topic.model_dump()
    db_topic = update_topic_in_db(db, topic_id, topic_data)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return TopicSchema.model_validate(db_topic)

@router.delete("/topics/{topic_id}", status_code=204)
def delete_topic_endpoint(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_topic_from_db(db, topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return None

```

## File: user_responses.py
```py
# filename: backend/app/api/endpoints/user_responses.py

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.crud.crud_user_responses import (create_user_response_in_db,
                                                  delete_user_response_from_db,
                                                  read_user_response_from_db,
                                                  read_user_responses_from_db,
                                                  update_user_response_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.user_responses import (UserResponseCreateSchema,
                                                UserResponseSchema,
                                                UserResponseUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post(
    "/user-responses/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED
)
def create_user_response_endpoint(
    user_response: UserResponseCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_response_data = user_response.model_dump()
    created_response = create_user_response_in_db(db=db, user_response_data=user_response_data)
    return UserResponseSchema.model_validate(created_response)

@router.get("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def get_user_response_endpoint(
    user_response_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_response = read_user_response_from_db(db, user_response_id)
    if not user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    return UserResponseSchema.model_validate(user_response)

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
def update_user_response_endpoint(
    user_response_id: int,
    user_response: UserResponseUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_response_data = user_response.model_dump()
    updated_user_response = update_user_response_in_db(db, user_response_id, user_response_data)
    if not updated_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    return UserResponseSchema.model_validate(updated_user_response)

@router.delete("/user-responses/{user_response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_response_endpoint(
    user_response_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = delete_user_response_from_db(db, user_response_id)
    if not success:
        raise HTTPException(status_code=404, detail="User response not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

```

## File: users.py
```py
# filename: backend/app/api/endpoints/users.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.crud.crud_user import (create_user_in_db, read_users_from_db,
                                        update_user_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.user import (UserCreateSchema, UserSchema,
                                      UserUpdateSchema)
from backend.app.services.logging_service import logger
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/users/", response_model=UserSchema, status_code=201)
def create_user(
    user: UserCreateSchema, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_data = user.model_dump()
    try:
        new_user = create_user_in_db(db=db, user_data=user_data)
        return UserSchema.model_validate(new_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
        ) from e

@router.get("/users/", response_model=List[UserSchema])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    users = read_users_from_db(db, skip=skip, limit=limit)
    return [UserSchema.model_validate(user) for user in users]

@router.get("/users/me", response_model=UserSchema)
def read_user_me(
    current_user: UserModel = Depends(get_current_user)
):
    return UserSchema.model_validate(current_user)

@router.put("/users/me", response_model=UserSchema)
def update_user_me(
    user: UserUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    logger.debug("Received user data: %s", user)
    user_data = user.model_dump()
    try:
        updated_user = update_user_in_db(db=db, user_id=current_user.id, user_data=user_data)
        logger.debug("User updated successfully: %s", updated_user)
        return UserSchema.model_validate(updated_user)
    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except HTTPException as e:
        logger.error("Error updating user: %s", e)
        raise e

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
from sqlalchemy.sql import func

from backend.app.db.base import Base


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
# filename: backend/app/models/topics.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


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
# filename: backend/app/models/users.py

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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

# Directory: /code/quiz-app/backend/app/middleware

## File: __init__.py
```py

```

## File: authorization_middleware.py
```py
# app/middleware/authorization_middleware.py

from fastapi import HTTPException, Request, status
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.config import settings_core
from backend.app.db.session import get_db
from backend.app.models.permissions import PermissionModel
from backend.app.services.authorization_service import has_permission
from backend.app.services.logging_service import logger
from backend.app.services.user_service import get_current_user, oauth2_scheme


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
# filename: backend/app/middleware/blacklist_middleware.py

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.config import settings_core
from backend.app.db.session import get_db
from backend.app.models.authentication import RevokedTokenModel
from backend.app.services.logging_service import logger


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
# filename: backend/app/middleware/cors_middleware.py

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

# Directory: /code/quiz-app/backend/app/core

## File: __init__.py
```py

```

## File: config.py
```py
# filename: backend/app/core/config.py

import os
from enum import Enum as PyEnum

import dotenv
import toml
from pydantic import ValidationError
from pydantic_settings import BaseSettings

from backend.app.services.logging_service import logger


class DifficultyLevel(PyEnum):
    BEGINNER = "Beginner"
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"

class SettingsCore(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    UNPROTECTED_ENDPOINTS: list

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
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
# filename: backend/app/core/jwt.py

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt

from backend.app.core.config import settings_core
from backend.app.services.logging_service import logger


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
# filename: backend/app/core/security.py

from passlib.context import CryptContext
from pydantic import SecretStr

from backend.app.services.logging_service import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    result = pwd_context.verify(plain_password, hashed_password)
    logger.debug(f"verify_password called with plain_password: {plain_password}, hashed_password: {hashed_password}")
    logger.debug(f"verify_password result: {result}")
    return result

def get_password_hash(password):
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    hashed = pwd_context.hash(password)
    logger.debug(f"get_password_hash called with password: {password}")
    logger.debug(f"get_password_hash result: {hashed}")
    return hashed

```

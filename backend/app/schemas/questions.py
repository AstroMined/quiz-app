# filename: backend/app/schemas/questions.py

from typing import List, Optional, Any

from pydantic import BaseModel, Field, validator, field_validator

from backend.app.core.config import DifficultyLevel
from backend.app.schemas.answer_choices import (
    AnswerChoiceCreateSchema,
    AnswerChoiceSchema,
)
from backend.app.schemas.question_sets import QuestionSetCreateSchema
from backend.app.schemas.question_tags import QuestionTagCreateSchema


class QuestionBaseSchema(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=10000, description="The text of the question"
    )
    difficulty: DifficultyLevel = Field(
        ..., description="The difficulty level of the question"
    )

    @validator("text")
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Question text cannot be empty or only whitespace")
        return v


class QuestionCreateSchema(QuestionBaseSchema):
    subject_ids: List[int] = Field(
        ..., min_items=1, description="IDs of the subjects associated with the question"
    )
    topic_ids: List[int] = Field(
        ..., min_items=1, description="IDs of the topics associated with the question"
    )
    subtopic_ids: List[int] = Field(
        ...,
        min_items=1,
        description="IDs of the subtopics associated with the question",
    )
    concept_ids: List[int] = Field(
        ..., min_items=1, description="IDs of the concepts associated with the question"
    )
    answer_choice_ids: Optional[List[int]] = Field(
        None, description="List of answer choice IDs associated with the question"
    )
    question_tag_ids: Optional[List[int]] = Field(
        None, description="List of tag IDs associated with the question"
    )
    question_set_ids: Optional[List[int]] = Field(
        None, description="List of question set IDs the question belongs to"
    )


class QuestionReplaceSchema(QuestionBaseSchema):
    subject_ids: List[int] = Field(
        ..., min_items=1, description="IDs of the subjects associated with the question"
    )
    topic_ids: List[int] = Field(
        ..., min_items=1, description="IDs of the topics associated with the question"
    )
    subtopic_ids: List[int] = Field(
        ...,
        min_items=1,
        description="IDs of the subtopics associated with the question",
    )
    concept_ids: List[int] = Field(
        ..., min_items=1, description="IDs of the concepts associated with the question"
    )
    answer_choice_ids: List[int] = Field(
        ...,
        min_items=1,
        description="List of answer choice IDs associated with the question",
    )
    question_tag_ids: List[int] = Field(
        ..., description="List of tag IDs associated with the question"
    )
    question_set_ids: List[int] = Field(
        ..., description="List of question set IDs the question belongs to"
    )


class QuestionUpdateSchema(BaseModel):
    text: Optional[str] = Field(
        None, min_length=1, max_length=10000, description="The text of the question"
    )
    difficulty: Optional[DifficultyLevel] = Field(
        None, description="The difficulty level of the question"
    )
    subject_ids: Optional[List[int]] = Field(
        None, description="IDs of the subjects associated with the question"
    )
    topic_ids: Optional[List[int]] = Field(
        None, description="IDs of the topics associated with the question"
    )
    subtopic_ids: Optional[List[int]] = Field(
        None, description="IDs of the subtopics associated with the question"
    )
    concept_ids: Optional[List[int]] = Field(
        None, description="IDs of the concepts associated with the question"
    )
    answer_choice_ids: Optional[List[int]] = Field(
        None, description="List of answer choice IDs associated with the question"
    )
    question_tag_ids: Optional[List[int]] = Field(
        None, description="List of tag IDs associated with the question"
    )
    question_set_ids: Optional[List[int]] = Field(
        None, description="List of question set IDs the question belongs to"
    )

    @validator("text")
    def validate_text(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Question text cannot be empty or only whitespace")
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
    text: str = Field(
        ..., min_length=1, max_length=10000, description="The text of the question"
    )
    difficulty: DifficultyLevel
    subjects: List[dict] = Field(
        ..., description="List of subjects associated with this question"
    )
    topics: List[dict] = Field(
        ..., description="List of topics associated with this question"
    )
    subtopics: List[dict] = Field(
        ..., description="List of subtopics associated with this question"
    )
    concepts: List[dict] = Field(
        ..., description="List of concepts associated with this question"
    )
    answer_choices: List[AnswerChoiceSchema] = Field(
        ..., description="List of answer choices for this question"
    )
    question_tags: List[dict] = Field(
        ..., description="List of tags associated with this question"
    )
    question_sets: List[dict] = Field(
        ..., description="List of question sets this question belongs to"
    )

    class Config:
        from_attributes = True

    @field_validator('subjects', 'topics', 'subtopics', 'concepts', 'question_tags', 'question_sets', mode='before')
    @classmethod
    def convert_sqlalchemy_objects_to_dicts(cls, value: Any) -> List[dict]:
        """Convert SQLAlchemy objects to dictionaries for JSON serialization."""
        if not value:
            return []
        
        result = []
        for item in value:
            if hasattr(item, '__dict__'):
                # Convert SQLAlchemy object to dict, excluding private attributes
                item_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
                result.append(item_dict)
            elif isinstance(item, dict):
                result.append(item)
            else:
                # Fallback for other types
                result.append({'id': getattr(item, 'id', None), 'name': getattr(item, 'name', str(item))})
        return result


class QuestionWithAnswersCreateSchema(QuestionCreateSchema):
    answer_choices: List[AnswerChoiceCreateSchema]
    question_tags: Optional[List["QuestionTagCreateSchema"]] = None
    question_sets: Optional[List["QuestionSetCreateSchema"]] = None


class QuestionWithAnswersReplaceSchema(QuestionReplaceSchema):
    answer_choice_ids: List[int] = Field(
        ..., description="IDs of existing answer choices to keep"
    )
    new_answer_choices: Optional[List[AnswerChoiceCreateSchema]] = Field(
        None, description="New answer choices to create"
    )

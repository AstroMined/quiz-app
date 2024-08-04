# filename: app/schemas/questions.py

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator, field_validator

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

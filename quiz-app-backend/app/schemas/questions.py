# filename: app/schemas/questions.py

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from app.schemas.answer_choices import AnswerChoiceSchema, AnswerChoiceCreateSchema
from app.schemas.question_tags import QuestionTagSchema


class QuestionBaseSchema(BaseModel):
    text: str
    subject_id: int
    topic_id: int
    subtopic_id: int

    class Config:
        from_attributes = True

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

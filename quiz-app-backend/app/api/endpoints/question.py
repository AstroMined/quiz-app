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
        explanation=question_db.explanation,
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
        explanation=db_question.explanation,
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

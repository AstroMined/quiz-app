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

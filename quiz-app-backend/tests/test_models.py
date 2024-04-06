# filename: tests/test_models.py
import pytest
from app.models import UserModel, SubjectModel, TopicModel, SubtopicModel, QuestionModel, AnswerChoiceModel, QuestionSetModel

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

def test_question_model(db_session):
    question_set = QuestionSetModel(name="Test Question Set")
    db_session.add(question_set)
    db_session.commit()
    question = QuestionModel(text="Test Question", question_set=question_set)
    db_session.add(question)
    db_session.commit()
    assert question.id
    assert question.text == "Test Question"
    assert question.question_set == question_set
    
# Add similar tests for other models: Topic, Subtopic, Question, AnswerChoice

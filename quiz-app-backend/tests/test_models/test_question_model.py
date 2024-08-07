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

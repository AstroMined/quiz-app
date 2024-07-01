# filename: tests/test_models.py

import pytest
from sqlalchemy.exc import SQLAlchemyError
from app.models.users import UserModel
from app.models.subjects import SubjectModel
from app.models.questions import QuestionModel
from app.models.answer_choices import AnswerChoiceModel
from app.models.roles import RoleModel
from app.models.permissions import PermissionModel
from app.services.logging_service import logger, sqlalchemy_obj_to_dict
from app.services.validation_service import validate_foreign_keys


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

def test_question_model_with_answers(db_session, test_subject, test_topic, test_subtopic):
    question = QuestionModel(text="What is the capital of France?", difficulty="Easy", 
                             subject=test_subject, topic=test_topic, subtopic=test_subtopic)
    logger.debug("Created question: %s", sqlalchemy_obj_to_dict(question))
    logger.debug("Question subject: %s", sqlalchemy_obj_to_dict(question.subject))
    logger.debug("Question topic: %s", sqlalchemy_obj_to_dict(question.topic))
    logger.debug("Question subtopic: %s", sqlalchemy_obj_to_dict(question.subtopic))
    
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    logger.debug("Added and refreshed the question: %s", sqlalchemy_obj_to_dict(question))
    
    answer = AnswerChoiceModel(text="Paris", is_correct=True, explanation="Paris is the capital and largest city of France.", question=question)
    
    db_session.add(answer)
    db_session.commit()
    db_session.refresh(answer)
    logger.debug("Added and refreshed answer: %s", sqlalchemy_obj_to_dict(answer))
    
    validate_foreign_keys(QuestionModel, db_session.connection(), question)
    validate_foreign_keys(AnswerChoiceModel, db_session.connection(), answer)
    logger.debug("Validated foreign keys")
    
    assert question.id is not None
    assert answer.id is not None
    assert answer.question == question
    logger.debug("Assertions passed")

def test_question_model_deletion_cascades_to_answers(db_session, test_subject, test_topic, test_subtopic):
    question = QuestionModel(text="What is the capital of France?", difficulty="Easy", 
                             subject=test_subject, topic=test_topic, subtopic=test_subtopic)
    logger.debug("Created question: %s", sqlalchemy_obj_to_dict(question))
    logger.debug("Question subject: %s", sqlalchemy_obj_to_dict(question.subject))
    logger.debug("Question topic: %s", sqlalchemy_obj_to_dict(question.topic))
    logger.debug("Question subtopic: %s", sqlalchemy_obj_to_dict(question.subtopic))
    
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    logger.debug("Added and refreshed the question: %s", sqlalchemy_obj_to_dict(question))
    
    answer = AnswerChoiceModel(text="Paris", is_correct=True, explanation="Paris is the capital and largest city of France.", question=question)
    
    db_session.add(answer)
    db_session.commit()
    db_session.refresh(answer)
    logger.debug("Added and refreshed answer: %s", sqlalchemy_obj_to_dict(answer))
    
    validate_foreign_keys(QuestionModel, db_session.connection(), question)
    validate_foreign_keys(AnswerChoiceModel, db_session.connection(), answer)
    logger.debug("Validated foreign keys")
    
    db_session.delete(question)
    logger.debug("Deleted question: %s", question)
    
    db_session.commit()
    logger.debug("Committed the session after deleting the question")
    
    assert db_session.query(AnswerChoiceModel).filter_by(question_id=question.id).first() is None
    logger.debug("Assertion passed: Answer choice is deleted along with the question")

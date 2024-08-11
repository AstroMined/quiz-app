
# Directory: /code/quiz-app/quiz-app-backend/tests/test_crud/

## File: test_crud_filters.py
```py
# filename: tests/test_crud_filters.py

import pytest
from pydantic import ValidationError
from app.crud.crud_filters import read_filtered_questions_from_db


def test_filter_questions_extra_invalid_parameter(db_session):
    # Test case: Extra invalid parameter
    filters = {
        "subject": "Math",
        "invalid_param": "InvalidValue"
    }
    with pytest.raises(ValidationError) as exc_info:
        read_filtered_questions_from_db(db=db_session, filters=filters)
    assert "Extra inputs are not permitted" in str(exc_info.value)

def test_filter_questions_invalid_parameter_type(db_session):
    # Test case: Invalid parameter type
    filters = {
        "subject": 123,  # Invalid type, should be a string
        "topic": "Geometry"
    }
    with pytest.raises(ValidationError) as exc_info:
        read_filtered_questions_from_db(db=db_session, filters=filters)
    assert "Input should be a valid string" in str(exc_info.value)

def test_filter_questions_invalid_tag_type(db_session):
    # Test case: Invalid tag type
    filters = {
        "question_tags": "InvalidTag"  # Invalid type, should be a list of strings
    }
    with pytest.raises(ValidationError) as exc_info:
        read_filtered_questions_from_db(db=db_session, filters=filters)
    assert "Input should be a valid list" in str(exc_info.value)

def test_filter_questions_no_filters(db_session):
    # Test case: No filters provided
    filters = {}
    result = read_filtered_questions_from_db(db=db_session, filters=filters)
    assert result is None

def test_filter_questions_invalid_subject(db_session):
    # Test case: Invalid subject filter
    filters = {
        "subject": "InvalidSubject"
    }
    result = read_filtered_questions_from_db(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_topic(db_session):
    # Test case: Invalid topic filter
    filters = {
        "topic": "InvalidTopic"
    }
    result = read_filtered_questions_from_db(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_subtopic(db_session):
    # Test case: Invalid subtopic filter
    filters = {
        "subtopic": "InvalidSubtopic"
    }
    result = read_filtered_questions_from_db(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_invalid_difficulty(db_session):
    # Test case: Invalid difficulty filter
    filters = {
        "difficulty": "InvalidDifficulty"
    }
    with pytest.raises(ValidationError) as excinfo:
        result = read_filtered_questions_from_db(db=db_session, filters=filters)
    assert "Invalid difficulty. Must be one of: Beginner, Easy, Medium, Hard, Expert" in str(excinfo.value)

def test_filter_questions_invalid_tags(db_session):
    # Test case: Invalid tags filter
    filters = {
        "question_tags": ["InvalidTag"]
    }
    result = read_filtered_questions_from_db(db=db_session, filters=filters)
    assert result == []

def test_filter_questions_valid_filters(db_session, test_questions):
    # Test case: Valid filters
    subject = test_questions[0].subject
    topic = test_questions[0].topic
    subtopic = test_questions[0].subtopic
    difficulty = test_questions[0].difficulty
    question_tags = [tag.tag for tag in test_questions[0].question_tags]

    filters = {
        "subject": subject.name,
        "topic": topic.name,
        "subtopic": subtopic.name,
        "difficulty": difficulty,
        "question_tags": question_tags
    }
    result = read_filtered_questions_from_db(db=db_session, filters=filters)
    assert len(result) == 1
    assert result[0].id == test_questions[0].id

```

## File: test_crud_question_sets.py
```py
# filename: tests/test_crud_question_sets.py

import pytest
from fastapi import HTTPException
from app.crud.crud_question_sets import create_question_set_in_db, delete_question_set_from_db, update_question_set_in_db
from app.crud.crud_subjects import create_subject_in_db
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.question_sets import QuestionSetCreateSchema, QuestionSetUpdateSchema


def test_create_question_set_in_db(db_session, test_user, test_questions, test_group):
    question_set_data = QuestionSetCreateSchema(
        db=db_session,
        name="test_create_question_set_in_db Question Set",
        is_public=True,
        creator_id=test_user.id,
        question_ids=[test_questions[0].id],
        group_ids=[test_group.id]
    )
    question_set = create_question_set_in_db(db=db_session, question_set=question_set_data)

    assert question_set.name == "test_create_question_set_in_db Question Set"
    assert question_set.is_public == True
    assert question_set.creator_id == test_user.id
    assert len(question_set.questions) == 1
    assert question_set.questions[0].id == test_questions[0].id
    assert len(question_set.groups) == 1
    assert question_set.groups[0].id == test_group.id

def test_create_question_set_duplicate_name(db_session, test_user):
    question_set_data = QuestionSetCreateSchema(
        db=db_session,
        name="Duplicate Test Set",
        is_public=True,
        creator_id=test_user.id
    )
    create_question_set_in_db(db=db_session, question_set=question_set_data)
    
    with pytest.raises(HTTPException) as exc_info:
        create_question_set_in_db(db=db_session, question_set=question_set_data)
    
    assert exc_info.value.status_code == 400
    assert "already exists" in str(exc_info.value.detail)

def test_update_question_set_in_db(db_session, test_question_set, test_questions, test_group):
    update_data = QuestionSetUpdateSchema(
        db = db_session,
        name="Updated Question Set",
        is_public=False,
        question_ids=[test_questions[0].id],
        group_ids=[test_group.id]
    )
    updated_question_set = update_question_set_in_db(db_session, test_question_set.id, update_data)

    assert updated_question_set.name == "Updated Question Set"
    assert updated_question_set.is_public == False
    assert len(updated_question_set.questions) == 1
    assert updated_question_set.questions[0].id == test_questions[0].id
    assert len(updated_question_set.groups) == 1
    assert updated_question_set.groups[0].id == test_group.id

def test_update_question_set_not_found(db_session):
    update_data = QuestionSetUpdateSchema(name="Updated Name")
    with pytest.raises(HTTPException) as exc_info:
        update_question_set_in_db(db_session, 999, update_data)
    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail)

def test_delete_question_set(db_session, test_question_set_data, test_user):
    test_question_set_data.name = "Unique Question Set for Deletion"
    question_set_data = QuestionSetCreateSchema(**test_question_set_data.dict())
    question_set = create_question_set_in_db(
        db=db_session,
        question_set=question_set_data
    )
    assert delete_question_set_from_db(db=db_session, question_set_id=question_set.id) is True, "Question set deletion failed."

def test_delete_question_set_not_found(db_session):
    question_set_id = 999  # Assuming this ID does not exist
    with pytest.raises(HTTPException) as exc_info:
        delete_question_set_from_db(db=db_session, question_set_id=question_set_id)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)


```

## File: test_crud_questions.py
```py
# filename: tests/test_crud/test_crud_questions.py

from app.schemas.questions import QuestionCreateSchema, QuestionUpdateSchema, QuestionWithAnswersCreateSchema
from app.models.questions import DifficultyLevel
from app.schemas.answer_choices import AnswerChoiceCreateSchema
from app.crud.crud_questions import create_question_in_db, read_question_from_db, update_question_in_db, delete_question_from_db, create_question_with_answers_in_db


def test_create_question_with_answers(db_session, test_subject, test_topic, test_subtopic, test_concept):
    question_data = QuestionWithAnswersCreateSchema(
        text="Test Question",
        subject_ids=[test_subject.id],
        topic_ids=[test_topic.id],
        subtopic_ids=[test_subtopic.id],
        concept_ids=[test_concept.id],
        difficulty=DifficultyLevel.EASY,
        answer_choices=[
            AnswerChoiceCreateSchema(text="Answer 1", is_correct=True, explanation="Explanation 1"),
            AnswerChoiceCreateSchema(text="Answer 2", is_correct=False, explanation="Explanation 2"),
        ]
    )
    question = create_question_with_answers_in_db(db_session, question_data.model_dump())
    assert question.text == "Test Question"
    assert question.difficulty == "Easy"
    assert len(question.answer_choices) == 2
    assert question.answer_choices[0].text == "Answer 1"
    assert question.answer_choices[1].text == "Answer 2"

def test_read_question_detailed(db_session, test_questions):
    question = read_question_from_db(db_session, test_questions[0].id)
    assert question.text == test_questions[0].text
    assert question.difficulty == test_questions[0].difficulty
    assert question.subject == test_questions[0].subject.name
    assert question.topic == test_questions[0].topic.name
    assert question.subtopic == test_questions[0].subtopic.name
    assert question.concept == test_questions[0].concept.name
    assert len(question.answer_choices) == len(test_questions[0].answer_choices)

def test_update_question_with_answer_choices(db_session, test_questions):
    update_data = QuestionUpdateSchema(
        text="Updated Question",
        difficulty=DifficultyLevel.MEDIUM,
        answer_choice_ids=[test_questions[0].answer_choices[0].id]
    )
    updated_question = update_question_in_db(db_session, test_questions[0].id, update_data)
    assert updated_question.text == "Updated Question"
    assert updated_question.difficulty == "Medium"
    assert len(updated_question.answer_choices) == 1

def test_get_nonexistent_question(db_session):
    """Test retrieval of a non-existent question."""
    question = read_question_from_db(db_session, question_id=999)
    assert question is None, "Fetching a non-existent question should return None."

def test_delete_nonexistent_question(db_session):
    """Test deletion of a non-existent question."""
    result = delete_question_from_db(db_session, question_id=999)
    assert result is False, "Deleting a non-existent question should return False."

def test_update_question_not_found(db_session):
    """
    Test updating a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    updated_question = update_question_in_db(db_session, question_id, question_update)
    assert updated_question is None

def test_delete_question_not_found(db_session):
    """
    Test deleting a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    deleted = delete_question_from_db(db_session, question_id)
    assert deleted is False


```

## File: test_crud_roles.py
```py
# filename: tests/test_crud/test_crud_roles.py

import pytest
from fastapi import HTTPException
from app.crud.crud_roles import create_role_in_db, read_role_from_db, read_roles_from_db, update_role_in_db, delete_role_from_db
from app.schemas.roles import RoleCreateSchema, RoleUpdateSchema
from app.services.logging_service import logger
from app.crud.crud_permissions import read_permissions_from_db


def test_create_role_in_db(db_session, test_permissions):
    read_permissions = read_permissions_from_db(db_session, limit=2)  # Retrieve the first two permissions from the database
    logger.debug("Permissions read: %s", read_permissions)
    permissions_id_list = [p.id for p in read_permissions]
    logger.debug("Permissions list: %s", permissions_id_list)
    permissions_name_list = [p.name for p in read_permissions]
    logger.debug("Permissions name list: %s", permissions_name_list)
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=permissions_name_list)
    logger.debug("Role data: %s", role_data)
    role = create_role_in_db(db_session, role_data)
    logger.debug("Role created: %s", role)
    assert role.name == "Test Role"
    assert role.description == "Test role description"
    logger.debug("Role permissions: %s", role.permissions)
    assert len(role.permissions) == 2

def test_read_role_from_db(db_session):
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=[])
    created_role = create_role_in_db(db_session, role_data)
    
    read_role = read_role_from_db(db_session, created_role.id)
    assert read_role.id == created_role.id
    assert read_role.name == "Test Role"

def test_read_role_from_db_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        read_role_from_db(db_session, 999)  # Assuming 999 is not a valid role id
    assert exc_info.value.status_code == 404

def test_read_roles_from_db(db_session):
    role_data1 = RoleCreateSchema(name="Test Role 1", description="Test role description 1", permissions=[])
    role_data2 = RoleCreateSchema(name="Test Role 2", description="Test role description 2", permissions=[])
    create_role_in_db(db_session, role_data1)
    create_role_in_db(db_session, role_data2)

    roles = read_roles_from_db(db_session)
    assert len(roles) >= 2

def test_update_role_in_db(db_session, test_permissions):
    permissions = read_permissions_from_db(db_session, limit=2)  # Retrieve the first two permissions from the database
    logger.debug("Permissions read: %s", permissions)
    permissions_id_list = [p.id for p in permissions]
    logger.debug("Permissions list: %s", permissions_id_list)
    permissions_name_list = [p.name for p in permissions]
    logger.debug("Permissions name list: %s", permissions_name_list)
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=permissions_name_list)
    logger.debug("Role data: %s", role_data)
    created_role = create_role_in_db(db_session, role_data)
    logger.debug("Created role: %s", created_role)
    logger.debug("Created role permissions: %s", created_role.permissions)

    db_session.rollback()  # Roll back the previous transaction

    update_data = RoleUpdateSchema(name="Updated Role", description="Updated description", permissions=permissions_name_list)
    logger.debug("Update data: %s", update_data)
    updated_role = update_role_in_db(db_session, created_role.id, update_data)
    logger.debug("Updated role: %s", updated_role)
    logger.debug("Updated role permissions: %s", updated_role.permissions)

    assert updated_role.name == "Updated Role"
    assert updated_role.description == "Updated description"
    assert len(updated_role.permissions) == 2

def test_delete_role_from_db(db_session):
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=[])
    created_role = create_role_in_db(db_session, role_data)

    assert delete_role_from_db(db_session, created_role.id) == True

    with pytest.raises(HTTPException) as exc_info:
        read_role_from_db(db_session, created_role.id)
    assert exc_info.value.status_code == 404

```

## File: test_crud_subjects.py
```py
# filename: tests/test_crud_subjects.py

from app.schemas.subjects import SubjectCreateSchema
from app.crud.crud_subjects import create_subject_in_db


def test_create_subject(db_session, test_discipline):
    subject_data = SubjectCreateSchema(
        name="Test Subject",
        discipline_id=test_discipline.id
    )
    created_subject = create_subject_in_db(db=db_session, subject=subject_data)
    assert created_subject.name == "Test Subject"
    assert created_subject.discipline_id == test_discipline.id

```

## File: test_crud_user.py
```py
# filename: tests/test_crud_user.py

from app.crud.crud_user import delete_user_from_db, create_user_in_db, update_user_in_db
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.services.authentication_service import authenticate_user
from app.core.security import get_password_hash

def test_remove_user_not_found(db_session):
    user_id = 999  # Assuming this ID does not exist
    removed_user = delete_user_from_db(db_session, user_id)
    assert removed_user is None

def test_authenticate_user(db_session, random_username, test_role):
    hashed_password = get_password_hash("AuthPassword123!")
    user_data = UserCreateSchema(
        username=random_username,
        password=hashed_password,
        email=f"{random_username}@example.com",
        role=test_role.name
    )
    create_user_in_db(db_session, user_data)
    authenticated_user = authenticate_user(db_session, username=random_username, password="AuthPassword123!")
    assert authenticated_user
    assert authenticated_user.username == random_username

def test_create_user(db_session, random_username, test_role):
    user_data = UserCreateSchema(
        username=random_username,
        password="NewPassword123!",
        email=f"{random_username}@example.com",
        role=test_role.name
    )
    created_user = create_user_in_db(db_session, user_data)
    assert created_user.username == random_username

def test_update_user(db_session, test_user):
    updated_data = UserUpdateSchema(
        db = db_session,
        username="updated_username"
    )
    updated_user = update_user_in_db(db=db_session, user_id=test_user.id, updated_user=updated_data)
    assert updated_user.username == "updated_username"

```

## File: test_crud_user_responses.py
```py
# filename: tests/test_crud/test_crud_user_responses.py

from datetime import datetime, timezone
from app.schemas.user_responses import UserResponseCreateSchema, UserResponseUpdateSchema
from app.crud.crud_user_responses import create_user_response_in_db, update_user_response_in_db, delete_user_response_from_db
from app.models.user_responses import UserResponseModel
from app.services.logging_service import logger, sqlalchemy_obj_to_dict

def test_create_and_retrieve_user_response(db_session, test_user_with_group, test_questions):
    response_data = UserResponseCreateSchema(
        db=db_session,
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[0].id
    )
    created_response = create_user_response_in_db(db=db_session, user_response=response_data)
    assert created_response is not None, "Failed to create user response."
    assert created_response.user_id == test_user_with_group.id
    assert created_response.question_id == test_questions[0].id
    assert created_response.answer_choice_id == test_questions[0].answer_choices[0].id
    assert created_response.timestamp is not None

def test_update_user_response(db_session, test_user_with_group, test_questions):
    response_data = UserResponseCreateSchema(
        db=db_session,
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[0].id
    )
    created_response = create_user_response_in_db(db=db_session, user_response=response_data)
    logger.debug("Created response: %s", sqlalchemy_obj_to_dict(created_response))
    
    update_data = UserResponseUpdateSchema(
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[1].id
    )
    logger.debug("Update data: %s", update_data.model_dump())
    updated_response = update_user_response_in_db(db=db_session, user_response_id=created_response.id, user_response=update_data)
    logger.debug("Updated response: %s", sqlalchemy_obj_to_dict(updated_response))
    assert updated_response.answer_choice_id == test_questions[0].answer_choices[1].id
    assert updated_response.timestamp is not None

def test_delete_user_response(db_session, test_user_with_group, test_questions):
    response_data = UserResponseCreateSchema(
        db=db_session,
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[0].id
    )
    created_response = create_user_response_in_db(db=db_session, user_response=response_data)
    delete_user_response_from_db(db=db_session, user_response_id=created_response.id)
    deleted_response = db_session.query(UserResponseModel).filter(UserResponseModel.id == created_response.id).first()
    assert deleted_response is None

```

# filename: backend/tests/models/test_user_model.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.groups import GroupModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel


def test_user_model_creation(db_session, test_model_permissions, test_model_default_role):
    # Use existing default role instead of creating a new one
    import uuid
    unique_username = f"testuser_{str(uuid.uuid4())[:8]}"
    unique_email = f"testuser_{str(uuid.uuid4())[:8]}@example.com"

    user = UserModel(
        username=unique_username,
        email=unique_email,
        hashed_password="hashed_password",
        role_id=test_model_default_role.id,
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == unique_username
    assert user.email == unique_email
    assert user.hashed_password == "hashed_password"
    assert user.is_active == True
    assert user.is_admin == False
    assert user.role.name == "user"


def test_user_model_unique_constraints(db_session):
    import uuid
    
    # Create a role first
    unique_role_name = f"user_{str(uuid.uuid4())[:8]}"
    role = RoleModel(name=unique_role_name, description="Regular user")
    db_session.add(role)
    db_session.commit()
    
    # Store role ID to avoid accessing potentially detached object
    role_id = role.id
    
    # Test 1: Username uniqueness constraint
    unique_id1 = str(uuid.uuid4())[:8]
    base_username1 = f"testuser_{unique_id1}"
    
    user1 = UserModel(
        username=base_username1,
        email=f"email1_{unique_id1}@example.com",
        hashed_password="hashed_password",
        role_id=role_id,
    )
    db_session.add(user1)
    db_session.commit()

    # Try to create another user with the same username
    with pytest.raises(IntegrityError):
        user2 = UserModel(
            username=base_username1,  # Same username should fail
            email=f"email2_{unique_id1}@example.com",
            hashed_password="hashed_password",
            role_id=role_id,
        )
        db_session.add(user2)
        db_session.commit()

    # Clean up failed transaction and clear identity map to avoid conflicts
    db_session.rollback()
    db_session.expunge_all()  # Clear all objects from the session identity map

    # Test 2: Email uniqueness constraint  
    unique_id2 = str(uuid.uuid4())[:8]
    base_email2 = f"email_{unique_id2}@example.com"
    
    user3 = UserModel(
        username=f"username1_{unique_id2}",
        email=base_email2,
        hashed_password="hashed_password",
        role_id=role_id,
    )
    db_session.add(user3)
    db_session.commit()

    # Try to create another user with the same email
    with pytest.raises(IntegrityError):
        user4 = UserModel(
            username=f"username2_{unique_id2}",
            email=base_email2,  # Same email should fail
            hashed_password="hashed_password",
            role_id=role_id,
        )
        db_session.add(user4)
        db_session.commit()
    
    # Clean up failed transaction and clear identity map
    db_session.rollback()
    db_session.expunge_all()  # Clear all objects from the session identity map


def test_user_model_relationships(
    db_session, test_model_group, test_model_question_set, test_model_default_role
):
    # Use existing default role instead of creating a new one
    import uuid
    unique_username = f"testuser_{str(uuid.uuid4())[:8]}"
    unique_email = f"testuser_{str(uuid.uuid4())[:8]}@example.com"

    user = UserModel(
        username=unique_username,
        email=unique_email,
        hashed_password="hashed_password",
        role_id=test_model_default_role.id,
    )
    db_session.add(user)
    db_session.commit()

    # Test group relationship
    user.groups.append(test_model_group)
    db_session.commit()
    assert test_model_group in user.groups

    # Test created_groups relationship
    unique_group_name = f"Created Group {str(uuid.uuid4())[:8]}"
    created_group = GroupModel(name=unique_group_name, creator=user)
    db_session.add(created_group)
    db_session.commit()
    assert created_group in user.created_groups

    # Test created_question_sets relationship
    unique_qs_name = f"Created Question Set {str(uuid.uuid4())[:8]}"
    created_question_set = QuestionSetModel(name=unique_qs_name, creator=user)
    db_session.add(created_question_set)
    db_session.commit()
    assert created_question_set in user.created_question_sets


def test_user_model_repr(db_session, test_model_default_role):
    # Use existing default role instead of creating a new one
    import uuid
    unique_username = f"testuser_{str(uuid.uuid4())[:8]}"
    unique_email = f"testuser_{str(uuid.uuid4())[:8]}@example.com"

    user = UserModel(
        username=unique_username,
        email=unique_email,
        hashed_password="hashed_password",
        role_id=test_model_default_role.id,
    )
    db_session.add(user)
    db_session.commit()

    expected_repr = f"<User(id={user.id}, username='{unique_username}', email='{unique_email}', role_id='{test_model_default_role.id}')>"
    assert repr(user) == expected_repr

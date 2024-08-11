# filename: tests/models/test_user_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.models.groups import GroupModel
from app.models.question_sets import QuestionSetModel

def test_user_model_creation(db_session, test_model_permissions):
    # Create a role first
    role = RoleModel(name="user", description="Regular user")
    db_session.add(role)
    db_session.commit()

    user = UserModel(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashed_password",
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    assert user.hashed_password == "hashed_password"
    assert user.is_active == True
    assert user.is_admin == False
    assert user.role.name == "user"

def test_user_model_unique_constraints(db_session):
    # Create a role first
    role = RoleModel(name="user", description="Regular user")
    db_session.add(role)
    db_session.commit()

    user1 = UserModel(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashed_password",
        role_id=role.id
    )
    db_session.add(user1)
    db_session.commit()

    # Try to create another user with the same username
    with pytest.raises(IntegrityError):
        user2 = UserModel(
            username="testuser",
            email="testuser2@example.com",
            hashed_password="hashed_password",
            role_id=role.id
        )
        db_session.add(user2)
        db_session.commit()

    db_session.rollback()

    # Try to create another user with the same email
    with pytest.raises(IntegrityError):
        user3 = UserModel(
            username="testuser3",
            email="testuser@example.com",
            hashed_password="hashed_password",
            role_id=role.id
        )
        db_session.add(user3)
        db_session.commit()

def test_user_model_relationships(db_session, test_model_group, test_model_question_set):
    # Create a role first
    role = RoleModel(name="user", description="Regular user")
    db_session.add(role)
    db_session.commit()

    user = UserModel(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashed_password",
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()

    # Test group relationship
    user.groups.append(test_model_group)
    db_session.commit()
    assert test_model_group in user.groups

    # Test created_groups relationship
    created_group = GroupModel(name="Created Group", creator=user)
    db_session.add(created_group)
    db_session.commit()
    assert created_group in user.created_groups

    # Test created_question_sets relationship
    created_question_set = QuestionSetModel(name="Created Question Set", creator=user)
    db_session.add(created_question_set)
    db_session.commit()
    assert created_question_set in user.created_question_sets

def test_user_model_repr(db_session):
    # Create a role first
    role = RoleModel(name="user", description="Regular user")
    db_session.add(role)
    db_session.commit()

    user = UserModel(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashed_password",
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()

    assert repr(user) == f"<User(id={user.id}, username='testuser', email='testuser@example.com', role_id='1')>"

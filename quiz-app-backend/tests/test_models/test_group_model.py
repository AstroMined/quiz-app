# filename: tests/models/test_group_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.groups import GroupModel
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.models.question_sets import QuestionSetModel
from app.models.leaderboard import LeaderboardModel
from app.models.time_period import TimePeriodModel

def test_group_model_creation(db_session, test_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    assert group.id is not None
    assert group.name == "Test Group"
    assert group.description == "This is a test group"
    assert group.creator_id == test_user.id

def test_group_model_unique_constraint(db_session, test_user):
    group1 = GroupModel(
        name="Unique Group",
        description="This is a unique group",
        creator_id=test_user.id
    )
    db_session.add(group1)
    db_session.commit()

    # Try to create another group with the same name
    group2 = GroupModel(
        name="Unique Group",
        description="This is another group with the same name",
        creator_id=test_user.id
    )
    db_session.add(group2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()  # Roll back the failed transaction

    # Assert that only one group with this name exists
    groups = db_session.query(GroupModel).filter_by(name="Unique Group").all()
    assert len(groups) == 1
    assert groups[0].description == "This is a unique group"

def test_group_user_relationship(db_session, test_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    group.users.append(test_user)
    db_session.commit()

    assert test_user in group.users
    assert group in test_user.groups

def test_group_creator_relationship(db_session, test_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    assert group.creator == test_user
    assert group in test_user.created_groups

def test_group_question_set_relationship(db_session, test_user, test_question_set):
    group = GroupModel(
        name="test_group_question_set_relationship Test Group",
        description="This is a group for the test_group_question_set_relationship test",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    group.question_sets.append(test_question_set)
    db_session.commit()

    assert test_question_set in group.question_sets
    assert group in test_question_set.groups

def test_group_leaderboard_relationship(db_session, test_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    leaderboard = LeaderboardModel(
        user_id=test_user.id,
        group_id=group.id,
        score=100,
        time_period_id=7
    )
    db_session.add(leaderboard)
    db_session.commit()

    assert leaderboard in group.leaderboards
    assert group == leaderboard.group

def test_group_model_repr(db_session, test_user):
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_user.id
    )
    db_session.add(group)
    db_session.commit()

    assert repr(group) == f"<GroupModel(id={group.id}, name='Test Group', creator_id={test_user.id}, is_active={test_user.is_active})>"
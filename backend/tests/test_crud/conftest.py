# filename: backend/tests/test_crud/conftest.py

import pytest

from backend.app.core.security import get_password_hash
from backend.app.services.logging_service import logger


@pytest.fixture(scope="function")
def test_user_data(test_schema_user):
    user_data = test_schema_user.model_dump()
    logger.debug("test_user_data: %s", user_data)
    user_data["hashed_password"] = get_password_hash(user_data["password"])
    return user_data


@pytest.fixture(scope="function")
def test_group_data(test_schema_group):
    logger.debug("test_group_data: %s", test_schema_group.model_dump())
    return test_schema_group.model_dump()


@pytest.fixture(scope="function")
def test_role_data(test_schema_role):
    logger.debug("test_role_data: %s", test_schema_role.model_dump())
    return test_schema_role.model_dump()


@pytest.fixture(scope="function")
def test_question_set_data(test_schema_question_set):
    logger.debug("test_question_set_data: %s", test_schema_question_set.model_dump())
    return test_schema_question_set.model_dump()

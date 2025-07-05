# filename: backend/tests/test_crud/test_crud_authentication.py

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import ExpiredSignatureError

from backend.app.core.jwt import create_access_token, decode_access_token
from backend.app.crud.authentication import (
    create_revoked_token_in_db,
    is_token_revoked,
    read_revoked_token_from_db,
    revoke_all_tokens_for_user,
    revoke_token,
)
from backend.app.models.authentication import RevokedTokenModel
from backend.app.services.logging_service import logger


def test_create_revoked_token_in_db(db_session, test_model_user):
    import uuid
    jti = f"test_jti_{str(uuid.uuid4())[:8]}"
    token = f"test_token_{str(uuid.uuid4())[:8]}"
    expires_at = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())

    revoked_token = create_revoked_token_in_db(
        db_session, jti, token, test_model_user.id, expires_at
    )

    assert revoked_token.jti == jti
    assert revoked_token.token == token
    assert revoked_token.user_id == test_model_user.id
    assert revoked_token.expires_at.replace(
        tzinfo=timezone.utc
    ) == datetime.fromtimestamp(expires_at, tz=timezone.utc)


def test_read_revoked_token_from_db(db_session, test_model_user):
    import uuid
    jti = f"test_jti_{str(uuid.uuid4())[:8]}"
    token = f"test_token_{str(uuid.uuid4())[:8]}"
    expires_at = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())

    create_revoked_token_in_db(db_session, jti, token, test_model_user.id, expires_at)

    retrieved_token = read_revoked_token_from_db(db_session, token)
    assert retrieved_token is not None
    assert retrieved_token.token == token


def test_is_token_revoked(db_session, test_model_user):
    access_token = create_access_token({"sub": test_model_user.username}, db_session)

    # Token should not be revoked initially
    assert not is_token_revoked(db_session, access_token)

    # Revoke the token
    revoke_token(db_session, access_token)

    # Token should now be revoked
    assert is_token_revoked(db_session, access_token)


def test_revoke_all_tokens_for_user(db_session, test_model_user):
    # Create some active tokens for the user
    token1 = create_access_token({"sub": test_model_user.username}, db_session)
    token2 = create_access_token({"sub": test_model_user.username}, db_session)

    active_tokens = [token1, token2]

    # Revoke all tokens for the user
    revoke_all_tokens_for_user(db_session, test_model_user.id, active_tokens)

    # Check if all tokens are revoked
    assert is_token_revoked(db_session, token1)
    assert is_token_revoked(db_session, token2)


def test_revoke_token(db_session, test_model_user):
    access_token = create_access_token({"sub": test_model_user.username}, db_session)

    # Token should not be revoked initially
    assert not is_token_revoked(db_session, access_token)

    # Revoke the token
    revoke_token(db_session, access_token)

    # Token should now be revoked
    assert is_token_revoked(db_session, access_token)


def test_revoke_token_twice(db_session, test_model_user):
    access_token = create_access_token({"sub": test_model_user.username}, db_session)

    # Revoke the token
    revoke_token(db_session, access_token)

    # Attempt to revoke the same token again (should not raise an error)
    revoke_token(db_session, access_token)

    # Token should still be revoked
    assert is_token_revoked(db_session, access_token)


def test_revoke_expired_token(db_session, test_model_user):
    # Create an expired token
    expired_token = create_access_token(
        {"sub": test_model_user.username}, db_session, expires_delta=timedelta(seconds=-1)
    )

    # Attempt to revoke the expired token (should not raise an error)
    revoke_token(db_session, expired_token)

    # The expired token should throw ExpiredSignatureError when checked
    # (expired tokens are different from revoked tokens)
    with pytest.raises(ExpiredSignatureError):
        is_token_revoked(db_session, expired_token)


def test_create_token_with_nonexistent_user(db_session):
    with pytest.raises(ValueError):
        create_access_token({"sub": "nonexistent_user"}, db_session)


def test_is_token_revoked_with_invalid_token(db_session):
    # Create an invalid token
    invalid_token = "invalid.token.format"

    # The invalid token should fail the check
    with pytest.raises(HTTPException) as exc_info:
        is_token_revoked(db_session, invalid_token)
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail


def test_revoke_all_tokens_for_user_with_no_active_tokens(db_session, test_model_user):
    # Attempt to revoke all tokens when there are no active tokens
    revoke_all_tokens_for_user(db_session, test_model_user.id, [])

    # No error should be raised, and no new tokens should be in the revoked_tokens table
    assert (
        db_session.query(RevokedTokenModel)
        .filter_by(user_id=test_model_user.id)
        .count()
        == 0
    )


def test_is_token_revoked_with_old_token(db_session, test_model_user):
    # Create a token with expiration date in the past
    old_token = create_access_token(
        {"sub": test_model_user.username}, db_session, expires_delta=timedelta(days=-7)
    )
    with pytest.raises(ExpiredSignatureError) as exc_info:
        decode_access_token(old_token, db_session)
    assert "Signature has expired" in str(exc_info.value)

    # The old token should throw ExpiredSignatureError when checked for revocation
    # (expired tokens are different from revoked tokens)
    with pytest.raises(ExpiredSignatureError):
        is_token_revoked(db_session, old_token)

    # Create a new token
    new_token = create_access_token({"sub": test_model_user.username}, db_session)

    # The new token should not be revoked
    assert not is_token_revoked(db_session, new_token)

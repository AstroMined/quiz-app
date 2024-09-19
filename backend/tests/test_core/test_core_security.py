# filename: backend/tests/test_core/test_core_security.py

import pytest
from pydantic import SecretStr
from backend.app.core.security import verify_password, get_password_hash

def test_password_hashing():
    password = "testpassword123"
    hashed_password = get_password_hash(password)
    
    assert hashed_password != password
    assert verify_password(password, hashed_password)

def test_password_verification():
    password = "testpassword123"
    wrong_password = "wrongpassword123"
    hashed_password = get_password_hash(password)
    
    assert verify_password(password, hashed_password)
    assert not verify_password(wrong_password, hashed_password)

def test_get_password_hash_with_secret_str():
    password = SecretStr("testpassword123")
    hashed_password = get_password_hash(password)
    
    assert hashed_password != password.get_secret_value()
    assert verify_password(password.get_secret_value(), hashed_password)

def test_verify_password_with_incorrect_hash():
    password = "testpassword123"
    # This is a valid bcrypt hash for a different password
    incorrect_hash = "$2b$12$K8PdA2lHSM2uokGn2hhSAuvZ3DQyM6vhvGfOWexCVE5cHBF5pZ.Jm"
    
    assert not verify_password(password, incorrect_hash)

@pytest.mark.parametrize("password", [
    "short",
    "longerpasswordbutnospecialchars123",
    "Password123!",
    "VeryLongPasswordWithSpecialChars123!@#",
])
def test_password_hashing_various_inputs(password):
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
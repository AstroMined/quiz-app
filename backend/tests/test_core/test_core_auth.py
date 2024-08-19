# filename: backend/tests/test_core_auth.py

from backend.app.services.user_service import oauth2_scheme


def test_oauth2_scheme():
    """
    Test the OAuth2 authentication scheme.
    """
    assert oauth2_scheme.scheme_name == "OAuth2PasswordBearer"
    assert oauth2_scheme.auto_error is True

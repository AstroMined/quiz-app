# filename: backend/tests/test_core/test_core_init.py

from backend.app.core import config, jwt, security

def test_core_config_import():
    assert hasattr(config, 'settings_core')
    assert config.settings_core is not None

def test_core_jwt_imports():
    assert hasattr(jwt, 'create_access_token')
    assert callable(jwt.create_access_token)
    assert hasattr(jwt, 'decode_access_token')
    assert callable(jwt.decode_access_token)

def test_core_security_imports():
    assert hasattr(security, 'verify_password')
    assert callable(security.verify_password)
    assert hasattr(security, 'get_password_hash')
    assert callable(security.get_password_hash)
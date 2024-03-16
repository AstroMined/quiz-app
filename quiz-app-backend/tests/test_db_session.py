# filename: tests/test_db_session.py

def test_database_session_lifecycle(db_session):
    """Test the lifecycle of a database session."""
    # Assuming 'db_session' is already using the correct test database ('test.db') as configured in conftest.py
    assert db_session.bind.url.__to_string__() == "sqlite:///./test.db", "Not using the test database"

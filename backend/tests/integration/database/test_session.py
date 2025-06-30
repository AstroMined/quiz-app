# filename: backend/tests/test_db_session.py

from sqlalchemy import inspect


def test_revoked_tokens_table_exists(db_session):
    inspector = inspect(db_session.bind)
    available_tables = inspector.get_table_names()
    assert (
        "revoked_tokens" in available_tables
    ), "Table 'revoked_tokens' does not exist in the test database."


def test_database_session_lifecycle(db_session):
    """Test the lifecycle of a database session."""
    # With the new transaction-based architecture, db_session.bind is a Connection, not an Engine
    # We need to access the engine through the connection
    assert (
        db_session.bind.engine.url.__to_string__() == "sqlite:///:memory:"
    ), "Not using the in-memory test database"

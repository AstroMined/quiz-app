# filename: tests/test_crud_user.py
from app.crud import crud_user

def test_remove_user_not_found(db_session):
    """
    Test removing a user that does not exist.
    """
    user_id = 999  # Assuming this ID does not exist
    removed_user = crud_user.remove_user_crud(db_session, user_id)
    assert removed_user is None

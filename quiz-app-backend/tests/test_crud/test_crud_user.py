# filename: tests/test_crud_user.py
from app.crud import delete_user_crud, create_user_crud, update_user_crud
from app.schemas import UserCreateSchema, UserUpdateSchema
from app.services import authenticate_user

def test_remove_user_not_found(db_session):
    """
    Test removing a user that does not exist.
    """
    user_id = 999  # Assuming this ID does not exist
    removed_user = delete_user_crud(db_session, user_id)
    assert removed_user is None

def test_authenticate_user(db_session, random_username):
    user_data = UserCreateSchema(
        username=random_username,
        password="AuthPassword123!",
        email=f"{random_username}@example.com"
    )
    create_user_crud(db_session, user_data)
    authenticated_user = authenticate_user(db_session, username=random_username, password="AuthPassword123!")
    assert authenticated_user
    assert authenticated_user.username == random_username

def test_create_user(db_session, random_username):
    user_data = UserCreateSchema(
        username=random_username,
        password="NewPassword123!",
        email=f"{random_username}@example.com"
    )
    created_user = create_user_crud(db_session, user_data)
    assert created_user.username == random_username

def test_update_user(db_session, test_user):
    updated_data = UserUpdateSchema(username="updated_username")
    updated_user = update_user_crud(db=db_session, user_id=test_user.id, updated_user=updated_data)
    assert updated_user.username == "updated_username"
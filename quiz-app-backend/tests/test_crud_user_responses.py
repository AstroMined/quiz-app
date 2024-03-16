# filename: tests/test_crud_user_responses.py
from app.schemas import UserResponseCreate
from app.crud import crud_user_responses

def test_create_and_retrieve_user_response(db_session, test_user, test_question):
    """Test creation and retrieval of a user response."""
    response_data = UserResponseCreate(user_id=test_user.id, question_id=test_question.id, answer_choice_id=1, is_correct=True)
    created_response = crud_user_responses.create_user_response(db=db_session, user_response=response_data)
    assert created_response is not None, "Failed to create user response."
    assert created_response.is_correct == True, "User response correctness does not match."

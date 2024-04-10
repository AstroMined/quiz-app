# filename: tests/test_crud_user_responses.py
from app.schemas import UserResponseCreateSchema
from app.crud import crud_user_responses

def test_create_and_retrieve_user_response(db_session, test_user, test_question, test_answer_choice_1):
    """Test creation and retrieval of a user response."""
    response_data = UserResponseCreateSchema(user_id=test_user.id, question_id=test_question.id, answer_choice_id=test_answer_choice_1.id, is_correct=True)
    created_response = crud_user_responses.create_user_response_crud(db=db_session, user_response=response_data)
    assert created_response is not None, "Failed to create user response."
    assert created_response.is_correct is True, "User response correctness does not match."

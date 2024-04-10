# filename: tests/test_crud_questions.py
from app.schemas import (
    QuestionCreateSchema,
    QuestionUpdateSchema,
    AnswerChoiceCreateSchema,
    SubjectCreateSchema,
    TopicCreateSchema
)    
from app.crud import (
    create_question_crud,
    get_question_crud,
    update_question_crud,
    delete_question_crud,
    create_topic_crud,
    create_subject_crud
)

def test_create_and_retrieve_question(db_session, test_question_set, test_subtopic):
    """Test creation and retrieval of a question."""
    test_question_set.name = "Unique Question Set for Question Creation"
    subject_data = SubjectCreateSchema(name="Test Subject")
    subject = create_subject_crud(db_session, subject_data)
    topic_data = TopicCreateSchema(name="Test Topic", subject_id=subject.id)
    topic = create_topic_crud(db_session, topic_data)
    answer_choice_1 = AnswerChoiceCreateSchema(text="Test Answer 1", is_correct=True)
    answer_choice_2 = AnswerChoiceCreateSchema(text="Test Answer 2", is_correct=False)
    question_data = QuestionCreateSchema(
        text="Sample Question?",
        subject_id=subject.id,
        topic_id=topic.id,
        subtopic_id=test_subtopic.id,
        question_set_id=test_question_set.id,
        difficulty="Easy",
        answer_choices=[answer_choice_1, answer_choice_2],
        explanation="Test Explanation"
    )
    created_question = create_question_crud(db=db_session, question=question_data)
    retrieved_question = get_question_crud(db_session, question_id=created_question.id)
    assert retrieved_question is not None, "Failed to retrieve created question."
    assert retrieved_question.text == "Sample Question?", "Question text does not match."
    assert retrieved_question.difficulty == "Easy", "Question difficulty level does not match."
    assert len(retrieved_question.answer_choices) == 2, "Answer choices not created correctly."

def test_get_nonexistent_question(db_session):
    """Test retrieval of a non-existent question."""
    question = get_question_crud(db_session, question_id=999)
    assert question is None, "Fetching a non-existent question should return None."

def test_delete_nonexistent_question(db_session):
    """Test deletion of a non-existent question."""
    result = delete_question_crud(db_session, question_id=999)
    assert result is False, "Deleting a non-existent question should return False."

def test_update_question_not_found(db_session):
    """
    Test updating a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    updated_question = update_question_crud(db_session, question_id, question_update)
    assert updated_question is None

def test_delete_question_not_found(db_session):
    """
    Test deleting a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    deleted = delete_question_crud(db_session, question_id)
    assert deleted is False

def test_update_question_crud(db_session, test_question, test_question_set):
    question_update = QuestionUpdateSchema(
        text="Updated Question",
        difficulty="Medium",
        explanation="Updated Explanation",
        question_set_ids=[test_question_set.id]
    )
    updated_question = update_question_crud(db_session, test_question.id, question_update)

    assert updated_question.text == "Updated Question"
    assert updated_question.difficulty == "Medium"
    assert updated_question.explanation == "Updated Explanation"
    assert test_question_set.id in updated_question.question_set_ids

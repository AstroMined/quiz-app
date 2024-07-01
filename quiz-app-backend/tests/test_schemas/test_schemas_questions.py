# filename: tests/test_schemas.py

from app.schemas.questions import QuestionCreateSchema


def test_question_create_schema(
    db_session,
    test_subtopic,
    test_question_set,
    test_subject,
    test_topic
):
    question_data = {
        "db": db_session,
        "text": "Test question",
        "subject_id": test_subject.id,
        "topic_id": test_topic.id,
        "subtopic_id": test_subtopic.id,
        "question_set_ids": [test_question_set.id],
        "difficulty": "Easy",
        "answer_choices": [
            {"text": "Answer 1", "is_correct": True, "explanation": "Test explanation 1"},
            {"text": "Answer 2", "is_correct": False, "explanation": "Test explanation 2"}
        ]
    }
    question_schema = QuestionCreateSchema(**question_data)
    assert question_schema.text == "Test question"
    assert question_schema.subject_id == 1
    assert question_schema.topic_id == 1
    assert question_schema.subtopic_id == 1
    assert question_schema.question_set_ids == [1]
    assert question_schema.difficulty == "Easy"
    assert len(question_schema.answer_choices) == 2

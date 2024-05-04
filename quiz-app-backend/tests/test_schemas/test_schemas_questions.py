# filename: tests/test_schemas.py

from app.schemas import QuestionCreateSchema

def test_question_create_schema():
    question_data = {
        "text": "Test question",
        "subject_id": 1,
        "topic_id": 1,
        "subtopic_id": 1,
        "question_set_ids": [1],
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

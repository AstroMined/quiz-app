# filename: tests/test_api_filters.py

from app.models import (
    SubjectModel,
    TopicModel,
    SubtopicModel,
    QuestionTagModel,
    QuestionSetModel,
    QuestionModel
)

def test_setup_filter_questions_data(db_session, setup_filter_questions_data):
    # Check if the required data is created in the database
    assert db_session.query(SubjectModel).filter(SubjectModel.name == "Math").first() is not None
    assert db_session.query(SubjectModel).filter(SubjectModel.name == "Science").first() is not None
    assert db_session.query(TopicModel).filter(TopicModel.name == "Algebra").first() is not None
    assert db_session.query(TopicModel).filter(TopicModel.name == "Geometry").first() is not None
    assert db_session.query(TopicModel).filter(TopicModel.name == "Physics").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Linear Equations").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Quadratic Equations").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Triangles").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Mechanics").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "equations").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "solving").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "geometry").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "physics").first() is not None
    assert db_session.query(QuestionSetModel).filter(QuestionSetModel.name == "Math Question Set").first() is not None
    assert db_session.query(QuestionSetModel).filter(QuestionSetModel.name == "Science Question Set").first() is not None
    assert db_session.query(QuestionModel).count() == 4

def test_filter_questions(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "Math",
            "topic": "Algebra",
            "subtopic": "Linear Equations",
            "difficulty": "Easy",
            "tags": ["equations", "solving"]
        }
    )
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    if questions:
        subject = db_session.query(SubjectModel).filter(SubjectModel.name == "Math").first()
        topic = db_session.query(TopicModel).filter(TopicModel.name == "Algebra").first()
        subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Linear Equations").first()
        for question in questions:
            assert question["subject_id"] == subject.id
            assert question["topic_id"] == topic.id
            assert question["subtopic_id"] == subtopic.id
            assert question["difficulty"] == "Easy"
            assert "equations" in [tag["tag"] for tag in question["tags"]]
            assert "solving" in [tag["tag"] for tag in question["tags"]]

def test_filter_questions_by_subject(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"subject": "Math"}
    )
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    subject = db_session.query(SubjectModel).filter(SubjectModel.name == "Math").first()
    assert all(question["subject_id"] == subject.id for question in questions)

def test_filter_questions_by_topic(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"topic": "Algebra"}
    )
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    topic = db_session.query(TopicModel).filter(TopicModel.name == "Algebra").first()
    assert all(question["topic_id"] == topic.id for question in questions)

def test_filter_questions_by_subtopic(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"subtopic": "Linear Equations"}
    )
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Linear Equations").first()
    assert all(question["subtopic_id"] == subtopic.id for question in questions)

def test_filter_questions_by_difficulty(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"difficulty": "Easy"}
    )
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    assert all(question["difficulty"] == "Easy" for question in questions)

def test_filter_questions_by_single_tag(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"tags": ["equations"]}
    )
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    tag = db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "equations").first()
    assert all(tag.id in [t.id for t in question["tags"]] for question in questions)

def test_filter_questions_by_tags(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"tags": ["geometry"]}
    )
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    tag = db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "geometry").first()
    assert all(tag.id in [t.id for t in question["tags"]] for question in questions)

def test_filter_questions_by_multiple_criteria(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "Math",
            "topic": "Algebra",
            "difficulty": "Easy"
        }
    )
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    subject = db_session.query(SubjectModel).filter(SubjectModel.name == "Math").first()
    topic = db_session.query(TopicModel).filter(TopicModel.name == "Algebra").first()
    for question in questions:
        assert question["subject_id"] == subject.id
        assert question["topic_id"] == topic.id
        assert question["difficulty"] == "Easy"

def test_filter_questions_with_pagination(logged_in_client, db_session, setup_filter_questions_data):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "Math",
            "skip": 1,
            "limit": 2
        }
    )
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) <= 2
    assert all(question["subject_id"] == 1 for question in questions)

def test_filter_questions_no_results(logged_in_client, db_session, setup_filter_questions_data):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "NonexistentSubject"
        }
    )
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) == 0

def test_filter_questions_invalid_params(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"invalid_param": "value"}
    )
    assert response.status_code == 422
    assert "Unknown field" in response.json()["detail"][0]["msg"]

def test_filter_questions_no_params(logged_in_client, db_session):
    response = logged_in_client.get("/questions/filter")
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)

# filename: backend/tests/test_api_filters.py

import pytest

from backend.app.api.endpoints.filters import filter_questions
from backend.app.models.concepts import ConceptModel
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.domains import DomainModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def test_setup_filter_questions_data(db_session, setup_filter_questions_data):
    # Check if the required data is created in the database
    assert db_session.query(DomainModel).filter(DomainModel.name == "Science").first() is not None
    assert db_session.query(DomainModel).filter(DomainModel.name == "Mathematics").first() is not None
    
    assert db_session.query(DisciplineModel).filter(DisciplineModel.name == "Physics").first() is not None
    assert db_session.query(DisciplineModel).filter(DisciplineModel.name == "Pure Mathematics").first() is not None
    
    assert db_session.query(SubjectModel).filter(SubjectModel.name == "Classical Mechanics").first() is not None
    assert db_session.query(SubjectModel).filter(SubjectModel.name == "Algebra").first() is not None
    
    assert db_session.query(TopicModel).filter(TopicModel.name == "Newton's Laws").first() is not None
    assert db_session.query(TopicModel).filter(TopicModel.name == "Linear Algebra").first() is not None
    
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "First Law of Motion").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Second Law of Motion").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Matrices").first() is not None
    assert db_session.query(SubtopicModel).filter(SubtopicModel.name == "Vector Spaces").first() is not None
    
    assert db_session.query(ConceptModel).filter(ConceptModel.name == "Inertia").first() is not None
    assert db_session.query(ConceptModel).filter(ConceptModel.name == "Force and Acceleration").first() is not None
    assert db_session.query(ConceptModel).filter(ConceptModel.name == "Matrix Operations").first() is not None
    assert db_session.query(ConceptModel).filter(ConceptModel.name == "Linear Independence").first() is not None
    
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "physics").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "mathematics").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "mechanics").first() is not None
    assert db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "linear algebra").first() is not None
    
    assert db_session.query(QuestionSetModel).filter(QuestionSetModel.name == "Physics Question Set").first() is not None
    assert db_session.query(QuestionSetModel).filter(QuestionSetModel.name == "Math Question Set").first() is not None
    
    assert db_session.query(QuestionModel).count() == 4

    # Check if the topics are correctly associated with their respective subjects
    newtons_laws_topic = db_session.query(TopicModel).filter(TopicModel.name == "Newton's Laws").first()
    assert newtons_laws_topic.subjects[0].name == "Classical Mechanics"

    linear_algebra_topic = db_session.query(TopicModel).filter(TopicModel.name == "Linear Algebra").first()
    assert linear_algebra_topic.subjects[0].name == "Algebra"

    # Check if the subtopics are correctly associated with their respective topics
    first_law_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "First Law of Motion").first()
    assert first_law_subtopic.topics[0].name == "Newton's Laws"

    second_law_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Second Law of Motion").first()
    assert second_law_subtopic.topics[0].name == "Newton's Laws"

    matrices_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Matrices").first()
    assert matrices_subtopic.topics[0].name == "Linear Algebra"

    vector_spaces_subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Vector Spaces").first()
    assert vector_spaces_subtopic.topics[0].name == "Linear Algebra"

    # Check if the concepts are correctly associated with their respective subtopics
    inertia_concept = db_session.query(ConceptModel).filter(ConceptModel.name == "Inertia").first()
    assert inertia_concept.subtopics[0].name == "First Law of Motion"

    force_acceleration_concept = db_session.query(ConceptModel).filter(ConceptModel.name == "Force and Acceleration").first()
    assert force_acceleration_concept.subtopics[0].name == "Second Law of Motion"

    matrix_operations_concept = db_session.query(ConceptModel).filter(ConceptModel.name == "Matrix Operations").first()
    assert matrix_operations_concept.subtopics[0].name == "Matrices"

    linear_independence_concept = db_session.query(ConceptModel).filter(ConceptModel.name == "Linear Independence").first()
    assert linear_independence_concept.subtopics[0].name == "Vector Spaces"

    # Check if the questions are correctly associated with their respective subjects, topics, subtopics, and concepts
    questions = db_session.query(QuestionModel).all()
    for question in questions:
        assert question.subjects is not None
        assert question.topics is not None
        assert question.subtopics is not None
        assert question.concepts is not None

    # Check specific questions
    newton_first_law_question = db_session.query(QuestionModel).filter(QuestionModel.text == "What is Newton's First Law of Motion?").first()
    assert newton_first_law_question.subjects[0].name == "Classical Mechanics"
    assert newton_first_law_question.topics[0].name == "Newton's Laws"
    assert newton_first_law_question.subtopics[0].name == "First Law of Motion"
    assert newton_first_law_question.concepts[0].name == "Inertia"
    assert set([question_tag.tag for question_tag in newton_first_law_question.question_tags]) == {"physics", "mechanics"}

    linear_independence_question = db_session.query(QuestionModel).filter(QuestionModel.text == "What does it mean for a set of vectors to be linearly independent?").first()
    assert linear_independence_question.subjects[0].name == "Algebra"
    assert linear_independence_question.topics[0].name == "Linear Algebra"
    assert linear_independence_question.subtopics[0].name == "Vector Spaces"
    assert linear_independence_question.concepts[0].name == "Linear Independence"
    assert set([question_tag.tag for question_tag in linear_independence_question.question_tags]) == {"mathematics", "linear algebra"}

def test_filter_questions(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "Math",
            "topic": "Algebra",
            "subtopic": "Linear Equations",
            "difficulty": "Easy",
            "question_tags": ["equations", "solving"]
        }
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
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
            assert "equations" in [tag["tag"] for tag in question["question_tags"]]
            assert "solving" in [tag["tag"] for tag in question["question_tags"]]

def test_filter_questions_by_subject(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"subject": "Math"}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    subject = db_session.query(SubjectModel).filter(SubjectModel.name == "Math").first()
    assert all(question["subject_id"] == subject.id for question in questions)

def test_filter_questions_by_topic(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"topic": "Algebra"}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    topic = db_session.query(TopicModel).filter(TopicModel.name == "Algebra").first()
    assert all(question["topic_id"] == topic.id for question in questions)

def test_filter_questions_by_subtopic(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"subtopic": "Linear Equations"}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    subtopic = db_session.query(SubtopicModel).filter(SubtopicModel.name == "Linear Equations").first()
    assert all(question["subtopic_id"] == subtopic.id for question in questions)

def test_filter_questions_by_difficulty(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"difficulty": "Easy"}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    assert all(question["difficulty"] == "Easy" for question in questions)

def test_filter_questions_by_single_tag(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"question_tags": ["equations"]}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    question_tag = db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "equations").first()
    assert all(question_tag.id in [t.id for t in question["question_tags"]] for question in questions)

def test_filter_questions_by_tags(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={"question_tags": ["geometry"]}
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)
    question_tag = db_session.query(QuestionTagModel).filter(QuestionTagModel.tag == "geometry").first()
    assert all(question_tag.id in [t.id for t in question["question_tags"]] for question in questions)

def test_filter_questions_by_multiple_criteria(logged_in_client, db_session):
    response = logged_in_client.get(
        "/questions/filter",
        params={
            "subject": "Math",
            "topic": "Algebra",
            "difficulty": "Easy"
        }
    )
    assert response.status_code == 200, f"Failed with response: {response.json()}"
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
    assert response.status_code == 200, f"Failed with response: {response.json()}"
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
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert len(questions) == 0

def test_filter_questions_no_params(logged_in_client, db_session):
    response = logged_in_client.get("/questions/filter")
    assert response.status_code == 200, f"Failed with response: {response.json()}"
    questions = response.json()
    assert isinstance(questions, list)

def test_filter_questions_endpoint_invalid_params(logged_in_client, db_session):
    response = logged_in_client.get("/questions/filter", params={"invalid_param": "value"})
    assert response.status_code == 422, f"Failed with response: {response.json()}"
    assert "Unexpected parameters provided" in response.json()["detail"]

@pytest.mark.asyncio
async def test_filter_questions_endpoint_invalid_params_direct(db_session):
    invalid_params = {
        "invalid_param": "value",  # This should cause validation to fail
        "subject": None,
        "topic": None,
        "subtopic": None,
        "difficulty": None,
        "tags": None
    }
    with pytest.raises(TypeError) as exc_info:
        # Simulate the endpoint call with invalid parameters
        # pylint: disable=unexpected-keyword-arg
        await filter_questions(db=db_session, **invalid_params)
    assert "got an unexpected keyword argument" in str(exc_info.value)

# filename: backend/tests/fixtures/integration/complex_data_fixtures.py

import pytest

from backend.app.crud.crud_concepts import create_concept_in_db
from backend.app.crud.crud_disciplines import create_discipline_in_db
from backend.app.crud.crud_domains import create_domain_in_db
from backend.app.crud.crud_question_sets import create_question_set_in_db
from backend.app.crud.crud_question_tags import create_question_tag_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subjects import create_subject_in_db
from backend.app.crud.crud_subtopics import create_subtopic_in_db
from backend.app.crud.crud_topics import create_topic_in_db
from backend.app.models.questions import DifficultyLevel
from backend.app.schemas.concepts import ConceptCreateSchema
from backend.app.schemas.disciplines import DisciplineCreateSchema
from backend.app.schemas.domains import DomainCreateSchema
from backend.app.schemas.question_sets import QuestionSetCreateSchema
from backend.app.schemas.question_tags import QuestionTagCreateSchema
from backend.app.schemas.questions import QuestionCreateSchema
from backend.app.schemas.subjects import SubjectCreateSchema
from backend.app.schemas.subtopics import SubtopicCreateSchema
from backend.app.schemas.topics import TopicCreateSchema


@pytest.fixture(scope="function")
def setup_filter_questions_data(db_session, test_model_user_with_group):
    """Create a comprehensive dataset for testing question filtering functionality."""
    # Create Domains
    domain1 = create_domain_in_db(
        db_session, DomainCreateSchema(name="Science").model_dump()
    )
    domain2 = create_domain_in_db(
        db_session, DomainCreateSchema(name="Mathematics").model_dump()
    )

    # Create Disciplines
    discipline1 = create_discipline_in_db(
        db_session,
        DisciplineCreateSchema(name="Physics", domain_ids=[domain1.id]).model_dump(),
    )
    discipline2 = create_discipline_in_db(
        db_session,
        DisciplineCreateSchema(
            name="Pure Mathematics", domain_ids=[domain2.id]
        ).model_dump(),
    )

    # Create Subjects
    subject1 = create_subject_in_db(
        db_session,
        SubjectCreateSchema(
            name="Classical Mechanics", discipline_ids=[discipline1.id]
        ).model_dump(),
    )
    subject2 = create_subject_in_db(
        db_session,
        SubjectCreateSchema(
            name="Algebra", discipline_ids=[discipline2.id]
        ).model_dump(),
    )

    # Create Topics
    topic1 = create_topic_in_db(
        db_session,
        TopicCreateSchema(name="Newton's Laws", subject_ids=[subject1.id]).model_dump(),
    )
    topic2 = create_topic_in_db(
        db_session,
        TopicCreateSchema(
            name="Linear Algebra", subject_ids=[subject2.id]
        ).model_dump(),
    )

    # Create Subtopics
    subtopic1 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name="First Law of Motion", topic_ids=[topic1.id]
        ).model_dump(),
    )
    subtopic2 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(
            name="Second Law of Motion", topic_ids=[topic1.id]
        ).model_dump(),
    )
    subtopic3 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(name="Matrices", topic_ids=[topic2.id]).model_dump(),
    )
    subtopic4 = create_subtopic_in_db(
        db_session,
        SubtopicCreateSchema(name="Vector Spaces", topic_ids=[topic2.id]).model_dump(),
    )

    # Create Concepts
    concept1 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(name="Inertia", subtopic_ids=[subtopic1.id]).model_dump(),
    )
    concept2 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name="Force and Acceleration", subtopic_ids=[subtopic2.id]
        ).model_dump(),
    )
    concept3 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name="Matrix Operations", subtopic_ids=[subtopic3.id]
        ).model_dump(),
    )
    concept4 = create_concept_in_db(
        db_session,
        ConceptCreateSchema(
            name="Linear Independence", subtopic_ids=[subtopic4.id]
        ).model_dump(),
    )

    # Create Tags
    tag1 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="physics").model_dump()
    )
    tag2 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="mathematics").model_dump()
    )
    tag3 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="mechanics").model_dump()
    )
    tag4 = create_question_tag_in_db(
        db_session, QuestionTagCreateSchema(tag="linear algebra").model_dump()
    )

    # Create Question Sets
    question_set1 = create_question_set_in_db(
        db_session,
        QuestionSetCreateSchema(
            name="Physics Question Set",
            is_public=True,
            creator_id=test_model_user_with_group.id,
        ).model_dump(),
    )
    question_set2 = create_question_set_in_db(
        db_session,
        QuestionSetCreateSchema(
            name="Math Question Set",
            is_public=True,
            creator_id=test_model_user_with_group.id,
        ).model_dump(),
    )

    # Create Questions
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What is Newton's First Law of Motion?",
            subject_ids=[subject1.id],
            topic_ids=[topic1.id],
            subtopic_ids=[subtopic1.id],
            concept_ids=[concept1.id],
            difficulty=DifficultyLevel.EASY,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id],
        ).model_dump(),
    )
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="How does force relate to acceleration according to Newton's Second Law?",
            subject_ids=[subject1.id],
            topic_ids=[topic1.id],
            subtopic_ids=[subtopic2.id],
            concept_ids=[concept2.id],
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag1.id, tag3.id],
            question_set_ids=[question_set1.id],
        ).model_dump(),
    )
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What is the result of multiplying a 2x2 identity matrix with any 2x2 matrix?",
            subject_ids=[subject2.id],
            topic_ids=[topic2.id],
            subtopic_ids=[subtopic3.id],
            concept_ids=[concept3.id],
            difficulty=DifficultyLevel.MEDIUM,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id],
        ).model_dump(),
    )
    create_question_in_db(
        db_session,
        QuestionCreateSchema(
            text="What does it mean for a set of vectors to be linearly independent?",
            subject_ids=[subject2.id],
            topic_ids=[topic2.id],
            subtopic_ids=[subtopic4.id],
            concept_ids=[concept4.id],
            difficulty=DifficultyLevel.HARD,
            question_tag_ids=[tag2.id, tag4.id],
            question_set_ids=[question_set2.id],
        ).model_dump(),
    )


@pytest.fixture(scope="function")
def filter_test_data(
    db_session,
    test_schema_question,
    test_schema_subject,
    test_schema_topic,
    test_schema_subtopic,
    test_schema_question_tag,
):
    """Create a simple dataset for testing basic filtering functionality."""
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())

    question_data = test_schema_question.model_dump()
    question_data.update(
        {
            "subject_ids": [subject.id],
            "topic_ids": [topic.id],
            "subtopic_ids": [subtopic.id],
            "question_tag_ids": [tag.id],
            "difficulty": DifficultyLevel.MEDIUM,
        }
    )
    question = create_question_in_db(db_session, question_data)

    return {
        "subject": subject,
        "topic": topic,
        "subtopic": subtopic,
        "tag": tag,
        "question": question,
    }
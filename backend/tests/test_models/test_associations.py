# filename: backend/tests/models/test_associations.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.concepts import ConceptModel
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.groups import GroupModel
from backend.app.models.permissions import PermissionModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import DifficultyLevel, QuestionModel
from backend.app.models.roles import RoleModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.models.users import UserModel


def test_user_to_group_association(db_session, test_model_user, test_model_group):
    test_model_user.groups.append(test_model_group)
    db_session.commit()

    assert test_model_group in test_model_user.groups
    assert test_model_user in test_model_group.users

def test_question_to_subject_association(db_session):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    subject = SubjectModel(name="Test Subject")
    question.subjects.append(subject)
    db_session.add_all([question, subject])
    db_session.commit()

    assert subject in question.subjects
    assert question in subject.questions

def test_question_to_topic_association(db_session):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    topic = TopicModel(name="Test Topic")
    question.topics.append(topic)
    db_session.add_all([question, topic])
    db_session.commit()

    assert topic in question.topics
    assert question in topic.questions

def test_question_to_subtopic_association(db_session):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    subtopic = SubtopicModel(name="Test Subtopic")
    question.subtopics.append(subtopic)
    db_session.add_all([question, subtopic])
    db_session.commit()

    assert subtopic in question.subtopics
    assert question in subtopic.questions

def test_question_to_concept_association(db_session):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    concept = ConceptModel(name="Test Concept")
    question.concepts.append(concept)
    db_session.add_all([question, concept])
    db_session.commit()

    assert concept in question.concepts
    assert question in concept.questions

def test_question_to_tag_association(db_session):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    tag = QuestionTagModel(tag="Test Tag")
    question.question_tags.append(tag)
    db_session.add_all([question, tag])
    db_session.commit()

    assert tag in question.question_tags
    assert question in tag.questions

def test_model_question_set_to_question_association(db_session, test_model_user_with_group):
    question = QuestionModel(text="Test Question", difficulty=DifficultyLevel.EASY)
    question_set = QuestionSetModel(name="Test Set", creator_id=test_model_user_with_group.id)
    question_set.questions.append(question)
    db_session.add_all([question, question_set])
    db_session.commit()

    assert question in question_set.questions
    assert question_set in question.question_sets

def test_model_question_set_to_group_association(db_session, test_model_question_set, test_model_group):
    test_model_question_set.groups.append(test_model_group)
    db_session.commit()

    assert test_model_group in test_model_question_set.groups
    assert test_model_question_set in test_model_group.question_sets

def test_role_to_permission_association(db_session, test_model_role, test_permission):
    test_model_role.permissions.append(test_permission)
    db_session.commit()

    assert test_permission in test_model_role.permissions
    assert test_model_role in test_permission.roles

def test_discipline_subject_association(db_session):
    discipline = DisciplineModel(name="Science")
    subject = SubjectModel(name="Physics")
    discipline.subjects.append(subject)
    db_session.add_all([discipline, subject])
    db_session.commit()

    assert subject in discipline.subjects
    assert discipline in subject.disciplines

def test_subject_topic_association(db_session):
    subject = SubjectModel(name="Mathematics")
    topic = TopicModel(name="Algebra")
    subject.topics.append(topic)
    db_session.add_all([subject, topic])
    db_session.commit()

    assert topic in subject.topics
    assert subject in topic.subjects

def test_topic_subtopic_association(db_session):
    topic = TopicModel(name="Geometry")
    subtopic = SubtopicModel(name="Triangles")
    topic.subtopics.append(subtopic)
    db_session.add_all([topic, subtopic])
    db_session.commit()

    assert subtopic in topic.subtopics
    assert topic in subtopic.topics

def test_subtopic_concept_association(db_session):
    subtopic = SubtopicModel(name="Calculus")
    concept = ConceptModel(name="Derivatives")
    subtopic.concepts.append(concept)
    db_session.add_all([subtopic, concept])
    db_session.commit()

    assert concept in subtopic.concepts
    assert subtopic in concept.subtopics

def test_question_associations(db_session):
    question = QuestionModel(text="What is 2+2?", difficulty=DifficultyLevel.EASY)
    subject = SubjectModel(name="Math")
    topic = TopicModel(name="Arithmetic")
    subtopic = SubtopicModel(name="Addition")
    concept = ConceptModel(name="Basic Addition")

    question.subjects.append(subject)
    question.topics.append(topic)
    question.subtopics.append(subtopic)
    question.concepts.append(concept)

    db_session.add_all([question, subject, topic, subtopic, concept])
    db_session.commit()

    assert subject in question.subjects
    assert topic in question.topics
    assert subtopic in question.subtopics
    assert concept in question.concepts

    assert question in subject.questions
    assert question in topic.questions
    assert question in subtopic.questions
    assert question in concept.questions

def test_multiple_associations(db_session):
    subject1 = SubjectModel(name="Physics")
    subject2 = SubjectModel(name="Engineering")
    topic = TopicModel(name="Mechanics")

    topic.subjects.extend([subject1, subject2])
    db_session.add_all([subject1, subject2, topic])
    db_session.commit()

    assert subject1 in topic.subjects
    assert subject2 in topic.subjects
    assert topic in subject1.topics
    assert topic in subject2.topics

def test_association_integrity(db_session, test_model_user, test_model_group):
    test_model_user.groups.append(test_model_group)
    db_session.commit()

    # Try to add the same association again
    with pytest.raises(IntegrityError):
        test_model_user.groups.append(test_model_group)
        db_session.commit()

    db_session.rollback()

    # Remove the association
    test_model_user.groups.remove(test_model_group)
    db_session.commit()

    assert test_model_group not in test_model_user.groups
    assert test_model_user not in test_model_group.users

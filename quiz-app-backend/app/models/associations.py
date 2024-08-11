# filename: app/models/associations.py

from sqlalchemy import Column, ForeignKey, Integer

from app.db.base import Base


class UserToGroupAssociation(Base):
    __tablename__ = "user_to_group_association"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)


class QuestionToAnswerAssociation(Base):
    __tablename__ = "question_to_answer_association"
    
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    answer_choice_id = Column(Integer, ForeignKey('answer_choices.id'), primary_key=True)


class QuestionToTagAssociation(Base):
    __tablename__ = "question_to_tag_association"

    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    question_tag_id = Column(Integer, ForeignKey("question_tags.id"), primary_key=True)


class QuestionSetToQuestionAssociation(Base):
    __tablename__ = "question_set_to_question_association"

    question_id = Column(ForeignKey('questions.id'), primary_key=True)
    question_set_id = Column(ForeignKey('question_sets.id'), primary_key=True)


class QuestionSetToGroupAssociation(Base):
    __tablename__ = "question_set_to_group_association"

    question_set_id = Column(ForeignKey('question_sets.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)


class RoleToPermissionAssociation(Base):
    __tablename__ = "role_to_permission_association"

    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)


class QuestionToSubjectAssociation(Base):
    __tablename__ = 'question_to_subject_association'
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), primary_key=True)


class QuestionToTopicAssociation(Base):
    __tablename__ = 'question_to_topic_association'
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), primary_key=True)


class QuestionToSubtopicAssociation(Base):
    __tablename__ = 'question_to_subtopic_association'
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'), primary_key=True)


class QuestionToConceptAssociation(Base):
    __tablename__ = 'question_to_concept_association'
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    concept_id = Column(Integer, ForeignKey('concepts.id'), primary_key=True)


class DomainToDisciplineAssociation(Base):
    __tablename__ = 'domain_to_discipline_association'
    domain_id = Column(Integer, ForeignKey('domains.id'), primary_key=True)
    discipline_id = Column(Integer, ForeignKey('disciplines.id'), primary_key=True)

class DisciplineToSubjectAssociation(Base):
    __tablename__ = 'discipline_to_subject_association'
    discipline_id = Column(Integer, ForeignKey('disciplines.id'), primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), primary_key=True)


class SubjectToTopicAssociation(Base):
    __tablename__ = 'subject_to_topic_association'
    subject_id = Column(Integer, ForeignKey('subjects.id'), primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), primary_key=True)


class TopicToSubtopicAssociation(Base):
    __tablename__ = 'topic_to_subtopic_association'
    topic_id = Column(Integer, ForeignKey('topics.id'), primary_key=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'), primary_key=True)


class SubtopicToConceptAssociation(Base):
    __tablename__ = 'subtopic_to_concept_association'
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'), primary_key=True)
    concept_id = Column(Integer, ForeignKey('concepts.id'), primary_key=True)

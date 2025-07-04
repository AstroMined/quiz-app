# filename: backend/tests/models/test_question_model.py

from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.associations import QuestionToAnswerAssociation
from backend.app.models.concepts import ConceptModel
from backend.app.models.questions import DifficultyLevel, QuestionModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.models.user_responses import UserResponseModel


def test_question_model_creation(db_session):
    question = QuestionModel(
        text="What is the capital of France?", difficulty=DifficultyLevel.EASY
    )
    db_session.add(question)
    db_session.commit()

    assert question.id is not None
    assert question.text == "What is the capital of France?"
    assert question.difficulty == DifficultyLevel.EASY


def test_question_model_relationships(
    db_session,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    question = QuestionModel(
        text="What is the capital of France?", difficulty=DifficultyLevel.EASY
    )
    question.subjects.append(test_model_subject)
    question.topics.append(test_model_topic)
    question.subtopics.append(test_model_subtopic)
    question.concepts.append(test_model_concept)
    db_session.add(question)
    db_session.commit()

    assert test_model_subject in question.subjects
    assert test_model_topic in question.topics
    assert test_model_subtopic in question.subtopics
    assert test_model_concept in question.concepts


def test_question_multiple_relationships(
    db_session,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    question = QuestionModel(
        text="What is the capital of France?", difficulty=DifficultyLevel.EASY
    )
    question.subjects.extend([test_model_subject, SubjectModel(name="Another Subject")])
    question.topics.extend([test_model_topic, TopicModel(name="Another Topic")])
    question.subtopics.extend(
        [test_model_subtopic, SubtopicModel(name="Another Subtopic")]
    )
    question.concepts.extend([test_model_concept, ConceptModel(name="Another Concept")])
    db_session.add(question)
    db_session.commit()

    assert len(question.subjects) == 2
    assert len(question.topics) == 2
    assert len(question.subtopics) == 2
    assert len(question.concepts) == 2


def test_question_tag_relationship(db_session, test_model_tag):
    question = QuestionModel(
        text="What is the capital of France?", difficulty=DifficultyLevel.EASY
    )
    question.question_tags.append(test_model_tag)
    db_session.add(question)
    db_session.commit()

    assert test_model_tag in question.question_tags
    assert question in test_model_tag.questions


def test_answer_choice_relationship(db_session):
    # Create the question first
    question = QuestionModel(
        text="What is the capital of France?", difficulty=DifficultyLevel.EASY
    )
    db_session.add(question)
    db_session.flush()  # Flush to get the question ID

    # Create the answer choice
    answer_choice = AnswerChoiceModel(
        text="Paris", is_correct=True, explanation="Paris is the capital of France"
    )
    db_session.add(answer_choice)
    db_session.flush()  # Flush to get the answer choice ID

    # Associate the answer choice with the question
    question.answer_choices.append(answer_choice)
    db_session.commit()

    # Refresh the objects to ensure we have the latest data
    db_session.refresh(question)
    db_session.refresh(answer_choice)

    # Assert the relationships
    assert answer_choice in question.answer_choices
    assert (
        question in answer_choice.questions
    )  # Note: This is now 'questions' (plural) due to the many-to-many relationship

    # Additional assertions to verify the relationship
    assert len(question.answer_choices) == 1
    assert len(answer_choice.questions) == 1
    assert question.answer_choices[0].text == "Paris"
    assert answer_choice.questions[0].text == "What is the capital of France?"


def test_model_question_set_relationship(db_session, test_model_question_set):
    question = QuestionModel(
        text="What is the capital of France?", difficulty=DifficultyLevel.EASY
    )
    question.question_sets.append(test_model_question_set)
    db_session.add(question)
    db_session.commit()

    assert test_model_question_set in question.question_sets
    assert question in test_model_question_set.questions


def test_user_response_relationship(db_session, test_model_user):
    question = QuestionModel(
        text="What is the capital of France?", difficulty=DifficultyLevel.EASY
    )
    db_session.add(question)
    db_session.commit()

    user_response = UserResponseModel(
        user_id=test_model_user.id,
        question_id=question.id,
        answer_choice_id=1,  # Assuming an answer choice with id 1 exists
        is_correct=True,
    )
    db_session.add(user_response)
    db_session.commit()

    assert user_response in question.user_responses
    assert question == user_response.question


def test_question_model_repr(db_session):
    question = QuestionModel(
        text="What is the capital of France?", difficulty=DifficultyLevel.EASY
    )
    db_session.add(question)
    db_session.commit()

    expected_repr = f"<QuestionModel(id={question.id}, text='What is the capital of France?...', difficulty='DifficultyLevel.EASY')>"
    assert repr(question) == expected_repr


def test_question_model_with_answers(
    db_session, test_model_subject, test_model_topic, test_model_subtopic
):
    question = QuestionModel(
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY,
        subjects=[test_model_subject],
        topics=[test_model_topic],
        subtopics=[test_model_subtopic],
    )

    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)

    answer = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital and largest city of France.",
    )

    db_session.add(answer)
    db_session.commit()
    db_session.refresh(answer)

    # Associate the answer with the question
    question.answer_choices.append(answer)
    db_session.commit()

    
    assert question.id is not None
    assert answer.id is not None
    assert answer in question.answer_choices


def test_question_deletion_removes_association_to_answers(
    db_session, test_model_subject, test_model_topic, test_model_subtopic
):
    question = QuestionModel(
        text="What is the capital of France?",
        difficulty=DifficultyLevel.EASY,
        subjects=[test_model_subject],
        topics=[test_model_topic],
        subtopics=[test_model_subtopic],
    )

    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)

    answer = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital and largest city of France.",
    )

    db_session.add(answer)
    db_session.commit()
    db_session.refresh(answer)

    # Associate the answer with the question
    question.answer_choices.append(answer)
    db_session.commit()

    
    # Store the answer ID for later checking
    answer_id = answer.id

    db_session.delete(question)

    db_session.commit()

    # Check that the answer still exists
    assert (
        db_session.query(AnswerChoiceModel).filter_by(id=answer_id).first() is not None
    )

    # Check that the association between the question and answer is removed
    assert (
        db_session.query(QuestionToAnswerAssociation)
        .filter_by(answer_choice_id=answer_id)
        .first()
        is None
    )

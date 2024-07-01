# filename: tests/test_utils/test_randomization.py

from app.services.randomization_service import randomize_questions, randomize_answer_choices
from app.models.questions import QuestionModel
from app.models.answer_choices import AnswerChoiceModel


def test_randomize_questions():
    questions = [
        QuestionModel(text="Question 1"),
        QuestionModel(text="Question 2"),
        QuestionModel(text="Question 3"),
    ]
    randomized_questions = randomize_questions(questions)
    assert len(randomized_questions) == len(questions)
    assert set(randomized_questions) == set(questions)

def test_randomize_answer_choices():
    answer_choices = [
        AnswerChoiceModel(text="Choice 1"),
        AnswerChoiceModel(text="Choice 2"),
        AnswerChoiceModel(text="Choice 3"),
    ]
    randomized_choices = randomize_answer_choices(answer_choices)
    assert len(randomized_choices) == len(answer_choices)
    assert set(randomized_choices) == set(answer_choices)

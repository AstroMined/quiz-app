# filename: backend/tests/test_services/test_randomization_service.py

import pytest

from backend.app.services.randomization_service import (
    randomize_answer_choices,
    randomize_questions,
)


def test_randomize_questions():
    questions = [1, 2, 3, 4, 5]
    randomized = randomize_questions(questions)

    # Check that all elements are present
    assert set(randomized) == set(questions)

    # Check that the order has changed (this could theoretically fail, but it's very unlikely)
    assert randomized != questions

    # Check that multiple randomizations produce different results
    another_randomized = randomize_questions(questions)
    assert randomized != another_randomized or randomized != questions


def test_randomize_answer_choices():
    answer_choices = ["A", "B", "C", "D"]
    randomized = randomize_answer_choices(answer_choices)

    # Check that all elements are present
    assert set(randomized) == set(answer_choices)

    # Check that the order has changed (this could theoretically fail, but it's very unlikely)
    assert randomized != answer_choices

    # Check that multiple randomizations produce different results
    another_randomized = randomize_answer_choices(answer_choices)
    assert randomized != another_randomized or randomized != answer_choices


def test_randomize_single_element():
    single_element = [1]
    assert randomize_questions(single_element) == single_element
    assert randomize_answer_choices(single_element) == single_element


def test_randomize_empty_list():
    empty_list = []
    assert randomize_questions(empty_list) == empty_list
    assert randomize_answer_choices(empty_list) == empty_list


# Add more tests if needed, such as testing with a large number of elements
# or testing the distribution of randomizations over many iterations

# filename: app/utils/randomization.py

import random

def randomize_questions(questions):
    return random.sample(questions, len(questions))

def randomize_answer_choices(answer_choices):
    return random.sample(answer_choices, len(answer_choices))

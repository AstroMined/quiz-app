#!/bin/bash

# Path to your template and output files
TEMPLATE_FILE="/code/quiz-app/prompts/prompt_template.md"
OUTPUT_FILE="/code/quiz-app/prompts/test_failure_prompt.md"

# Combine the template content with the output of pytest and overwrite the output file
cat $TEMPLATE_FILE > $OUTPUT_FILE
pytest --cov=app /code/quiz-app/backend/tests/test_crud/test_crud_questions.py -q >> $OUTPUT_FILE

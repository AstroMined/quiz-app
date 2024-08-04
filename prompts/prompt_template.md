Hello, I'm presenting you with a detailed markdown file named `quiz-app-backend_repo_summary.md`, which acts as a comprehensive representation of a project's repository. This file is generated using a Python script that meticulously walks through the project directory, encapsulating the essence of the entire project structure, including directories, files (e.g., README.md, LICENSE), and specific file contents (with a focus on `.py`, `.js`, `.html`, `.css` files) into a structured markdown document. Here's how the content is organized:

1. **Directories** are prominently highlighted as main headers, formatted as `# Directory: path/to/directory`. This layout showcases each directory within the project with its full path, ensuring a transparent hierarchy of the project's architecture.

2. **Files**, specifically focusing on README.md files, Python scripts, and other specified file types, are listed under secondary headers within their respective directory sections, formatted as `## File: filename`. README.md files are given precedence, appearing first in each section, followed by Python scripts and other files, arranged to reflect the project's logical structure.

3. **Content** of these files is presented in code blocks right after their corresponding headers, using syntax highlighting appropriate to the file type (```markdown for README.md, ```python for Python scripts, etc.), facilitating a clear understanding of each file's purpose and content.

**Guidelines for Engaging with the Project:**

- When recommending changes or additions, please provide precise file paths. For modifications, reference the existing path as outlined in the markdown. For new file suggestions, align with the existing project structure.

- Aim to output complete scripts or file contents directly, avoiding placeholders. This method enables immediate application and simplifies integration into the project.

- Ensure thorough commenting within Python files, including detailed module and function docstrings. The first line of each Python script should be a descriptive comment in the form `# filename: path/to/file.py`, indicating the script's filename and location.

- In cases where project functionality needs clarification or specific details are unclear, please ask targeted questions to avoid assumptions and ensure accuracy.

**[Task-Specific Guidance]:**

*In this section, detailed assistance is requested for the following tasks within my project:*

**Task:** 

As my senior Python engineer, it is your duty to provide working code to resolve test failures and general problems in the codebase as well as produce clean code to introduce new features.

Please develop a plan for resolving these test failures that doesn't interfere with the normal operation of the app.

============================= test session starts ==============================
platform linux -- Python 3.11.8, pytest-8.1.2, pluggy-1.4.0
rootdir: /code/quiz-app/quiz-app-backend
configfile: pyproject.toml
plugins: anyio-4.3.0, asyncio-0.23.6, cov-4.1.0
asyncio: mode=Mode.STRICT
collected 7 items

tests/test_crud/test_crud_questions.py FEEF...                           [100%]

==================================== ERRORS ====================================
________________ ERROR at setup of test_read_question_detailed _________________

db_session = <sqlalchemy.orm.session.Session object at 0x7a4b2e326410>
test_subject = <Subject(id=1, name='Test Subject', discipline_id=1)>
test_topic = <Topic(id=1, name='Test Topic', subject_id=1)>
test_subtopic = <Subtopic(id=1, name='Test Subtopic', topic_id=1)>
test_concept = <Concept(id=1, name='Test Concept', subtopic_id=1)>
test_answer_choices = [AnswerChoiceCreateSchema(text='Answer 1', is_correct=True, explanation='Explanation 1'), AnswerChoiceCreateSchema(tex... explanation='Explanation 3'), AnswerChoiceCreateSchema(text='Answer 4', is_correct=True, explanation='Explanation 4')]

    @pytest.fixture(scope="function")
    def test_questions(db_session, test_subject, test_topic, test_subtopic, test_concept, test_answer_choices):
        try:
            logger.debug("Setting up test_questions fixture")
            questions_data = [
                QuestionWithAnswersCreateSchema(
                    text="Test Question 1",
                    subject_id=test_subject.id,
                    topic_id=test_topic.id,
                    subtopic_id=test_subtopic.id,
                    concept_id=test_concept.id,
                    difficulty="Easy",
                    answer_choices=[test_answer_choices[0], test_answer_choices[1]]
                ),
                QuestionWithAnswersCreateSchema(
                    text="Test Question 2",
                    subject_id=test_subject.id,
                    topic_id=test_topic.id,
                    subtopic_id=test_subtopic.id,
                    concept_id=test_concept.id,
                    difficulty="Medium",
                    answer_choices=[test_answer_choices[2], test_answer_choices[3]]
                )
            ]
>           questions = [create_question_with_answers(db_session, q) for q in questions_data]

tests/conftest.py:303: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tests/conftest.py:303: in <listcomp>
    questions = [create_question_with_answers(db_session, q) for q in questions_data]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

db = <sqlalchemy.orm.session.Session object at 0x7a4b2e326410>
question = QuestionWithAnswersCreateSchema(text='Test Question 1', subject_id=1, topic_id=1, subtopic_id=1, concept_id=1, difficu...eSchema(text='Answer 2', is_correct=False, explanation='Explanation 2')], question_tag_ids=None, question_set_ids=None)

    def create_question_with_answers(db: Session, question: QuestionWithAnswersCreateSchema) -> QuestionModel:
        # First, create the question
        db_question = QuestionModel(
            text=question.text,
            subject_id=question.subject_id,
            topic_id=question.topic_id,
            subtopic_id=question.subtopic_id,
            concept_id=question.concept_id,
            difficulty=question.difficulty
        )
        db.add(db_question)
        db.flush()  # This assigns an ID to db_question
    
        # Now create the answer choices and associate them with the question
        for answer_choice in question.answer_choices:
            db_answer_choice = create_answer_choice_crud(db, answer_choice)
>           db_question.answer_choices.append(db_answer_choice)
E           AttributeError: 'QuestionModel' object has no attribute 'answer_choices'

app/crud/crud_questions.py:57: AttributeError
------------------------------ Captured log setup ------------------------------
DEBUG    backend:conftest.py:82 Running test: tests/test_crud/test_crud_questions.py::test_read_question_detailed
DEBUG    backend:conftest.py:93 Begin setting up database fixture
DEBUG    backend:conftest.py:327 Setting up test_subject fixture
DEBUG    backend:conftest.py:328 Test discipline: <Discipline(id=1, name='Test Discipline', domain_id=1)>
DEBUG    backend:conftest.py:282 Setting up test_questions fixture
ERROR    backend:conftest.py:306 Error in test_questions fixture: 'QuestionModel' object has no attribute 'answer_choices'
Traceback (most recent call last):
  File "/code/quiz-app/quiz-app-backend/tests/conftest.py", line 303, in test_questions
    questions = [create_question_with_answers(db_session, q) for q in questions_data]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/code/quiz-app/quiz-app-backend/tests/conftest.py", line 303, in <listcomp>
    questions = [create_question_with_answers(db_session, q) for q in questions_data]
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/code/quiz-app/quiz-app-backend/app/crud/crud_questions.py", line 57, in create_question_with_answers
    db_question.answer_choices.append(db_answer_choice)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'QuestionModel' object has no attribute 'answer_choices'
DEBUG    backend:conftest.py:309 Tearing down test_questions fixture
__________ ERROR at setup of test_update_question_with_answer_choices __________

db_session = <sqlalchemy.orm.session.Session object at 0x7a4b2dd18610>
test_subject = <Subject(id=1, name='Test Subject', discipline_id=1)>
test_topic = <Topic(id=1, name='Test Topic', subject_id=1)>
test_subtopic = <Subtopic(id=1, name='Test Subtopic', topic_id=1)>
test_concept = <Concept(id=1, name='Test Concept', subtopic_id=1)>
test_answer_choices = [AnswerChoiceCreateSchema(text='Answer 1', is_correct=True, explanation='Explanation 1'), AnswerChoiceCreateSchema(tex... explanation='Explanation 3'), AnswerChoiceCreateSchema(text='Answer 4', is_correct=True, explanation='Explanation 4')]

    @pytest.fixture(scope="function")
    def test_questions(db_session, test_subject, test_topic, test_subtopic, test_concept, test_answer_choices):
        try:
            logger.debug("Setting up test_questions fixture")
            questions_data = [
                QuestionWithAnswersCreateSchema(
                    text="Test Question 1",
                    subject_id=test_subject.id,
                    topic_id=test_topic.id,
                    subtopic_id=test_subtopic.id,
                    concept_id=test_concept.id,
                    difficulty="Easy",
                    answer_choices=[test_answer_choices[0], test_answer_choices[1]]
                ),
                QuestionWithAnswersCreateSchema(
                    text="Test Question 2",
                    subject_id=test_subject.id,
                    topic_id=test_topic.id,
                    subtopic_id=test_subtopic.id,
                    concept_id=test_concept.id,
                    difficulty="Medium",
                    answer_choices=[test_answer_choices[2], test_answer_choices[3]]
                )
            ]
>           questions = [create_question_with_answers(db_session, q) for q in questions_data]

tests/conftest.py:303: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tests/conftest.py:303: in <listcomp>
    questions = [create_question_with_answers(db_session, q) for q in questions_data]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

db = <sqlalchemy.orm.session.Session object at 0x7a4b2dd18610>
question = QuestionWithAnswersCreateSchema(text='Test Question 1', subject_id=1, topic_id=1, subtopic_id=1, concept_id=1, difficu...eSchema(text='Answer 2', is_correct=False, explanation='Explanation 2')], question_tag_ids=None, question_set_ids=None)

    def create_question_with_answers(db: Session, question: QuestionWithAnswersCreateSchema) -> QuestionModel:
        # First, create the question
        db_question = QuestionModel(
            text=question.text,
            subject_id=question.subject_id,
            topic_id=question.topic_id,
            subtopic_id=question.subtopic_id,
            concept_id=question.concept_id,
            difficulty=question.difficulty
        )
        db.add(db_question)
        db.flush()  # This assigns an ID to db_question
    
        # Now create the answer choices and associate them with the question
        for answer_choice in question.answer_choices:
            db_answer_choice = create_answer_choice_crud(db, answer_choice)
>           db_question.answer_choices.append(db_answer_choice)
E           AttributeError: 'QuestionModel' object has no attribute 'answer_choices'

app/crud/crud_questions.py:57: AttributeError
------------------------------ Captured log setup ------------------------------
DEBUG    backend:conftest.py:82 Running test: tests/test_crud/test_crud_questions.py::test_update_question_with_answer_choices
DEBUG    backend:conftest.py:93 Begin setting up database fixture
DEBUG    backend:conftest.py:327 Setting up test_subject fixture
DEBUG    backend:conftest.py:328 Test discipline: <Discipline(id=1, name='Test Discipline', domain_id=1)>
DEBUG    backend:conftest.py:282 Setting up test_questions fixture
ERROR    backend:conftest.py:306 Error in test_questions fixture: 'QuestionModel' object has no attribute 'answer_choices'
Traceback (most recent call last):
  File "/code/quiz-app/quiz-app-backend/tests/conftest.py", line 303, in test_questions
    questions = [create_question_with_answers(db_session, q) for q in questions_data]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/code/quiz-app/quiz-app-backend/tests/conftest.py", line 303, in <listcomp>
    questions = [create_question_with_answers(db_session, q) for q in questions_data]
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/code/quiz-app/quiz-app-backend/app/crud/crud_questions.py", line 57, in create_question_with_answers
    db_question.answer_choices.append(db_answer_choice)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'QuestionModel' object has no attribute 'answer_choices'
DEBUG    backend:conftest.py:309 Tearing down test_questions fixture
=================================== FAILURES ===================================
______________________ test_create_question_with_answers _______________________

db_session = <sqlalchemy.orm.session.Session object at 0x7a4b2e2dcbd0>
test_subject = <Subject(id=1, name='Test Subject', discipline_id=1)>
test_topic = <Topic(id=1, name='Test Topic', subject_id=1)>
test_subtopic = <Subtopic(id=1, name='Test Subtopic', topic_id=1)>
test_concept = <Concept(id=1, name='Test Concept', subtopic_id=1)>

    def test_create_question_with_answers(db_session, test_subject, test_topic, test_subtopic, test_concept):
        question_data = QuestionWithAnswersCreateSchema(
            text="Test Question",
            subject_id=test_subject.id,
            topic_id=test_topic.id,
            subtopic_id=test_subtopic.id,
            concept_id=test_concept.id,
            difficulty="Easy",
            answer_choices=[
                AnswerChoiceCreateSchema(text="Answer 1", is_correct=True, explanation="Explanation 1"),
                AnswerChoiceCreateSchema(text="Answer 2", is_correct=False, explanation="Explanation 2"),
            ]
        )
>       question = create_question_with_answers(db_session, question_data)

tests/test_crud/test_crud_questions.py:21: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

db = <sqlalchemy.orm.session.Session object at 0x7a4b2e2dcbd0>
question = QuestionWithAnswersCreateSchema(text='Test Question', subject_id=1, topic_id=1, subtopic_id=1, concept_id=1, difficult...eSchema(text='Answer 2', is_correct=False, explanation='Explanation 2')], question_tag_ids=None, question_set_ids=None)

    def create_question_with_answers(db: Session, question: QuestionWithAnswersCreateSchema) -> QuestionModel:
        # First, create the question
        db_question = QuestionModel(
            text=question.text,
            subject_id=question.subject_id,
            topic_id=question.topic_id,
            subtopic_id=question.subtopic_id,
            concept_id=question.concept_id,
            difficulty=question.difficulty
        )
        db.add(db_question)
        db.flush()  # This assigns an ID to db_question
    
        # Now create the answer choices and associate them with the question
        for answer_choice in question.answer_choices:
            db_answer_choice = create_answer_choice_crud(db, answer_choice)
>           db_question.answer_choices.append(db_answer_choice)
E           AttributeError: 'QuestionModel' object has no attribute 'answer_choices'

app/crud/crud_questions.py:57: AttributeError
------------------------------ Captured log setup ------------------------------
DEBUG    backend:conftest.py:82 Running test: tests/test_crud/test_crud_questions.py::test_create_question_with_answers
DEBUG    backend:conftest.py:93 Begin setting up database fixture
DEBUG    backend:conftest.py:327 Setting up test_subject fixture
DEBUG    backend:conftest.py:328 Test discipline: <Discipline(id=1, name='Test Discipline', domain_id=1)>
---------------------------- Captured log teardown -----------------------------
DEBUG    backend:conftest.py:101 Begin tearing down database fixture
DEBUG    backend:conftest.py:104 Finished tearing down database fixture
DEBUG    backend:conftest.py:84 Finished test: tests/test_crud/test_crud_questions.py::test_create_question_with_answers
________________________ test_get_nonexistent_question _________________________

db_session = <sqlalchemy.orm.session.Session object at 0x7a4b2de83b90>

    def test_get_nonexistent_question(db_session):
        """Test retrieval of a non-existent question."""
>       question = read_question(db_session, question_id=999)

tests/test_crud/test_crud_questions.py:51: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

db = <sqlalchemy.orm.session.Session object at 0x7a4b2de83b90>
question_id = 999

    def read_question(db: Session, question_id: int) -> Optional[DetailedQuestionSchema]:
        db_question = db.query(QuestionModel).options(
            joinedload(QuestionModel.subject),
            joinedload(QuestionModel.topic),
            joinedload(QuestionModel.subtopic),
            joinedload(QuestionModel.concept),
>           joinedload(QuestionModel.answer_choices),
            joinedload(QuestionModel.question_tag_ids),
            joinedload(QuestionModel.question_set_ids)
        ).filter(QuestionModel.id == question_id).first()
E       AttributeError: type object 'QuestionModel' has no attribute 'answer_choices'

app/crud/crud_questions.py:77: AttributeError
------------------------------ Captured log setup ------------------------------
DEBUG    backend:conftest.py:82 Running test: tests/test_crud/test_crud_questions.py::test_get_nonexistent_question
DEBUG    backend:conftest.py:93 Begin setting up database fixture
---------------------------- Captured log teardown -----------------------------
DEBUG    backend:conftest.py:101 Begin tearing down database fixture
DEBUG    backend:conftest.py:104 Finished tearing down database fixture
DEBUG    backend:conftest.py:84 Finished test: tests/test_crud/test_crud_questions.py::test_get_nonexistent_question
=========================== short test summary info ============================
FAILED tests/test_crud/test_crud_questions.py::test_create_question_with_answers
FAILED tests/test_crud/test_crud_questions.py::test_get_nonexistent_question
ERROR tests/test_crud/test_crud_questions.py::test_read_question_detailed - A...
ERROR tests/test_crud/test_crud_questions.py::test_update_question_with_answer_choices
==================== 2 failed, 3 passed, 2 errors in 2.95s =====================

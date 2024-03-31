Hello, I'm presenting you with a detailed markdown file named `repo_summary.md`, which acts as a comprehensive representation of a project's repository. This file is generated using a Python script that meticulously walks through the project directory, encapsulating the essence of the entire project structure, including directories, files (e.g., README.md, LICENSE), and specific file contents (with a focus on `.py`, `.js`, `.html`, `.css` files) into a structured markdown document. Here's how the content is organized:

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

**Context:** You are tasked with addressing and fixing failing tests within the pytest testing suite for the `/code/quiz-app/quiz-app-backend` FastAPI project. This project encompasses Python scripts for models, schemas, CRUD operations, and API endpoints, which have been experiencing issues in their testing components. Utilizing SQLAlchemy ORM for database management and Pydantic for data validation, your goal is to identify and rectify the failing tests to ensure the project's stability and reliability.

**Steps:**

1. **Identify Failing Tests:**
   - Review the test execution results to identify which tests are failing. Pay special attention to tests related to API endpoints, database models, schemas, and CRUD operations.
   - Analyze the output and stack traces of failing tests to understand the nature of failures.

2. **Diagnose Issues:**
   - For each failing test, diagnose the underlying issue. This could involve problems with the test logic, incorrect assumptions about the codebase, or actual bugs in the application code.
   - Utilize logging, debugging tools, or insert additional assertions to gather more information about the test failure context.

3. **Address Test Environment Configurations:**
   - Ensure that the test environment setup, including installations and configurations (e.g., `pytest.ini` settings), are correctly aligned with the project requirements. Verify that any necessary plugins, like pytest-asyncio and pytest-factoryboy, are properly integrated.

4. **Refactor and Fix Tests:**
   - Based on your diagnosis, refactor or fix the failing tests. This may include updating test logic, correcting test data, or enhancing test setups with improved fixtures in `conftest.py`.
   - For issues stemming from the application code, work closely with the development team to address these bugs or inconsistencies.

5. **Verify Models and Schemas:**
   - Revisit tests for SQLAlchemy models (`app/models`) and Pydantic schemas (`app/schemas`) to ensure they accurately test database schema integrity, relationships, and validation rules.

6. **Enhance CRUD and API Endpoint Tests:**
   - Update tests covering CRUD operations (`app/crud`) and API endpoints (`app/api/endpoints`) to cover more edge cases and potential error scenarios, ensuring comprehensive validation of functionality and error handling.

7. **Improve Serialization and ORM Interaction Tests:**
   - Focus on enhancing tests that validate data serialization/deserialization and ORM interactions to confirm the fidelity of data conversion and database operations.

8. **Review and Optimize Test Coverage:**
   - After addressing the immediate failing tests, review the entire test suite for coverage gaps or areas that could benefit from additional test cases, especially as the application evolves.

9. **Refactor the Test Suite for Maintainability:**
   - Continuously refactor the test suite to improve readability, maintainability, and performance. Prioritize clean code, meaningful test names, and comprehensive comments to aid in debugging and future development.

10. **Document Fixes and Insights:**
    - Document the process of diagnosing and fixing each issue, including the root cause, the approach taken to fix it, and any changes made to the test or application code. This documentation will be invaluable for future troubleshooting and development efforts.

**Note:** While focusing on fixing failing tests, maintain a critical eye on the quality and clarity of both the tests and the application code. Collaborate with your development team to ensure that fixes are robust and in line with the project's standards and goals.
============================= test session starts ==============================
platform linux -- Python 3.11.8, pytest-8.0.2, pluggy-1.4.0
rootdir: /code/quiz-app/quiz-app-backend
configfile: pyproject.toml
plugins: anyio-4.3.0, cov-4.1.0
collected 67 items

tests/test_api.py ...                                                    [  4%]
tests/test_api_authentication.py .................FFF.                   [ 35%]
tests/test_api_question_sets.py .....                                    [ 43%]
tests/test_api_questions.py ....                                         [ 49%]
tests/test_api_user_responses.py .                                       [ 50%]
tests/test_api_users.py ..                                               [ 53%]
tests/test_auth_integration.py ...                                       [ 58%]
tests/test_core_auth.py .                                                [ 59%]
tests/test_core_jwt.py ....                                              [ 65%]
tests/test_crud.py ...                                                   [ 70%]
tests/test_crud_question_sets.py ...                                     [ 74%]
tests/test_crud_questions.py .....                                       [ 82%]
tests/test_crud_user.py .                                                [ 83%]
tests/test_crud_user_responses.py .                                      [ 85%]
tests/test_db_session.py .                                               [ 86%]
tests/test_jwt.py .                                                      [ 88%]
tests/test_models.py ...                                                 [ 92%]
tests/test_schemas.py ...                                                [ 97%]
tests/test_schemas_user.py ..                                            [100%]

=================================== FAILURES ===================================
___________________________ test_login_inactive_user ___________________________

client = <starlette.testclient.TestClient object at 0x7f4f71fea510>
test_user = <app.models.users.User object at 0x7f4f71fcdf10>
db_session = <sqlalchemy.orm.session.Session object at 0x7f4f71fe9290>

    def test_login_inactive_user(client, test_user, db_session):
        """
        Test login with an inactive user.
        """
        # Set the user as inactive
        test_user.is_active = False
        db_session.commit()
    
        response = client.post("/login", json={"username": test_user.username, "password": "TestPassword123"})
        assert response.status_code == 401
>       assert "User is inactive" in response.json()["detail"]
E       AssertionError: assert 'User is inactive' in 'Incorrect username or password'

tests/test_api_authentication.py:135: AssertionError
---------------------------- Captured stdout setup -----------------------------
Starting a new test session: <sqlalchemy.orm.session.Session object at 0x7f4f71fe9290>
----------------------------- Captured stdout call -----------------------------
Overriding get_db dependency with test session: <sqlalchemy.orm.session.Session object at 0x7f4f71fe9290>
Ending use of test session: <sqlalchemy.orm.session.Session object at 0x7f4f71fe9290>
--------------------------- Captured stdout teardown ---------------------------
Removed get_db override.
Test session committed.
Test session closed: <sqlalchemy.orm.session.Session object at 0x7f4f71fe9290>
_______________________ test_login_invalid_token_format ________________________

client = <starlette.testclient.TestClient object at 0x7f4f71ec48d0>

    def test_login_invalid_token_format(client):
        headers = {"Authorization": "Bearer invalid_token_format"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401
>       assert "Could not validate credentials" in response.json()["detail"]
E       AssertionError: assert 'Could not validate credentials' in 'Invalid token'

tests/test_api_authentication.py:141: AssertionError
---------------------------- Captured stdout setup -----------------------------
Starting a new test session: <sqlalchemy.orm.session.Session object at 0x7f4f71ec4790>
----------------------------- Captured stdout call -----------------------------
Overriding get_db dependency with test session: <sqlalchemy.orm.session.Session object at 0x7f4f71ec4790>
Ending use of test session: <sqlalchemy.orm.session.Session object at 0x7f4f71ec4790>
--------------------------- Captured stdout teardown ---------------------------
Removed get_db override.
Test session committed.
Test session closed: <sqlalchemy.orm.session.Session object at 0x7f4f71ec4790>
___________________________ test_login_expired_token ___________________________

client = <starlette.testclient.TestClient object at 0x7f4f71eddc10>
test_user = <app.models.users.User object at 0x7f4f71edf390>
test_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcl9GWVRrNSIsImV4cCI6MTcxMTg0NDg4Nn0.IKkGT0DcDyNoEEHIlVykCieZKGs-944JxFJaqiQqHNs'

    def test_login_expired_token(client, test_user, test_token):
        """
        Test accessing a protected route with an expired token.
        """
        # Create an expired token
        expired_token = create_access_token(data={"sub": test_user.username}, expires_delta=timedelta(minutes=-1))
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401
>       assert "Could not validate credentials" in response.json()["detail"]
E       AssertionError: assert 'Could not validate credentials' in 'Token has expired'

tests/test_api_authentication.py:152: AssertionError
---------------------------- Captured stdout setup -----------------------------
Starting a new test session: <sqlalchemy.orm.session.Session object at 0x7f4f71eddb10>
----------------------------- Captured stdout call -----------------------------
Overriding get_db dependency with test session: <sqlalchemy.orm.session.Session object at 0x7f4f71eddb10>
Ending use of test session: <sqlalchemy.orm.session.Session object at 0x7f4f71eddb10>
--------------------------- Captured stdout teardown ---------------------------
Removed get_db override.
Test session committed.
Test session closed: <sqlalchemy.orm.session.Session object at 0x7f4f71eddb10>

---------- coverage: platform linux, python 3.11.8-final-0 -----------
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
app/__init__.py                           0      0   100%
app/api/__init__.py                       1      0   100%
app/api/endpoints/__init__.py             1      0   100%
app/api/endpoints/auth.py                39      7    82%
app/api/endpoints/question_sets.py       42     11    74%
app/api/endpoints/questions.py           27      2    93%
app/api/endpoints/register.py            17      0   100%
app/api/endpoints/token.py               20      0   100%
app/api/endpoints/user_responses.py      27      9    67%
app/api/endpoints/users.py               21      2    90%
app/core/__init__.py                      1      0   100%
app/core/auth.py                         25      3    88%
app/core/config.py                        7      0   100%
app/core/jwt.py                          30      1    97%
app/core/security.py                      7      0   100%
app/crud/__init__.py                      4      0   100%
app/crud/crud_question_sets.py           28      4    86%
app/crud/crud_questions.py               31      8    74%
app/crud/crud_user.py                    30      3    90%
app/crud/crud_user_responses.py          13      1    92%
app/db/__init__.py                        2      0   100%
app/db/base_class.py                      3      0   100%
app/db/session.py                        14      1    93%
app/main.py                              40      3    92%
app/models/__init__.py                    8      0   100%
app/models/answer_choices.py             11      0   100%
app/models/question_sets.py               9      0   100%
app/models/questions.py                  13      0   100%
app/models/subjects.py                    9      0   100%
app/models/subtopics.py                  11      0   100%
app/models/token.py                       8      0   100%
app/models/topics.py                     11      0   100%
app/models/user_responses.py             18      0   100%
app/models/users.py                      11      0   100%
app/schemas/__init__.py                   6      0   100%
app/schemas/auth.py                       4      0   100%
app/schemas/question_sets.py             12      0   100%
app/schemas/questions.py                 15      0   100%
app/schemas/token.py                      5      0   100%
app/schemas/user.py                      24      0   100%
app/schemas/user_responses.py            15      0   100%
---------------------------------------------------------
TOTAL                                   620     55    91%

=========================== short test summary info ============================
FAILED tests/test_api_authentication.py::test_login_inactive_user - Assertion...
FAILED tests/test_api_authentication.py::test_login_invalid_token_format - As...
FAILED tests/test_api_authentication.py::test_login_expired_token - Assertion...
======================== 3 failed, 64 passed in 17.33s =========================

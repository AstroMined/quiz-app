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
platform linux -- Python 3.11.8, pytest-6.2.5, py-1.11.0, pluggy-1.4.0
rootdir: /code/quiz-app/quiz-app-backend, configfile: pyproject.toml
plugins: anyio-4.3.0, cov-4.1.0
collected 76 items

tests/test_api_authentication.py .........F........F..F.F                [ 31%]
tests/test_api_question_sets.py F.FFF.FFFFF                              [ 46%]
tests/test_api_questions.py .....                                        [ 52%]
tests/test_api_user_responses.py .                                       [ 53%]
tests/test_api_users.py ..                                               [ 56%]
tests/test_auth_integration.py .FF                                       [ 60%]
tests/test_core_auth.py .                                                [ 61%]
tests/test_core_jwt.py ....                                              [ 67%]
tests/test_crud.py ...                                                   [ 71%]
tests/test_crud_question_sets.py .....                                   [ 77%]
tests/test_crud_questions.py .....                                       [ 84%]
tests/test_crud_user.py .                                                [ 85%]
tests/test_crud_user_responses.py .                                      [ 86%]
tests/test_db_session.py .                                               [ 88%]
tests/test_jwt.py .                                                      [ 89%]
tests/test_models.py ...                                                 [ 93%]
tests/test_schemas.py ...                                                [ 97%]
tests/test_schemas_user.py ..                                            [100%]

=================================== FAILURES ===================================
______________ test_access_protected_endpoint_with_invalid_token _______________

self = <sqlalchemy.engine.base.Connection object at 0x7f785cc7e7d0>
dialect = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f785e503310>
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f785cc7ded0>
statement = <sqlalchemy.dialects.sqlite.base.SQLiteCompiler object at 0x7f785cc8b250>
parameters = [('invalid_token', 1, 0)]

    def _exec_single_context(
        self,
        dialect: Dialect,
        context: ExecutionContext,
        statement: Union[str, Compiled],
        parameters: Optional[_AnyMultiExecuteParams],
    ) -> CursorResult[Any]:
        """continue the _execute_context() method for a single DBAPI
        cursor.execute() or cursor.executemany() call.
    
        """
        if dialect.bind_typing is BindTyping.SETINPUTSIZES:
            generic_setinputsizes = context._prepare_set_input_sizes()
    
            if generic_setinputsizes:
                try:
                    dialect.do_set_input_sizes(
                        context.cursor, generic_setinputsizes, context
                    )
                except BaseException as e:
                    self._handle_dbapi_exception(
                        e, str(statement), parameters, None, context
                    )
    
        cursor, str_statement, parameters = (
            context.cursor,
            context.statement,
            context.parameters,
        )
    
        effective_parameters: Optional[_AnyExecuteParams]
    
        if not context.executemany:
            effective_parameters = parameters[0]
        else:
            effective_parameters = parameters
    
        if self._has_events or self.engine._has_events:
            for fn in self.dispatch.before_cursor_execute:
                str_statement, effective_parameters = fn(
                    self,
                    cursor,
                    str_statement,
                    effective_parameters,
                    context,
                    context.executemany,
                )
    
        if self._echo:
            self._log_info(str_statement)
    
            stats = context._get_cache_stats()
    
            if not self.engine.hide_parameters:
                self._log_info(
                    "[%s] %r",
                    stats,
                    sql_util._repr_params(
                        effective_parameters,
                        batches=10,
                        ismulti=context.executemany,
                    ),
                )
            else:
                self._log_info(
                    "[%s] [SQL parameters hidden due to hide_parameters=True]",
                    stats,
                )
    
        evt_handled: bool = False
        try:
            if context.execute_style is ExecuteStyle.EXECUTEMANY:
                effective_parameters = cast(
                    "_CoreMultiExecuteParams", effective_parameters
                )
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_executemany:
                        if fn(
                            cursor,
                            str_statement,
                            effective_parameters,
                            context,
                        ):
                            evt_handled = True
                            break
                if not evt_handled:
                    self.dialect.do_executemany(
                        cursor,
                        str_statement,
                        effective_parameters,
                        context,
                    )
            elif not effective_parameters and context.no_parameters:
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_execute_no_params:
                        if fn(cursor, str_statement, context):
                            evt_handled = True
                            break
                if not evt_handled:
                    self.dialect.do_execute_no_params(
                        cursor, str_statement, context
                    )
            else:
                effective_parameters = cast(
                    "_CoreSingleExecuteParams", effective_parameters
                )
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_execute:
                        if fn(
                            cursor,
                            str_statement,
                            effective_parameters,
                            context,
                        ):
                            evt_handled = True
                            break
                if not evt_handled:
>                   self.dialect.do_execute(
                        cursor, str_statement, effective_parameters, context
                    )

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1960: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f785e503310>
cursor = <sqlite3.Cursor object at 0x7f785cc18740>
statement = 'SELECT revoked_tokens.id AS revoked_tokens_id, revoked_tokens.token AS revoked_tokens_token, revoked_tokens.revoked_at AS revoked_tokens_revoked_at \nFROM revoked_tokens \nWHERE revoked_tokens.token = ?\n LIMIT ? OFFSET ?'
parameters = ('invalid_token', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f785cc7ded0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlite3.OperationalError: no such table: revoked_tokens

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError

The above exception was the direct cause of the following exception:

client = <starlette.testclient.TestClient object at 0x7f785d619790>

    def test_access_protected_endpoint_with_invalid_token(client):
        headers = {"Authorization": "Bearer invalid_token"}
>       response = client.get("/users/", headers=headers)

tests/test_api_authentication.py:70: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:523: in get
    return super().get(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1054: in get
    return self.request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:491: in request
    return super().request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:827: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1015: in _send_single_request
    response = transport.handle_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:372: in handle_request
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:369: in handle_request
    portal.call(self.app, scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:288: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:456: in result
    return self.__get_result()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:217: in _call_func
    retval = await retval_or_awaitable
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/applications.py:123: in __call__
    await self.middleware_stack(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:189: in __call__
    with collapse_excgroups():
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/contextlib.py:158: in __exit__
    self.gen.throw(typ, value, traceback)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:93: in collapse_excgroups
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:191: in __call__
    response = await self.dispatch_func(request, call_next)
app/main.py:50: in check_revoked_token
    revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/query.py:2727: in first
    return self.limit(1)._iter().first()  # type: ignore
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/query.py:2826: in _iter
    result: Union[ScalarResult[_T], Result[_T]] = self.session.execute(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/session.py:2306: in execute
    return self._execute_internal(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/session.py:2191: in _execute_internal
    result: Result[Any] = compile_state_cls.orm_execute_statement(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/context.py:293: in orm_execute_statement
    result = conn.execute(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1408: in execute
    return meth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/sql/elements.py:513: in _execute_on_connection
    return connection._execute_clauseelement(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1630: in _execute_clauseelement
    ret = self._execute_context(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1839: in _execute_context
    return self._exec_single_context(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1979: in _exec_single_context
    self._handle_dbapi_exception(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:2335: in _handle_dbapi_exception
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1960: in _exec_single_context
    self.dialect.do_execute(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f785e503310>
cursor = <sqlite3.Cursor object at 0x7f785cc18740>
statement = 'SELECT revoked_tokens.id AS revoked_tokens_id, revoked_tokens.token AS revoked_tokens_token, revoked_tokens.revoked_at AS revoked_tokens_revoked_at \nFROM revoked_tokens \nWHERE revoked_tokens.token = ?\n LIMIT ? OFFSET ?'
parameters = ('invalid_token', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f785cc7ded0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: revoked_tokens
E       [SQL: SELECT revoked_tokens.id AS revoked_tokens_id, revoked_tokens.token AS revoked_tokens_token, revoked_tokens.revoked_at AS revoked_tokens_revoked_at 
E       FROM revoked_tokens 
E       WHERE revoked_tokens.token = ?
E        LIMIT ? OFFSET ?]
E       [parameters: ('invalid_token', 1, 0)]
E       (Background on this error at: https://sqlalche.me/e/20/e3q8)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError
_______________________ test_login_invalid_token_format ________________________

self = <sqlalchemy.engine.base.Connection object at 0x7f7857b25f50>
dialect = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f785e503310>
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f7857b260d0>
statement = <sqlalchemy.dialects.sqlite.base.SQLiteCompiler object at 0x7f785cc8b250>
parameters = [('invalid_token_format', 1, 0)]

    def _exec_single_context(
        self,
        dialect: Dialect,
        context: ExecutionContext,
        statement: Union[str, Compiled],
        parameters: Optional[_AnyMultiExecuteParams],
    ) -> CursorResult[Any]:
        """continue the _execute_context() method for a single DBAPI
        cursor.execute() or cursor.executemany() call.
    
        """
        if dialect.bind_typing is BindTyping.SETINPUTSIZES:
            generic_setinputsizes = context._prepare_set_input_sizes()
    
            if generic_setinputsizes:
                try:
                    dialect.do_set_input_sizes(
                        context.cursor, generic_setinputsizes, context
                    )
                except BaseException as e:
                    self._handle_dbapi_exception(
                        e, str(statement), parameters, None, context
                    )
    
        cursor, str_statement, parameters = (
            context.cursor,
            context.statement,
            context.parameters,
        )
    
        effective_parameters: Optional[_AnyExecuteParams]
    
        if not context.executemany:
            effective_parameters = parameters[0]
        else:
            effective_parameters = parameters
    
        if self._has_events or self.engine._has_events:
            for fn in self.dispatch.before_cursor_execute:
                str_statement, effective_parameters = fn(
                    self,
                    cursor,
                    str_statement,
                    effective_parameters,
                    context,
                    context.executemany,
                )
    
        if self._echo:
            self._log_info(str_statement)
    
            stats = context._get_cache_stats()
    
            if not self.engine.hide_parameters:
                self._log_info(
                    "[%s] %r",
                    stats,
                    sql_util._repr_params(
                        effective_parameters,
                        batches=10,
                        ismulti=context.executemany,
                    ),
                )
            else:
                self._log_info(
                    "[%s] [SQL parameters hidden due to hide_parameters=True]",
                    stats,
                )
    
        evt_handled: bool = False
        try:
            if context.execute_style is ExecuteStyle.EXECUTEMANY:
                effective_parameters = cast(
                    "_CoreMultiExecuteParams", effective_parameters
                )
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_executemany:
                        if fn(
                            cursor,
                            str_statement,
                            effective_parameters,
                            context,
                        ):
                            evt_handled = True
                            break
                if not evt_handled:
                    self.dialect.do_executemany(
                        cursor,
                        str_statement,
                        effective_parameters,
                        context,
                    )
            elif not effective_parameters and context.no_parameters:
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_execute_no_params:
                        if fn(cursor, str_statement, context):
                            evt_handled = True
                            break
                if not evt_handled:
                    self.dialect.do_execute_no_params(
                        cursor, str_statement, context
                    )
            else:
                effective_parameters = cast(
                    "_CoreSingleExecuteParams", effective_parameters
                )
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_execute:
                        if fn(
                            cursor,
                            str_statement,
                            effective_parameters,
                            context,
                        ):
                            evt_handled = True
                            break
                if not evt_handled:
>                   self.dialect.do_execute(
                        cursor, str_statement, effective_parameters, context
                    )

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1960: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f785e503310>
cursor = <sqlite3.Cursor object at 0x7f7856af4ac0>
statement = 'SELECT revoked_tokens.id AS revoked_tokens_id, revoked_tokens.token AS revoked_tokens_token, revoked_tokens.revoked_at AS revoked_tokens_revoked_at \nFROM revoked_tokens \nWHERE revoked_tokens.token = ?\n LIMIT ? OFFSET ?'
parameters = ('invalid_token_format', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f7857b260d0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlite3.OperationalError: no such table: revoked_tokens

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError

The above exception was the direct cause of the following exception:

client = <starlette.testclient.TestClient object at 0x7f785d637390>

    def test_login_invalid_token_format(client):
        headers = {"Authorization": "Bearer invalid_token_format"}
>       response = client.get("/users/", headers=headers)

tests/test_api_authentication.py:138: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:523: in get
    return super().get(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1054: in get
    return self.request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:491: in request
    return super().request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:827: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1015: in _send_single_request
    response = transport.handle_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:372: in handle_request
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:369: in handle_request
    portal.call(self.app, scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:288: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:456: in result
    return self.__get_result()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:217: in _call_func
    retval = await retval_or_awaitable
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/applications.py:123: in __call__
    await self.middleware_stack(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:189: in __call__
    with collapse_excgroups():
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/contextlib.py:158: in __exit__
    self.gen.throw(typ, value, traceback)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:93: in collapse_excgroups
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:191: in __call__
    response = await self.dispatch_func(request, call_next)
app/main.py:50: in check_revoked_token
    revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/query.py:2727: in first
    return self.limit(1)._iter().first()  # type: ignore
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/query.py:2826: in _iter
    result: Union[ScalarResult[_T], Result[_T]] = self.session.execute(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/session.py:2306: in execute
    return self._execute_internal(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/session.py:2191: in _execute_internal
    result: Result[Any] = compile_state_cls.orm_execute_statement(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/context.py:293: in orm_execute_statement
    result = conn.execute(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1408: in execute
    return meth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/sql/elements.py:513: in _execute_on_connection
    return connection._execute_clauseelement(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1630: in _execute_clauseelement
    ret = self._execute_context(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1839: in _execute_context
    return self._exec_single_context(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1979: in _exec_single_context
    self._handle_dbapi_exception(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:2335: in _handle_dbapi_exception
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1960: in _exec_single_context
    self.dialect.do_execute(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f785e503310>
cursor = <sqlite3.Cursor object at 0x7f7856af4ac0>
statement = 'SELECT revoked_tokens.id AS revoked_tokens_id, revoked_tokens.token AS revoked_tokens_token, revoked_tokens.revoked_at AS revoked_tokens_revoked_at \nFROM revoked_tokens \nWHERE revoked_tokens.token = ?\n LIMIT ? OFFSET ?'
parameters = ('invalid_token_format', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f7857b260d0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: revoked_tokens
E       [SQL: SELECT revoked_tokens.id AS revoked_tokens_id, revoked_tokens.token AS revoked_tokens_token, revoked_tokens.revoked_at AS revoked_tokens_revoked_at 
E       FROM revoked_tokens 
E       WHERE revoked_tokens.token = ?
E        LIMIT ? OFFSET ?]
E       [parameters: ('invalid_token_format', 1, 0)]
E       (Background on this error at: https://sqlalche.me/e/20/e3q8)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError
__________________________ test_logout_revoked_token ___________________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f785d6e1410>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f785e6d1990>, 'client': None, 'extensions': {'http.response.debug':...*'), (b'accept-encoding', b'gzip, deflate'), (b'connection', b'keep-alive'), (b'user-agent', b'testclient'), ...], ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f785ccc5760>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f785ccc7880>

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
    
        request = _CachedRequest(scope, receive)
        wrapped_receive = request.wrapped_receive
        response_sent = anyio.Event()
    
        async def call_next(request: Request) -> Response:
            app_exc: typing.Optional[Exception] = None
            send_stream: ObjectSendStream[typing.MutableMapping[str, typing.Any]]
            recv_stream: ObjectReceiveStream[typing.MutableMapping[str, typing.Any]]
            send_stream, recv_stream = anyio.create_memory_object_stream()
    
            async def receive_or_disconnect() -> Message:
                if response_sent.is_set():
                    return {"type": "http.disconnect"}
    
                async with anyio.create_task_group() as task_group:
    
                    async def wrap(func: typing.Callable[[], typing.Awaitable[T]]) -> T:
                        result = await func()
                        task_group.cancel_scope.cancel()
                        return result
    
                    task_group.start_soon(wrap, response_sent.wait)
                    message = await wrap(wrapped_receive)
    
                if response_sent.is_set():
                    return {"type": "http.disconnect"}
    
                return message
    
            async def close_recv_stream_on_response_sent() -> None:
                await response_sent.wait()
                recv_stream.close()
    
            async def send_no_error(message: Message) -> None:
                try:
                    await send_stream.send(message)
                except anyio.BrokenResourceError:
                    # recv_stream has been closed, i.e. response_sent has been set.
                    return
    
            async def coro() -> None:
                nonlocal app_exc
    
                async with send_stream:
                    try:
                        await self.app(scope, receive_or_disconnect, send_no_error)
                    except Exception as exc:
                        app_exc = exc
    
            task_group.start_soon(close_recv_stream_on_response_sent)
            task_group.start_soon(coro)
    
            try:
                message = await recv_stream.receive()
                info = message.get("info", None)
                if message["type"] == "http.response.debug" and info is not None:
                    message = await recv_stream.receive()
            except anyio.EndOfStream:
                if app_exc is not None:
                    raise app_exc
                raise RuntimeError("No response returned.")
    
            assert message["type"] == "http.response.start"
    
            async def body_stream() -> typing.AsyncGenerator[bytes, None]:
                async with recv_stream:
                    async for message in recv_stream:
                        assert message["type"] == "http.response.body"
                        body = message.get("body", b"")
                        if body:
                            yield body
                        if not message.get("more_body", False):
                            break
    
                if app_exc is not None:
                    raise app_exc
    
            response = _StreamingResponse(
                status_code=message["status"], content=body_stream(), info=info
            )
            response.raw_headers = message["headers"]
            return response
    
        with collapse_excgroups():
>           async with anyio.create_task_group() as task_group:

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:190: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <anyio._backends._asyncio.TaskGroup object at 0x7f78577ef250>
exc_type = <class 'fastapi.exceptions.HTTPException'>
exc_val = HTTPException(status_code=401, detail='Token has been revoked')
exc_tb = <traceback object at 0x7f785776bd40>

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        ignore_exception = self.cancel_scope.__exit__(exc_type, exc_val, exc_tb)
        if exc_val is not None:
            self.cancel_scope.cancel()
            if not isinstance(exc_val, CancelledError):
                self._exceptions.append(exc_val)
    
        cancelled_exc_while_waiting_tasks: CancelledError | None = None
        while self._tasks:
            try:
                await asyncio.wait(self._tasks)
            except CancelledError as exc:
                # This task was cancelled natively; reraise the CancelledError later
                # unless this task was already interrupted by another exception
                self.cancel_scope.cancel()
                if cancelled_exc_while_waiting_tasks is None:
                    cancelled_exc_while_waiting_tasks = exc
    
        self._active = False
        if self._exceptions:
>           raise BaseExceptionGroup(
                "unhandled errors in a TaskGroup", self._exceptions
            )
E           ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:678: ExceptionGroup

During handling of the above exception, another exception occurred:

client = <starlette.testclient.TestClient object at 0x7f7857125e50>
test_user = <app.models.users.UserModel object at 0x7f78577d8350>
test_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcl91Szg1cCIsImV4cCI6MTcxMjE4NzA2MX0.zCTl4-WdWctC3o9RyL2FmvXTyEdto0yL8cDd8D1OgKE'
db_session = <sqlalchemy.orm.session.Session object at 0x7f78577d9f50>

    def test_logout_revoked_token(client, test_user, test_token, db_session):
        """
        Test logout with an already revoked token.
        """
        # Revoke the token manually
        revoked_token = RevokedTokenModel(token=test_token)
        db_session.add(revoked_token)
        db_session.commit()
    
        headers = {"Authorization": f"Bearer {test_token}"}
>       response = client.post("/logout", headers=headers)

tests/test_api_authentication.py:172: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:608: in post
    return super().post(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1145: in post
    return self.request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:491: in request
    return super().request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:827: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1015: in _send_single_request
    response = transport.handle_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:372: in handle_request
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:369: in handle_request
    portal.call(self.app, scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:288: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:456: in result
    return self.__get_result()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:217: in _call_func
    retval = await retval_or_awaitable
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/applications.py:123: in __call__
    await self.middleware_stack(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:189: in __call__
    with collapse_excgroups():
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/contextlib.py:158: in __exit__
    self.gen.throw(typ, value, traceback)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:93: in collapse_excgroups
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:191: in __call__
    response = await self.dispatch_func(request, call_next)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

request = <starlette.middleware.base._CachedRequest object at 0x7f78577eea10>
call_next = <function BaseHTTPMiddleware.__call__.<locals>.call_next at 0x7f785ccc45e0>

    @app.middleware("http")
    async def check_revoked_token(request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            db = next(get_db())
            revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
            if revoked_token:
>               raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
E               fastapi.exceptions.HTTPException: 401: Token has been revoked

app/main.py:52: HTTPException
____________________________ test_login_logout_flow ____________________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f785d6e1410>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f785e6d1990>, 'client': None, 'extensions': {'http.response.debug':...I6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcl9DUEk1cCIsImV4cCI6MTcxMjE4NzA2M30.bp_EGkFtkVS4xajmMUyU239gZddK3OosxeGg9mDbZN4')], ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f785d7f7240>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f7857ebb100>

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
    
        request = _CachedRequest(scope, receive)
        wrapped_receive = request.wrapped_receive
        response_sent = anyio.Event()
    
        async def call_next(request: Request) -> Response:
            app_exc: typing.Optional[Exception] = None
            send_stream: ObjectSendStream[typing.MutableMapping[str, typing.Any]]
            recv_stream: ObjectReceiveStream[typing.MutableMapping[str, typing.Any]]
            send_stream, recv_stream = anyio.create_memory_object_stream()
    
            async def receive_or_disconnect() -> Message:
                if response_sent.is_set():
                    return {"type": "http.disconnect"}
    
                async with anyio.create_task_group() as task_group:
    
                    async def wrap(func: typing.Callable[[], typing.Awaitable[T]]) -> T:
                        result = await func()
                        task_group.cancel_scope.cancel()
                        return result
    
                    task_group.start_soon(wrap, response_sent.wait)
                    message = await wrap(wrapped_receive)
    
                if response_sent.is_set():
                    return {"type": "http.disconnect"}
    
                return message
    
            async def close_recv_stream_on_response_sent() -> None:
                await response_sent.wait()
                recv_stream.close()
    
            async def send_no_error(message: Message) -> None:
                try:
                    await send_stream.send(message)
                except anyio.BrokenResourceError:
                    # recv_stream has been closed, i.e. response_sent has been set.
                    return
    
            async def coro() -> None:
                nonlocal app_exc
    
                async with send_stream:
                    try:
                        await self.app(scope, receive_or_disconnect, send_no_error)
                    except Exception as exc:
                        app_exc = exc
    
            task_group.start_soon(close_recv_stream_on_response_sent)
            task_group.start_soon(coro)
    
            try:
                message = await recv_stream.receive()
                info = message.get("info", None)
                if message["type"] == "http.response.debug" and info is not None:
                    message = await recv_stream.receive()
            except anyio.EndOfStream:
                if app_exc is not None:
                    raise app_exc
                raise RuntimeError("No response returned.")
    
            assert message["type"] == "http.response.start"
    
            async def body_stream() -> typing.AsyncGenerator[bytes, None]:
                async with recv_stream:
                    async for message in recv_stream:
                        assert message["type"] == "http.response.body"
                        body = message.get("body", b"")
                        if body:
                            yield body
                        if not message.get("more_body", False):
                            break
    
                if app_exc is not None:
                    raise app_exc
    
            response = _StreamingResponse(
                status_code=message["status"], content=body_stream(), info=info
            )
            response.raw_headers = message["headers"]
            return response
    
        with collapse_excgroups():
>           async with anyio.create_task_group() as task_group:

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:190: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <anyio._backends._asyncio.TaskGroup object at 0x7f7857304910>
exc_type = <class 'fastapi.exceptions.HTTPException'>
exc_val = HTTPException(status_code=401, detail='Token has been revoked')
exc_tb = <traceback object at 0x7f7857307680>

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        ignore_exception = self.cancel_scope.__exit__(exc_type, exc_val, exc_tb)
        if exc_val is not None:
            self.cancel_scope.cancel()
            if not isinstance(exc_val, CancelledError):
                self._exceptions.append(exc_val)
    
        cancelled_exc_while_waiting_tasks: CancelledError | None = None
        while self._tasks:
            try:
                await asyncio.wait(self._tasks)
            except CancelledError as exc:
                # This task was cancelled natively; reraise the CancelledError later
                # unless this task was already interrupted by another exception
                self.cancel_scope.cancel()
                if cancelled_exc_while_waiting_tasks is None:
                    cancelled_exc_while_waiting_tasks = exc
    
        self._active = False
        if self._exceptions:
>           raise BaseExceptionGroup(
                "unhandled errors in a TaskGroup", self._exceptions
            )
E           ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:678: ExceptionGroup

During handling of the above exception, another exception occurred:

client = <starlette.testclient.TestClient object at 0x7f78576fcc50>
test_user = <app.models.users.UserModel object at 0x7f78576e3690>

    def test_login_logout_flow(client, test_user):
        """
        Test the complete login and logout flow.
        """
        # Login
        login_data = {"username": test_user.username, "password": "TestPassword123!"}
        login_response = client.post("/login", json=login_data)
        access_token = login_response.json()["access_token"]
        assert login_response.status_code == 200, "Authentication failed."
        assert "access_token" in login_response.json(), "Access token missing in response."
        assert login_response.json()["token_type"] == "bearer", "Incorrect token type."
    
        # Access a protected endpoint with the token
        headers = {"Authorization": f"Bearer {access_token}"}
        protected_response = client.get("/users/", headers=headers)
        assert protected_response.status_code == 200
    
        # Logout
        logout_response = client.post("/logout", headers=headers)
        assert logout_response.status_code == 200
    
        # Try accessing the protected endpoint again after logout
>       protected_response_after_logout = client.get("/users/", headers=headers)

tests/test_api_authentication.py:211: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:523: in get
    return super().get(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1054: in get
    return self.request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:491: in request
    return super().request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:827: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1015: in _send_single_request
    response = transport.handle_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:372: in handle_request
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:369: in handle_request
    portal.call(self.app, scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:288: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:456: in result
    return self.__get_result()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:217: in _call_func
    retval = await retval_or_awaitable
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/applications.py:123: in __call__
    await self.middleware_stack(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:189: in __call__
    with collapse_excgroups():
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/contextlib.py:158: in __exit__
    self.gen.throw(typ, value, traceback)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:93: in collapse_excgroups
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:191: in __call__
    response = await self.dispatch_func(request, call_next)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

request = <starlette.middleware.base._CachedRequest object at 0x7f7857305690>
call_next = <function BaseHTTPMiddleware.__call__.<locals>.call_next at 0x7f7857eb8e00>

    @app.middleware("http")
    async def check_revoked_token(request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            db = next(get_db())
            revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
            if revoked_token:
>               raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
E               fastapi.exceptions.HTTPException: 401: Token has been revoked

app/main.py:52: HTTPException
___________________________ test_create_question_set ___________________________

client = <starlette.testclient.TestClient object at 0x7f785c291390>
db_session = <sqlalchemy.orm.session.Session object at 0x7f785c292990>

    def test_create_question_set(client, db_session):
        data = {"name": "Test Create Question Set"}
        response = client.post("/question-sets/", json=data)
>       assert response.status_code == 201
E       assert 401 == 201
E        +  where 401 = <Response [401 Unauthorized]>.status_code

tests/test_api_question_sets.py:9: AssertionError
_____________________ test_update_nonexistent_question_set _____________________

client = <starlette.testclient.TestClient object at 0x7f785cc4b6d0>
test_user = <app.models.users.UserModel object at 0x7f785c293890>

    def test_update_nonexistent_question_set(client, test_user):
        """
        Test updating a question set that does not exist.
        """
        question_set_update = {"name": "Updated Name"}
        response = client.put("/question-sets/99999", json=question_set_update)
>       assert response.status_code == 404
E       assert 401 == 404
E        +  where 401 = <Response [401 Unauthorized]>.status_code

tests/test_api_question_sets.py:23: AssertionError
______________________ test_update_question_set_not_found ______________________

client = <starlette.testclient.TestClient object at 0x7f78571f84d0>
db_session = <sqlalchemy.orm.session.Session object at 0x7f785cc49f90>

    def test_update_question_set_not_found(client, db_session):
        question_set_id = 999
        question_set_update = {"name": "Updated Name"}
        response = client.put(f"/question-sets/{question_set_id}", json=question_set_update)
>       assert response.status_code == 404
E       assert 401 == 404
E        +  where 401 = <Response [401 Unauthorized]>.status_code

tests/test_api_question_sets.py:30: AssertionError
______________________ test_delete_question_set_not_found ______________________

client = <starlette.testclient.TestClient object at 0x7f7857323750>
db_session = <sqlalchemy.orm.session.Session object at 0x7f785d61b850>

    def test_delete_question_set_not_found(client, db_session):
        """
        Test deleting a question set that does not exist.
        """
        question_set_id = 999
        response = client.delete(f"/question-sets/{question_set_id}")
>       assert response.status_code == 404
E       assert 401 == 404
E        +  where 401 = <Response [401 Unauthorized]>.status_code

tests/test_api_question_sets.py:39: AssertionError
____________________ test_upload_question_set_invalid_json _____________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f785d6e1410>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f785e6d1990>, 'client': None, 'endpoint': <function upload_question_set_endpoint at 0x7f785d8e2020>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f785cccd440>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f785ccce340>

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
    
        request = _CachedRequest(scope, receive)
        wrapped_receive = request.wrapped_receive
        response_sent = anyio.Event()
    
        async def call_next(request: Request) -> Response:
            app_exc: typing.Optional[Exception] = None
            send_stream: ObjectSendStream[typing.MutableMapping[str, typing.Any]]
            recv_stream: ObjectReceiveStream[typing.MutableMapping[str, typing.Any]]
            send_stream, recv_stream = anyio.create_memory_object_stream()
    
            async def receive_or_disconnect() -> Message:
                if response_sent.is_set():
                    return {"type": "http.disconnect"}
    
                async with anyio.create_task_group() as task_group:
    
                    async def wrap(func: typing.Callable[[], typing.Awaitable[T]]) -> T:
                        result = await func()
                        task_group.cancel_scope.cancel()
                        return result
    
                    task_group.start_soon(wrap, response_sent.wait)
                    message = await wrap(wrapped_receive)
    
                if response_sent.is_set():
                    return {"type": "http.disconnect"}
    
                return message
    
            async def close_recv_stream_on_response_sent() -> None:
                await response_sent.wait()
                recv_stream.close()
    
            async def send_no_error(message: Message) -> None:
                try:
                    await send_stream.send(message)
                except anyio.BrokenResourceError:
                    # recv_stream has been closed, i.e. response_sent has been set.
                    return
    
            async def coro() -> None:
                nonlocal app_exc
    
                async with send_stream:
                    try:
                        await self.app(scope, receive_or_disconnect, send_no_error)
                    except Exception as exc:
                        app_exc = exc
    
            task_group.start_soon(close_recv_stream_on_response_sent)
            task_group.start_soon(coro)
    
            try:
                message = await recv_stream.receive()
                info = message.get("info", None)
                if message["type"] == "http.response.debug" and info is not None:
                    message = await recv_stream.receive()
            except anyio.EndOfStream:
                if app_exc is not None:
                    raise app_exc
                raise RuntimeError("No response returned.")
    
            assert message["type"] == "http.response.start"
    
            async def body_stream() -> typing.AsyncGenerator[bytes, None]:
                async with recv_stream:
                    async for message in recv_stream:
                        assert message["type"] == "http.response.body"
                        body = message.get("body", b"")
                        if body:
                            yield body
                        if not message.get("more_body", False):
                            break
    
                if app_exc is not None:
                    raise app_exc
    
            response = _StreamingResponse(
                status_code=message["status"], content=body_stream(), info=info
            )
            response.raw_headers = message["headers"]
            return response
    
        with collapse_excgroups():
>           async with anyio.create_task_group() as task_group:

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:190: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <anyio._backends._asyncio.TaskGroup object at 0x7f7857ba0fd0>
exc_type = <class 'NameError'>
exc_val = NameError("name 'ValidationError' is not defined")
exc_tb = <traceback object at 0x7f7857ba0140>

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        ignore_exception = self.cancel_scope.__exit__(exc_type, exc_val, exc_tb)
        if exc_val is not None:
            self.cancel_scope.cancel()
            if not isinstance(exc_val, CancelledError):
                self._exceptions.append(exc_val)
    
        cancelled_exc_while_waiting_tasks: CancelledError | None = None
        while self._tasks:
            try:
                await asyncio.wait(self._tasks)
            except CancelledError as exc:
                # This task was cancelled natively; reraise the CancelledError later
                # unless this task was already interrupted by another exception
                self.cancel_scope.cancel()
                if cancelled_exc_while_waiting_tasks is None:
                    cancelled_exc_while_waiting_tasks = exc
    
        self._active = False
        if self._exceptions:
>           raise BaseExceptionGroup(
                "unhandled errors in a TaskGroup", self._exceptions
            )
E           ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:678: ExceptionGroup

During handling of the above exception, another exception occurred:

client = <starlette.testclient.TestClient object at 0x7f7857322fd0>
test_user = <app.models.users.UserModel object at 0x7f78577ec050>

    def test_upload_question_set_invalid_json(client, test_user):
        # Login
        login_data = {"username": test_user.username, "password": "TestPassword123!"}
        login_response = client.post("/login", json=login_data)
        access_token = login_response.json()["access_token"]
    
        # Prepare invalid JSON data
        invalid_json = "{'invalid': 'json'}"
    
        # Create a temporary file with the invalid JSON data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_file.write(invalid_json)
            temp_file.flush()  # Ensure the contents are written to the file
            headers = {"Authorization": f"Bearer {access_token}"}
>           response = client.post("/upload-questions/", files={"file": ("invalid.json", open(temp_file.name, 'rb'), "application/json")}, headers=headers)

tests/test_api_question_sets.py:102: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:608: in post
    return super().post(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1145: in post
    return self.request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:491: in request
    return super().request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:827: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1015: in _send_single_request
    response = transport.handle_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:372: in handle_request
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:369: in handle_request
    portal.call(self.app, scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:288: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:456: in result
    return self.__get_result()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:217: in _call_func
    retval = await retval_or_awaitable
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/applications.py:123: in __call__
    await self.middleware_stack(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:189: in __call__
    with collapse_excgroups():
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/contextlib.py:158: in __exit__
    self.gen.throw(typ, value, traceback)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:93: in collapse_excgroups
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:191: in __call__
    response = await self.dispatch_func(request, call_next)
app/main.py:53: in check_revoked_token
    response = await call_next(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:165: in call_next
    raise app_exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:151: in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:189: in __call__
    with collapse_excgroups():
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/contextlib.py:158: in __exit__
    self.gen.throw(typ, value, traceback)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:93: in collapse_excgroups
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:191: in __call__
    response = await self.dispatch_func(request, call_next)
app/main.py:41: in check_blacklist
    response = await call_next(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:165: in call_next
    raise app_exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:151: in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/exceptions.py:62: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_exception_handler.py:64: in wrapped_app
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    await app(scope, receive, sender)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/routing.py:758: in __call__
    await self.middleware_stack(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/routing.py:778: in app
    await route.handle(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/routing.py:299: in handle
    await self.app(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/routing.py:79: in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_exception_handler.py:64: in wrapped_app
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    await app(scope, receive, sender)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/routing.py:74: in app
    response = await func(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/routing.py:278: in app
    raw_response = await run_endpoint_function(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/routing.py:191: in run_endpoint_function
    return await dependant.call(**values)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

file = UploadFile(filename='invalid.json', size=19, headers=Headers({'content-disposition': 'form-data; name="file"; filename="invalid.json"', 'content-type': 'application/json'}))
db = <sqlalchemy.orm.session.Session object at 0x7f785cc49050>
current_user = <app.models.users.UserModel object at 0x7f7857321410>

    @router.post("/upload-questions/")
    async def upload_question_set_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
        """
        Endpoint to upload a question set in JSON format.
        """
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can upload question sets")
    
        try:
            content = await file.read()
            question_data = json.loads(content.decode('utf-8'))
    
            # Validate question data
            for question in question_data:
                QuestionCreateSchema(**question)  # Validate question against schema
    
            # Create question set
            question_set = QuestionSetCreateSchema(name=file.filename)
            question_set_created = create_question_set_crud(db, question_set)
    
            # Create questions and associate with question set
            for question in question_data:
                question['question_set_id'] = question_set_created.id
                create_question_crud(db, QuestionCreateSchema(**question))
    
            return {"message": "Question set uploaded successfully"}
    
>       except (json.JSONDecodeError, ValidationError) as exc:
E       NameError: name 'ValidationError' is not defined

app/api/endpoints/question_sets.py:69: NameError
_________________ test_create_question_set_with_existing_name __________________

client = <starlette.testclient.TestClient object at 0x7f7857056610>
db_session = <sqlalchemy.orm.session.Session object at 0x7f7857057c90>
test_question_set = <app.models.question_sets.QuestionSetModel object at 0x7f7857056f50>

    def test_create_question_set_with_existing_name(client, db_session, test_question_set):
        data = {"name": test_question_set.name}
        response = client.post("/question-sets/", json=data)
>       assert response.status_code == 400
E       assert 401 == 400
E        +  where 401 = <Response [401 Unauthorized]>.status_code

tests/test_api_question_sets.py:112: AssertionError
__________________ test_retrieve_question_set_with_questions ___________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f785d6e1410>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f785e6d1990>, 'client': None, 'endpoint': <function get_question_set_endpoint at 0x7f785d8bff60>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f7857a26160>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f7857a276a0>

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
    
        request = _CachedRequest(scope, receive)
        wrapped_receive = request.wrapped_receive
        response_sent = anyio.Event()
    
        async def call_next(request: Request) -> Response:
            app_exc: typing.Optional[Exception] = None
            send_stream: ObjectSendStream[typing.MutableMapping[str, typing.Any]]
            recv_stream: ObjectReceiveStream[typing.MutableMapping[str, typing.Any]]
            send_stream, recv_stream = anyio.create_memory_object_stream()
    
            async def receive_or_disconnect() -> Message:
                if response_sent.is_set():
                    return {"type": "http.disconnect"}
    
                async with anyio.create_task_group() as task_group:
    
                    async def wrap(func: typing.Callable[[], typing.Awaitable[T]]) -> T:
                        result = await func()
                        task_group.cancel_scope.cancel()
                        return result
    
                    task_group.start_soon(wrap, response_sent.wait)
                    message = await wrap(wrapped_receive)
    
                if response_sent.is_set():
                    return {"type": "http.disconnect"}
    
                return message
    
            async def close_recv_stream_on_response_sent() -> None:
                await response_sent.wait()
                recv_stream.close()
    
            async def send_no_error(message: Message) -> None:
                try:
                    await send_stream.send(message)
                except anyio.BrokenResourceError:
                    # recv_stream has been closed, i.e. response_sent has been set.
                    return
    
            async def coro() -> None:
                nonlocal app_exc
    
                async with send_stream:
                    try:
                        await self.app(scope, receive_or_disconnect, send_no_error)
                    except Exception as exc:
                        app_exc = exc
    
            task_group.start_soon(close_recv_stream_on_response_sent)
            task_group.start_soon(coro)
    
            try:
                message = await recv_stream.receive()
                info = message.get("info", None)
                if message["type"] == "http.response.debug" and info is not None:
                    message = await recv_stream.receive()
            except anyio.EndOfStream:
                if app_exc is not None:
                    raise app_exc
                raise RuntimeError("No response returned.")
    
            assert message["type"] == "http.response.start"
    
            async def body_stream() -> typing.AsyncGenerator[bytes, None]:
                async with recv_stream:
                    async for message in recv_stream:
                        assert message["type"] == "http.response.body"
                        body = message.get("body", b"")
                        if body:
                            yield body
                        if not message.get("more_body", False):
                            break
    
                if app_exc is not None:
                    raise app_exc
    
            response = _StreamingResponse(
                status_code=message["status"], content=body_stream(), info=info
            )
            response.raw_headers = message["headers"]
            return response
    
        with collapse_excgroups():
>           async with anyio.create_task_group() as task_group:

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:190: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <anyio._backends._asyncio.TaskGroup object at 0x7f7857f016d0>
exc_type = <class 'NameError'>
exc_val = NameError("name 'get_question_set_crud' is not defined")
exc_tb = <traceback object at 0x7f7857f013c0>

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        ignore_exception = self.cancel_scope.__exit__(exc_type, exc_val, exc_tb)
        if exc_val is not None:
            self.cancel_scope.cancel()
            if not isinstance(exc_val, CancelledError):
                self._exceptions.append(exc_val)
    
        cancelled_exc_while_waiting_tasks: CancelledError | None = None
        while self._tasks:
            try:
                await asyncio.wait(self._tasks)
            except CancelledError as exc:
                # This task was cancelled natively; reraise the CancelledError later
                # unless this task was already interrupted by another exception
                self.cancel_scope.cancel()
                if cancelled_exc_while_waiting_tasks is None:
                    cancelled_exc_while_waiting_tasks = exc
    
        self._active = False
        if self._exceptions:
>           raise BaseExceptionGroup(
                "unhandled errors in a TaskGroup", self._exceptions
            )
E           ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:678: ExceptionGroup

During handling of the above exception, another exception occurred:

client = <starlette.testclient.TestClient object at 0x7f7857056a50>
db_session = <sqlalchemy.orm.session.Session object at 0x7f7857fc6e90>
test_question_set = <app.models.question_sets.QuestionSetModel object at 0x7f78570572d0>
test_question = <app.models.questions.QuestionModel object at 0x7f7857f90d10>

    def test_retrieve_question_set_with_questions(client, db_session, test_question_set, test_question):
>       response = client.get(f"/question-sets/{test_question_set.id}")

tests/test_api_question_sets.py:116: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:523: in get
    return super().get(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1054: in get
    return self.request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:491: in request
    return super().request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:827: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1015: in _send_single_request
    response = transport.handle_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:372: in handle_request
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:369: in handle_request
    portal.call(self.app, scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:288: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:456: in result
    return self.__get_result()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:217: in _call_func
    retval = await retval_or_awaitable
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/applications.py:123: in __call__
    await self.middleware_stack(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:189: in __call__
    with collapse_excgroups():
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/contextlib.py:158: in __exit__
    self.gen.throw(typ, value, traceback)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:93: in collapse_excgroups
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:191: in __call__
    response = await self.dispatch_func(request, call_next)
app/main.py:53: in check_revoked_token
    response = await call_next(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:165: in call_next
    raise app_exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:151: in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:189: in __call__
    with collapse_excgroups():
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/contextlib.py:158: in __exit__
    self.gen.throw(typ, value, traceback)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:93: in collapse_excgroups
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:191: in __call__
    response = await self.dispatch_func(request, call_next)
app/main.py:41: in check_blacklist
    response = await call_next(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:165: in call_next
    raise app_exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:151: in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/exceptions.py:62: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_exception_handler.py:64: in wrapped_app
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    await app(scope, receive, sender)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/routing.py:758: in __call__
    await self.middleware_stack(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/routing.py:778: in app
    await route.handle(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/routing.py:299: in handle
    await self.app(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/routing.py:79: in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_exception_handler.py:64: in wrapped_app
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    await app(scope, receive, sender)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/routing.py:74: in app
    response = await func(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/routing.py:278: in app
    raw_response = await run_endpoint_function(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/routing.py:193: in run_endpoint_function
    return await run_in_threadpool(dependant.call, **values)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/concurrency.py:42: in run_in_threadpool
    return await anyio.to_thread.run_sync(func, *args)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/to_thread.py:56: in run_sync
    return await get_async_backend().run_sync_in_worker_thread(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:2144: in run_sync_in_worker_thread
    return await future
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:851: in run
    result = context.run(func, *args)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

question_set_id = 1
db = <sqlalchemy.orm.session.Session object at 0x7f7857f020d0>

    @router.get("/question-sets/{question_set_id}", response_model=QuestionSetSchema)
    def get_question_set_endpoint(question_set_id: int, db: Session = Depends(get_db)):
        """
        Retrieve a question set by ID.
        """
>       question_set = get_question_set_crud(db, question_set_id=question_set_id)
E       NameError: name 'get_question_set_crud' is not defined

app/api/endpoints/question_sets.py:112: NameError
________________________ test_update_question_set_name _________________________

client = <starlette.testclient.TestClient object at 0x7f785c2ac250>
db_session = <sqlalchemy.orm.session.Session object at 0x7f785c2ade90>
test_question_set = <app.models.question_sets.QuestionSetModel object at 0x7f785c2ae010>

    def test_update_question_set_name(client, db_session, test_question_set):
        updated_name = "Updated Question Set"
        data = {"name": updated_name}
        response = client.put(f"/question-sets/{test_question_set.id}", json=data)
>       assert response.status_code == 200
E       assert 401 == 200
E        +  where 401 = <Response [401 Unauthorized]>.status_code

tests/test_api_question_sets.py:125: AssertionError
___________________________ test_delete_question_set ___________________________

client = <starlette.testclient.TestClient object at 0x7f785c201510>
db_session = <sqlalchemy.orm.session.Session object at 0x7f785c2afd50>
test_question_set = <app.models.question_sets.QuestionSetModel object at 0x7f785c2006d0>

    def test_delete_question_set(client, db_session, test_question_set):
        response = client.delete(f"/question-sets/{test_question_set.id}")
>       assert response.status_code == 204
E       assert 401 == 204
E        +  where 401 = <Response [401 Unauthorized]>.status_code

tests/test_api_question_sets.py:130: AssertionError
___________________ test_protected_route_with_invalid_token ____________________

self = <sqlalchemy.engine.base.Connection object at 0x7f7857b360d0>
dialect = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f785e503310>
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f7857b35890>
statement = <sqlalchemy.dialects.sqlite.base.SQLiteCompiler object at 0x7f785cc8b250>
parameters = [('invalid_token', 1, 0)]

    def _exec_single_context(
        self,
        dialect: Dialect,
        context: ExecutionContext,
        statement: Union[str, Compiled],
        parameters: Optional[_AnyMultiExecuteParams],
    ) -> CursorResult[Any]:
        """continue the _execute_context() method for a single DBAPI
        cursor.execute() or cursor.executemany() call.
    
        """
        if dialect.bind_typing is BindTyping.SETINPUTSIZES:
            generic_setinputsizes = context._prepare_set_input_sizes()
    
            if generic_setinputsizes:
                try:
                    dialect.do_set_input_sizes(
                        context.cursor, generic_setinputsizes, context
                    )
                except BaseException as e:
                    self._handle_dbapi_exception(
                        e, str(statement), parameters, None, context
                    )
    
        cursor, str_statement, parameters = (
            context.cursor,
            context.statement,
            context.parameters,
        )
    
        effective_parameters: Optional[_AnyExecuteParams]
    
        if not context.executemany:
            effective_parameters = parameters[0]
        else:
            effective_parameters = parameters
    
        if self._has_events or self.engine._has_events:
            for fn in self.dispatch.before_cursor_execute:
                str_statement, effective_parameters = fn(
                    self,
                    cursor,
                    str_statement,
                    effective_parameters,
                    context,
                    context.executemany,
                )
    
        if self._echo:
            self._log_info(str_statement)
    
            stats = context._get_cache_stats()
    
            if not self.engine.hide_parameters:
                self._log_info(
                    "[%s] %r",
                    stats,
                    sql_util._repr_params(
                        effective_parameters,
                        batches=10,
                        ismulti=context.executemany,
                    ),
                )
            else:
                self._log_info(
                    "[%s] [SQL parameters hidden due to hide_parameters=True]",
                    stats,
                )
    
        evt_handled: bool = False
        try:
            if context.execute_style is ExecuteStyle.EXECUTEMANY:
                effective_parameters = cast(
                    "_CoreMultiExecuteParams", effective_parameters
                )
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_executemany:
                        if fn(
                            cursor,
                            str_statement,
                            effective_parameters,
                            context,
                        ):
                            evt_handled = True
                            break
                if not evt_handled:
                    self.dialect.do_executemany(
                        cursor,
                        str_statement,
                        effective_parameters,
                        context,
                    )
            elif not effective_parameters and context.no_parameters:
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_execute_no_params:
                        if fn(cursor, str_statement, context):
                            evt_handled = True
                            break
                if not evt_handled:
                    self.dialect.do_execute_no_params(
                        cursor, str_statement, context
                    )
            else:
                effective_parameters = cast(
                    "_CoreSingleExecuteParams", effective_parameters
                )
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_execute:
                        if fn(
                            cursor,
                            str_statement,
                            effective_parameters,
                            context,
                        ):
                            evt_handled = True
                            break
                if not evt_handled:
>                   self.dialect.do_execute(
                        cursor, str_statement, effective_parameters, context
                    )

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1960: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f785e503310>
cursor = <sqlite3.Cursor object at 0x7f7857ee5140>
statement = 'SELECT revoked_tokens.id AS revoked_tokens_id, revoked_tokens.token AS revoked_tokens_token, revoked_tokens.revoked_at AS revoked_tokens_revoked_at \nFROM revoked_tokens \nWHERE revoked_tokens.token = ?\n LIMIT ? OFFSET ?'
parameters = ('invalid_token', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f7857b35890>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlite3.OperationalError: no such table: revoked_tokens

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError

The above exception was the direct cause of the following exception:

client = <starlette.testclient.TestClient object at 0x7f7857b63ed0>

    def test_protected_route_with_invalid_token(client):
        headers = {"Authorization": "Bearer invalid_token"}
>       response = client.get("/users/", headers=headers)

tests/test_auth_integration.py:8: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:523: in get
    return super().get(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1054: in get
    return self.request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:491: in request
    return super().request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:827: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1015: in _send_single_request
    response = transport.handle_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:372: in handle_request
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:369: in handle_request
    portal.call(self.app, scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:288: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:449: in result
    return self.__get_result()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:217: in _call_func
    retval = await retval_or_awaitable
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/applications.py:123: in __call__
    await self.middleware_stack(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:189: in __call__
    with collapse_excgroups():
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/contextlib.py:158: in __exit__
    self.gen.throw(typ, value, traceback)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:93: in collapse_excgroups
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:191: in __call__
    response = await self.dispatch_func(request, call_next)
app/main.py:50: in check_revoked_token
    revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/query.py:2727: in first
    return self.limit(1)._iter().first()  # type: ignore
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/query.py:2826: in _iter
    result: Union[ScalarResult[_T], Result[_T]] = self.session.execute(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/session.py:2306: in execute
    return self._execute_internal(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/session.py:2191: in _execute_internal
    result: Result[Any] = compile_state_cls.orm_execute_statement(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/orm/context.py:293: in orm_execute_statement
    result = conn.execute(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1408: in execute
    return meth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/sql/elements.py:513: in _execute_on_connection
    return connection._execute_clauseelement(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1630: in _execute_clauseelement
    ret = self._execute_context(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1839: in _execute_context
    return self._exec_single_context(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1979: in _exec_single_context
    self._handle_dbapi_exception(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:2335: in _handle_dbapi_exception
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/base.py:1960: in _exec_single_context
    self.dialect.do_execute(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f785e503310>
cursor = <sqlite3.Cursor object at 0x7f7857ee5140>
statement = 'SELECT revoked_tokens.id AS revoked_tokens_id, revoked_tokens.token AS revoked_tokens_token, revoked_tokens.revoked_at AS revoked_tokens_revoked_at \nFROM revoked_tokens \nWHERE revoked_tokens.token = ?\n LIMIT ? OFFSET ?'
parameters = ('invalid_token', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f7857b35890>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: revoked_tokens
E       [SQL: SELECT revoked_tokens.id AS revoked_tokens_id, revoked_tokens.token AS revoked_tokens_token, revoked_tokens.revoked_at AS revoked_tokens_revoked_at 
E       FROM revoked_tokens 
E       WHERE revoked_tokens.token = ?
E        LIMIT ? OFFSET ?]
E       [parameters: ('invalid_token', 1, 0)]
E       (Background on this error at: https://sqlalche.me/e/20/e3q8)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError
___________________ test_protected_route_with_revoked_token ____________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f785d6e1410>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f785e6d1990>, 'client': None, 'extensions': {'http.response.debug':...I6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcl93WGNNeiIsImV4cCI6MTcxMjE4NzA3NX0.l25bSODFYb0lWCqRcfWeLgxlmGwMP_Zu6wOwrkvnW7o')], ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f7857ae0720>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f7857a27ce0>

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
    
        request = _CachedRequest(scope, receive)
        wrapped_receive = request.wrapped_receive
        response_sent = anyio.Event()
    
        async def call_next(request: Request) -> Response:
            app_exc: typing.Optional[Exception] = None
            send_stream: ObjectSendStream[typing.MutableMapping[str, typing.Any]]
            recv_stream: ObjectReceiveStream[typing.MutableMapping[str, typing.Any]]
            send_stream, recv_stream = anyio.create_memory_object_stream()
    
            async def receive_or_disconnect() -> Message:
                if response_sent.is_set():
                    return {"type": "http.disconnect"}
    
                async with anyio.create_task_group() as task_group:
    
                    async def wrap(func: typing.Callable[[], typing.Awaitable[T]]) -> T:
                        result = await func()
                        task_group.cancel_scope.cancel()
                        return result
    
                    task_group.start_soon(wrap, response_sent.wait)
                    message = await wrap(wrapped_receive)
    
                if response_sent.is_set():
                    return {"type": "http.disconnect"}
    
                return message
    
            async def close_recv_stream_on_response_sent() -> None:
                await response_sent.wait()
                recv_stream.close()
    
            async def send_no_error(message: Message) -> None:
                try:
                    await send_stream.send(message)
                except anyio.BrokenResourceError:
                    # recv_stream has been closed, i.e. response_sent has been set.
                    return
    
            async def coro() -> None:
                nonlocal app_exc
    
                async with send_stream:
                    try:
                        await self.app(scope, receive_or_disconnect, send_no_error)
                    except Exception as exc:
                        app_exc = exc
    
            task_group.start_soon(close_recv_stream_on_response_sent)
            task_group.start_soon(coro)
    
            try:
                message = await recv_stream.receive()
                info = message.get("info", None)
                if message["type"] == "http.response.debug" and info is not None:
                    message = await recv_stream.receive()
            except anyio.EndOfStream:
                if app_exc is not None:
                    raise app_exc
                raise RuntimeError("No response returned.")
    
            assert message["type"] == "http.response.start"
    
            async def body_stream() -> typing.AsyncGenerator[bytes, None]:
                async with recv_stream:
                    async for message in recv_stream:
                        assert message["type"] == "http.response.body"
                        body = message.get("body", b"")
                        if body:
                            yield body
                        if not message.get("more_body", False):
                            break
    
                if app_exc is not None:
                    raise app_exc
    
            response = _StreamingResponse(
                status_code=message["status"], content=body_stream(), info=info
            )
            response.raw_headers = message["headers"]
            return response
    
        with collapse_excgroups():
>           async with anyio.create_task_group() as task_group:

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:190: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <anyio._backends._asyncio.TaskGroup object at 0x7f7857848cd0>
exc_type = <class 'fastapi.exceptions.HTTPException'>
exc_val = HTTPException(status_code=401, detail='Token has been revoked')
exc_tb = <traceback object at 0x7f7857849540>

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        ignore_exception = self.cancel_scope.__exit__(exc_type, exc_val, exc_tb)
        if exc_val is not None:
            self.cancel_scope.cancel()
            if not isinstance(exc_val, CancelledError):
                self._exceptions.append(exc_val)
    
        cancelled_exc_while_waiting_tasks: CancelledError | None = None
        while self._tasks:
            try:
                await asyncio.wait(self._tasks)
            except CancelledError as exc:
                # This task was cancelled natively; reraise the CancelledError later
                # unless this task was already interrupted by another exception
                self.cancel_scope.cancel()
                if cancelled_exc_while_waiting_tasks is None:
                    cancelled_exc_while_waiting_tasks = exc
    
        self._active = False
        if self._exceptions:
>           raise BaseExceptionGroup(
                "unhandled errors in a TaskGroup", self._exceptions
            )
E           ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:678: ExceptionGroup

During handling of the above exception, another exception occurred:

client = <starlette.testclient.TestClient object at 0x7f7857b10610>
test_user = <app.models.users.UserModel object at 0x7f7857b13690>
test_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcl93WGNNeiIsImV4cCI6MTcxMjE4NzA3NX0.l25bSODFYb0lWCqRcfWeLgxlmGwMP_Zu6wOwrkvnW7o'

    def test_protected_route_with_revoked_token(client, test_user, test_token):
        """
        Test accessing a protected route with a revoked token.
        """
        # Logout to revoke the token
        headers = {"Authorization": f"Bearer {test_token}"}
        logout_response = client.post("/logout", headers=headers)
        assert logout_response.status_code == 200
    
        # Try accessing the protected route with the revoked token
>       response = client.get("/users/", headers=headers)

tests/test_auth_integration.py:21: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:523: in get
    return super().get(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1054: in get
    return self.request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:491: in request
    return super().request(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:827: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/httpx/_client.py:1015: in _send_single_request
    response = transport.handle_request(request)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:372: in handle_request
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/testclient.py:369: in handle_request
    portal.call(self.app, scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:288: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:456: in result
    return self.__get_result()
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/anyio/from_thread.py:217: in _call_func
    retval = await retval_or_awaitable
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/applications.py:123: in __call__
    await self.middleware_stack(scope, receive, send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:189: in __call__
    with collapse_excgroups():
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/contextlib.py:158: in __exit__
    self.gen.throw(typ, value, traceback)
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:93: in collapse_excgroups
    raise exc
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/middleware/base.py:191: in __call__
    response = await self.dispatch_func(request, call_next)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

request = <starlette.middleware.base._CachedRequest object at 0x7f7857822910>
call_next = <function BaseHTTPMiddleware.__call__.<locals>.call_next at 0x7f785cccf4c0>

    @app.middleware("http")
    async def check_revoked_token(request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            db = next(get_db())
            revoked_token = db.query(RevokedTokenModel).filter(RevokedTokenModel.token == token).first()
            if revoked_token:
>               raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
E               fastapi.exceptions.HTTPException: 401: Token has been revoked

app/main.py:52: HTTPException

---------- coverage: platform linux, python 3.11.8-final-0 -----------
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
app/__init__.py                           1      0   100%
app/api/__init__.py                       1      0   100%
app/api/endpoints/__init__.py             1      0   100%
app/api/endpoints/auth.py                40      8    80%
app/api/endpoints/question_sets.py       72     29    60%
app/api/endpoints/questions.py           33      4    88%
app/api/endpoints/register.py            17      0   100%
app/api/endpoints/token.py               19      0   100%
app/api/endpoints/user_responses.py      27      9    67%
app/api/endpoints/users.py               21      2    90%
app/core/__init__.py                      4      0   100%
app/core/config.py                        8      0   100%
app/core/jwt.py                          30      3    90%
app/core/security.py                      7      0   100%
app/crud/__init__.py                      6      0   100%
app/crud/crud_question_sets.py           34      6    82%
app/crud/crud_questions.py               36      8    78%
app/crud/crud_subtopics.py                9      0   100%
app/crud/crud_user.py                    19      3    84%
app/crud/crud_user_responses.py          13      1    92%
app/crud/crud_user_utils.py               5      0   100%
app/db/__init__.py                        2      0   100%
app/db/base_class.py                      3      0   100%
app/db/session.py                        17      1    94%
app/main.py                              37      2    95%
app/models/__init__.py                    9      0   100%
app/models/answer_choices.py             11      0   100%
app/models/question_sets.py               9      0   100%
app/models/questions.py                  13      0   100%
app/models/subjects.py                    9      0   100%
app/models/subtopics.py                  11      0   100%
app/models/token.py                       8      0   100%
app/models/topics.py                     11      0   100%
app/models/user_responses.py             17      0   100%
app/models/users.py                      13      0   100%
app/schemas/__init__.py                   8      0   100%
app/schemas/answer_choices.py            10      0   100%
app/schemas/auth.py                       4      0   100%
app/schemas/question_sets.py             12      0   100%
app/schemas/questions.py                 20      0   100%
app/schemas/subtopics.py                  9      0   100%
app/schemas/token.py                      5      0   100%
app/schemas/user.py                      33      3    91%
app/schemas/user_responses.py            15      0   100%
app/services/__init__.py                  2      0   100%
app/services/auth_service.py             14      1    93%
app/services/user_service.py             25      4    84%
---------------------------------------------------------
TOTAL                                   730     84    88%

=========================== short test summary info ============================
FAILED tests/test_api_authentication.py::test_access_protected_endpoint_with_invalid_token
FAILED tests/test_api_authentication.py::test_login_invalid_token_format - sq...
FAILED tests/test_api_authentication.py::test_logout_revoked_token - fastapi....
FAILED tests/test_api_authentication.py::test_login_logout_flow - fastapi.exc...
FAILED tests/test_api_question_sets.py::test_create_question_set - assert 401...
FAILED tests/test_api_question_sets.py::test_update_nonexistent_question_set
FAILED tests/test_api_question_sets.py::test_update_question_set_not_found - ...
FAILED tests/test_api_question_sets.py::test_delete_question_set_not_found - ...
FAILED tests/test_api_question_sets.py::test_upload_question_set_invalid_json
FAILED tests/test_api_question_sets.py::test_create_question_set_with_existing_name
FAILED tests/test_api_question_sets.py::test_retrieve_question_set_with_questions
FAILED tests/test_api_question_sets.py::test_update_question_set_name - asser...
FAILED tests/test_api_question_sets.py::test_delete_question_set - assert 401...
FAILED tests/test_auth_integration.py::test_protected_route_with_invalid_token
FAILED tests/test_auth_integration.py::test_protected_route_with_revoked_token
======================== 15 failed, 61 passed in 31.32s ========================

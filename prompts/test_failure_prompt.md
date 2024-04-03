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
collected 24 items

tests/test_api_authentication.py .FF.F..........F....F...                [100%]

=================================== FAILURES ===================================
__________________________ test_register_user_success __________________________

self = <sqlalchemy.engine.base.Connection object at 0x7f0517bb9690>
dialect = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f0517bb97d0>
statement = <sqlalchemy.dialects.sqlite.base.SQLiteCompiler object at 0x7f0517b79710>
parameters = [('new_user', 1, 0)]

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

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
cursor = <sqlite3.Cursor object at 0x7f0517b92840>
statement = 'SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active \nFROM users \nWHERE users.username = ?\n LIMIT ? OFFSET ?'
parameters = ('new_user', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f0517bb97d0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlite3.OperationalError: no such table: users

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError

The above exception was the direct cause of the following exception:

client = <starlette.testclient.TestClient object at 0x7f051857aad0>

    def test_register_user_success(client):
        user_data = {"username": "new_user", "password": "NewPassword123!"}
>       response = client.post("/register/", json=user_data)

tests/test_api_authentication.py:16: 
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
app/api/endpoints/register.py:32: in register_user
    db_user = get_user_by_username(db, username=user.username)
app/crud/crud_user_utils.py:20: in get_user_by_username
    return db.query(User).filter(User.username == username).first()
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

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
cursor = <sqlite3.Cursor object at 0x7f0517b92840>
statement = 'SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active \nFROM users \nWHERE users.username = ?\n LIMIT ? OFFSET ?'
parameters = ('new_user', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f0517bb97d0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users
E       [SQL: SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active 
E       FROM users 
E       WHERE users.username = ?
E        LIMIT ? OFFSET ?]
E       [parameters: ('new_user', 1, 0)]
E       (Background on this error at: https://sqlalche.me/e/20/e3q8)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError
___________________________ test_login_user_success ____________________________

client = <starlette.testclient.TestClient object at 0x7f0515ebe090>
test_user = <app.models.users.User object at 0x7f0515dd1b50>

    def test_login_user_success(client, test_user):
        """Test successful user login and token retrieval."""
        user_data = {"username": test_user.username, "password": "TestPassword123!"}
        response = client.post("/register/", json=user_data)
>       assert response.status_code == 201, "User register failed"
E       AssertionError: User register failed
E       assert 422 == 201
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_api_authentication.py:23: AssertionError
__________________ test_token_access_with_invalid_credentials __________________

self = <sqlalchemy.engine.base.Connection object at 0x7f05167c4cd0>
dialect = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f05167c6ad0>
statement = <sqlalchemy.dialects.sqlite.base.SQLiteCompiler object at 0x7f0517b79710>
parameters = [('nonexistentuser', 1, 0)]

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

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
cursor = <sqlite3.Cursor object at 0x7f05150449c0>
statement = 'SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active \nFROM users \nWHERE users.username = ?\n LIMIT ? OFFSET ?'
parameters = ('nonexistentuser', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f05167c6ad0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlite3.OperationalError: no such table: users

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError

The above exception was the direct cause of the following exception:

client = <starlette.testclient.TestClient object at 0x7f0515dabe50>

    def test_token_access_with_invalid_credentials(client):
        """Test token access with invalid credentials."""
>       response = client.post("/token", data={"username": "nonexistentuser", "password": "wrongpassword"})

tests/test_api_authentication.py:34: 
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
app/api/endpoints/token.py:34: in login_for_access_token
    user = authenticate_user(db, form_data.username, form_data.password)
app/services/auth_service.py:23: in authenticate_user
    user = get_user_by_username(db, username)
app/crud/crud_user_utils.py:20: in get_user_by_username
    return db.query(User).filter(User.username == username).first()
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

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
cursor = <sqlite3.Cursor object at 0x7f05150449c0>
statement = 'SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active \nFROM users \nWHERE users.username = ?\n LIMIT ? OFFSET ?'
parameters = ('nonexistentuser', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f05167c6ad0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users
E       [SQL: SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active 
E       FROM users 
E       WHERE users.username = ?
E        LIMIT ? OFFSET ?]
E       [parameters: ('nonexistentuser', 1, 0)]
E       (Background on this error at: https://sqlalche.me/e/20/e3q8)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError
________________________ test_login_invalid_credentials ________________________

self = <sqlalchemy.engine.base.Connection object at 0x7f0516091d90>
dialect = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f05160c40d0>
statement = <sqlalchemy.dialects.sqlite.base.SQLiteCompiler object at 0x7f0517b79710>
parameters = [('invalid_user', 1, 0)]

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

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
cursor = <sqlite3.Cursor object at 0x7f0516aff840>
statement = 'SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active \nFROM users \nWHERE users.username = ?\n LIMIT ? OFFSET ?'
parameters = ('invalid_user', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f05160c40d0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlite3.OperationalError: no such table: users

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError

The above exception was the direct cause of the following exception:

client = <starlette.testclient.TestClient object at 0x7f0516682b10>

    def test_login_invalid_credentials(client):
        """
        Test login with invalid credentials.
        """
>       response = client.post("/login", json={"username": "invalid_user", "password": "invalid_password"})

tests/test_api_authentication.py:116: 
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
app/api/endpoints/auth.py:25: in login_for_access_token
    user = db.query(User).filter(User.username == form_data.username).first()
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

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
cursor = <sqlite3.Cursor object at 0x7f0516aff840>
statement = 'SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active \nFROM users \nWHERE users.username = ?\n LIMIT ? OFFSET ?'
parameters = ('invalid_user', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f05160c40d0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users
E       [SQL: SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active 
E       FROM users 
E       WHERE users.username = ?
E        LIMIT ? OFFSET ?]
E       [parameters: ('invalid_user', 1, 0)]
E       (Background on this error at: https://sqlalche.me/e/20/e3q8)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError
_________________________ test_login_nonexistent_user __________________________

self = <sqlalchemy.engine.base.Connection object at 0x7f0515d18dd0>
dialect = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f0515d1a2d0>
statement = <sqlalchemy.dialects.sqlite.base.SQLiteCompiler object at 0x7f0517b79710>
parameters = [('nonexistent_user', 1, 0)]

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

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
cursor = <sqlite3.Cursor object at 0x7f051541b4c0>
statement = 'SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active \nFROM users \nWHERE users.username = ?\n LIMIT ? OFFSET ?'
parameters = ('nonexistent_user', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f0515d1a2d0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlite3.OperationalError: no such table: users

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError

The above exception was the direct cause of the following exception:

client = <starlette.testclient.TestClient object at 0x7f051579fcd0>

    def test_login_nonexistent_user(client):
        """
        Test login with a non-existent username.
        """
        login_data = {"username": "nonexistent_user", "password": "password123"}
>       response = client.post("/login", json=login_data)

tests/test_api_authentication.py:160: 
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
app/api/endpoints/auth.py:25: in login_for_access_token
    user = db.query(User).filter(User.username == form_data.username).first()
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

self = <sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite object at 0x7f05194c4c50>
cursor = <sqlite3.Cursor object at 0x7f051541b4c0>
statement = 'SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active \nFROM users \nWHERE users.username = ?\n LIMIT ? OFFSET ?'
parameters = ('nonexistent_user', 1, 0)
context = <sqlalchemy.dialects.sqlite.base.SQLiteExecutionContext object at 0x7f0515d1a2d0>

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users
E       [SQL: SELECT users.id AS users_id, users.username AS users_username, users.hashed_password AS users_hashed_password, users.is_active AS users_is_active 
E       FROM users 
E       WHERE users.username = ?
E        LIMIT ? OFFSET ?]
E       [parameters: ('nonexistent_user', 1, 0)]
E       (Background on this error at: https://sqlalche.me/e/20/e3q8)

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/sqlalchemy/engine/default.py:924: OperationalError

---------- coverage: platform linux, python 3.11.8-final-0 -----------
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
app/__init__.py                           1      0   100%
app/api/__init__.py                       1      0   100%
app/api/endpoints/__init__.py             1      0   100%
app/api/endpoints/auth.py                40      5    88%
app/api/endpoints/question_sets.py       59     33    44%
app/api/endpoints/questions.py           34     14    59%
app/api/endpoints/register.py            17      4    76%
app/api/endpoints/token.py               19      0   100%
app/api/endpoints/user_responses.py      27     12    56%
app/api/endpoints/users.py               21      5    76%
app/core/__init__.py                      4      0   100%
app/core/config.py                        7      0   100%
app/core/jwt.py                          30      8    73%
app/core/security.py                      7      0   100%
app/crud/__init__.py                      6      0   100%
app/crud/crud_question_sets.py           34     24    29%
app/crud/crud_questions.py               37     27    27%
app/crud/crud_subtopics.py                9      5    44%
app/crud/crud_user.py                    19      6    68%
app/crud/crud_user_responses.py          13      6    54%
app/crud/crud_user_utils.py               5      0   100%
app/db/__init__.py                        2      0   100%
app/db/base_class.py                      3      0   100%
app/db/session.py                        14      1    93%
app/main.py                              37      3    92%
app/models/__init__.py                    9      0   100%
app/models/answer_choices.py             11      0   100%
app/models/question_sets.py               9      0   100%
app/models/questions.py                  16      1    94%
app/models/subjects.py                    9      0   100%
app/models/subtopics.py                  11      0   100%
app/models/token.py                       8      0   100%
app/models/topics.py                     11      0   100%
app/models/user_responses.py             18      0   100%
app/models/users.py                      12      0   100%
app/schemas/__init__.py                   8      0   100%
app/schemas/answer_choices.py            10      0   100%
app/schemas/auth.py                       4      0   100%
app/schemas/question_sets.py             12      0   100%
app/schemas/questions.py                 23      2    91%
app/schemas/subtopics.py                  9      0   100%
app/schemas/token.py                      5      0   100%
app/schemas/user.py                      32      3    91%
app/schemas/user_responses.py            15      0   100%
app/services/__init__.py                  2      0   100%
app/services/auth_service.py             14      2    86%
app/services/user_service.py             25      3    88%
---------------------------------------------------------
TOTAL                                   720    164    77%

=========================== short test summary info ============================
FAILED tests/test_api_authentication.py::test_register_user_success - sqlalch...
FAILED tests/test_api_authentication.py::test_login_user_success - AssertionE...
FAILED tests/test_api_authentication.py::test_token_access_with_invalid_credentials
FAILED tests/test_api_authentication.py::test_login_invalid_credentials - sql...
FAILED tests/test_api_authentication.py::test_login_nonexistent_user - sqlalc...
======================== 5 failed, 19 passed in 17.51s =========================

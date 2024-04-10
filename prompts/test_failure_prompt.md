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


.........................FFFFFFFFF.FF.F.F.F.FF.FF....................... [ 75%]
F......................                                                  [100%]
=================================== FAILURES ===================================
____________________________ test_filter_questions _____________________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f1175d82a90>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f1175f23950>, 'client': None, 'endpoint': <function filter_questions_endpoint at 0x7f1175f05f80>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f1174a1fec0>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f1174a1e200>

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

self = <anyio._backends._asyncio.TaskGroup object at 0x7f1174a3de50>
exc_type = <class 'pydantic_core._pydantic_core.ValidationError'>
exc_val = 4 validation errors for QuestionSchema
subject
  Input should be a valid dictionary [type=dict_type, input_value=<app....1174a70fd0>, input_type=QuestionTagModel]
    For further information visit https://errors.pydantic.dev/2.6/v/dict_type
exc_tb = <traceback object at 0x7f1174a7c640>

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

logged_in_client = <starlette.testclient.TestClient object at 0x7f11753c6710>
setup_filter_questions_data = None
db_session = <sqlalchemy.orm.session.Session object at 0x7f1175393c90>

    def test_filter_questions(logged_in_client, setup_filter_questions_data, db_session):
>       response = logged_in_client.get(
            "/questions/filter",
            params={
                "subject": "Math",
                "topic": "Algebra",
                "subtopic": "Linear Equations",
                "difficulty": "Easy",
                "tags": ["equations", "solving"]
            }
        )

tests/test_api/test_api_filters.py:32: 
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
app/main.py:65: in check_revoked_token
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
app/main.py:49: in check_blacklist
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
app/api/endpoints/filters.py:17: in filter_questions_endpoint
    filtered_questions = filter_questions(
app/crud/crud_questions.py:81: in filter_questions
    return [QuestionSchema.from_orm(question) for question in questions]
app/crud/crud_questions.py:81: in <listcomp>
    return [QuestionSchema.from_orm(question) for question in questions]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'app.schemas.questions.QuestionSchema'>
obj = <app.models.questions.QuestionModel object at 0x7f1174a4a9d0>

    @classmethod
    @typing_extensions.deprecated(
        'The `from_orm` method is deprecated; set '
        "`model_config['from_attributes']=True` and use `model_validate` instead.",
        category=None,
    )
    def from_orm(cls: type[Model], obj: Any) -> Model:  # noqa: D102
        warnings.warn(
            'The `from_orm` method is deprecated; set '
            "`model_config['from_attributes']=True` and use `model_validate` instead.",
            category=PydanticDeprecatedSince20,
        )
        if not cls.model_config.get('from_attributes', None):
            raise PydanticUserError(
                'You must set the config attribute `from_attributes=True` to use from_orm', code=None
            )
>       return cls.model_validate(obj)
E       pydantic_core._pydantic_core.ValidationError: 4 validation errors for QuestionSchema
E       subject
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subjects.Subj...bject at 0x7f11753ae4d0>, input_type=SubjectModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       topic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.topics.TopicM...bject at 0x7f1174a68210>, input_type=TopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       subtopic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subtopics.Sub...bject at 0x7f1174a69d10>, input_type=SubtopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.0
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f1174a70fd0>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/pydantic/main.py:1174: ValidationError
_______________________ test_filter_questions_by_subject _______________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f1175d82a90>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f1175f23950>, 'client': None, 'endpoint': <function filter_questions_endpoint at 0x7f1175f05f80>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f1174a8aac0>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f11745bf060>

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

self = <anyio._backends._asyncio.TaskGroup object at 0x7f116fecb490>
exc_type = <class 'pydantic_core._pydantic_core.ValidationError'>
exc_val = 5 validation errors for QuestionSchema
subject
  Input should be a valid dictionary [type=dict_type, input_value=<app....11740fd110>, input_type=QuestionTagModel]
    For further information visit https://errors.pydantic.dev/2.6/v/dict_type
exc_tb = <traceback object at 0x7f116fe57540>

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

logged_in_client = <starlette.testclient.TestClient object at 0x7f1174a305d0>
setup_filter_questions_data = None
db_session = <sqlalchemy.orm.session.Session object at 0x7f11754ebd90>

    def test_filter_questions_by_subject(logged_in_client, setup_filter_questions_data, db_session):
        print("Running test_filter_questions_by_subject")
>       response = logged_in_client.get(
            "/questions/filter",
            params={"subject": "Math"}
        )

tests/test_api/test_api_filters.py:56: 
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
app/main.py:65: in check_revoked_token
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
app/main.py:49: in check_blacklist
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
app/api/endpoints/filters.py:17: in filter_questions_endpoint
    filtered_questions = filter_questions(
app/crud/crud_questions.py:81: in filter_questions
    return [QuestionSchema.from_orm(question) for question in questions]
app/crud/crud_questions.py:81: in <listcomp>
    return [QuestionSchema.from_orm(question) for question in questions]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'app.schemas.questions.QuestionSchema'>
obj = <app.models.questions.QuestionModel object at 0x7f11740fc610>

    @classmethod
    @typing_extensions.deprecated(
        'The `from_orm` method is deprecated; set '
        "`model_config['from_attributes']=True` and use `model_validate` instead.",
        category=None,
    )
    def from_orm(cls: type[Model], obj: Any) -> Model:  # noqa: D102
        warnings.warn(
            'The `from_orm` method is deprecated; set '
            "`model_config['from_attributes']=True` and use `model_validate` instead.",
            category=PydanticDeprecatedSince20,
        )
        if not cls.model_config.get('from_attributes', None):
            raise PydanticUserError(
                'You must set the config attribute `from_attributes=True` to use from_orm', code=None
            )
>       return cls.model_validate(obj)
E       pydantic_core._pydantic_core.ValidationError: 5 validation errors for QuestionSchema
E       subject
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subjects.Subj...bject at 0x7f11740ffcd0>, input_type=SubjectModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       topic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.topics.TopicM...bject at 0x7f11740fc4d0>, input_type=TopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       subtopic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subtopics.Sub...bject at 0x7f11740fcbd0>, input_type=SubtopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.0
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f11740fd090>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.1
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f11740fd110>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/pydantic/main.py:1174: ValidationError
----------------------------- Captured stdout call -----------------------------
Running test_filter_questions_by_subject
________________________ test_filter_questions_by_topic ________________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f1175d82a90>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f1175f23950>, 'client': None, 'endpoint': <function filter_questions_endpoint at 0x7f1175f05f80>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f1174aa7420>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f1174aa6e80>

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

self = <anyio._backends._asyncio.TaskGroup object at 0x7f1174a31c50>
exc_type = <class 'pydantic_core._pydantic_core.ValidationError'>
exc_val = 5 validation errors for QuestionSchema
subject
  Input should be a valid dictionary [type=dict_type, input_value=<app....116fa88510>, input_type=QuestionTagModel]
    For further information visit https://errors.pydantic.dev/2.6/v/dict_type
exc_tb = <traceback object at 0x7f116fac5f00>

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

logged_in_client = <starlette.testclient.TestClient object at 0x7f1174a3d910>
setup_filter_questions_data = None
db_session = <sqlalchemy.orm.session.Session object at 0x7f11754beb90>

    def test_filter_questions_by_topic(logged_in_client, setup_filter_questions_data, db_session):
>       response = logged_in_client.get(
            "/questions/filter",
            params={"topic": "Algebra"}
        )

tests/test_api/test_api_filters.py:68: 
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
app/main.py:65: in check_revoked_token
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
app/main.py:49: in check_blacklist
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
app/api/endpoints/filters.py:17: in filter_questions_endpoint
    filtered_questions = filter_questions(
app/crud/crud_questions.py:81: in filter_questions
    return [QuestionSchema.from_orm(question) for question in questions]
app/crud/crud_questions.py:81: in <listcomp>
    return [QuestionSchema.from_orm(question) for question in questions]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'app.schemas.questions.QuestionSchema'>
obj = <app.models.questions.QuestionModel object at 0x7f116fa8b5d0>

    @classmethod
    @typing_extensions.deprecated(
        'The `from_orm` method is deprecated; set '
        "`model_config['from_attributes']=True` and use `model_validate` instead.",
        category=None,
    )
    def from_orm(cls: type[Model], obj: Any) -> Model:  # noqa: D102
        warnings.warn(
            'The `from_orm` method is deprecated; set '
            "`model_config['from_attributes']=True` and use `model_validate` instead.",
            category=PydanticDeprecatedSince20,
        )
        if not cls.model_config.get('from_attributes', None):
            raise PydanticUserError(
                'You must set the config attribute `from_attributes=True` to use from_orm', code=None
            )
>       return cls.model_validate(obj)
E       pydantic_core._pydantic_core.ValidationError: 5 validation errors for QuestionSchema
E       subject
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subjects.Subj...bject at 0x7f116fa88290>, input_type=SubjectModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       topic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.topics.TopicM...bject at 0x7f116fa88090>, input_type=TopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       subtopic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subtopics.Sub...bject at 0x7f116fa88410>, input_type=SubtopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.0
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f116fa88450>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.1
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f116fa88510>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/pydantic/main.py:1174: ValidationError
______________________ test_filter_questions_by_subtopic _______________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f1175d82a90>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f1175f23950>, 'client': None, 'endpoint': <function filter_questions_endpoint at 0x7f1175f05f80>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f1174a1de40>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f1174aa4ae0>

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

self = <anyio._backends._asyncio.TaskGroup object at 0x7f11746dfb50>
exc_type = <class 'pydantic_core._pydantic_core.ValidationError'>
exc_val = 4 validation errors for QuestionSchema
subject
  Input should be a valid dictionary [type=dict_type, input_value=<app....116f8ae2d0>, input_type=QuestionTagModel]
    For further information visit https://errors.pydantic.dev/2.6/v/dict_type
exc_tb = <traceback object at 0x7f116f650ec0>

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

logged_in_client = <starlette.testclient.TestClient object at 0x7f11746119d0>
setup_filter_questions_data = None
db_session = <sqlalchemy.orm.session.Session object at 0x7f1174610790>

    def test_filter_questions_by_subtopic(logged_in_client, setup_filter_questions_data, db_session):
>       response = logged_in_client.get(
            "/questions/filter",
            params={"subtopic": "Linear Equations"}
        )

tests/test_api/test_api_filters.py:79: 
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
app/main.py:65: in check_revoked_token
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
app/main.py:49: in check_blacklist
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
app/api/endpoints/filters.py:17: in filter_questions_endpoint
    filtered_questions = filter_questions(
app/crud/crud_questions.py:81: in filter_questions
    return [QuestionSchema.from_orm(question) for question in questions]
app/crud/crud_questions.py:81: in <listcomp>
    return [QuestionSchema.from_orm(question) for question in questions]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'app.schemas.questions.QuestionSchema'>
obj = <app.models.questions.QuestionModel object at 0x7f116f8aeed0>

    @classmethod
    @typing_extensions.deprecated(
        'The `from_orm` method is deprecated; set '
        "`model_config['from_attributes']=True` and use `model_validate` instead.",
        category=None,
    )
    def from_orm(cls: type[Model], obj: Any) -> Model:  # noqa: D102
        warnings.warn(
            'The `from_orm` method is deprecated; set '
            "`model_config['from_attributes']=True` and use `model_validate` instead.",
            category=PydanticDeprecatedSince20,
        )
        if not cls.model_config.get('from_attributes', None):
            raise PydanticUserError(
                'You must set the config attribute `from_attributes=True` to use from_orm', code=None
            )
>       return cls.model_validate(obj)
E       pydantic_core._pydantic_core.ValidationError: 4 validation errors for QuestionSchema
E       subject
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subjects.Subj...bject at 0x7f116f8ac0d0>, input_type=SubjectModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       topic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.topics.TopicM...bject at 0x7f116f8ad590>, input_type=TopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       subtopic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subtopics.Sub...bject at 0x7f116f8ae450>, input_type=SubtopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.0
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f116f8ae2d0>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/pydantic/main.py:1174: ValidationError
_____________________ test_filter_questions_by_difficulty ______________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f1175d82a90>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f1175f23950>, 'client': None, 'endpoint': <function filter_questions_endpoint at 0x7f1175f05f80>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f1174a1fa60>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f1174a1c860>

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

self = <anyio._backends._asyncio.TaskGroup object at 0x7f116f658050>
exc_type = <class 'pydantic_core._pydantic_core.ValidationError'>
exc_val = 5 validation errors for QuestionSchema
subject
  Input should be a valid dictionary [type=dict_type, input_value=<app....11746eb310>, input_type=QuestionTagModel]
    For further information visit https://errors.pydantic.dev/2.6/v/dict_type
exc_tb = <traceback object at 0x7f11746e74c0>

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

logged_in_client = <starlette.testclient.TestClient object at 0x7f117473e090>
setup_filter_questions_data = None
db_session = <sqlalchemy.orm.session.Session object at 0x7f117473c690>

    def test_filter_questions_by_difficulty(logged_in_client, setup_filter_questions_data, db_session):
>       response = logged_in_client.get(
            "/questions/filter",
            params={"difficulty": "Easy"}
        )

tests/test_api/test_api_filters.py:90: 
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
app/main.py:65: in check_revoked_token
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
app/main.py:49: in check_blacklist
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
app/api/endpoints/filters.py:17: in filter_questions_endpoint
    filtered_questions = filter_questions(
app/crud/crud_questions.py:81: in filter_questions
    return [QuestionSchema.from_orm(question) for question in questions]
app/crud/crud_questions.py:81: in <listcomp>
    return [QuestionSchema.from_orm(question) for question in questions]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'app.schemas.questions.QuestionSchema'>
obj = <app.models.questions.QuestionModel object at 0x7f11746e9950>

    @classmethod
    @typing_extensions.deprecated(
        'The `from_orm` method is deprecated; set '
        "`model_config['from_attributes']=True` and use `model_validate` instead.",
        category=None,
    )
    def from_orm(cls: type[Model], obj: Any) -> Model:  # noqa: D102
        warnings.warn(
            'The `from_orm` method is deprecated; set '
            "`model_config['from_attributes']=True` and use `model_validate` instead.",
            category=PydanticDeprecatedSince20,
        )
        if not cls.model_config.get('from_attributes', None):
            raise PydanticUserError(
                'You must set the config attribute `from_attributes=True` to use from_orm', code=None
            )
>       return cls.model_validate(obj)
E       pydantic_core._pydantic_core.ValidationError: 5 validation errors for QuestionSchema
E       subject
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subjects.Subj...bject at 0x7f11746ea7d0>, input_type=SubjectModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       topic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.topics.TopicM...bject at 0x7f11746ea850>, input_type=TopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       subtopic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subtopics.Sub...bject at 0x7f11746ea5d0>, input_type=SubtopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.0
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f11746eb290>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.1
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f11746eb310>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/pydantic/main.py:1174: ValidationError
_____________________ test_filter_questions_by_single_tag ______________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f1175d82a90>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f1175f23950>, 'client': None, 'endpoint': <function filter_questions_endpoint at 0x7f1175f05f80>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f116fe8bec0>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f1174ad0ae0>

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

self = <anyio._backends._asyncio.TaskGroup object at 0x7f1174835590>
exc_type = <class 'pydantic_core._pydantic_core.ValidationError'>
exc_val = 4 validation errors for QuestionSchema
subject
  Input should be a valid dictionary [type=dict_type, input_value=<app....11748df1d0>, input_type=QuestionTagModel]
    For further information visit https://errors.pydantic.dev/2.6/v/dict_type
exc_tb = <traceback object at 0x7f1174834380>

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

logged_in_client = <starlette.testclient.TestClient object at 0x7f1174826fd0>
setup_filter_questions_data = None
db_session = <sqlalchemy.orm.session.Session object at 0x7f1174825010>

    def test_filter_questions_by_single_tag(logged_in_client, setup_filter_questions_data, db_session):
>       response = logged_in_client.get(
            "/questions/filter",
            params={"tags": ["equations"]}
        )

tests/test_api/test_api_filters.py:101: 
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
app/main.py:65: in check_revoked_token
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
app/main.py:49: in check_blacklist
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
app/api/endpoints/filters.py:17: in filter_questions_endpoint
    filtered_questions = filter_questions(
app/crud/crud_questions.py:81: in filter_questions
    return [QuestionSchema.from_orm(question) for question in questions]
app/crud/crud_questions.py:81: in <listcomp>
    return [QuestionSchema.from_orm(question) for question in questions]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'app.schemas.questions.QuestionSchema'>
obj = <app.models.questions.QuestionModel object at 0x7f11748de210>

    @classmethod
    @typing_extensions.deprecated(
        'The `from_orm` method is deprecated; set '
        "`model_config['from_attributes']=True` and use `model_validate` instead.",
        category=None,
    )
    def from_orm(cls: type[Model], obj: Any) -> Model:  # noqa: D102
        warnings.warn(
            'The `from_orm` method is deprecated; set '
            "`model_config['from_attributes']=True` and use `model_validate` instead.",
            category=PydanticDeprecatedSince20,
        )
        if not cls.model_config.get('from_attributes', None):
            raise PydanticUserError(
                'You must set the config attribute `from_attributes=True` to use from_orm', code=None
            )
>       return cls.model_validate(obj)
E       pydantic_core._pydantic_core.ValidationError: 4 validation errors for QuestionSchema
E       subject
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subjects.Subj...bject at 0x7f11748ddf50>, input_type=SubjectModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       topic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.topics.TopicM...bject at 0x7f11748ddc90>, input_type=TopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       subtopic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subtopics.Sub...bject at 0x7f11748dee50>, input_type=SubtopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.0
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f11748df1d0>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/pydantic/main.py:1174: ValidationError
__________________ test_filter_questions_by_multiple_criteria __________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f1175d82a90>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f1175f23950>, 'client': None, 'endpoint': <function filter_questions_endpoint at 0x7f1175f05f80>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f11745bcb80>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f1174ad0ea0>

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

self = <anyio._backends._asyncio.TaskGroup object at 0x7f116f6dae90>
exc_type = <class 'pydantic_core._pydantic_core.ValidationError'>
exc_val = 4 validation errors for QuestionSchema
subject
  Input should be a valid dictionary [type=dict_type, input_value=<app....116fa16750>, input_type=QuestionTagModel]
    For further information visit https://errors.pydantic.dev/2.6/v/dict_type
exc_tb = <traceback object at 0x7f116fa0fa80>

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

logged_in_client = <starlette.testclient.TestClient object at 0x7f11744dfbd0>
setup_filter_questions_data = None
db_session = <sqlalchemy.orm.session.Session object at 0x7f11744ddb50>

    def test_filter_questions_by_multiple_criteria(logged_in_client, setup_filter_questions_data, db_session):
>       response = logged_in_client.get(
            "/questions/filter",
            params={
                "subject": "Math",
                "topic": "Algebra",
                "difficulty": "Easy"
            }
        )

tests/test_api/test_api_filters.py:112: 
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
app/main.py:65: in check_revoked_token
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
app/main.py:49: in check_blacklist
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
app/api/endpoints/filters.py:17: in filter_questions_endpoint
    filtered_questions = filter_questions(
app/crud/crud_questions.py:81: in filter_questions
    return [QuestionSchema.from_orm(question) for question in questions]
app/crud/crud_questions.py:81: in <listcomp>
    return [QuestionSchema.from_orm(question) for question in questions]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'app.schemas.questions.QuestionSchema'>
obj = <app.models.questions.QuestionModel object at 0x7f116fa161d0>

    @classmethod
    @typing_extensions.deprecated(
        'The `from_orm` method is deprecated; set '
        "`model_config['from_attributes']=True` and use `model_validate` instead.",
        category=None,
    )
    def from_orm(cls: type[Model], obj: Any) -> Model:  # noqa: D102
        warnings.warn(
            'The `from_orm` method is deprecated; set '
            "`model_config['from_attributes']=True` and use `model_validate` instead.",
            category=PydanticDeprecatedSince20,
        )
        if not cls.model_config.get('from_attributes', None):
            raise PydanticUserError(
                'You must set the config attribute `from_attributes=True` to use from_orm', code=None
            )
>       return cls.model_validate(obj)
E       pydantic_core._pydantic_core.ValidationError: 4 validation errors for QuestionSchema
E       subject
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subjects.Subj...bject at 0x7f116fa15b50>, input_type=SubjectModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       topic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.topics.TopicM...bject at 0x7f116fa15550>, input_type=TopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       subtopic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subtopics.Sub...bject at 0x7f116fa16bd0>, input_type=SubtopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.0
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f116fa16750>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/pydantic/main.py:1174: ValidationError
________________________ test_filter_questions_by_tags _________________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f1175d82a90>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f1175f23950>, 'client': None, 'endpoint': <function filter_questions_endpoint at 0x7f1175f05f80>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f1174ad1da0>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f1174ad27a0>

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

self = <anyio._backends._asyncio.TaskGroup object at 0x7f11744f2d50>
exc_type = <class 'pydantic_core._pydantic_core.ValidationError'>
exc_val = 5 validation errors for QuestionSchema
subject
  Input should be a valid dictionary [type=dict_type, input_value=<app....11749db150>, input_type=QuestionTagModel]
    For further information visit https://errors.pydantic.dev/2.6/v/dict_type
exc_tb = <traceback object at 0x7f117493d800>

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

logged_in_client = <starlette.testclient.TestClient object at 0x7f116f654f90>
setup_filter_questions_data = None
db_session = <sqlalchemy.orm.session.Session object at 0x7f116f655790>

    def test_filter_questions_by_tags(logged_in_client, setup_filter_questions_data, db_session):
>       response = logged_in_client.get(
            "/questions/filter",
            params={"tags": ["geometry"]}
        )

tests/test_api/test_api_filters.py:129: 
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
app/main.py:65: in check_revoked_token
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
app/main.py:49: in check_blacklist
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
app/api/endpoints/filters.py:17: in filter_questions_endpoint
    filtered_questions = filter_questions(
app/crud/crud_questions.py:81: in filter_questions
    return [QuestionSchema.from_orm(question) for question in questions]
app/crud/crud_questions.py:81: in <listcomp>
    return [QuestionSchema.from_orm(question) for question in questions]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'app.schemas.questions.QuestionSchema'>
obj = <app.models.questions.QuestionModel object at 0x7f11749d9e10>

    @classmethod
    @typing_extensions.deprecated(
        'The `from_orm` method is deprecated; set '
        "`model_config['from_attributes']=True` and use `model_validate` instead.",
        category=None,
    )
    def from_orm(cls: type[Model], obj: Any) -> Model:  # noqa: D102
        warnings.warn(
            'The `from_orm` method is deprecated; set '
            "`model_config['from_attributes']=True` and use `model_validate` instead.",
            category=PydanticDeprecatedSince20,
        )
        if not cls.model_config.get('from_attributes', None):
            raise PydanticUserError(
                'You must set the config attribute `from_attributes=True` to use from_orm', code=None
            )
>       return cls.model_validate(obj)
E       pydantic_core._pydantic_core.ValidationError: 5 validation errors for QuestionSchema
E       subject
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subjects.Subj...bject at 0x7f11749d9990>, input_type=SubjectModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       topic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.topics.TopicM...bject at 0x7f11749daf90>, input_type=TopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       subtopic
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.subtopics.Sub...bject at 0x7f11749d83d0>, input_type=SubtopicModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.0
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f11749d9450>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type
E       tags.1
E         Input should be a valid dictionary [type=dict_type, input_value=<app.models.questions.Que...bject at 0x7f11749db150>, input_type=QuestionTagModel]
E           For further information visit https://errors.pydantic.dev/2.6/v/dict_type

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/pydantic/main.py:1174: ValidationError
___________________________ test_create_question_set ___________________________

logged_in_client = <starlette.testclient.TestClient object at 0x7f116f850950>

    def test_create_question_set(logged_in_client):
        data = {"name": "Test Create Question Set"}
        response = logged_in_client.post("/question-sets/", json=data)
>       assert response.status_code == 201
E       assert 422 == 201
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_api/test_api_question_sets.py:9: AssertionError
_____________________ test_update_nonexistent_question_set _____________________

logged_in_client = <starlette.testclient.TestClient object at 0x7f116f850d90>
test_user = <app.models.users.UserModel object at 0x7f1174123710>

    def test_update_nonexistent_question_set(logged_in_client, test_user):
        """
        Test updating a question set that does not exist.
        """
        question_set_update = {"name": "Updated Name"}
        response = logged_in_client.put("/question-sets/99999", json=question_set_update)
>       assert response.status_code == 404
E       assert 422 == 404
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_api/test_api_question_sets.py:23: AssertionError
______________________ test_update_question_set_not_found ______________________

logged_in_client = <starlette.testclient.TestClient object at 0x7f116f85c410>

    def test_update_question_set_not_found(logged_in_client):
        question_set_id = 999
        question_set_update = {"name": "Updated Name"}
        response = logged_in_client.put(f"/question-sets/{question_set_id}", json=question_set_update)
>       assert response.status_code == 404
E       assert 422 == 404
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_api/test_api_question_sets.py:30: AssertionError
_______________________ test_upload_question_set_success _______________________

client = <starlette.testclient.TestClient object at 0x7f116fa0f3d0>
db_session = <sqlalchemy.orm.session.Session object at 0x7f1174131590>
test_user = <app.models.users.UserModel object at 0x7f116faf6f50>

    def test_upload_question_set_success(client, db_session, test_user):
        # Login
        login_data = {"username": test_user.username, "password": "TestPassword123!"}
        login_response = client.post("/login", json=login_data)
        access_token = login_response.json()["access_token"]
        assert login_response.status_code == 200, "Authentication failed."
        assert "access_token" in login_response.json(), "Access token missing in response."
        assert login_response.json()["token_type"] == "bearer", "Incorrect token type."
    
        # Prepare valid JSON data
        json_data = [
            {
                "text": "Question 1",
                "subtopic_id": 1,
                "question_set_id": 1,
                "answer_choices": [
                    {"text": "Answer 1", "is_correct": True},
                    {"text": "Answer 2", "is_correct": False}
                ],
                "explanation": "Explanation for Question 1"
            },
            {
                "text": "Question 2",
                "subtopic_id": 1,
                "question_set_id": 1,
                "answer_choices": [
                    {"text": "Answer 1", "is_correct": False},
                    {"text": "Answer 2", "is_correct": True}
                ],
                "explanation": "Explanation for Question 2"
            }
        ]
    
        # Create a temporary file with the JSON data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            json.dump(json_data, temp_file)
            temp_file.flush()  # Ensure the contents are written to the file
            # Access a protected endpoint with the token
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.post("/upload-questions/",
                                   files={"file": ("question_set.json", open(temp_file.name, 'rb'), "application/json")},
                                   headers=headers)
    
>       assert response.status_code == 200
E       assert 400 == 200
E        +  where 400 = <Response [400 Bad Request]>.status_code

tests/test_api/test_api_question_sets.py:85: AssertionError
_________________ test_create_question_set_with_existing_name __________________

logged_in_client = <starlette.testclient.TestClient object at 0x7f1174131e50>
test_question_set = <app.models.question_sets.QuestionSetModel object at 0x7f116fa0f710>

    def test_create_question_set_with_existing_name(logged_in_client, test_question_set):
        data = {"name": test_question_set.name}
        response = logged_in_client.post("/question-sets/", json=data)
>       assert response.status_code == 400
E       assert 422 == 400
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_api/test_api_question_sets.py:110: AssertionError
________________________ test_update_question_set_name _________________________

logged_in_client = <starlette.testclient.TestClient object at 0x7f116faf6c10>
test_question_set = <app.models.question_sets.QuestionSetModel object at 0x7f116fa3d8d0>

    def test_update_question_set_name(logged_in_client, test_question_set):
        updated_name = "Updated Question Set"
        data = {"name": updated_name}
        response = logged_in_client.put(f"/question-sets/{test_question_set.id}", json=data)
>       assert response.status_code == 200
E       assert 422 == 200
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_api/test_api_question_sets.py:123: AssertionError
_______________________ test_create_private_question_set _______________________

logged_in_client = <starlette.testclient.TestClient object at 0x7f117473c150>

    def test_create_private_question_set(logged_in_client):
        response = logged_in_client.post("/question-sets/", json={"name": "Test Private Set", "is_public": False})
>       assert response.status_code == 201
E       assert 422 == 201
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_api/test_api_question_sets.py:152: AssertionError
_____________________________ test_create_question _____________________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f1175d82a90>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f1175f23950>, 'client': None, 'endpoint': <function create_question_endpoint at 0x7f1175f05d00>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f116fe87100>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f116fee6160>

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

self = <anyio._backends._asyncio.TaskGroup object at 0x7f116fa17110>
exc_type = <class 'fastapi.exceptions.ResponseValidationError'>
exc_val = ResponseValidationError()
exc_tb = <traceback object at 0x7f11746011c0>

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

client = <starlette.testclient.TestClient object at 0x7f11744dfdd0>
db_session = <sqlalchemy.orm.session.Session object at 0x7f116f6da610>
test_question_set = <app.models.question_sets.QuestionSetModel object at 0x7f116fa3c3d0>
test_subtopic = <app.models.subtopics.SubtopicModel object at 0x7f116f942250>

    def test_create_question(client, db_session, test_question_set, test_subtopic):
        subject_data = SubjectCreateSchema(name="Test Subject")
        subject = create_subject_crud(db_session, subject_data)
        topic_data = TopicCreateSchema(name="Test Topic", subject_id=subject.id)
        topic = create_topic_crud(db_session, topic_data)
        data = {
            "text": "Test Question",
            "subject_id": subject.id,
            "topic_id": topic.id,
            "subtopic_id": test_subtopic.id,
            "question_set_id": test_question_set.id,
            "difficulty_level": "Easy",
            "answer_choices": [
                {"text": "Answer 1", "is_correct": True},
                {"text": "Answer 2", "is_correct": False}
            ],
            "explanation": "Test Explanation"
        }
>       response = client.post("/question/", json=data)

tests/test_api/test_api_questions.py:24: 
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
app/main.py:65: in check_revoked_token
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
app/main.py:49: in check_blacklist
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
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/routing.py:296: in app
    content = await serialize_response(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    async def serialize_response(
        *,
        field: Optional[ModelField] = None,
        response_content: Any,
        include: Optional[IncEx] = None,
        exclude: Optional[IncEx] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        is_coroutine: bool = True,
    ) -> Any:
        if field:
            errors = []
            if not hasattr(field, "serialize"):
                # pydantic v1
                response_content = _prepare_response_content(
                    response_content,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                )
            if is_coroutine:
                value, errors_ = field.validate(response_content, {}, loc=("response",))
            else:
                value, errors_ = await run_in_threadpool(
                    field.validate, response_content, {}, loc=("response",)
                )
            if isinstance(errors_, list):
                errors.extend(errors_)
            elif errors_:
                errors.append(errors_)
            if errors:
>               raise ResponseValidationError(
                    errors=_normalize_errors(errors), body=response_content
                )
E               fastapi.exceptions.ResponseValidationError: 6 validation errors:
E                 {'type': 'int_type', 'loc': ('response', 'subject_id'), 'msg': 'Input should be a valid integer', 'input': None, 'url': 'https://errors.pydantic.dev/2.6/v/int_type'}
E                 {'type': 'int_type', 'loc': ('response', 'topic_id'), 'msg': 'Input should be a valid integer', 'input': None, 'url': 'https://errors.pydantic.dev/2.6/v/int_type'}
E                 {'type': 'dict_type', 'loc': ('response', 'subject'), 'msg': 'Input should be a valid dictionary', 'input': None, 'url': 'https://errors.pydantic.dev/2.6/v/dict_type'}
E                 {'type': 'dict_type', 'loc': ('response', 'topic'), 'msg': 'Input should be a valid dictionary', 'input': None, 'url': 'https://errors.pydantic.dev/2.6/v/dict_type'}
E                 {'type': 'dict_type', 'loc': ('response', 'subtopic'), 'msg': 'Input should be a valid dictionary', 'input': <app.models.subtopics.SubtopicModel object at 0x7f116fb58e10>, 'url': 'https://errors.pydantic.dev/2.6/v/dict_type'}
E                 {'type': 'string_type', 'loc': ('response', 'difficulty_level'), 'msg': 'Input should be a valid string', 'input': None, 'url': 'https://errors.pydantic.dev/2.6/v/string_type'}

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/routing.py:155: ResponseValidationError
________________________ test_read_questions_with_token ________________________

    @contextmanager
    def collapse_excgroups() -> typing.Generator[None, None, None]:
        try:
>           yield

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/starlette/_utils.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <starlette.middleware.base.BaseHTTPMiddleware object at 0x7f1175d82a90>
scope = {'app': <fastapi.applications.FastAPI object at 0x7f1175f23950>, 'client': None, 'endpoint': <function get_questions_endpoint at 0x7f1175f707c0>, 'extensions': {'http.response.debug': {}}, ...}
receive = <function _TestClientTransport.handle_request.<locals>.receive at 0x7f116fe1dbc0>
send = <function ServerErrorMiddleware.__call__.<locals>._send at 0x7f116fe876a0>

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

self = <anyio._backends._asyncio.TaskGroup object at 0x7f11744a0d50>
exc_type = <class 'fastapi.exceptions.ResponseValidationError'>
exc_val = ResponseValidationError()
exc_tb = <traceback object at 0x7f11744a2b80>

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

client = <starlette.testclient.TestClient object at 0x7f11744e1ad0>
db_session = <sqlalchemy.orm.session.Session object at 0x7f1174641d90>
test_question = <app.models.questions.QuestionModel object at 0x7f1174643890>
test_user = <app.models.users.UserModel object at 0x7f11744509d0>

    def test_read_questions_with_token(client, db_session, test_question, test_user):
        # Authenticate and get the access token
        login_data = {"username": test_user.username, "password": "TestPassword123!"}
        response = client.post("/token", data=login_data)
        access_token = response.json()["access_token"]
        assert response.status_code == 200, "Authentication failed."
        assert "access_token" in response.json(), "Access token missing in response."
        assert response.json()["token_type"] == "bearer", "Incorrect token type."
    
        # Make the request to the /questions/ endpoint with the access token
        headers = {"Authorization": f"Bearer {access_token}"}
>       response = client.get("/questions/", headers=headers)

tests/test_api/test_api_questions.py:42: 
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
app/main.py:65: in check_revoked_token
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
app/main.py:49: in check_blacklist
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
/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/routing.py:296: in app
    content = await serialize_response(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    async def serialize_response(
        *,
        field: Optional[ModelField] = None,
        response_content: Any,
        include: Optional[IncEx] = None,
        exclude: Optional[IncEx] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        is_coroutine: bool = True,
    ) -> Any:
        if field:
            errors = []
            if not hasattr(field, "serialize"):
                # pydantic v1
                response_content = _prepare_response_content(
                    response_content,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                )
            if is_coroutine:
                value, errors_ = field.validate(response_content, {}, loc=("response",))
            else:
                value, errors_ = await run_in_threadpool(
                    field.validate, response_content, {}, loc=("response",)
                )
            if isinstance(errors_, list):
                errors.extend(errors_)
            elif errors_:
                errors.append(errors_)
            if errors:
>               raise ResponseValidationError(
                    errors=_normalize_errors(errors), body=response_content
                )
E               fastapi.exceptions.ResponseValidationError: 6 validation errors:
E                 {'type': 'int_type', 'loc': ('response', 0, 'subject_id'), 'msg': 'Input should be a valid integer', 'input': None, 'url': 'https://errors.pydantic.dev/2.6/v/int_type'}
E                 {'type': 'int_type', 'loc': ('response', 0, 'topic_id'), 'msg': 'Input should be a valid integer', 'input': None, 'url': 'https://errors.pydantic.dev/2.6/v/int_type'}
E                 {'type': 'dict_type', 'loc': ('response', 0, 'subject'), 'msg': 'Input should be a valid dictionary', 'input': None, 'url': 'https://errors.pydantic.dev/2.6/v/dict_type'}
E                 {'type': 'dict_type', 'loc': ('response', 0, 'topic'), 'msg': 'Input should be a valid dictionary', 'input': None, 'url': 'https://errors.pydantic.dev/2.6/v/dict_type'}
E                 {'type': 'dict_type', 'loc': ('response', 0, 'subtopic'), 'msg': 'Input should be a valid dictionary', 'input': <app.models.subtopics.SubtopicModel object at 0x7f116f804e50>, 'url': 'https://errors.pydantic.dev/2.6/v/dict_type'}
E                 {'type': 'string_type', 'loc': ('response', 0, 'difficulty_level'), 'msg': 'Input should be a valid string', 'input': None, 'url': 'https://errors.pydantic.dev/2.6/v/string_type'}

/home/astromined/anaconda3/envs/fastapi_quiz_app/lib/python3.11/site-packages/fastapi/routing.py:155: ResponseValidationError
________________________ test_update_question_not_found ________________________

client = <starlette.testclient.TestClient object at 0x7f116f69db90>
db_session = <sqlalchemy.orm.session.Session object at 0x7f116f69fd90>

    def test_update_question_not_found(client, db_session):
        """
        Test updating a question that does not exist.
        """
        question_id = 999  # Assuming this ID does not exist
        question_update = {"text": "Updated Question"}
        response = client.put(f"/question/{question_id}", json=question_update)
>       assert response.status_code == 404
E       assert 422 == 404
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_api/test_api_questions.py:61: AssertionError
______________________ test_create_and_retrieve_question _______________________

db_session = <sqlalchemy.orm.session.Session object at 0x7f1175f68f90>
test_question_set = <app.models.question_sets.QuestionSetModel object at 0x7f116f69d6d0>
test_subtopic = <app.models.subtopics.SubtopicModel object at 0x7f116f659610>

    def test_create_and_retrieve_question(db_session, test_question_set, test_subtopic):
        """Test creation and retrieval of a question."""
        test_question_set.name = "Unique Question Set for Question Creation"
        subject_data = SubjectCreateSchema(name="Test Subject")
        subject = create_subject_crud(db_session, subject_data)
        topic_data = TopicCreateSchema(name="Test Topic", subject_id=subject.id)
        topic = create_topic_crud(db_session, topic_data)
        answer_choice_1 = AnswerChoiceCreateSchema(text="Test Answer 1", is_correct=True)
        answer_choice_2 = AnswerChoiceCreateSchema(text="Test Answer 2", is_correct=False)
        question_data = QuestionCreateSchema(
            text="Sample Question?",
            subject_id=subject.id,
            topic_id=topic.id,
            subtopic_id=test_subtopic.id,
            question_set_id=test_question_set.id,
            difficulty_level="Easy",
            answer_choices=[answer_choice_1, answer_choice_2],
            explanation="Test Explanation"
        )
        created_question = create_question_crud(db=db_session, question=question_data)
        retrieved_question = get_question_crud(db_session, question_id=created_question.id)
        assert retrieved_question is not None, "Failed to retrieve created question."
        assert retrieved_question.text == "Sample Question?", "Question text does not match."
>       assert retrieved_question.difficulty_level == "Easy", "Question difficulty level does not match."
E       AssertionError: Question difficulty level does not match.
E       assert None == 'Easy'
E        +  where None = <app.models.questions.QuestionModel object at 0x7f116f65bb10>.difficulty_level

tests/test_crud/test_crud_questions.py:40: AssertionError

---------- coverage: platform linux, python 3.11.8-final-0 -----------
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
app/__init__.py                           1      0   100%
app/api/__init__.py                       1      0   100%
app/api/endpoints/__init__.py             1      0   100%
app/api/endpoints/auth.py                34      4    88%
app/api/endpoints/filters.py             13      3    77%
app/api/endpoints/question.py            25      7    72%
app/api/endpoints/question_sets.py       65     23    65%
app/api/endpoints/questions.py           15      1    93%
app/api/endpoints/register.py            17      0   100%
app/api/endpoints/subjects.py            27      2    93%
app/api/endpoints/token.py               19      0   100%
app/api/endpoints/topics.py              27      2    93%
app/api/endpoints/user_responses.py      27      9    67%
app/api/endpoints/users.py               20      2    90%
app/core/__init__.py                      4      0   100%
app/core/config.py                        8      0   100%
app/core/jwt.py                          30      1    97%
app/core/security.py                      7      0   100%
app/crud/__init__.py                      8      0   100%
app/crud/crud_question_sets.py           41      7    83%
app/crud/crud_questions.py               52     10    81%
app/crud/crud_subjects.py                25      1    96%
app/crud/crud_subtopics.py                9      0   100%
app/crud/crud_topics.py                  26      1    96%
app/crud/crud_user.py                    19      3    84%
app/crud/crud_user_responses.py          13      1    92%
app/crud/crud_user_utils.py               5      0   100%
app/db/__init__.py                        2      0   100%
app/db/base_class.py                      3      0   100%
app/db/session.py                        14      2    86%
app/main.py                              46      5    89%
app/models/__init__.py                    9      0   100%
app/models/answer_choices.py             11      0   100%
app/models/question_sets.py              11      0   100%
app/models/questions.py                  28      0   100%
app/models/subjects.py                   10      0   100%
app/models/subtopics.py                  11      0   100%
app/models/token.py                       7      0   100%
app/models/topics.py                     12      0   100%
app/models/user_responses.py             16      0   100%
app/models/users.py                      13      0   100%
app/schemas/__init__.py                  11      0   100%
app/schemas/answer_choices.py            10      0   100%
app/schemas/auth.py                       4      0   100%
app/schemas/filters.py                    8      0   100%
app/schemas/question_sets.py             14      0   100%
app/schemas/questions.py                 28      0   100%
app/schemas/subjects.py                   9      0   100%
app/schemas/subtopics.py                  9      0   100%
app/schemas/token.py                      4      0   100%
app/schemas/topics.py                    10      0   100%
app/schemas/user.py                      32      3    91%
app/schemas/user_responses.py            14      0   100%
app/services/__init__.py                  2      0   100%
app/services/auth_service.py             14      1    93%
app/services/user_service.py             25      4    84%
---------------------------------------------------------
TOTAL                                   926     92    90%

=========================== short test summary info ============================
FAILED tests/test_api/test_api_filters.py::test_filter_questions - pydantic_c...
FAILED tests/test_api/test_api_filters.py::test_filter_questions_by_subject
FAILED tests/test_api/test_api_filters.py::test_filter_questions_by_topic - p...
FAILED tests/test_api/test_api_filters.py::test_filter_questions_by_subtopic
FAILED tests/test_api/test_api_filters.py::test_filter_questions_by_difficulty
FAILED tests/test_api/test_api_filters.py::test_filter_questions_by_single_tag
FAILED tests/test_api/test_api_filters.py::test_filter_questions_by_multiple_criteria
FAILED tests/test_api/test_api_filters.py::test_filter_questions_by_tags - py...
FAILED tests/test_api/test_api_question_sets.py::test_create_question_set - a...
FAILED tests/test_api/test_api_question_sets.py::test_update_nonexistent_question_set
FAILED tests/test_api/test_api_question_sets.py::test_update_question_set_not_found
FAILED tests/test_api/test_api_question_sets.py::test_upload_question_set_success
FAILED tests/test_api/test_api_question_sets.py::test_create_question_set_with_existing_name
FAILED tests/test_api/test_api_question_sets.py::test_update_question_set_name
FAILED tests/test_api/test_api_question_sets.py::test_create_private_question_set
FAILED tests/test_api/test_api_questions.py::test_create_question - fastapi.e...
FAILED tests/test_api/test_api_questions.py::test_read_questions_with_token
FAILED tests/test_api/test_api_questions.py::test_update_question_not_found
FAILED tests/test_crud/test_crud_questions.py::test_create_and_retrieve_question
19 failed, 76 passed in 62.12s (0:01:02)

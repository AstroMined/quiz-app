# Quiz App Backend

The Quiz App Backend is a FastAPI-based backend system for managing and serving quiz questions and user responses. It provides a comprehensive set of API endpoints for user management, question set management, filtering, and user response tracking.

## Getting Started

To get started with the Quiz App Backend, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/AstroMined/quiz-app/backend.git
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:

   - For development, the backend uses SQLite.
   - For production, configure a PostgreSQL database.

4. Run the database migrations:

   ```bash
   alembic upgrade head
   ```

5. Start the FastAPI server:

   ```bash
   uvicorn app.main:app --reload
   ```

   The backend server will start running at `http://localhost:8000`.

## API Endpoints

The Quiz App Backend provides the following API endpoints:

### User Management

- `POST /register/`: Register a new user.
- `POST /login`: User login.
- `POST /logout`: User logout.
- `GET /users/`: Get a list of all users (admin only).
- `GET /users/me`: Get the current user's profile.
- `PUT /users/me`: Update the current user's profile.

### Question Set Management

- [x] `POST /upload-questions/`: Upload a question set from a JSON file (admin only).
- [x] `GET /question-set/`: Get a list of all question sets.
- [x] `POST /question-sets/`: Create a new question set (admin only).
- [x] `GET /question-sets/{question_set_id}`: Get a specific question set by ID.
- [x] `PUT /question-sets/{question_set_id}`: Update a question set (admin only).
- [x] `DELETE /question-sets/{question_set_id}`: Delete a question set (admin only).

### Question Management

- [x] `POST /question/`: Create a new question.
- [x] `GET /question/{question_id}`: Get a specific question by ID.
- [x] `PUT /question/{question_id}`: Update a question.
- [x] `DELETE /question/{question_id}`: Delete a question.
- [x] `GET /questions/`: Get a list of all questions.

### Filtering

- [x] `GET /questions/filter`: Filter questions based on subject, topic, subtopic, difficulty, or tags.

### User Response Tracking

- [x] `POST /user-responses/`: Create a new user response.
- [x] `GET /user-responses/{user_response_id}`: Get a specific user response by ID.
- [x] `GET /user-responses/`: Get a list of all user responses.
- [x] `PUT /user-responses/{user_response_id}`: Update a user response.
- [x] `DELETE /user-responses/{user_response_id}`: Delete a user response.

### Subjects, Topics, and Subtopics

- [x] `POST /subjects/`: Create a new subject.
- [x] `GET /subjects/{subject_id}`: Get a specific subject by ID.
- [x] `PUT /subjects/{subject_id}`: Update a subject.
- [x] `DELETE /subjects/{subject_id}`: Delete a subject.
- [x] `POST /topics/`: Create a new topic.
- [x] `GET /topics/{topic_id}`: Get a specific topic by ID.
- [x] `PUT /topics/{topic_id}`: Update a topic.
- [x] `DELETE /topics/{topic_id}`: Delete a topic.

## Database Models

The Quiz App Backend uses the following database models:

- [x] `UserModel`: Represents a user in the system.
- [x] `QuestionSetModel`: Represents a question set containing multiple questions.
- [x] `QuestionModel`: Represents a single question.
- [x] `AnswerChoiceModel`: Represents an answer choice for a question.
- [x] `UserResponseModel`: Represents a user's response to a question.
- [x] `SubjectModel`: Represents a subject category for questions.
- [x] `TopicModel`: Represents a topic within a subject.
- [x] `SubtopicModel`: Represents a subtopic within a topic.
- [x] `QuestionTagModel`: Represents a tag associated with a question.
- [x] `RevokedTokenModel`: Represents a revoked access token.

## Authentication and Authorization

The Quiz App Backend uses JSON Web Tokens (JWT) for authentication and authorization. The following authentication and authorization mechanisms are implemented:

- [x] User registration and login.
- [x] Password hashing using bcrypt.
- [x] JWT token generation and verification.
- [x] Access token revocation on logout.
- [x] Protected routes that require authentication.
- [x] Admin-only routes for privileged operations.

## Testing

The Quiz App Backend includes a comprehensive test suite to ensure the functionality and reliability of the system. The tests cover various aspects, including:

- [x] API endpoints
- [x] Authentication and authorization
- [x] Database models
- [x] CRUD operations
- [x] Filtering and pagination
- [x] Error handling and validation

To run the tests, use the following command:

```bash
pytest tests/ --cov=app
```

## Future Enhancements

The following features and enhancements are planned for future development:

- [ ] Scoring system and leaderboards
- [ ] Review mode for incorrect answers
- [ ] Performance optimization and caching
- [ ] Improved error handling and logging
- [ ] Documentation using Swagger UI

## Contributing

Contributions to the Quiz App Backend are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

The Quiz App Backend is open-source software licensed under the [MIT License](https://opensource.org/licenses/MIT).

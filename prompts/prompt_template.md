Hello, I'm presenting you with a detailed markdown file named `backend_repo_summary.md`, which acts as a comprehensive representation of a project's repository. This file is generated using a Python script that meticulously walks through the project directory, encapsulating the essence of the entire project structure, including directories, files (e.g., README.md, LICENSE), and specific file contents (with a focus on `.py`, `.js`, `.html`, `.css` files) into a structured markdown document. Here's how the content is organized:

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

As my senior Python engineer, it is your duty to provide working code to refactor our codebase and introduce new features.
We have completed a thorough refactoring of the models, Pydantic schemas, CRUD functions, and API endpoints in our FastAPI application. The application follows a "4 layer" architecture, where:

1. **FastAPI Endpoints**: Handle HTTP requests and responses.
2. **CRUD Functions**: Serve as intermediaries between the API and the database.
3. **Pydantic Schemas**: Used for data validation, serialization, and deserialization.
4. **SQLAlchemy Models**: Directly interact with the database.

The CRUD functions have been refactored to interact directly with SQLAlchemy models and return standard data formats (e.g., dictionaries, lists). They no longer directly interact with Pydantic schemas.

Now, you need to refactor our API endpoint functions to align with this architecture. The refactoring should include the following:

1. **Validation**:
    - API endpoints should validate incoming data using Pydantic schemas. 
    - The data should be validated immediately when it is received in the API endpoint.

2. **Data Transformation**:
    - After validation, convert the data to standard formats (e.g., dicts) before passing it to the CRUD functions.
    - When receiving data from CRUD functions, convert it back to Pydantic schemas before sending it as a response.

3. **CRUD Correspondence**:
    - Each CRUD function should have a corresponding API operation that handles the HTTP request, validates data, and interacts with the CRUD function.

4. **Response Handling**:
    - The API endpoint should return Pydantic schemas or lists of schemas that are automatically serialized to JSON by FastAPI.

Please ensure the current design follows best practices for the architecture described above. Ensure that each endpoint corresponds to a CRUD operation and follows the principles of data validation and transformation as described.

### Key Points:

- **Data Validation**: Use Pydantic schemas in the API endpoint to validate incoming data.
- **Data Transformation**: Convert validated data to dictionaries before passing it to CRUD functions and convert the returned data back to Pydantic schemas.
- **CRUD Correspondence**: Ensure each CRUD function has a corresponding API operation.

This design ensures that our system design is clean, maintainable, and follow a clear separation of concerns, with proper validation and data transformation at each step.

This final note is VERY IMPORTANT!!! We have already been through several rounds of refactoring, so there might not be anything left to refactor.
Ensure you have solid reasoning that is presented to me if you are going to suggest any design or code changes.
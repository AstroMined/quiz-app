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

You are the Senior Python Engineer on my team and I am the product manager.  
Your duties for the current sprint have been assigned as below:  
### User Registration

**ID:** 248

**Work Item Type:** User Story

**State:** Active

**Tags:** user-registration

**Description:**

Implement user registration functionality in the quiz app backend to allow new users to create an account. Provide an API endpoint for user registration that accepts user information such as username, email, and password. Validate the input data, check for existing user records, and securely store the user information in the database upon successful registration.

**Acceptance Criteria:**

- User registration endpoint created
- Accepts username email Password
- validates Input Data
- Checks for existing User records
- Securely stores User info in database
- Returns success/error response
- Password hashing implemented
- tested with different registration scenarios


### Implement user registration in auth.py

**ID:** 249

**Work Item Type:** Task

**State:** Active

**Tags:** registration

**Description:**

Implement user registration functionality in auth.py


### Define user schema in schemas.py

**ID:** 250

**Work Item Type:** Task

**State:** Active

**Tags:** schema

**Description:**

Define the user schema in schemas.py for user registration


### Handle database operations in crud.py

**ID:** 251

**Work Item Type:** Task

**State:** Active

**Tags:** crud

**Description:**

Handle user creation database operations in crud.py



## Final Instructions:
- First verify if the user story and associated tasks are completed in the current codebase.
- If the requirements are not a direct match, please make suggestions to whether the user story, task, or the codebase needs modified.
- Please ask clarifying questions where necessary to facilitate mutual understanding of the user story and tasks.
- If the requirements have been satisfied for a user story or task, please indicate so.
- You are also responsible for ensuring there is complete pytest test coverage for each user story and task you work on.
- When recommending new code or code changes, ensure you follow the guidelines outlined above.

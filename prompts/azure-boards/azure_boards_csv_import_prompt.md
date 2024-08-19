Hello, Claude!

I'm presenting you with a detailed markdown file named `frontend_repo_summary.md`, which acts as a comprehensive representation of a project's repository. This file is generated using a Python script that meticulously walks through the project directory, encapsulating the essence of the entire project structure, including directories, files (e.g., README.md, LICENSE), and specific file contents (with a focus on `.py`, `.js`, `.html`, `.css` files) into a structured markdown document. Here's how the content is organized:

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

As my coding partner and product manager, I need your expert help defining Epics, Features, User Stories, and Tasks for this project.
The various README.md files in the repo contain ideas of features I've identified so far that I'd like to implement.

Your first task is to thoroughly review the codebase to understand which features have been implemented.
Using what you have learned, I want you to produce Epics, Features, User Stories, and Tasks for use in Azure Boards.
The attached CSV file is a good starting point, but it needs several fields filled out or expanded on to be useful.
If there are features that you feel are missing, please feel free to add your own ideas.

Your output should be a CSV that I can import into Azure Boards.
Ensure that you mention any Area Paths and Iteration Paths that I need to create before importing the file.

## Summary for Bulk Import into Azure Boards
1. Introduction to Bulk Import:
Azure Boards supports the import and update of work items using a CSV formatted file. This feature allows for the bulk management of work items without the need for Excel. Work items are created in a 'New' state during import, and specific field rules must be met.

2. Preparing the CSV File:

- Required Fields: Each row in the CSV file must include at least these fields:
  - Work Item Type
  - Title 1 (for epics)
  - Title 2 (for features)
  - Title 3 (for user stories)
  - Title 4 (for tasks)
  - Description
  - State
  - Area Path
  - Iteration Path
  - Priority
  - Effort
  - Tags
  - Acceptance Criteria (only for epics, features, user stories, and tasks)
- Rich Text Fields: The 'Description' and 'Acceptance Criteria' fields support HTML formatting. Ensure detailed information is provided in these fields for clarity.
- Tags: Use semicolons (;) to separate multiple tags within the 'Tags' field.
- Child Work Items: Indent 'Title' columns to create parent-child relationships between work items. This feature allows for the hierarchical organization of tasks under Epics or Features. This means the parent item must be defined first using the "Title 1" field. Child work items should be defined immediately after the parent with their title in the "Title 2" column. This concept can be expanded to "Title 3" and "Title 4" columns to create a hierarchy from Epic to Feature to User Story to Task.

3. Field Specifications:

- Description & Acceptance Criteria: Provide detailed, HTML-formatted content.
- State: Work items are imported in the 'New' state by default.
- Area Path & Iteration Path: Must exist in Azure Boards prior to import. Use these fields to assign work items to specific areas or iterations for organizational purposes.
- Priority, Effort: Specify the importance and the estimated effort required for the task.
- Tags: Apply tags for easier filtering and identification. Separate multiple tags with semicolons.

4. Tips for Success:

- Do not assign IDs to new work items to avoid errors.
- The maximum import limit is 1000 work items per file. For larger imports, split the data into multiple files.
- Be mindful of the detailed requirements for the 'Description' and 'Acceptance Criteria' fields, utilizing HTML for formatting.
- Area Path and Iteration Path fields are crucial for organizing work items post-import and must be predefined in Azure Boards, so you must ensure you inform me of area and iteration paths that I need to create before importing.
Hello, I'm providing you with a markdown file named `repo_summary.md` that serves as a single file representation of a project repository. This file organizes the content of an entire project repository, including various Python scripts and README.md files, into a structured markdown document. Here's how the file is structured:

1. **Directories** are marked as main headers, formatted as `# Directory: path/to/directory`. Each directory within the project is listed with its full path, providing a clear hierarchy of the project's structure.

2. **Files** within those directories, including Python scripts and README.md files, are listed under secondary headers within their respective directory sections, formatted as `## File: filename`. README.md files, when present, are prioritized and appear first under each directory section, followed by Python scripts.

3. **Content** of each file is enclosed in code blocks immediately following the file header, using the appropriate syntax highlighting (```markdown for README.md and ```python for Python scripts).

When recommending changes or additions to the project, please specify the exact file paths. If suggesting modifications to existing files, reference the file path as noted in the markdown structure. For new file suggestions, specify a proposed file path consistent with the project's organizational structure.

Please output full scripts or file content whenever possible, without using placeholders. This approach ensures ease of use and allows for straightforward copy/pasting of the generated code into the project.

If there are aspects of the functionality you need to clarify or if you're unsure about how certain parts of the project are intended to work, please ask specific questions rather than making assumptions or "hallucinating" details.

**[Task-Specific Section]:**

*Here, I'm seeking assistance with the following tasks for my project:*
I would first like you to thoroughly comment all python files in the /code/quiz-app/quiz-app-backend/app/api/endpoints directory, including module and function docstrings.
Ensure that the first line of each Python script is a comment in the form of filename: path/to/file.py with the scripts filename and path.
Using what you learn by commenting these files, I then want you to create a README.md file for the /code/quiz-app/quiz-app-backend/app/api/endpoints directory which explains the purpose of each file and the functions they make available.
You can also make suggestions in the README.md file about new files that might need to be created or what the purpose of empty files in this directory might be given the goals of the project, which are explained briefly in /code/quiz-app/quiz-app-backend/README.md.
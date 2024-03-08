import os
import argparse
import subprocess

def generate_markdown(repo_path):
    markdown_content = ""
    for root, dirs, files in os.walk(repo_path):
        readme_content = ""
        python_files_content = ""
        # Sort files to ensure README.md comes first if it exists
        files.sort()
        has_readme = False

        for file in files:
            if file == "README.md":
                has_readme = True
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as file_content:
                    content = file_content.read()
                    readme_content = f"\n## File: {file}\n```markdown\n{content}\n```\n"
            elif file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as file_content:
                    content = file_content.read()
                    python_files_content += f"\n## File: {file}\n```python\n{content}\n```\n"

        if has_readme or python_files_content:
            # Adding directory as a main header
            markdown_content += f"\n# Directory: {root}\n"
            markdown_content += readme_content + python_files_content

    return markdown_content

def main():
    parser = argparse.ArgumentParser(description='Generate a markdown file from a repository, with directory and README.md prioritization.')
    parser.add_argument('repo_path', type=str, help='Path to the repository')

    args = parser.parse_args()

    # Generate the markdown content
    markdown = generate_markdown(args.repo_path)

    # Save the markdown content to a file
    markdown_file_path = 'repo_summary.md'
    with open(markdown_file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown)

    # Use the external command line utility to count tokens
    result = subprocess.run(['token-count', '--file', markdown_file_path, '--model_name', 'gpt-4'], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Token count for {markdown_file_path}: {result.stdout.strip()}")
    else:
        print(f"Error calculating token count: {result.stderr}")

if __name__ == "__main__":
    main()

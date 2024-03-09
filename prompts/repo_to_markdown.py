import os
import argparse
import subprocess
import json

def generate_markdown(config):
    repo_path = config['root_directory']
    file_extensions = config['file_extensions']
    specific_files = config.get('specific_files', {})
    ignore_directories = config.get('ignore_directories', [])
    
    markdown_content = ""
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_directories]

        files.sort()
        dir_content = ""

        for file in files:
            if specific_files and file in [os.path.basename(f['path']) for f in specific_files.values()]:
                file_path = [f['path'] for f in specific_files.values() if os.path.basename(f['path']) == file][0]
                with open(file_path, 'r', encoding='utf-8') as file_content:
                    content = file_content.read()
                    if specific_files[file_path]['position'] == "first":
                        dir_content = f"\n## File: {file}\n```markdown\n{content}\n```\n" + dir_content
                    elif specific_files[file_path]['position'] == "last":
                        dir_content += f"\n## File: {file}\n```markdown\n{content}\n```\n"
            elif any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as file_content:
                    content = file_content.read()
                    dir_content += f"\n## File: {file}\n```{file.split('.')[-1]}\n{content}\n```\n"

        if dir_content:
            markdown_content += f"\n# Directory: {root}\n{dir_content}"

    return markdown_content

def main():
    parser = argparse.ArgumentParser(description='Generate a markdown file from a repository based on a JSON configuration file.')
    parser.add_argument('config_file', type=str, help='Path to the JSON configuration file')

    args = parser.parse_args()

    # Load the JSON configuration file
    with open(args.config_file, 'r') as config_file:
        config = json.load(config_file)

    # Generate the markdown content
    markdown = generate_markdown(config)

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
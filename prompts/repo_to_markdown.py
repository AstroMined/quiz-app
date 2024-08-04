import os
import argparse
import subprocess
import json


def is_directory_ignored(directory, ignore_directories, specific_files):
    """Check if the directory is in the list of directories to ignore, 
       excluding directories containing specific files.

    Args:
        directory (str): The directory to check.
        ignore_directories (list): List of directories to ignore.
        specific_files (dict): Dictionary of specific files and their positions.

    Returns:
        bool: True if the directory is in the list of directories to ignore and does not contain specific files, False otherwise.
    """
    abs_dir = os.path.abspath(directory)
    for ignore_dir in ignore_directories:
        abs_ignore_dir = os.path.abspath(ignore_dir)
        if abs_dir.startswith(abs_ignore_dir):
            # Check if any specific files are within this directory
            for specific_file in specific_files:
                abs_specific_file = os.path.abspath(os.path.join(directory, specific_file))
                if abs_specific_file.startswith(abs_dir):
                    return False
            return True
    return False


def process_files_in_directory(root, files, file_extensions, specific_files, markdown_content):
    """Process the files in a directory and generate markdown content.

    Args:
        root (str): The root directory.
        files (list): List of files in the directory.
        file_extensions (list): List of file extensions to include.
        specific_files (dict): Dictionary of specific files and their positions.
        markdown_content (str): The existing markdown content.

    Returns:
        str: The updated markdown content.
    """
    files.sort()
    dir_content = ""

    for file in files:
        file_path = os.path.join(root, file)
        if specific_files and file_path in specific_files:
            with open(file_path, 'r', encoding='utf-8') as file_content:
                content = file_content.read()
                position = specific_files[file_path]
                if position == "first":
                    dir_content = f"\n## File: {file}\n```markdown\n{content}\n```\n" + dir_content
                elif position == "last":
                    dir_content += f"\n## File: {file}\n```markdown\n{content}\n```\n"
        elif any(file.endswith(ext) for ext in file_extensions):
            with open(file_path, 'r', encoding='utf-8') as file_content:
                content = file_content.read()
                dir_content += f"\n## File: {file}\n```{file.split('.')[-1]}\n{content}\n```\n"

    if dir_content:
        markdown_content += f"\n# Directory: {root}\n{dir_content}"

    return markdown_content


def generate_markdown(config):
    """Generate a markdown file from a repository based on a JSON configuration.

    Args:
        config (dict): The JSON configuration.

    Returns:
        str: The generated markdown content.
    """
    repo_path = config['root_directory']
    file_extensions = config['file_extensions']
    specific_files = {os.path.join(repo_path, k): v for k, v in config.get('specific_files', {}).items()}
    ignore_directories = [os.path.join(repo_path, d) for d in config.get('ignore_directories', [])]

    markdown_content = ""

    for root, dirs, files in os.walk(repo_path, topdown=True):
        if is_directory_ignored(root, ignore_directories, specific_files):
            dirs[:] = []  # Don't walk into ignored directories
            continue

        # Process only the files that are not in ignored directories
        filtered_files = [f for f in files if not is_directory_ignored(
            os.path.join(root, f), ignore_directories, specific_files)]
        markdown_content = process_files_in_directory(
            root, filtered_files, file_extensions, specific_files, markdown_content)

    return markdown_content


def main():
    """
    Main function to generate a markdown file from a repository based on a JSON configuration file.
    """
    parser = argparse.ArgumentParser(
        description='Generate a markdown file from a repository based on a JSON configuration file.'
    )
    parser.add_argument('config_file', type=str,
                        help='Path to the JSON configuration file')

    args = parser.parse_args()

    # Load the JSON configuration file
    with open(args.config_file, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    # Generate the markdown content
    markdown = generate_markdown(config)

    # Create a unique filename for the markdown file
    root_dir_name = os.path.basename(
        os.path.normpath(config['root_directory']))
    markdown_file_path = f"{root_dir_name}_repo_summary.md"

    # Save the markdown content to the file
    with open(markdown_file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown)

    print(f"Markdown file generated: {markdown_file_path}")

    # Use the external command line utility to count tokens
    result = subprocess.run(['token-count', '--file', markdown_file_path,
                            '--model_name', 'gpt-4'], capture_output=True, text=True, check=True)

    if result.returncode == 0:
        print(f"Token count for {markdown_file_path}: {result.stdout.strip()}")
    else:
        print(f"Error calculating token count: {result.stderr}")


if __name__ == "__main__":
    main()

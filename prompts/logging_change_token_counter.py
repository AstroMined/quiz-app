import os
import subprocess

# Path to your project directory
project_directory = '/code/quiz-app/backend'

# List to store logging statements
logging_statements = []

# Traverse the directory and collect logging statements
for root, dirs, files in os.walk(project_directory):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    if 'logger.' in line:
                        logging_statements.append(line.strip())

# Create a temporary file to store logging statements
temp_file_path = '/code/quiz-app/prompts/temp_logging_statements.txt'
with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
    temp_file.write('\n'.join(logging_statements))

# Use the external command line utility to count tokens
result = subprocess.run(['token-count', '--file', temp_file_path,
                         '--model_name', 'gpt-4'], capture_output=True, text=True, check=True)

if result.returncode == 0:
    print(f"Token count for logging statements: {result.stdout.strip()}")
else:
    print(f"Error calculating token count: {result.stderr}")

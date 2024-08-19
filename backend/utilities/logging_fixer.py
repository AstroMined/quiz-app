import os
import re


def replace_fstring_with_percent_format(line):
    # Match lines that include a logging statement with f-string
    pattern = r'(\s*)logger\.(\w+)\(f"(.*?)"\)'
    match = re.search(pattern, line)
    if match:
        indent = match.group(1)
        level = match.group(2)
        fstring_content = match.group(3)

        # Extract variable names within {}
        variables = re.findall(r'{(.*?)}', fstring_content)
        percent_format_string = re.sub(r'{(.*?)}', r'%s', fstring_content)
        
        # Join the variables to be used as arguments in logging
        variables_string = ', '.join(variables)

        new_line = f'{indent}logger.{level}("{percent_format_string}", {variables_string})\n'
        return new_line
    return line

def process_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    with open(filepath, 'w') as file:
        for line in lines:
            new_line = replace_fstring_with_percent_format(line)
            file.write(new_line)

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))

# Example usage: process the directory containing your Python files
process_directory('tests')

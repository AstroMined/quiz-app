import os
import importlib.util

def find_broken_imports(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('import') or line.startswith('from'):
                            module_name = line.split()[1]
                            if '.' in module_name:
                                module_name = module_name.split('.')[0]
                            try:
                                spec = importlib.util.find_spec(module_name)
                                if spec is None:
                                    print(f"Broken import in {filepath}: {line.strip()}")
                            except ModuleNotFoundError:
                                print(f"Broken import in {filepath}: {line.strip()}")

find_broken_imports('/code/quiz/quiz-app-backend/app')

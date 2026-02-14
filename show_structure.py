import os

# ===== ADD ALL FOLDERS/FILES YOU WANT TO SKIP =====
IGNORE_DIRS = {
    '__pycache__',
    '.git',
    'venv',
    'env',
    '.venv',
    '.env',
    'node_modules',
    '.idea',
    '.vscode',
    '.mypy_cache',
    '.pytest_cache',
    'staticfiles',
    '.tox',
}

IGNORE_FILES = {
    '.pyc',
    '.pyo',
    '.sqlite3',
    '.db',
    '.DS_Store',
    'Thumbs.db',
    '.env',
}

IGNORE_EXACT_FILES = {
    'db.sqlite3',
    '.gitignore',
    'show_structure.py',
    'project_structure.txt',
}

def should_ignore_file(filename):
    if filename in IGNORE_EXACT_FILES:
        return True
    for ext in IGNORE_FILES:
        if filename.endswith(ext):
            return True
    return False

def show_tree(path='.', prefix=''):
    entries = sorted(os.listdir(path))
    
    # Filter out ignored directories and files
    dirs = [e for e in entries 
            if os.path.isdir(os.path.join(path, e)) and e not in IGNORE_DIRS]
    files = [e for e in entries 
             if os.path.isfile(os.path.join(path, e)) and not should_ignore_file(e)]
    
    all_items = files + dirs
    
    for i, item in enumerate(all_items):
        is_last = (i == len(all_items) - 1)
        connector = '└── ' if is_last else '├── '
        
        if item in dirs:
            print(f"{prefix}{connector}{item}/")
            new_prefix = prefix + ('    ' if is_last else '│   ')
            show_tree(os.path.join(path, item), new_prefix)
        else:
            print(f"{prefix}{connector}{item}")

if __name__ == '__main__':
    project_name = os.path.basename(os.path.abspath('.'))
    print(f"{project_name}/")
    show_tree('.')
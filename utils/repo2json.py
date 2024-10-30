import os
import json 

def collect_files(repo_path, extensions):
    """ Recursively collect all files with specified extensions in the repository """
    files = []
    for root, _, filenames in os.walk(repo_path):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files

def read_file_content(filepath):
    """ Read the content of a file """
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def create_json_entry(filepath, repo_name, language):
    """ Create a JSON entry for a file """
    content = read_file_content(filepath)
    return {
        "repo_name": repo_name,
        "file_path": filepath,
        "language": language,
        "content": content
    }

def save_to_json(data, output_file):
    """ Save the data to a JSON file """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def repo_to_json(repo_path, repo_name, extensions, output_file):
    """ Preprocess a repository and save the data to a JSON file """
    files = collect_files(repo_path, extensions)
    data = []
    for file in files:
        language = file.split('.')[-1]
        entry = create_json_entry(file, repo_name, language)
        data.append(entry)
    save_to_json(data, output_file)

if __name__ == '__main__':
    repo_path = 'data/repo'
    repo_name = 'repo'
    extensions = ['.py', '.java']
    output_file = 'data/repo.json'
    repo_to_json(repo_path, repo_name, extensions, output_file)
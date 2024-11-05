import os
import json 
import random 

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

def repo_to_json(repo_path, repo_name, extensions, output_file=None):
    """ Preprocess a repository and save the data to a JSON file """
    files = collect_files(repo_path, extensions)
    print(f"Found {len(files)} files in {repo_name}")
    data = []
    for file in files:
        language = file.split('.')[-1]
        entry = create_json_entry(file, repo_name, language)
        data.append(entry)
    if output_file:
        save_to_json(data, output_file)
    return data

def all_repos_to_json(repos, output_file, setting=2):
    """ Preprocess all repositories and save the data to JSON files """
    data = []
    for repo in repos:
        repo_path = repo['path']
        repo_name = repo['name']
        extensions = repo['extensions']
        print(f"Processing {repo_name} at {repo_path}")
        repo_data = repo_to_json(repo_path, repo_name, extensions)
        print(f"Processed {repo_name} with {len(repo_data)} files")
        if setting == 3:
            # Organize files reversely topologically
            from depana import get_dependency_graph
            import networkx as nx
            graph_py = get_dependency_graph(repo_path, 'python')
            graph_java = get_dependency_graph(repo_path, 'java')
            graph = nx.compose(graph_py, graph_java)
            # Eliminate cycles
            graph.remove_edges_from(nx.selfloop_edges(graph))
            sorted_files = list(nx.topological_sort(graph))
            def cmp(file):
                try:
                    return -sorted_files.index(file['file_path'])
                except ValueError:
                    return len(sorted_files)
            repo_data = sorted(repo_data, key=cmp)
        elif setting == 2:
            random.shuffle(repo_data)
        data.extend(repo_data)
    
    if setting == 1:
        random.shuffle(data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return data

if __name__ == '__main__':
    repos = [
        {
            "name": "tornado",
            "path": "D:\\cxsj\\tornado\\tornado",
            "extensions": [".py"]
        }
    ]
    all_repos_to_json(repos, "test.json", setting=2)
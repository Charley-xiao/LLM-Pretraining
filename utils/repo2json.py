import os
import json 
import random 
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import sys
import time 
from concurrent.futures import ProcessPoolExecutor
import networkx as nx

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
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    except Exception as e:
        print('!' * 80)
        print(f"UnicodeDecodeError in file {filepath}: {e}")
        return ""  # Return empty string or handle the error as needed

def create_json_entry(filepath, repo_name, language):
    """ Create a JSON entry for a file """
    content = read_file_content(filepath)
    if random.random() < 0.5:
        full_context = f"<repo_name>{repo_name}<file_sep>{filepath}\n{content}<|endoftext|>"
    else:
        full_context = f"{content}<|endoftext|>"
    return {
        "repo_name": repo_name,
        "file_path": filepath,
        "language": language,
        "content": full_context
    }

def save_to_json(data, output_file):
    """ Save the data to a JSON file """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def process_file(file, repo_name):
    language = file.split('.')[-1]
    entry = create_json_entry(file, repo_name, language)
    return entry

def repo_to_json(repo_path, repo_name, extensions, output_file=None, num_cpus=None):
    """ Preprocess a repository and save the data to a JSON file """
    files = collect_files(repo_path, extensions)
    print(f"Found {len(files)} files in {repo_name}")

    data = []
    max_workers = num_cpus or os.cpu_count() 

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_file, file, repo_name): file for file in files}
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                entry = future.result()
                data.append(entry)
            except Exception as exc:
                print(f"{file} generated an exception: {exc}")

    if output_file:
        save_to_json(data, output_file)
    return data

def all_repos_to_json(repos, output_file, setting=2, num_cpus=None):
    """
    Preprocess all repositories and save the data to JSON files
    """
    # 创建一个与repos长度相同的结果列表，初始化为None
    data = [None] * len(repos)

    with ProcessPoolExecutor(max_workers=num_cpus) as executor:
        # 提交任务时传入索引
        futures = [executor.submit(process_repo, i, repo, setting, num_cpus) for i, repo in enumerate(repos)]
        
        # 按原始顺序收集结果
        for future in as_completed(futures):
            try:
                index, repo_data = future.result()
                data[index] = repo_data
            except Exception as e:
                print(e)
                sys.exit(0)

    # 展平结果列表
    data = [item for sublist in data for item in sublist]

    if setting == 1:
        random.shuffle(data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return data

def process_repo(index, repo, setting=3, num_cpus=None):
    repo_path = repo['path']
    repo_name = repo['name']
    extensions = repo['extensions']
    print(f"Processing {repo_name} at {repo_path}")
    repo_data = repo_to_json(repo_path, repo_name, extensions, num_cpus=num_cpus)
    print(f"Processed {repo_name} with {len(repo_data)} files")
    
    if setting == 3:
        print(f"Organizing files in {repo_name} topologically")
        from .depana import get_dependency_graph, visualize_graph
        
        cache_path = f"data/dependency_graph_{repo_name}.pkl"

        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                graph = pickle.load(f)
            print(f"Loaded dependency graph from cache for {repo_name}")
        else:
            start_time = time.time()
            graph_py = get_dependency_graph(repo_path, 'python')
            print(f"Python graph for {repo_name} built in {time.time() - start_time:.2f} seconds")
            start_time = time.time()
            graph_java = get_dependency_graph(repo_path, 'java')
            print(f"Java graph for {repo_name} built in {time.time() - start_time:.2f} seconds")
            graph = nx.compose(graph_py, graph_java)
            print(f"Combined graph for {repo_name} built")
            with open(cache_path, 'wb') as f:
                pickle.dump(graph, f)

        # print(f"Visualizing dependency graph for {repo_name}")
        # visualize_graph(graph, save_path=f"data/graph_{repo_name}.png")

        graph.remove_edges_from(nx.selfloop_edges(graph))
        cycles = list(nx.simple_cycles(graph))

        for cycle in cycles:
            if len(cycle) > 1:
                for i in range(len(cycle) - 1):
                    try:
                        graph.remove_edge(cycle[i], cycle[i + 1])
                    except nx.NetworkXError:
                        pass
                try:
                    graph.remove_edge(cycle[-1], cycle[0])
                except nx.NetworkXError:
                    pass
        sorted_files = list(nx.topological_sort(graph))

        def cmp(file):
            try:
                return -sorted_files.index(file['file_path'])
            except ValueError:
                return len(sorted_files)
        repo_data = sorted(repo_data, key=cmp)
        # visualize_graph(graph, save_path=f"data/graph_{repo_name}_final.png")

    elif setting == 2:
        random.shuffle(repo_data)
    
    return index, repo_data

if __name__ == '__main__':
    repos = [
        {
            "name": "tornado",
            "path": "D:\\cxsj\\tornado\\tornado",
            "extensions": [".py"]
        }
    ]
    all_repos_to_json(repos, "test.json", setting=2)

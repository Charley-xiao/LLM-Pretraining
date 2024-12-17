import logging
import os
import json
import random
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import networkx as nx
from networkx.algorithms.cycles import simple_cycles

# 设置logging输出文件，设置输出格式
logging.basicConfig(level=logging.INFO, filename='repo2json.log', filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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

# def repo_to_json(repo_path, repo_name, extensions, output_file=None, num_workers=None):
#     """ Preprocess a repository and save the data to a JSON file """
#     files = collect_files(repo_path, extensions)
#     print(f"Found {len(files)} files in {repo_name}")
#
#     data = []
#     max_workers = num_workers if num_workers else os.cpu_count()
#
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         future_to_file = {executor.submit(process_file, file, repo_name): file for file in files}
#         for future in as_completed(future_to_file):
#             file = future_to_file[future]
#             try:
#                 entry = future.result()
#                 data.append(entry)
#             except Exception as exc:
#                 print(f"{file} generated an exception: {exc}")
#
#     if output_file:
#         save_to_json(data, output_file)
#     return data

def repo_to_json(repo_path, repo_name, extensions, output_file=None, num_workers=None):
    """ Preprocess a repository and save the data to a JSON file """
    import os

    files = collect_files(repo_path, extensions)
    print(f"Found {len(files)} files in {repo_name}")

    data = []

    for file in files:
        try:
            entry = process_file(file, repo_name)
            data.append(entry)
        except Exception as exc:
            print(f"{file} generated an exception: {exc}")

    if output_file:
        save_to_json(data, output_file)
    return data

# def all_repos_to_json(repos, output_file, setting=2, num_cpus=None, num_workers=None):
#     """
#     Preprocess all repositories and save the data to JSON files
#     """
#     # 创建一个与repos长度相同的结果列表，初始化为None
#     data = [None] * len(repos)
#
#     with ProcessPoolExecutor(max_workers=num_cpus) as executor:
#         # 提交任务时传入索引
#         futures = [executor.submit(process_repo, i, repo, setting, num_workers) for i, repo in enumerate(repos)]
#
#         # 按原始顺序收集结果
#         for future in as_completed(futures):
#             try:
#                 # 增加超时处理，2分钟超时
#                 index, repo_data = future.result(timeout=120)
#                 data[index] = repo_data
#             except TimeoutException:
#                 logging.warning(f"Timeout for repo {index}")
#                 data[index] = []
#             except Exception as e:
#                 logging.error(f"Error processing repo {index}: {e}")
#                 data[index] = []
#
#     # 展平结果列表
#     data = [item for sublist in data for item in sublist]
#
#     if setting == 1:
#         random.shuffle(data)
#
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=4)
#     return data

def all_repos_to_json(repos, output_file, setting=2, num_cpus=None, num_workers=None):
    """
    Preprocess all repositories and save the data to JSON files
    """
    # 创建一个结果列表
    data = []

    for index, repo in enumerate(repos):
        try:
            index, repo_data = process_repo(index, repo, setting, num_workers)
            data.extend(repo_data)
        except TimeoutException:
            logging.warning(f"Timeout for repo {index}")
        except Exception as e:
            logging.error(f"Error processing repo {index}: {e}")

    if setting == 1:
        random.shuffle(data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return data

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Timed out!")

# def process_repo(index, repo, setting=3, num_workers=1):
#     repo_path = repo['path']
#     repo_name = repo['name']
#     extensions = repo['extensions']
#     try:
#         print(f"Processing {repo_name} at {repo_path}")
#         repo_data = repo_to_json(repo_path, repo_name, extensions, num_workers=num_workers)
#         print(f"Processed {repo_name} with {len(repo_data)} files")
#
#         if setting == 3:
#             print(f"Organizing files in {repo_name} topologically")
#             from .depana import get_dependency_graph, visualize_graph
#
#             cache_path = f"data/dependency_graph_{repo_name}.pkl"
#
#             if os.path.exists(cache_path):
#                 with open(cache_path, 'rb') as f:
#                     graph = pickle.load(f)
#                 print(f"Loaded dependency graph from cache for {repo_name}")
#             else:
#                 start_time = time.time()
#                 graph_py = get_dependency_graph(repo_path, 'python', num_workers=num_workers)
#                 print(f"Python graph for {repo_name} built in {time.time() - start_time:.2f} seconds")
#                 print(f"number of nodes: {len(graph_py.nodes)}")
#                 print(f"number of edges: {len(graph_py.edges)}")
#                 start_time = time.time()
#                 graph_java = get_dependency_graph(repo_path, 'java', num_workers=num_workers)
#                 print(f"Java graph for {repo_name} built in {time.time() - start_time:.2f} seconds")
#                 print(f"number of nodes: {len(graph_java.nodes)}")
#                 print(f"number of edges: {len(graph_java.edges)}")
#                 graph = nx.compose(graph_py, graph_java)
#                 print(f"Combined graph for {repo_name} built")
#                 with open(cache_path, 'wb') as f:
#                     pickle.dump(graph, f)
#
#             # print(f"Visualizing dependency graph for {repo_name}")
#             # visualize_graph(graph, save_path=f"data/graph_{repo_name}.png")
#
#             graph.remove_edges_from(nx.selfloop_edges(graph))
#             cycles = list(nx.simple_cycles(graph))
#
#             # # 如果cycles的数量过多，说明有问题，直接返回
#             # if len(cycles) > 100:
#             #     return index, []
#
#             logging.warning(f"Found {len(cycles)} cycles in {repo_name}")
#             for cycle in cycles:
#                 if len(cycle) > 1:
#                     for i in range(len(cycle) - 1):
#                         try:
#                             graph.remove_edge(cycle[i], cycle[i + 1])
#                         except nx.NetworkXError:
#                             pass
#                     try:
#                         graph.remove_edge(cycle[-1], cycle[0])
#                     except nx.NetworkXError:
#                         pass
#             sorted_files = list(nx.topological_sort(graph))
#
#             def cmp(file):
#                 try:
#                     return -sorted_files.index(file['file_path'])
#                 except ValueError:
#                     return len(sorted_files)
#             repo_data = sorted(repo_data, key=cmp)
#             # visualize_graph(graph, save_path=f"data/graph_{repo_name}_final.png")
#
#         elif setting == 2:
#             random.shuffle(repo_data)
#
#         sys.stdout.flush()
#
#         return index, repo_data
#     except TimeoutException:
#         print(f"Timeout for {repo_name}")
#         return index, []


def process_repo(index, repo, setting=3, num_workers=1):
    import signal

    def handler(signum, frame):
        raise TimeoutError()

    signal.signal(signal.SIGALRM, handler)
    time_limit = 3600  # 设置时间限制为1小时
    signal.alarm(time_limit)

    repo_path = repo['path']
    repo_name = repo['name']
    extensions = repo['extensions']
    try:
        print(f"Processing {repo_name} at {repo_path}")
        repo_data = repo_to_json(repo_path, repo_name, extensions, num_workers=num_workers)
        # 备份repo_data
        repo_data_bak = repo_data.copy()
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
                graph_py = get_dependency_graph(repo_path, 'python', num_workers=num_workers)
                print(f"Python graph for {repo_name} built in {time.time() - start_time:.2f} seconds")
                print(f"number of nodes: {len(graph_py.nodes)}")
                print(f"number of edges: {len(graph_py.edges)}")
                start_time = time.time()
                graph_java = get_dependency_graph(repo_path, 'java', num_workers=num_workers)
                print(f"Java graph for {repo_name} built in {time.time() - start_time:.2f} seconds")
                print(f"number of nodes: {len(graph_java.nodes)}")
                print(f"number of edges: {len(graph_java.edges)}")
                graph = nx.compose(graph_py, graph_java)
                print(f"Combined graph for {repo_name} built")
                with open(cache_path, 'wb') as f:
                    pickle.dump(graph, f)

            graph.remove_edges_from(nx.selfloop_edges(graph))
            cycles = list(nx.simple_cycles(graph))

            logging.warning(f"Found {len(cycles)} cycles in {repo_name}")
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

        elif setting == 2:
            random.shuffle(repo_data)

        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Processed {repo_name} with {len(repo_data)} files")
        sys.stdout.flush()

        return index, repo_data
    except TimeoutError:
        print(f"Timeout for {repo_name}")
        # 使用setting=2的方式处理并返回
        random.shuffle(repo_data_bak)
        return index, repo_data_bak
    finally:
        signal.alarm(0)  # 取消闹钟

if __name__ == '__main__':
    repos = [
        {
            "name": "tornado",
            "path": "D:\\cxsj\\tornado\\tornado",
            "extensions": [".py"]
        }
    ]
    all_repos_to_json(repos, "test.json", setting=2)

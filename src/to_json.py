import os
import json
import random


def extract_python_files(repo_dir, repo_name):
    """遍历指定目录，提取所有Python文件的内容和路径信息。"""
    python_files = []

    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 记录文件信息
                python_files.append({
                    "file_name": file,
                    "file_path": os.path.relpath(file_path, repo_dir),  # 相对路径
                    "content": content,
                    "repository": repo_name
                })

    return python_files


def save_to_json(data, output_file):
    """将数据保存为JSON文件。"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# 1. No-context: 将所有仓库的代码片段打乱并输出到一个 JSON 文件
def no_context_json(data):
    snippets = []
    for file_data in data:
        content_lines = file_data["content"].splitlines()
        snippets.extend(content_lines)

    # 打乱所有代码片段
    random.shuffle(snippets)
    return [{"snippet": snippet} for snippet in snippets]


# 2. File-context: 所有代码按文件内部顺序排列，但文件打乱，不保留仓库层级
def file_context_json(all_data):
    all_files = []
    for repo_data in all_data:
        all_files.extend(repo_data)  # 将所有仓库文件收集到一起

    random.shuffle(all_files)  # 打乱文件顺序，但保留文件内部代码的顺序
    return [
        {
            "file_name": file_data["file_name"],
            "content": file_data["content"].splitlines()
        }
        for file_data in all_files
    ]


# 3. Repository-context: 每个仓库单独生成一个 JSON 文件，仓库内的文件顺序打乱
def repository_context_json(repo_data, repo_name):
    random.shuffle(repo_data)  # 打乱仓库内部文件顺序
    return [
        {
            "file_path": file_data["file_path"],
            "content": file_data["content"].splitlines()
        }
        for file_data in repo_data
    ]


# 主函数：遍历各个仓库并生成不同上下文的 JSON 文件
def main():
    base_dir = "C:/Users/ZS/PycharmProjects/LLM-Pretraining-main/test_Repositories"
    raw_repo_dir = os.path.join(base_dir, "raw_repo")  # 原始仓库目录
    json_files_dir = os.path.join(base_dir, "json_files")  # JSON文件目录

    # 创建三个不同上下文的输出路径
    no_context_dir = os.path.join(json_files_dir, "no_context_json")
    file_context_dir = os.path.join(json_files_dir, "file_context_json")
    repo_context_dir = os.path.join(json_files_dir, "repository_context_json")
    os.makedirs(no_context_dir, exist_ok=True)
    os.makedirs(file_context_dir, exist_ok=True)
    os.makedirs(repo_context_dir, exist_ok=True)

    all_repos_data = []  # 用于保存所有仓库数据

    # 遍历raw_repo目录下的各个仓库
    for repo_name in os.listdir(raw_repo_dir):
        repo_dir = os.path.join(raw_repo_dir, repo_name)

        # 检查是否为文件夹，确保只处理仓库目录
        if os.path.isdir(repo_dir):
            python_files = extract_python_files(repo_dir, repo_name)
            all_repos_data.append(python_files)  # 将仓库数据加入总集合

            # 生成Repository-context JSON
            repo_context_data = repository_context_json(python_files, repo_name)
            repo_context_file = os.path.join(repo_context_dir, f"{repo_name}_repository_context.json")
            save_to_json(repo_context_data, repo_context_file)
            print(f"Saved Repository-context JSON for {repo_name} to {repo_context_file}")

    # 生成No-context JSON
    no_context_data = no_context_json([file for repo_data in all_repos_data for file in repo_data])
    no_context_file = os.path.join(no_context_dir, "all_repos_no_context.json")
    save_to_json(no_context_data, no_context_file)
    print(f"Saved No-context JSON to {no_context_file}")

    # 生成File-context JSON
    file_context_data = file_context_json(all_repos_data)
    file_context_file = os.path.join(file_context_dir, "all_repos_file_context.json")
    save_to_json(file_context_data, file_context_file)
    print(f"Saved File-context JSON to {file_context_file}")


# 运行脚本
if __name__ == "__main__":
    main()

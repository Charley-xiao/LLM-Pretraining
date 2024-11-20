import pandas as pd
import requests
import xml.etree.ElementTree as ET
from collections import Counter
import csv
import time

# 添加 GitHub Token
GITHUB_TOKEN = "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"  # 替换为你的 GitHub Token
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


# 获取默认分支
def get_default_branch(owner, repo_name):
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    try:
        response = requests.get(url, headers=HEADERS)  # 添加认证信息
        if response.status_code == 200:
            repo_info = response.json()
            return repo_info.get("default_branch", "main")  # 如果没有默认分支，返回 "main"
        else:
            print(f"Failed to fetch default branch for {owner}/{repo_name}. HTTP {response.status_code}")
            return "main"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching default branch for {owner}/{repo_name}: {e}")
        return "main"


# 下载依赖文件
def fetch_dependency_file(owner, repo_name, file_name):
    # 获取仓库的默认分支
    branch = get_default_branch(owner, repo_name)
    # 构造 URL
    url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{file_name}"
    try:
        response = requests.get(url, headers=HEADERS)  # 添加认证信息
        if response.status_code == 200:
            print(f"Successfully fetched {file_name} from {owner}/{repo_name} ({branch} branch)")
            return response.text
        elif response.status_code == 404:
            print(f"File not found: {file_name} in repository {owner}/{repo_name} ({branch} branch)")
            return None
        else:
            print(f"Failed to fetch {file_name} from {owner}/{repo_name}. HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {file_name} from {owner}/{repo_name}: {e}")
        return None


# 解析 requirements.txt 文件
def parse_requirements_file(content):
    dependencies = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):  # 忽略空行和注释
            dependencies.append(line.split("==")[0])  # 提取依赖名称，去掉版本信息
    return dependencies


# 解析 pom.xml 文件
def parse_pom_file(content):
    dependencies = []
    try:
        root = ET.fromstring(content)
        for dependency in root.findall(".//dependency"):
            group_id = dependency.find("groupId").text if dependency.find("groupId") is not None else ""
            artifact_id = dependency.find("artifactId").text if dependency.find("artifactId") is not None else ""
            dependencies.append(f"{group_id}:{artifact_id}")
    except ET.ParseError:
        print("Error parsing pom.xml content.")
    return dependencies


# 主分析逻辑
def analyze_dependencies(csv_file, output_file="dependency_analysis.csv"):
    # 读取 CSV 文件
    df = pd.read_csv(csv_file)
    dependency_counter = Counter()

    for _, row in df.iterrows():
        owner = row["owner"]
        repo_name = row["name"]
        dep_file = row["dependencies"]

        # 下载依赖文件内容
        content = fetch_dependency_file(owner, repo_name, dep_file)
        if content:
            if dep_file == "requirements.txt":
                dependencies = parse_requirements_file(content)
            elif dep_file == "pom.xml":
                dependencies = parse_pom_file(content)
            else:
                dependencies = []

            # 统计依赖项
            dependency_counter.update(dependencies)

        # 增加延时，避免触发 GitHub 的速率限制
        # time.sleep(0.01)

    # 按次数降序排列
    sorted_dependencies = dependency_counter.most_common()

    # 保存为 CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Dependency", "Count"])
        writer.writerows(sorted_dependencies)

    print(f"Dependency analysis saved to {output_file}")


# 主函数
if __name__ == "__main__":
    # 输入 CSV 文件路径
    input_csv = "repositories.csv"  # 替换为你的 CSV 文件路径
    analyze_dependencies(input_csv)

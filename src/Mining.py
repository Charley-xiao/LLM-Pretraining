import requests
import time
import csv

# 设置 GitHub API Token
GITHUB_API_TOKEN = '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'
HEADERS = {'Authorization': f'token {GITHUB_API_TOKEN}'}

# 设置语言过滤条件
LANGUAGES = ['Java', 'Python']


# 定义抓取仓库的基本函数

# def fetch_repositories(language, stars, per_page, max_pages):
#     all_repos = []
#     for page in range(1, max_pages + 1):
#         url = f'https://api.github.com/search/repositories?q=language:{language}+stars:>={stars}&sort=stars&order=desc&page={page}&per_page={per_page}'
#         response = requests.get(url, headers=HEADERS)
#
#         if response.status_code == 200:
#             repos = response.json()['items']
#             all_repos.extend(repos)
#         else:
#             print(f"Error fetching repositories: {response.status_code}")
#             break
#
#         # 防止触发 API 限制
#         time.sleep(2)
#
#     return all_repos

def fetch_repositories(language, stars=100, per_page=50, max_pages=1, page=1):
    url = f'https://api.github.com/search/repositories?q=language:{language}+stars:>={stars}&sort=stars&order=desc&page={page}&per_page={per_page}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"Error fetching repositories for {language}, page {page}: {response.status_code}")
        return []



# 获取仓库的依赖
def fetch_dependencies(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/contents'
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        files = response.json()
        # 检查文件中是否有关于依赖的文件（例如 pom.xml 或 requirements.txt）
        dependencies = []
        for file in files:
            if file['name'] == 'pom.xml' or file['name'] == 'requirements.txt':
                dependencies.append(file['name'])
        return dependencies
    else:
        print(f"Error fetching dependencies for {owner}/{repo}: {response.status_code}")
        return []


# def main():
#     all_repositories = []
#     max_repositories = 200  # 设置最大爬取仓库数量
#     stars = 100
#     per_page = 100
#     max_pages = 10
#
#     for language in LANGUAGES:
#         print(f"Fetching {language} repositories...")
#         repos = fetch_repositories(language, stars, per_page, max_pages)
#
#         for repo in repos:
#             if len(all_repositories) >= max_repositories:
#                 break  # 达到最大数量时停止爬取
#
#             owner = repo['owner']['login']
#             repo_name = repo['name']
#             print(f"Repository: {repo_name}, Owner: {owner}")
#
#             # 获取仓库依赖信息
#             dependencies = fetch_dependencies(owner, repo_name)
#             if not dependencies:  # 如果没有依赖文件，跳过这个仓库
#                 print(f"Skipping {repo_name} due to missing dependencies.")
#                 continue
#
#             print(f"Found dependencies in {repo_name}: {dependencies}")
#
#             all_repositories.append({
#                 'name': repo_name,
#                 'owner': owner,
#                 'dependencies': dependencies
#             })
#
#             # 为了不触发 GitHub API 限制，添加延时
#             time.sleep(1)
#
#         if len(all_repositories) >= max_repositories:
#             break  # 达到最大数量时停止爬取
#
#     return all_repositories


def main():
    all_repositories = []
    max_repositories = 1000  # 设置最大爬取仓库数量
    stars = 100
    per_page = 50  # 每次爬取50个仓库
    max_pages = 10  # 每种语言最多爬取10页
    language_index = 0  # 用于交替语言
    current_page = {lang: 1 for lang in LANGUAGES}  # 每种语言的当前页数

    while len(all_repositories) < max_repositories:
        # 交替选择语言
        current_language = LANGUAGES[language_index]
        page = current_page[current_language]
        print(f"Fetching {current_language} repositories (Page {page})...")

        # 爬取当前语言的仓库
        repos = fetch_repositories(current_language, stars, per_page, max_pages=1, page=page)

        # 处理仓库数据
        for repo in repos:
            if len(all_repositories) >= max_repositories:
                break  # 达到最大数量时停止爬取

            owner = repo['owner']['login']
            repo_name = repo['name']
            print(f"Repository: {repo_name}, Owner: {owner}")

            # 获取仓库依赖信息
            dependencies = fetch_dependencies(owner, repo_name)
            if not dependencies:  # 如果没有依赖文件，跳过这个仓库
                print(f"Skipping {repo_name} due to missing dependencies.")
                continue

            print(f"Found dependencies in {repo_name}: {dependencies}")

            # 保存仓库信息
            all_repositories.append({
                'name': repo_name,
                'owner': owner,
                'dependencies': dependencies
            })

            # 延时以避免触发 API 限制
            time.sleep(1)

        # 切换到下一个语言
        language_index = (language_index + 1) % len(LANGUAGES)

        # 增加当前语言的页数
        current_page[current_language] += 1

        # 如果所有语言的页数都超过 max_pages，则停止
        if all(page > max_pages for page in current_page.values()):
            print("Reached max pages for all languages.")
            break

    return all_repositories



def save_to_csv(repositories, filename="repositories.csv"):
    # 定义 CSV 的字段名
    fieldnames = ['name', 'owner', 'dependencies']

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # 写入 CSV 文件的表头
        writer.writeheader()

        # 写入抓取到的仓库数据
        for repo in repositories:
            writer.writerow({
                'name': repo['name'],
                'owner': repo['owner'],
                'dependencies': ', '.join(repo['dependencies'])  # 将依赖项列表转换为逗号分隔的字符串
            })
            print(f"{repo['name']} saved to {filename}")


if __name__ == "__main__":
    start_time = time.time()
    repositories = main()
    save_to_csv(repositories)
    print(f"Total repositories fetched: {len(repositories)}")
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time}")

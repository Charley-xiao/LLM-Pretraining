import requests
import json 
import os
import sys
import time 
import random 
import networkx as nx
from bs4 import BeautifulSoup

def invalid_description(description):
    if description is None:
        return True
    blacklisted = ['mirror', 'fork', 'test', 'example', 'assignment', 'homework',
                   'tutorial', 'course', 'workshop', 'bootcamp', 'practice', 'solution',
                   'interview', 'coding', 'challenge', 'template', 'study', 'education',
                   '教程', '学习', '教育', '课程', '练习', '解决方案', '挑战', '作业', '测试', '示例',
                    '教學', '學習', '教育', '課程', '練習', '解決方案', '挑戰', '作業', '測試', '示例',
                    'チュートリアル', '学習', '教育', 'コース', '演習', '解決', 'チャレンジ', '課題', 'テスト', '例',
                    '튜토리얼', '학습', '교육', '코스', '연습', '해결', '도전', '과제', '테스트', '예제']
    whitelisted = ['机器学习']
    for word in blacklisted:
        if word in description.lower() and all(w not in description.lower() for w in whitelisted):
            return True
        
    return False

def get_download(package_name):
    url = f'https://pypi.org/project/{package_name}/#files'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        father = soup.find('div', class_='card file__card')
        if father is None:
            print(f"Cannot find download URL for {package_name}")
            return None
        download_url = father.find('a')['href']
        print(f"Download URL for {package_name}: {download_url}")
        return download_url
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {package_name}: {e}")
        return None

def get_top_repos(top_k, repos_dir, source='github', language=None):
    """
    Get the top k repositories.

    Args:
        top_k (int): Number of top repositories to get
        repos_dir (str): Directory to save the repositories
        source (str): Source to get the repositories from (github, pypi, etc.)
        language (str): Language of the repositories to get

    Returns:
        list[dict]: List of repositories, each being a dictionary with keys 'name', 'url', 'path', 'extensions'
    """
    if language is None:
        language = 'python'

    language2ext = {
        'python': '.py',
        'java': '.java'
    }

    if source == 'github':
        url = 'https://api.github.com/search/repositories'
        query = 'stars:>1000'
        sort = 'stars'
        page = 1
        repos = []
        while len(repos) < top_k:
            try:
                response = requests.get(f'{url}?q={query}+language:{language}&sort={sort}&page={page}')
                response.raise_for_status()
                data = response.json()
                print(f'Fetched {len(data["items"])} repositories from page {page}')
                for item in data['items']:
                    repo_name = item['name']
                    repo_url = item['html_url']
                    repo_path = os.path.join(repos_dir, repo_name)
                    if (not item['has_issues']) or item['size'] <= 100000 or invalid_description(item['description']):
                        print(f"Skipping {repo_name} due to invalid description or size")
                        continue
                    print(f"Adding {repo_name} to the list")
                    repos.append({
                        "name": repo_name,
                        "url": repo_url,
                        "path": repo_path,
                        "extensions": [language2ext[language]]
                    })
                    if len(repos) == top_k:
                        break
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch repositories: {e}")
                break
            page += 1

        return repos
    elif source == 'pypi':
        pypi_top_packages = 'https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json'
        response = requests.get(pypi_top_packages)
        response.raise_for_status()
        data = response.json()['rows']
        top_packages = sorted(data, key=lambda x: x['download_count'], reverse=True)[:top_k]
        repos = []
        for package in top_packages:
            package_name = package['project']
            package_url = get_download(package_name)
            package_path = os.path.join(repos_dir, package_name)
            print(f"Adding {package_name} to the list")
            repos.append({
                "name": package_name,
                "url": package_url,
                "path": package_path,
                "extensions": [language2ext[language]]
            })
        return repos
    else:
        raise ValueError(f"Unknown source: {source}")
import json
import numpy as np
from transformers import GPT2Tokenizer
import mmap
import os
import random
import yaml 
import sys

CONFIG_FILE = "cfg/preprocess.yaml"
with open(CONFIG_FILE, 'r') as file:
    config = yaml.safe_load(file)

tokenizer = GPT2Tokenizer.from_pretrained(config['tokenizer'])
tokenizer.pad_token = tokenizer.eos_token

from utils import all_repos_to_json

if not config['use_cache']:
    repos_dict = []
    for repo in config['repos']:
        repo_url = repo['url']
        repo_path = repo['path']
        repo_name = repo['name']
        extensions = repo['extensions']
        if not os.path.exists(os.path.join(config['repos_dir'], f"{repo_path}.json")):
            print(f"Repo {repo_name} not found in {config['repos_dir']}. Downloading from {repo_url}")
            os.system(f"git clone {repo_url} {config['repos_dir']}")

        repos_dict.append({
            "name": repo_name,
            "path": os.path.join(config['repos_dir'], repo_path),
            "extensions": extensions
        })

    all_repos_to_json(repos_dict, config['data_file'], setting=config['setting'])

    with open(config['output_file'], 'r') as file:
        data = json.load(file)
else:
    with open(config['data_file'], 'r') as file:
        data = json.load(file)

tokenized_data = []
for item in data:
    repo_name = item['repo_name']
    file_path = item['file_path']
    content = item['content']
    
    if random.random() < 0.5:
        full_context = f"<repo_name>{repo_name}<file_sep>{file_path}\n{content}<|endoftext|>"
    else:
        full_context = f"{content}<|endoftext|>"

    tokens = tokenizer.encode(full_context, 
                              add_special_tokens=True, 
                              truncation=config['truncation'],
                              max_length=config['max_length'], 
                              padding='max_length')
    tokenized_data.append(tokens)

np.save(config['output_tokenized'], tokenized_data)

flat_data = np.array([token for tokens in tokenized_data for token in tokens], dtype=np.int32)
num_bytes = flat_data.nbytes

with open(config['output_mmap'], 'wb') as f:
    f.seek(num_bytes - 1)
    f.write(b'\x00')
    with mmap.mmap(f.fileno(), num_bytes, access=mmap.ACCESS_WRITE) as mm:
        mm[:] = flat_data.tobytes() 

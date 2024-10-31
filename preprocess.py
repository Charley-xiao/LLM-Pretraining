import json
import numpy as np
from transformers import AutoTokenizer
import os
import random
import yaml
import sys
from utils import all_repos_to_json
import multiprocessing

CONFIG_FILE = "cfg/preprocess.yaml"

def init_worker(_config):
    global tokenizer
    tokenizer = AutoTokenizer.from_pretrained(_config['tokenizer'], use_fast=True)
    tokenizer.pad_token = tokenizer.eos_token
    global config
    config = _config

def tokenize_item(item):
    repo_name = item['repo_name']
    file_path = item['file_path']
    content = item['content']
    
    if random.random() < 0.5:
        full_context = f"<repo_name>{repo_name}<file_sep>{file_path}\n{content}<|endoftext|>"
    else:
        full_context = f"{content}<|endoftext|>"

    tokens = tokenizer.encode(
        full_context,
        add_special_tokens=True,
        truncation=config['truncation'],
        max_length=config['max_length'],
        padding='max_length'
    )
    return tokens

def visualize_tokenization(data, tokenized_data, samples=1):
    """Visualize tokenization results for a few samples."""
    for _ in range(samples):
        idx = random.randint(0, len(data) - 1)
        item = data[idx]
        tokens = tokenized_data[idx]

        repo_name = item['repo_name']
        file_path = item['file_path']
        content = item['content']

        if random.random() < 0.5:
            full_context = f"<repo_name>{repo_name}<file_sep>{file_path}\n{content}<|endoftext|>"
        else:
            full_context = f"{content}<|endoftext|>"

        with open(CONFIG_FILE, 'r') as file:
            config = yaml.safe_load(file)

        tokenizer = AutoTokenizer.from_pretrained(config['tokenizer'], use_fast=True)
        tokenizer.pad_token = tokenizer.eos_token

        decoded_tokens = tokenizer.convert_ids_to_tokens(tokens)
        decoded_text = tokenizer.decode(tokens)

        print("\nOriginal Text:")
        print(full_context)
        print("\nToken IDs:")
        print(tokens)
        print("\nDecoded Tokens:")
        print(decoded_tokens)
        print("\nReconstructed Text from Tokens:")
        print(decoded_text)
        print("=" * 80)

def main():
    with open(CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)

    if not config['use_cache']:
        repos_dict = []
        for _repo in config['repos']:
            repo = _repo[list(_repo.keys())[0]]
            repo_url = repo['url']
            repo_path = repo['path']
            repo_name = repo['name']
            extensions = repo['extensions']
            if not os.path.exists(os.path.join(config['repos_dir'], f"{repo_path}")):
                print(f"Repo {repo_name} not found in {config['repos_dir']}. Downloading from {repo_url}")
                os.system(f"git clone {repo_url} {os.path.join(config['repos_dir'], repo_name)}")

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

    num_workers = config.get('num_workers', os.cpu_count())

    pool = multiprocessing.Pool(
        processes=num_workers,
        initializer=init_worker,
        initargs=(config,)
    )
    tokenized_data = pool.map(tokenize_item, data)
    pool.close()
    pool.join()

    np.save(config['output_tokenized'], tokenized_data)

    flat_data = np.array([token for tokens in tokenized_data for token in tokens], dtype=np.int32)

    mmapped_file = np.memmap(
        config['output_mmap'],
        dtype=np.int32,
        mode='w+',
        shape=flat_data.shape
    )
    mmapped_file[:] = flat_data[:]
    del mmapped_file

    print(f"Data saved to {config['output_tokenized']} and {config['output_mmap']}")

    visualize_tokenization(data, tokenized_data)

if __name__ == '__main__':
    main()

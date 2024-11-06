import json
import numpy as np
from transformers import AutoTokenizer
import os
import random
import yaml
import sys
from utils import all_repos_to_json
import multiprocessing
import urllib.request
import tarfile
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--config", type=str, default="cfg/preprocess.yaml", help="Path to the configuration file")
argparser.add_argument("-y", action='store_true', help="Skip confirmation")
args = argparser.parse_args()

CONFIG_FILE = args.config

if args.y:
    print("WARNING: By skipping confirmation, you agree to overwrite existing files.")

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

    tokens = tokenizer.encode(
        content,
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

    # Statistics
    total_tokens = sum(len(tokens) for tokens in tokenized_data)
    print(f"Total tokens: {total_tokens}")
    print(f"Average tokens per sample: {total_tokens / len(tokenized_data)}")
    print(f"Vocabulary size: {len(tokenizer)}")
    print(f"Padding token ID: {tokenizer.pad_token_id}")
    print(f"Padding token: {tokenizer.pad_token}")
    print(f"EOS token ID: {tokenizer.eos_token_id}")
    print(f"EOS token: {tokenizer.eos_token}")
    print(f"Truncation: {config['truncation']}")
    print(f"Max length: {config['max_length']}")

def main():
    with open(CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)

    if not config['use_cache']:
        if not config['ignore_preset_repos']:
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

            repos_dict = all_repos_to_json(repos_dict, config['data_file'], setting=config['setting'])

            with open(config['output_file'], 'w') as file:
                json.dump(repos_dict, file)
            data = repos_dict
        else: 
            if not os.path.exists(config['repos_dir']):
                os.makedirs(config['repos_dir'])
            else:
                print(f"WARNING: {config['repos_dir']} already exists.")
                if not args.y:
                    response = input("Do you want to overwrite it? (y/n): ")
                    if response.lower() != 'y':
                        print("ABORTED!")
                        sys.exit(1)
                else:
                    print("Overwriting existing files and directories.")
                for file in os.listdir(config['repos_dir']):
                    file_path = os.path.join(config['repos_dir'], file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        os.system(f"rm -rf {file_path}")
            from utils import get_top_repos
            raw = get_top_repos(config['top_k'], config['repos_dir'], source=config['get_repos_from'])
            repos_dict = []
            for repo in raw:
                repo_url = repo['url']
                repo_path = repo['path']
                repo_name = repo['name']
                extensions = repo['extensions']
                if not os.path.exists(os.path.join(config['repos_dir'], f"{repo_path}")):
                    print(f"Repo {repo_name} not found in {config['repos_dir']}. Downloading from {repo_url}")
                    if config['get_repos_from'] == 'github':
                        os.system(f"git clone {repo_url} {os.path.join(config['repos_dir'], repo_name)}")
                    elif config['get_repos_from'] == 'pypi':
                        print(f"Downloading {repo_name} from {repo_url}")
                        file_name = repo_url.split('/')[-1]
                        downloaded_file = os.path.join(config['repos_dir'], file_name)
                        urllib.request.urlretrieve(repo_url, downloaded_file)
                        print(f"Extracting {downloaded_file} to {os.path.join(config['repos_dir'], repo_name)}")
                        with tarfile.open(downloaded_file, 'r:gz') as tar:
                            tar.extractall(path=config['repos_dir'])
                            os.rename(os.path.join(config['repos_dir'], file_name.split('.tar.gz')[0]), 
                                    os.path.join(config['repos_dir'], repo_name))
                        print(f"Removing {downloaded_file}")
                        os.remove(downloaded_file)

                repos_dict.append({
                    "name": repo_name,
                    "path": repo_path,
                    "extensions": extensions
                })

            repos_dict = all_repos_to_json(repos_dict, config['data_file'], setting=config['setting'])

            with open(config['output_file'], 'w') as file:
                json.dump(repos_dict, file)
            data = repos_dict
            
    else:
        with open(config['data_file'], 'r') as file:
            data = json.load(file)

    # TODO: Remove near-duplicate files
    # TODO: PII redaction
    # TODO: Decontamination 

    num_workers = config.get('num_workers', os.cpu_count())
    print(f"Using {num_workers} workers for tokenization")

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

    print("Preprocessing successfully completed!")

if __name__ == '__main__':
    main()

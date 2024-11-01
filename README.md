# LLM-Pretraining

## 数据预处理

修改 `cfg/preprocess.yaml`.

示例：

```yaml
tokenizer: "gpt2" # 使用的分词器
max_length: 100000 # 最大长度
truncation: True # 是否截断

use_cache: False # 是否使用已有的json缓存
setting: 2 # 消融实验
data_file: "data/data_2.json" # 如果use_cache为True，将使用该文件

repos_dir: "repos" # 存放repo的目录
ignore_preset_repos: True # If True, ignore the repos in the following list, and get top_k repos from GitHub
top_k: 100
repos:
  - tornado:
      url: "https://github.com/tornadoweb/tornado" # repo的url，发现不存在则clone
      name: "tornado" # repo的名字，作为标识符
      path: "tornado/tornado" # repo需要训练的文件的路径
      extensions: [".py"] # 文件扩展名
  - flask:
      url: "https://github.com/pallets/flask"
      name: "flask"
      path: "flask/src/flask"
      extensions: [".py"]
output_file: "data/data_2.json" # 所有repo将生成的数据文件

output_tokenized: "data/data_2_tokenized.json" # 分词后的数据文件
output_mmap: "data/data_2.mmap" # 生成的mmap文件
num_workers: 8 # 多进程处理数据
```

运行 `python preprocess.py`.
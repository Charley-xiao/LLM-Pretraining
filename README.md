##### writen by Qiwen
## LLM-Pretraining

`utils/` 文件夹包含了一些工具函数：
- `depana/` 文件夹包含了一些处理依存分析的工具函数

------------------------------------
##### writen by ZhangS
py环境3.10
## 文件结构
-  `src`
    - `meerges.txt`和`vocab.json`: process_data需要的文件。
    - `to_json.py`: 将下载的仓库按照Qiwen提出的三种消融实验设计处理成json文件。
    - `prepocess_data.py`: 借鉴`https://github.com/NVIDIA/Megatron-LM/blob/main/tools/preprocess_data.py` 稍微做了一些改动，可以将json文件转为`.bin`和`.idx`文件。
    - `to_mmap.py`: `.bin`和`.idx`转mmap。
    - `megatron`: 从Megatron-LM里copy的一个文件夹，`prepocess_data.py`会用到。
- `test_Repositories`
    - `raw_repo`: 存放下载的源仓库。
    - `json_files`: 存放由源仓库转换出来的json文件。
    - `output`: 存放输出的`.bin`和`.idx`文件。
## 1. 克隆仓库
我们将以下仓库克隆到 `test_Repositories` 目录下，用于数据预处理和模型训练的消融实验：

1. [requests](https://github.com/psf/requests) - Python的HTTP库。
2. [flask](https://github.com/pallets/flask) - 轻量级的Python Web框架。
3. [pandas](https://github.com/pandas-dev/pandas) - 数据分析和处理库。
4. [scikit-learn](https://github.com/scikit-learn/scikit-learn) - 机器学习库。
5. [rich](https://github.com/Textualize/rich) - 用于生成富文本和格式化输出的Python库。

```bash
@echo off
cd LLM-Pretraining-main\test_Repositories\raw_repo
git clone https://github.com/psf/requests
git clone https://github.com/pallets/flask
git clone https://github.com/pandas-dev/pandas
git clone https://github.com/scikit-learn/scikit-learn
git clone https://github.com/Textualize/rich
echo All repositories have been cloned.
pause
```

## 2. 仓库转json
- 运行`to_json`
- 转换后的文件存在`test_Repositories/json_files`目录下

## 3. 数据清洗
这个没做

## 4. json转`.bin`和`.idx`
- 运行`prepocess_data`
- 转换后的文件存在`test_Repositories/output`目录下

## 5. `.bin`和`.idx`转mmap
- 运行`to_mmap`
- 转换后的文件存在`test_Repositories/mmap`目录下
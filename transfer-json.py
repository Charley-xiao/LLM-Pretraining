# 用来处理生成的json文件为jsonl格式，同时trunck掉超过指定长度的内容

import json

# 输入文件名，输出文件名，以及content字段的截取长度
input_file_name = 'data/data_1.json'
output_file_name = 'data/data_1.jsonl'
content_cut_length = 100000000000 # 如果需要更改截断长度，请修改该变量

def process_json_file(input_file, output_file, cut_length):
    # 打开输入文件并读取数据
    with open(input_file, 'r', encoding='utf-8') as infile:
        data = json.load(infile)
    
    # 打开输出文件准备写入
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for item in data:
            # 如果content字段比cut_length长，则截取，否则保持不变
            item['content'] = item['content'][:cut_length]
            # 将每个item转换为json字符串，并写入文件，后面加换行符
            json_line = json.dumps(item)
            outfile.write(json_line + '\n')

# 运行函数，进行文件处理
process_json_file(input_file_name, output_file_name, content_cut_length)
import numpy as np
import mmap
import os

def load_bin_as_mmap(bin_file_path, dtype=np.float32):
    """
    将 .bin 文件映射到内存并转换为 numpy 数组。
    """
    file_size = os.path.getsize(bin_file_path)
    num_elements = file_size // np.dtype(dtype).itemsize  # 计算元素数量

    # 打开文件并映射到内存
    with open(bin_file_path, "rb") as f:
        bin_mmap = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

    # 使用 numpy 从内存映射对象中创建数组
    data = np.frombuffer(bin_mmap, dtype=dtype, count=num_elements)

    return data, bin_mmap  # 返回数据和 mmap 对象


def load_idx_file(idx_file_path):
    """
    从 .idx 文件中读取偏移量，返回一个偏移列表。
    假设每个偏移量是 64 位整型（long long）。
    """
    offsets = []
    with open(idx_file_path, "rb") as f:
        while True:
            offset = f.read(8)  # 每次读取 8 字节（64 位）
            if not offset:
                break
            offsets.append(int.from_bytes(offset, byteorder='little'))
    return offsets


def read_data_using_offsets(bin_data, offsets, element_size):
    """
    根据偏移量列表从 bin_data 中读取特定的数据片段。
    element_size 表示每个数据段的大小。
    """
    results = []
    for offset in offsets:
        start = offset // np.dtype(bin_data.dtype).itemsize  # 计算元素起始位置
        end = start + element_size
        results.append(bin_data[start:end])
    return results


def main():
    # 文件路径
    base_dir = "C:/Users/ZS/PycharmProjects/LLM-Pretraining-main/test_Repositories"
    output_dir = os.path.join(base_dir, "mmap")  # mmap文件输出目录
    os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在

    bin_file_path = os.path.join(base_dir, "output", "flask_content_document.bin")
    idx_file_path = os.path.join(base_dir, "output", "flask_content_document.idx")

    # 加载 .bin 文件并映射到内存
    bin_data, bin_mmap = load_bin_as_mmap(bin_file_path)

    # 加载 .idx 文件获取偏移量列表
    offsets = load_idx_file(idx_file_path)

    # 定义每个数据块的大小（根据您的数据结构修改）
    element_size = 10  # 假设每个数据片段包含 10 个元素

    # 使用偏移量读取数据片段
    results = read_data_using_offsets(bin_data, offsets, element_size)

    # 将结果保存为 numpy mmap 格式的文件
    mmap_output_path = os.path.join(output_dir, "flask_content_document_mmap.npy")
    np.save(mmap_output_path, results)
    print(f"Saved mmap data to {mmap_output_path}")

    # 处理完成后关闭 mmap
    bin_mmap.close()


if __name__ == "__main__":
    main()

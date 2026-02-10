import os
import re

# 输入和输出文件夹路径
input_folder = r"F:\BaiduNetdiskDownload\input"
output_folder = r"F:\BaiduNetdiskDownload\output"

# HistCite 不支持的字段
remove_tags = {"D3", "DA", "CL", "BN", "RI", "OI"}

# 老版 WOS 核心字段顺序（HistCite 解析习惯）
core_order = [
    "PT", "AU", "AF", "BE", "TI", "SO", "LA", "DT",
    "CT", "CY", "SP", "DE", "ID", "AB", "C1", "C3", "RP", "EM",
    "FU", "FX", "CR", "NR", "TC", "Z9", "U1", "U2",
    "PU", "PI", "PA", "SN", "J9", "JI", "PD", "PY",
    "VL", "IS", "BP", "EP", "DI", "PG", "WC", "WE", "SC",
    "GA", "UT"
]

# 必须存在的标签（缺失时补全）
required_tags = {
    "CT": "CT [Conference Title Missing]",
    "CY": "CY [Conference Date Missing]",
    "SP": "SP [Conference Sponsor Missing]"
}

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 遍历输入文件夹中的所有 txt 文件
file_list = [f for f in os.listdir(input_folder) if f.lower().endswith(".txt")]
file_list.sort()  # 按文件名排序，保证顺序一致

for idx, filename in enumerate(file_list, start=1):
    input_file = os.path.join(input_folder, filename)
    output_file = os.path.join(output_folder, f"savedrecs{idx}.txt")  # HistCite 识别的命名

    with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # 保留或补全文件头
    header_lines = []
    if lines and lines[0].startswith("FN"):
        header_lines.append(lines[0].strip())
    else:
        header_lines.append("FN Thomson Reuters Web of Knowledge")

    if len(lines) > 1 and lines[1].startswith("VR"):
        header_lines.append(lines[1].strip())
    else:
        header_lines.append("VR 1.0")

    # 从正文开始处理
    records = []
    current_record = []

    for line in lines[len(header_lines):]:
        tag = line[:2].strip()
        if tag in remove_tags:
            continue
        if line.startswith("ER"):
            current_record.append(line.strip())
            records.append(current_record)
            current_record = []
        else:
            current_record.append(line.strip())

    # 处理每条记录
    cleaned_records = []
    for rec in records:
        tag_map = {}
        current_tag = None
        for line in rec:
            line = line.rstrip("\n")
            if len(line) >= 4 and line[:2].isupper() and line[2] == " ":
                current_tag = line[:2]
                tag_map.setdefault(current_tag, []).append(line)
            else:
                if current_tag:
                    tag_map[current_tag].append("   " + line.strip())

        # 自动补全缺失标签
        for req_tag, placeholder in required_tags.items():
            if req_tag not in tag_map:
                tag_map[req_tag] = [placeholder]

        # 按核心顺序重排
        ordered_lines = []
        for tag in core_order:
            if tag in tag_map:
                ordered_lines.extend(tag_map[tag])
        ordered_lines.append("ER")
        cleaned_records.append("\n".join(ordered_lines))

    # 合并文件头和正文
    final_text = "\n".join(header_lines) + "\n" + "\n\n".join(cleaned_records)

    # 保存为 ANSI 编码（Windows）
    with open(output_file, "w", encoding="mbcs", errors="ignore") as f:
        f.write(final_text)

    print(f"已处理 {filename} -> {output_file}")

print("批量清理完成！")

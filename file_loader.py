import pandas as pd
import os
import re

REPLACE_DICT = {
    '（': '(',
    '）': ')',
    '’': "'",
    '‘': "'",
    '，': ',',
}

COMBINATION = [['[dD]on', 't'],
    ['[cC]an', 't'],
    ['[iI]', "m"],
    ['[iI]', 've'],
]

class FILE_LOADER:
    def __init__(self, file_path: str, yrc_dir: str, lrc_dir: str, refresh = False, target_files: list = None) -> None:
        self.file_path = file_path
        self.yrc_dir = yrc_dir
        self.lrc_dir = lrc_dir

        if(target_files):
            self.target_files = target_files
        else:
            df = pd.read_excel(self.file_path)
            self.target_files = df['歌曲id'].dropna().tolist()

        if refresh:
            # Clear the yrc_dir and lrc_dir 
            for file in os.listdir(self.yrc_dir):
                os.remove(os.path.join(self.yrc_dir, file))
            # for file in os.listdir(self.lrc_dir):
            #     os.remove(os.path.join(self.lrc_dir, file))

    def load_single_yrc(self, target_id: int) -> None:
        ######## Load the file ########
        df = pd.read_excel(self.file_path)
        file_id = str(target_id) + '.yrc.txt'
        file_pos = os.path.join(self.yrc_dir, file_id)
        # 读取excel中target id行对应的yrc列的信息
        yrc_content = df[df['歌曲id'] == target_id]['YRC歌词'].dropna().tolist()
        
        ######## Preprocess the file ########
        # Replace the special characters
        for key in REPLACE_DICT:
            yrc_content[0] = yrc_content[0].replace(key, REPLACE_DICT[key])
        # yrc_content[0] = yrc_content[0].replace('（', '(').replace('）', ')').replace("’", "'").replace("‘", "'")
        # Check the Chinese pattern
        yrc_content = yrc_content[0].split('\n')
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        filtered_lines = [line for line in yrc_content if not chinese_pattern.search(line)]
        if(len(filtered_lines) < len(yrc_content) - 3):
            print(f"歌曲{target_id}的歌词中含有过多中文，已自动过滤。")
            return
        # Merge the split words
        merged_lines = merge_split_words(filtered_lines)
        
        ######## Save the file ########
        with open(file_pos, 'w', encoding = 'utf-8') as yrc_file:
            for line in merged_lines:
                yrc_file.write(f"{line}\n")
        print(f"内容已保存到{target_id} yrc.txt 文件中。")

    def load_all_yrc(self) -> None:
        # 读取 Excel 文件
        for target_id in self.target_files:
            self.load_single_yrc(target_id)
        print("内容已保存到 yrc.txt 文件中。")

    # def load_lrc(self, refresh: bool = True) -> None:
    #     # 读取 Excel 文件
    #     df = pd.read_excel(self.file_path)
    #     # 获取 "lrc" 列并保存到 lrc.txt
    #     lrc_content = df['lrc'].dropna().tolist()
    #     with open(self.lrc_dir, 'w') as lrc_file:
    #         for item in lrc_content:
    #             lrc_file.write(f"{item}\n")
    #     print("内容已保存到 lrc.txt 文件中。")


#### Helper Functions ####
def merge_split_words(lines):
    # 定义一个正则表达式模式，用于匹配形如 ( , , )don( , , )'( , , )t 的部分
    pattern = re.compile(r'\((\d+),(\d+),(\d+)\)([a-zA-Z]+)?\((\d+),(\d+),(\d+)\)\'\((\d+),(\d+),(\d+)\)([a-zA-Z]+)?')

    merged_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        match = pattern.search(line)
        if match:
            # print(f"匹配到的行：{match.group(0)}")
            # print(f"匹配到的部分：{match.group(9), match.group(10)}")
            # 提取匹配部分的时间戳和单词
            part1_time = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
            part2_time = (int(match.group(5)), int(match.group(6)), int(match.group(7)))
            part3_time = (int(match.group(8)), int(match.group(9)), int(match.group(10)))

            part1_word = match.group(4) if match.group(4) else ''
            part2_word = match.group(11) if match.group(11) else ''

            # 计算新的时间戳
            new_time = (part1_time[0], part1_time[1] + part2_time[1] + part3_time[1], part1_time[2])
            new_word = f"({new_time[0]},{new_time[1]},{new_time[2]}){part1_word}'{part2_word}"

            # 替换原来的分割部分
            new_line = pattern.sub(new_word, line)
            merged_lines.append(new_line)
        else:
            merged_lines.append(line)
        i += 1

    return merged_lines
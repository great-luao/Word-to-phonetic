import pandas as pd
import os
import re
import json
import requests
import shutil

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
    def __init__(self, file_path: str, 
                 yrc_dir: str, 
                 lrc_dir: str, 
                 yrccn_dir: str,
                 yrcy_dir: str,
                 yrc46_dir: str,
                 refresh = False, 
                 target_files: list = None,
                 number: int = 1) -> None:
        self.file_path = file_path
        self.yrc_dir = yrc_dir
        self.yrccn_dir = yrccn_dir
        self.yrcy_dir = yrcy_dir
        self.yrc46_dir = yrc46_dir
        self.lrc_dir = lrc_dir

        if(target_files):
            self.target_files = target_files
        else:
            df = pd.read_excel(self.file_path)
            self.target_files = df['歌曲id'].dropna().tolist()
            print(self.target_files)
        
        self.refresh = refresh
        self.number = number

    def load_single_yrc(self, target_id: int) -> bool:
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
        # print(yrc_content)
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        filtered_lines = [line for line in yrc_content if not chinese_pattern.search(line)]
        if(len(filtered_lines) < len(yrc_content) - 3):
            print(f"歌曲{target_id}的歌词中含有过多中文，已自动过滤。")
            return False
        # Merge the split words
        merged_lines = merge_split_words(filtered_lines)
        
        ######## Save the file ########
        with open(file_pos, 'w', encoding = 'utf-8') as yrc_file:
            for line in merged_lines:
                yrc_file.write(f"{line}\n")
        print(f"内容已保存到{target_id} yrc.txt 文件中。")
        return True

    def load_all_yrc(self) -> None:
        if self.refresh:
            # Clear the yrc_dir and lrc_dir 
            for file in os.listdir(self.yrc_dir):
                os.remove(os.path.join(self.yrc_dir, file))
            # for file in os.listdir(self.lrc_dir):
            #     os.remove(os.path.join(self.lrc_dir, file))
        # 读取 Excel 文件
        number = 0
        for target_id in self.target_files:
            if(self.load_single_yrc(target_id)): number += 1
            if(number >= self.number): break
        print("内容已保存到 yrc.txt 文件中。")

    def output_final_explorer(self, output_dir):
        df = pd.read_excel(self.file_path)
        # 遍历yrc文件夹
        for file in os.listdir(self.yrc_dir):
            # 获取歌曲id
            target_id = int(file.split('.')[0])
            print(target_id)
            # 获取歌曲封面地址，MV地址，音频地址
            cover_url = df[df['歌曲id'] == target_id]['歌曲封面cdn'].values[0]
            mv_url = df[df['歌曲id'] == target_id]['mv视频cdn'].values[0]
            audio_url = df[df['歌曲id'] == target_id]['歌曲音频cdn'].values[0]
            # 创建歌曲文件夹
            song_dir = os.path.join(output_dir, str(target_id))
            if not os.path.exists(song_dir):
                os.makedirs(song_dir)
            # 下载封面, mv, 音频
            self.download_image(cover_url, song_dir)
            self.download_mp4(mv_url, song_dir)
            self.download_audio(audio_url, song_dir)
            # 生成json文件
            self.output_single_json(target_id, song_dir)

    def output_all_json(self, json_dir:str ) -> None:
        # 读取 Excel 文件
        df = pd.read_excel(self.file_path)
        # 遍历yrc文件夹
        for file in os.listdir(self.yrc_dir):
            # 获取歌曲id
            target_id = int(file.split('.')[0])
            target_dir = os.path.join(json_dir, str(target_id))
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            self.output_single_json(target_id, target_dir)

    def output_single_json(self, target_id: int, json_dir:str) -> None:
        # json格式: {"song": "歌曲名", "singer": "歌手"，krc: "krc歌词", "translate": "yrccn", 
        # "phonetic": "yrcy", "level": "yrc46"}
        df = pd.read_excel(self.file_path)
        # 获取歌曲名和歌手
        print(df[df['歌曲id'] == target_id]['歌曲名'])
        song_name = df[df['歌曲id'] == target_id]['歌曲名'].values[0]
        if not song_name:
            print(f"歌曲{target_id}不存在！")
            return
        singer = df[df['歌曲id'] == target_id]['艺人名'].values[0]
        # 生成json
        json_content = {"song": song_name, "singer": singer}
        load_dirs = [self.yrc_dir, self.yrccn_dir, self.yrcy_dir, self.yrc46_dir]
        load_content = {'krc': '.yrc.txt', 'translate': '.yrccn.txt', 
                        'phonetic': '.yrcy.txt', 'level': '.yrc46.txt'}
        for key, dir in zip(load_content, load_dirs):
            with open(os.path.join(dir, str(target_id) + load_content[key]), 'r', encoding='utf-8') as file:
                content = file.readlines()
                content = ''.join(content)
                json_content[key] = content
        # 生成json文件
        with open(os.path.join(json_dir, 'lyrics.json'), 'w', encoding='utf-8') as json_file:
            json.dump(json_content, json_file, ensure_ascii=False, indent=4)

    def download_image(self, url, image_dir):
        # 发送HTTP请求获取图片
        response = requests.get(url)
        if response.status_code == 200:
            # 打开文件以二进制模式写入
            with open(image_dir + "/cover.jpg", 'wb') as file:
                file.write(response.content)
            print(f"图片已成功下载并保存到 {image_dir}")
        else:
            print(f"无法下载图片，状态码: {response.status_code}")
    
    def download_mp4(self, url, mp4_dir):
        # 发送HTTP请求获取MP4文件
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # 打开文件以二进制模式写入
            with open(mp4_dir + "/mv.mp4", 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            print(f"MP4文件已成功下载并保存到 {mp4_dir}")
        else:
            print(f"无法下载MP4文件，状态码: {response.status_code}")

    def download_audio(self, url, flac_dir):
        # 发送HTTP请求获取音频文件
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # 打开文件以二进制模式写入
            with open(flac_dir + "/audio.flac", 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            print(f"音频文件已成功下载并保存到 {flac_dir}")
        else:
            print(f"无法下载音频文件，状态码: {response.status_code}")

    def make_zip(self, dir):
        # 把dir下的所有文件压缩成一个zip文件
        # 检查文件夹是否存在
        if not os.path.isdir(dir):
            print(f"文件夹 {dir} 不存在")
            return
    
        # 压缩文件夹
        shutil.make_archive("Result", 'zip', dir)
        print(f"文件夹已压缩为 Result.zip")

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
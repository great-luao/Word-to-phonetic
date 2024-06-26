import eng_to_ipa as ipa
import re
import glob
import os
import numpy as np
from deep_translator import GoogleTranslator

# Define the translate class
class Translate:
    def __init__(self, 
                 yrc_dir: str, 
                 yrcy_dir: str, 
                 yrccn_dir: str, 
                 yrc46_dir: str,
                 lrc_dir: str,
                 CET4_dict: dict,
                 CET6_dict: dict) -> None:
        # Define the input dir and output dir
        self.yrc_dir = yrc_dir
        self.yrcy_dir = yrcy_dir
        self.yrccn_dir = yrccn_dir
        self.yrc46_dir = yrc46_dir
        self.lrc_dir = lrc_dir
        self.CET4_dict = CET4_dict
        self.CET6_dict = CET6_dict

    # 生成音标文件
    def process_lyrics(self):
        # Iterate all file in yrc_dir, output the file to yrcy_dir
        for input_file in list_txt_files(self.yrc_dir):
            output_file = os.path.join(self.yrcy_dir, 
                                       os.path.basename(input_file).replace('yrc', 'yrcy'))
            with open(input_file, 'r') as infile, open(output_file, 'w', encoding = 'utf-8') as yrcy:
                lines = infile.readlines()
                file_pre_process(lines)
                for line in lines:
                    # find and split parts as [], () and words
                    parts = re.findall(r'\[.*?\]|\(.*?\)|\w+|[^\s\w]', line)
                    for part in parts:
                        if not re.match (r'\w+', part): # 单词部分
                            yrcy.write(part)
                        else:
                            phoneme = convert_word_to_phoneme(part)
                            yrcy.write(phoneme)
                    yrcy.write('\n')
        print("处理完成，音标已写入输出文件。")

    # 生成四六级文件
    def process_foursix(self):
        # Load the CET4 and CET6 dictionaries
        # Handle the file
        for input_file in list_txt_files(self.yrc_dir):
            output_file = os.path.join(self.yrc46_dir, 
                                       os.path.basename(input_file).replace('yrc', 'yrc46'))
            with open(input_file, 'r') as infile, open(output_file, 'w', encoding = 'utf-8') as yrcf:
                lines = infile.readlines()
                file_pre_process(lines)
                for line in lines:
                    # find and split parts as [], () and words
                    parts = re.findall(r'\[.*?\]|\(.*?\)|\w+|[^\s\w]', line)
                    for part in parts:
                        if not re.match (r'\w+', part): # 单词部分
                            yrcf.write(part)
                        else:
                            four_six = convert_word_to_46(part, self.CET4_dict, self.CET6_dict)
                            yrcf.write(four_six)
                    yrcf.write('\n')
        print("处理完成，四六级信息已写入输出文件。")

    # 生成单词对应的中文文件
    def process_cn(self):
        # preprocess the input files
        for input_file in list_txt_files(self.yrc_dir):
            output_file = os.path.join(self.yrccn_dir, 
                                       os.path.basename(input_file).replace('yrc', 'yrccn'))
            with open(input_file, 'r') as infile:
                lines = infile.readlines()
            for line in lines:
                line = line.replace('to', "|to").replace('the', "|the")
            
            ### Write one line by line
            with open(output_file, 'w', encoding = 'utf-8') as yrccn:
                for line in lines:
                    # make line into string
                    # line = ''.join(line)
                    translated = GoogleTranslator(source='auto', target='zh-CN').translate(line)
                    translated = translated.replace(' ', '').replace("'", "").replace("|", " ")
                    yrccn.write(translated+'\n')

        ### Write the whole file
        # translated = GoogleTranslator(source='auto', target='zh-CN').translate_file('temp_file.txt')
        # # Remove all spaces
        # translated = translated.replace(' ', '').replace("'", "").replace("|", " ")
        # # Write the srting into the output file
        # with open(output_file, 'w', encoding = 'utf-8') as yrccn:
        #     yrccn.write(translated)
        # remove the temp file
        # os.remove('temp_file.txt')
        print("处理完成，中文翻译已写入输出文件。")

############# Helper functions #############


# 文件内容预处理, 生成中文文件前不需要处理
def file_pre_process(self, lines: list):
    # Iterate all file in yrc_dir
    for line in lines:
        # remove all ' symbol
        line = line.replace("'", "")
    # print("处理完成，已删除所有单引号。")

# 生成指定目录及其子目录下所有.txt文件的路径列表
def list_txt_files(directory):
    txt_files = glob.glob(os.path.join(directory, '**', '*.txt'), recursive=True)
    return txt_files

# 转换单词到对应的音标
def convert_word_to_phoneme(word):
    # we use ipa now instead of pronouncing
    # phonemes = ipa.ipa_list(word)
    phonemes = ipa.convert(word)
    if phonemes:
        return phonemes
        # return ' '.join(phonemes[0])  # the output is a 2-d list.
    return word  

# 转换单词到对应46级信息
def convert_word_to_46(word, CET4_dict, CET6_dict):
    # If the word exits in the CET4_dict or CET6_dict, mark it as '4', '6'
    # Otherwise, return '0'
    # print(word)
    if word in CET4_dict:
        return '4'
    elif word in CET6_dict:
        return '6'
    return '-'
import eng_to_ipa as ipa
import re
import glob
import os
import numpy as np
from deep_translator import GoogleTranslator
from chatgpt_api import GPT_TRANSLATOR

# Define the translate class
class Translator:
    def __init__(self, 
                 yrc_dir: str, 
                 yrcy_dir: str, 
                 yrccn_dir: str, 
                 yrc46_dir: str,
                 lrc_dir: str,
                 CET4_dict: dict,
                 CET6_dict: dict,
                 test: bool = False) -> None:
        # Define the input dir and output dir
        self.yrc_dir = yrc_dir
        self.yrcy_dir = yrcy_dir
        self.yrccn_dir = yrccn_dir
        self.yrc46_dir = yrc46_dir
        self.lrc_dir = lrc_dir
        self.CET4_dict = CET4_dict
        self.CET6_dict = CET6_dict
        # Check if the test is True
        self.yrc_files = []
        if test:
            # test the translation
            self.yrc_files = [os.path.join(self.yrc_dir, '447925342.yrc.txt')]
        else:
            self.yrc_files = list_txt_files(self.yrc_dir)
            # Remove the last file in the list
            self.yrc_files.pop()
    
    # 生成音标文件
    def process_lyrics(self):
        # Iterate all file in yrc_dir, output the file to yrcy_dir
        for input_file in self.yrc_files:
            output_file = os.path.join(self.yrcy_dir, 
                                       os.path.basename(input_file).replace('yrc', 'yrcy'))
            with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding = 'utf-8') as yrcy:
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
        for input_file in self.yrc_files:
            output_file = os.path.join(self.yrc46_dir, 
                                       os.path.basename(input_file).replace('yrc', 'yrc46'))
            with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding = 'utf-8') as yrcf:
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
    def process_cn(self, test:bool = True):
        # preprocess the input files
        for input_file in self.yrc_files:
            output_file = os.path.join(self.yrccn_dir, 
                                       os.path.basename(input_file).replace('yrc', 'yrccn'))
            with open(input_file, 'r', encoding = 'utf-8') as infile:
                temp_lines = infile.readlines()
            lines = []
            for line in temp_lines:
                # find and split parts as [], () and words
                parts = re.findall(r'\[.*?\]|\(.*?\)|\w+|[^\s\w]', line)
                for part in parts:
                    if re.match (r'\w+', part): # 单词部分
                        # add a '|' after the word
                        line = line.replace(part, part+"|") 
                lines.append(line)

            ### Write one line by line
            with open(output_file, 'w', encoding = 'utf-8') as yrccn:
                last_part = ''
                for line in lines:
                    # translate the line and check the style
                    translated = GoogleTranslator(source='en', target='zh-CN').translate(line)
                    translated = translated.replace("'", "").replace('|','').replace("（", "(").replace("）", ")").replace(' ', '')       
                    # print(translated)
                    # find and split parts as [], () and words
                    # parts = re.findall(r'\[.*?\]|\(.*?\)|\w+|[^\s\w]', translated)
                    # parts = re.findall(r'\(.*?\)', translated)
                    # # make sure the time line is right
                    # for part in parts:
                    #     # find those (a, b, c) parts where a b c are int numbers which stand for some time information
                    #     if re.match(r'\(\d+,\d+,\d+\)', part):
                    #         # print(part)
                    #         if last_part != '':
                    #             # Check if a in the last part plus b equals a in the current part, if not, rewrite b as current part a - last part a
                    #             new_part = time_check(last_part, part)
                    #             if(new_part != last_part):
                    #                 translated = translated.replace(last_part, new_part)
                    #                 print(f'替换 {last_part} 为 {new_part}')
                    #         last_part = part
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

def time_check(last_part: str, part: str) -> str:
    # 使用正则表达式提取括号内的三个数字
    last_a, last_b, last_c = map(int, re.findall(r'\d+', last_part))
    part_a, part_b, part_c = map(int, re.findall(r'\d+', part))
    # if(last_b != part_a - last_a):
        # print(f"Warning: 时间线不连续，上一句结尾时间为 {last_a}，当前句开始时间为 {part_a}，请检查。")
    # 计算新的 b 值
    new_b = part_a - last_a
    # 构造新的字符串
    return f"({last_a},{new_b},{last_c})"

# 文件内容预处理, 生成中文文件前不需要处理
def file_pre_process(lines: list):
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

def replace_word(text, old_word, new_word):
    # \b 表示单词边界，确保只匹配整个单词
    pattern = r'\b' + re.escape(old_word) + r'\b'
    result = re.sub(pattern, new_word, text)
    return result

if __name__ == '__main__':
    # Test the gpt translator
    translator = GPT_TRANSLATOR()
    with open("yrc/test.yrc.txt", 'r', encoding = 'utf-8') as yrc, open("yrccn/temp.yrccn.txt", 'w', encoding = 'utf-8') as temp_file:
        lines = yrc.readlines()
        temp_file.write(lines[0])
        for line in lines[1:] :
            words = []
            parts = re.findall(r'\[.*?\]|\(.*?\)|\w+', line)
            # print(words)
            # Find all words in a line
            for part in parts:
                if re.match (r'\w+', part):
                    words.append(part)
            # Combine the words as a sentence
            sentence = ' '.join(words)
            # Translate each word
            for word in words:
                # print(f"Translating {word} in {sentence}")
                translated_word = translator.translate(f"{sentence}, {word}")
                print(f"Translating {word} to {translated_word}")
                line = replace_word(line, word, translated_word)
            line = line.replace("'", "").replace('|','').replace("（", "(").replace("）", ")").replace(' ', '')
            print(line)
            temp_file.write(line)  
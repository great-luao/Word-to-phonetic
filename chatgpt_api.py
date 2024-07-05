import requests
import json
from openai import OpenAI
import os


class GPT_TRANSLATOR:
    def __init__(self):
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key= ''
        )
        self.messages = [ {"role": "system", "content":  
              "你是一个智能翻译机，我会给你一句英文歌词, 然后我会给你其中一个单词，你要联系句子直接告诉我这个单词对应的简短的中文, 不需要翻译整句句子。"},
               {"role": "user", "content": "Im a new soul, Im" },
               {"role": "assistant", "content": "我是" },
               {"role": "user", "content": "But since I came here" },
               {"role": "assistant", "content": "但是" },
            ]
    
    def translate(self, text:str) -> str:
        self.messages.append({"role": "user", "content": text})
        chat = self.client.chat.completions.create( 
            # model="gpt-4-0125-preview", messages=self.messages 
            model="gpt-3.5-turbo-1106", messages=self.messages 
        )
        self.messages.append({"role": "assistant", "content": chat.choices[0].message.content})
        return chat.choices[0].message.content
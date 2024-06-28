# krc file translation
Generally speaking, we want to translate the words in krc files of English songs to: 
1. The correspond phonetic symbol. 
2. It's Chinese meaning in the song. 
3. Some relevant information about that word. (Such as whether it's in CET4 range.)

File_Structure:

    +-Word-to-phonetic/         
    |   file_loader.py         Preprocess yrc and lrc files.
    |   translator.py          Translate api.
    |   chatgtp_api.py         Chatgpt api.
    |   translate_yrc.ipynb    Where to load and translate.
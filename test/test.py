# from google_trans_new import google_translator

# translator = google_translator()
# translate_text = translator.translate('abs',lang_tgt='en')

from deep_translator import GoogleTranslator

# Use any translator you like, in this example GoogleTranslator
translated = GoogleTranslator(source='auto', target='zh-CN').translate_file('yrc/3852042.yrc.txt')
# print(translated)
# from google_trans_new import google_translator

# translator = google_translator()
# translate_text = translator.translate('abs',lang_tgt='en')

from deep_translator import LingueeTranslator

# Use any translator you like, in this example GoogleTranslator
translated = LingueeTranslator(source='auto', target='chinese')._translate_file('yrc/3852042.yrc.txt')
print(translated)
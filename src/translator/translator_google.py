import re

# from googletrans import Translator
#
from .text_translator import TextTranslator
from google.cloud import translate_v2 as translate
from google.api_core import exceptions # Import for catching API exceptions

"""
TranslatorGoogle is a wrapper around google translate API.

Known issues:
 1. from time to time, google translate does not respond correctly and thus returns the following errors
      File "D:\workplace\changsin\pytranslator\venv\lib\site-packages\googletrans\client.py", line 182, in translate
        data = self._translate(translator, dest, src, kwargs)
      File "D:\workplace\changsin\pytranslator\venv\lib\site-packages\googletrans\client.py", line 78, in _translate
        token = self.token_acquirer.do(translator)
      File "D:\workplace\changsin\pytranslator\venv\lib\site-packages\googletrans\gtoken.py", line 194, in do
        self._update()
      File "D:\workplace\changsin\pytranslator\venv\lib\site-packages\googletrans\gtoken.py", line 62, in _update
        code = self.RE_TKK.search(r.translator).group(1).replace('var ', '')
    AttributeError: 'NoneType' object has no attribute 'group'
    
    If this happens, just rerun it till you get the correct response.
"""

MAX_RETRIES = 3


class TranslatorGoogle(TextTranslator):
    def __init__(self, from_language, to_language):
        super(TranslatorGoogle, self).__init__(from_language, to_language)
        self.client = translate.Client()

    def translate(self, text):
        text_translated = self.dictionary.get(text)

        # Condition to check if translation is needed
        # (not found in dictionary, or found but translated to itself, and not matching the regex)
        if (not text_translated or text == text_translated) and not re.match("^[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)?$", text):
            translated_text_result = None
            detected_language_result = None

            retries = 0
            while retries < MAX_RETRIES:
                try:
                    # First attempt to translate
                    response = self.client.translate(
                        text,
                        target_language=self.to_language,
                        source_language=self.from_language
                    )
                    translated_text_result = response['translatedText']

                    # Detect language for verification
                    detect_response = self.client.detect_language(text)
                    detected_language_result = detect_response['language']

                    # If successfully translated and detected language matches source, break
                    # or if the translated text is actually different from the original
                    if translated_text_result != text or detected_language_result != self.from_language:
                        break # Successfully translated or detected source is different

                    print(f"'{text}' not sufficiently translated. Detected as {detected_language_result}. Retrying...")

                except exceptions.GoogleAPICallError as e:
                    print(f"API call failed for '{text}': {e}. Retrying...")
                except Exception as e:
                    print(f"An unexpected error occurred for '{text}': {e}. Retrying...")

                retries += 1

            if translated_text_result is not None and translated_text_result != text:
                self.dictionary[text] = translated_text_result
                return translated_text_result
            else:
                # If all retries fail or translation result is same as original
                print(f"Failed to translate '{text}' after {MAX_RETRIES} attempts or translation was identical.")
                return text # Return original text if translation failed or was identical

        else:
            print("Known string or regex matched (not translating).")
            # If it was found in dictionary and is different, or regex matched, return it.
            if text_translated and text_translated != text:
                return text_translated
            else:
                return text # If it's a known string but identical, return original

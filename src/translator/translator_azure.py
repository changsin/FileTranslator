from azure_translator import Translator

from .text_translator import TextTranslator

"""
TranslatorAzure is a wrapper around Azure translator API.
https://pypi.org/project/azure-translator/

TODO: doesn't work due to access denied exception
"""


class TranslatorAzure(TextTranslator):
    def __init__(self, from_language, to_language):
        super(TranslatorAzure, self).__init__(from_language, to_language)
        self.client = Translator('48581afb-4631-4753-b2f3-c351f4d8026f')

    def translate(self, text):
        text_translated = self.dictionary.get(text)
        if not text_translated:
            text_translated = self.client.translate(text,
                                                        to=self.to_language,
                                                        source_language=self.from_language)

            self.dictionary[text] = text_translated
        else:
            print("known string")

        return text_translated

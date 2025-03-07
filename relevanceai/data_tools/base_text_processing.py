import string
import warnings
from typing import List
from collections import Counter

try:
    import nltk

    nltk.download("stopwords")
    from nltk.corpus import stopwords
except ModuleNotFoundError:
    warnings.warn("You are missing NLTK, please run `pip install nltk`")


class BaseTextProcessing:
    @staticmethod
    def normalize_text(
        txt: str,
        lower: bool = True,
        remove_digit: bool = True,
        remove_punct: bool = True,
    ) -> str:
        """
        * Lower-casing
        * Digit removal
        * Punctuation removal
        """
        if lower:
            txt = txt.lower()
        if remove_digit:
            txt = "".join([ch for ch in txt if ch not in string.digits])
        if remove_punct:
            txt = "".join([ch for ch in txt if ch not in string.punctuation])
        return txt

    @staticmethod
    def get_word_frequency(
        str_list: List[str],
        remove_stop_words: bool = True,
        additional_stop_words: List[str] = [],
        language="english",
    ) -> List:
        if remove_stop_words:
            stpw = stopwords.words(language)
            stpw += additional_stop_words
        else:
            stpw = []
        word_counter = Counter(
            [w.lower() for s in str_list for w in s.split() if w not in stpw]
        )
        return sorted(word_counter.items(), key=lambda item: (-item[1], item[0]))

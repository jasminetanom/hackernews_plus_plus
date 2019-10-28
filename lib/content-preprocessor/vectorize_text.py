from bs4 import BeautifulSoup
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import nltk
from nltk.stem import WordNetLemmatizer
from textacy.preprocess import preprocess_text, replace_numbers, replace_phone_numbers, replace_urls
from gensim.utils import to_utf8, tokenize
from gensim.models.phrases import Phrases, Phraser

STOP_WORDS = list(STOP_WORDS)
STOP_WORDS.append('http')
STOP_WORDS.append('www')

def strip_html(text):
    """Remove HTML characters, if any"""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def clean_text(text):
    text = text.replace('/n', ' ')).replace('.com', ' ').replace('.org', ' ').replace('.net', ' ')
    text = strip_html(text)
    # Remove contractions, if any:
    text = preprocess_text(text, fix_unicode=True, no_accents=True, no_contractions=True, lowercase=True, no_punct=True, no_currency_symbols=True), replace_with=' ')
    text = replace_urls(text, replace_with='')
    text = replace_numbers(text, replace_with='')
    return text

def tokenize_text(text):
    text = clean_text(text)
    return list(tokenize(text))

def lemmatize_words(words_list):
    wnl = WordNetLemmatizer()
    return [wnl.lemmatize(wnl.lemmatize(wnl.lemmatize(word, 'a'), 'v'), 'n') for word in words_list if len(word) >= 3]

def detect_phrases(lemmatized_list):
    phrases = Phrases(lemmatized_list)
    bigram = Phraser(phrases)
    trigram = Phrases(bigram[lemmatized_list])
    return bigram, trigram

import parallelization
import corpora
import vectorize_text
import gensim_models
import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
from gensim.corpora import Dictionary
from gensim.parsing.preprocessing import strip_tags, preprocess_string, remove_stopwords, strip_punctuation, strip_multiple_whitespaces, remove_stopwords, strip_numeric, strip_non_alphanum
import gensim
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../data-fetcher')
import config

sys.path.insert(2, '../utils')
import pickling

def fetch_all_content():
    conn = psycopg2.connect("host={} dbname={} user={}".format(config.POSTGRES_HOST, config.POSTGRES_DB_NAME, config.POSTGRES_USER))
    contents_df = sqlio.read_sql_query("SELECT id, all_text, article_content FROM {} LIMIT {}".format(config.POSTGRES_TABLE_NAME, config.STORY_COUNT), conn, index_col='id')
    contents_df["all_text"] += contents_df["article_content"]
    return contents_df

def do_preprocess_step(iterable_input, function, file_name):
    docs = parallelization.pool_iter_series(iterable_input)
    processed_docs = parallelization.pool_imap(function, docs)
    docs_list = list(processed_docs)
    pickling.save_pickle(file_name, docs_list)
    return docs_list

def get_phrases(doc_stream):
    return [word for word in trigram[bigram[doc_stream]] if len(word) >= 3]

def get_bow(tokens):
    """Convert text to bag-of-words (tokens to id)"""
    return dct.doc2bow(tokens)

def transform_tfidf(bow):
    return tfidf_model[bow]

def preprocess_content():
    contents_df = fetch_all_content()
    tokens_list = do_preprocess_step(contents_df["all_text"], vectorize_text.tokenize_text, 'tokens_list.pkl')
    lemmatized_list = do_preprocess_step(tokens_list, vectorize_text.lemmatize_words, 'lemmatized_list.pkl')
    bigram, trigram = vectorize_text.detect_phrases(lemmatized_list) # fit
    final_tokens_list = do_preprocess_step(lemmatized_list, get_phrases, 'final_tokens_list.pkl') # transform (multi-threaded)
    final_tokens = parallelization.pool_iter_series(final_tokens_list)
    return final_tokens

final_tokens = preprocess_content()
dct = corpora.train_dictionary(final_tokens) # fit
bow_corpus = pool_imap(get_bow, final_tokens) # transform (multi-threaded)
corpora.save_corpus('corpus_bow.mm', bow_corpus)
tfidf_model = gensim_models.train_and_save_gensim_model("tfidf", bow_corpus, "tfidf.model") #fit
tfidf_corpus = pool_imap(transform_tfidf, bow_corpus) # transform (multi-threaded)
corpora.save_corpus('corpus_tfidf.mm', tfidf_corpus)
lsimodel_300 = gensim_models.train_and_save_gensim_model("lsi", tfidf_corpus, 'lsimodel_300.model', num_topics=300)
lsi_300_corpus = lsimodel_300[tfidf_corpus] # convert tokens to topic distributions
corpora.save_corpus('lsi_300_corpus.mm', lsi_300_corpus)

import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
from gensim.corpora import Dictionary, MmCorpus
from gensim.models import LsiModel

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../data-fetcher')
import config

def fetch_commentors():
    conn = psycopg2.connect("host={} dbname={} user={}".format(config.POSTGRES_HOST, config.POSTGRES_DB_NAME, config.POSTGRES_USER))
    commenters_df = sqlio.read_sql_query("SELECT id, commenters FROM {} WHERE all_text IS NOT NULL AND all_text != '' AND article_content IS NOT NULL AND article_content != '' ORDER BY score DESC, story_time DESC LIMIT {}".format(config.POSTGRES_TABLE_NAME, STORY_COUNT), conn, index_col='id')
    return commenters_df

def listify_commenters(commenters_str):
    """Transform string of commenters into list"""
    return commenters_str.split(", ")

def get_commenters_set():
    """Get list of all unique commenters"""
    all_commenters = list(set(x for l in commenters_df["commenters"].values for x in l))
    all_commenters.remove("")
    return all_commenters

def get_boc(tokens):
    """Convert list of commenters for each story to "bag of commenters" (boc)"""
    return dct.doc2bow(tokens)

commenters_df = fetch_commentors()
dct = Dictionary(commenters_df["commenters"].values)
dct.filter_extremes()
dct.save('commenters_dct.dict')
commenters_df["boc"] = commenters_df["commenters"].apply(get_boc)
commenters_ary = commenters_df["boc"].values
# Dimensionality reduction of "bag of commenters" with LSI
commenters_dimrec_model = LsiModel(corpus=commenters_ary, num_topics=300, id2word=dct)
MmCorpus.serialize('commenters_corpus.mm', commenters_dimrec_ary)

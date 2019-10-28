import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
import gensim
from gensim.test.utils import get_tmpfile
from gensim.similarities import Similarity, MatrixSimilarity, SparseMatrixSimilarity
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../data-fetcher')
import config

sys.path.insert(2, '../content-preprocessor')
import parallelization

CONTENT_DICT_PATH = '../content-preprocessor/content-dct.dict'
CONTENT_CORPUS_PATH ='../content-preprocessor/lsi_300_corpus.mm'
COMMENTERS_DICT_PATH = '../commenters-preprocessor/commenters-dct.dict'
COMMENTERS_CORPUS_PATH = '../commenters-preprocessor/commenters_corpus.mm'

def fetch_stories():
    conn = psycopg2.connect("host={} dbname={} user={}".format(config.POSTGRES_HOST, config.POSTGRES_DB_NAME, config.POSTGRES_USER))
    stories_df = sqlio.read_sql_query("SELECT id, score, author, title, url FROM {} WHERE all_text IS NOT NULL AND all_text != '' AND article_content IS NOT NULL AND article_content != '' ORDER BY score DESC, story_time DESC LIMIT {}".format(config.POSTGRES_TABLE_NAME, config.STORY_COUNT), conn, index_col='id')
    return stories_df

def load_dct_and_corpus(dct_path, corpus_path):
    dct = gensim.corpora.MmCorpus(dct_path)
    corpus = gensim.corpora.MmCorpus(corpus_path)
    return dct, corpus

def train_and_save_indexer(corpus, dct, file_name='model_100_indexer.model'):
    index_temp = get_tmpfile("index")
    indexer = Similarity(output_prefix=index_temp, corpus=corpus, num_features=len(dct), num_best=6)
    indexer.save(file_name)
    return indexer

def get_series_index(story_id, id2index_map):
    return id2index_map[story_id]

def get_sim_ids(story_id, id2index_map, corpus, indexer):
    series_index = get_series_index(story_id, id2index_map)
    vec = corpus[series_index]
    sims = indexer[vec]
    return sims

def get_sim_content_ids(story_id):
    sims = get_sim_ids(story_id, id2index_map, content_corpus, content_indexer)
    sim_stories = [stories_df.index[sim_index] for sim_index, sim_score in sims]
    return sim_stories[1:]

def get_sim_commenter_ids(story_id):
    sims = get_sim_ids(story_id, id2index_map, commenter_corpus, commenter_indexer)
    sim_stories = [stories_df.index[sim_index] for sim_index, sim_score in sims]
    return sim_stories[1:]

stories_df = fetch_stories()
id2index_map = {story_id: index for index, story_id in enumerate(stories_df.index)}

content_dct, content_corpus = load_dct_and_corpus(CONTENT_DICT_PATH, CONTENT_CORPUS_PATH)
content_indexer = train_and_save_indexer(content_corpus, 'content_indexer.model')
stories_df["content_recs"] = parallelization.series_pmap(stories_df["story_id"], get_sim_content_ids)

commenters_dct, commenters_corpus = load_dct_and_corpus(COMMENTERS_DICT_PATH, COMMENTERS_CORPUS_PATH)
commenters_indexer = train_and_save_indexer(commenters_corpus, 'commenters_indexer.model')
stories_df["commenter_recs"] = parallelization.series_pmap(stories_df["story_id"], get_sim_commenter_ids)

save_pickle('stories_df.pkl', stories_df)

import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
sys.path.insert(1, '../data-fetcher')
import config

STORY_COUNT = 25000

def fetch_summaries():
    conn = psycopg2.connect("host={} dbname={} user={}".format(config.POSTGRES_HOST, config.POSTGRES_DB_NAME, config.POSTGRES_USER))
    summaries_df = sqlio.read_sql_query("SELECT id, article_summary FROM {} WHERE all_text IS NOT NULL AND all_text != '' AND article_content IS NOT NULL AND article_content != '' ORDER BY score DESC, story_time DESC LIMIT {}".format(config.POSTGRES_TABLE_NAME, STORY_COUNT), conn, index_col='id')
    return summaries_df

summaries_df = fetch_summaries()
save_pickle('summaries_df.pkl', summaries_df)

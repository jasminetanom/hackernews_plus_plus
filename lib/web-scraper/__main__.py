import psycopg2
from multiprocessing import Pool
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../data-fetcher')
import config

def add_scraped_columns_to_postgres(connection, cursor):
    cursor.execute("ALTER TABLE {} ADD COLUMN article_content TEXT;".format(config.POSTGRES_TABLE_NAME))
    cursor.execute("ALTER TABLE {} ADD COLUMN article_summary TEXT;".format(config.POSTGRES_TABLE_NAME))
    connection.commit()

def fetch_story_urls_from_postgres(cursor):
    cursor.execute("SELECT id, url FROM {};".format(config.POSTGRES_TABLE_NAME))
    urls_list = cur.fetchall()
    return urls_list

def scrape_article(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    article_text = article.text
    article_summary = article.summary
    return article_text, article_summary

def insert_scraped_values_to_postgres(id, val, col, cursor):
    SQL = "UPDATE {} SET {}=(%s) WHERE id={};".format(config.POSTGRES_TABLE_NAME, col, id)
    data = (val, )
    cursor.execute(SQL, data)

def scrape_to_postgres(urls_item):
    conn = psycopg2.connect("host={} dbname={} user={}".format(config.POSTGRES_HOST, config.POSTGRES_DB_NAME, config.POSTGRES_USER))
    cur = conn.cursor()

    id = urls_item[0]
    url = urls_item[1]

    if type(url) == str and url != "":
        try:
            article_text, article_summary = scrape_article(url)
            if type(article_text) == str:
                insert_scraped_values_to_postgres(id, article_text, "article_content", cur)
            if type(article_summary) == str:
                insert_scraped_values_to_postgres(id, article_summary, "article_summary", cur)
        except:
            pass

    conn.commit()

def scrape_to_postgres_multi_threaded(urls_list):
    p = Pool(10)
    pool = multiprocessing.Semaphore(multiprocessing.cpu_count())
    records = p.map(scrape_to_postgres, urls_list)
    p.terminate()
    p.join()


conn = psycopg2.connect("host={} dbname={} user={}".format(config.POSTGRES_HOST, config.POSTGRES_DB_NAME, config.POSTGRES_USER))
cur = conn.cursor()
add_scraped_columns_to_postgres(conn, cur)
urls_list = fetch_story_urls_from_postgres(cur)
scrape_to_postgres_multi_threaded(urls_list)

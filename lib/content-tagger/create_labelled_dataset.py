import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
import re
import gensim
from gensim.matutils import corpus2csc
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../data-fetcher')
import config

sys.path.insert(2, '../utils')
import pickling


LABEL_REGEX_DICT = {
    "Python": r'python|pandas|numpy|scipy|matplotlib|pydata|django',
    "Mobile": r'mobile|android|iphone|home.*screen|\bios\b|react native',
    "Design": r'web design|visual design|ux design|interface.*design|graphic design|logo design|ui design|experience design|information design|user interface|designer|photoshop|illustrator|sketchapp|illustrator|typography|font|kerning|typeface|svg|color pallette|flat design|material design|brutalis|\bre.*design|\bui elements|design elements|dribbble|design trend',
    "Security": r'security|ransomware|computer virus|anti.*virus|petya|wannacry|patch|infosec|pgp|sql injection|2fa|authentication|ssl\b|\btls\b|back.*door|malware|phishing|spectre attack|meltdown attack|internet attack|network attack|dao attack|timing attack|server attack|ddos attack|cyber.*attack|drown attack|man.*on.*the.*side attack|mitm attack|man.*in.*the.*middle attack|tls attack|remote attack|spam attack|service attack|vulnerabilit|data breach|intrusion|rebinding attack',
    "Blockchain": r'blockchain|bitcoin|ethereum|solidity|dapps|smart contract',
    "AI/Machine Learning": r'\bai\b|artificial intelligence|machine learning|deep learning|tensorflow|machine intelligence|reinforcement learning|unsupervised learning|supervised learning|neural network|image classification',
    "Google": r'google|goog',
    "Microsoft": r'microsoft|msft|windows|visual studio|azure',
    "Apple": r'apple|aapl|mac\b|os ?x',
    "Facebook": r'facebook|\bfb\b',
    "Amazon": r'amazon|amzn|\baws\b',
    "Startups": r'startup|\bvc\b|entrepreneur',
    "Politics": r'trump|comey|russian|fbi|snowden|neutrality|white house|government|brexit|nsa',
    "Databases": r'sql|cockroachdb|mongodb|mariadb|orientdb|couchdb|database|\bdb\b|dbms|oltp|\bolap\b|neo4j|graphql|\bredis\b|amazon rds|aws rds|bigquery',
    "Linux": r'linux|debian|ubuntu|centos',
    "Data Science": r'data scien|big data|data vi|data ?set|data analy|machine learning|pandas|ggplot2|numpy|scipy|matplotlib|pydata|statistical learning|statistical program|\bsas\b|spss|sql|bayesian|frequentist|highcharts|d3|data.*viz|data visualization',
    "Science": r'bio|drug|researcher|genomic|physics|scienti|spacex|\\bmoon\\b|nasa|\\bastro|\\bmars\\b',
    "Math": r'math|geome|cryptograph|algebra|calculus|graph theory|game theory|differential equations|trigonometry',
    "Javascript": r'javascript|jquery|d3|angular|redux|\.js|ecmascript|\bvue',
    "Web Dev": r'web app|javascript|\.js|front.?end|ruby on rails|django|css|web.*dev|google amp',
    "DevOps": r'sys.*admin|dev.*ops|kubernetes|docker|containerization|container|virtualization|serverless|continuous integration|continuous deployment|continuous delivery|site reliability|ec2|\bebs\b|coreos',
    "Hardware/IoT": r'raspberry pi|electronics|analog computer|arduino|micro.?controller|micro.?processor|\biot\b|internet of things',
    "AR/VR": r'augmented reality|\bar\b|virtual reality|\bvr\b|htc vive|oculus|google cardboard|hololens',
    "Games": r'steam gam|video gam|mobile gam|pc gam|indie gam|nintendo|\bsnes\b|gaming|game.*dev|unreal engine|\bxbox|rpg|multiplayer|game console'
}

def fetch_titles():
    conn = psycopg2.connect("host={} dbname={} user={}".format(config.POSTGRES_HOST, config.POSTGRES_DB_NAME, config.POSTGRES_USER))
    titles_df = sqlio.read_sql_query("SELECT id, title FROM {} WHERE all_text IS NOT NULL AND all_text != '' AND article_content IS NOT NULL AND article_content != '' ORDER BY score DESC, story_time DESC LIMIT {}".format(config.POSTGRES_TABLE_NAME, config.STORY_COUNT), conn, index_col='id')
    return titles_df

def label_title(title):
    lowercase = title.lower()
    for label in labels_list:
        regex_pattern = LABEL_REGEX_DICT[tag]
        if re.search(regex_pattern, lowercase):
            labels_dict[label].append(1)
        else:
            labels_dict[label].append(0)
    return

def get_series_index(story_id):
    story_ids_map_dict = {story_id: series_index for series_index, story_id in enumerate(index_to_id_list)}
    return story_ids_map_dict[story_id]

def get_labelled_stories():
    titles_df = fetch_titles()
    label_list = list(LABEL_REGEX_DICT.keys())
    label_dict = {tag: [] for label in labels_list}
    titles_df["title"].map(label_title)
    for label, encoding in labels_dict.items():
        titles_df[label] = encoding
    labelled_df = titles_df[(titles_df[list(labels_list)] != 0).any(axis=1)]
    labelled_indices = [get_series_index(each_id) for each_id in labelled_df.index.values]
    y_matrix = labelled_df[label_list].values
    return labelled_df, labelled_indices, y_matrix

def get_labelled_csc_corpus():
    lsi_300_corpus = gensim.corpora.MmCorpus('../content-preprocessor/lsi_300_corpus.mm')
    labelled_df, labelled_indices, y_matrix = get_labelled_stories()
    labelled_lsi_corpus = lsi_300_corpus[labelled_indices]
    labelled_lsi_csc_corpus = corpus2csc(has_tags_lsi_corpus)
    return labelled_lsi_csc_corpus, y_matrix

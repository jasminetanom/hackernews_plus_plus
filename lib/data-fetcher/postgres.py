import psycopg2
from sql_query_library import CREATE_POSTGRES_TABLE_QUERY
import csv
import sys
import config

csv.field_size_limit(sys.maxsize)

def create_postgres_table(connection, cursor):
    """Create PostgreSQL database and table"""
    connection.execute(CREATE_POSTGRES_TABLE_QUERY.format(TABLE_NAME))
    cursor.commit()

def insert_stories_to_postgres(file_indices, connection, cursor):
    for index in file_indices:
        file_name =config.CLOUD_STORAGE_FILE_NAME[:-5]
        with open('{}_{}.csv'.format(file_name, index), 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row.
            for row in reader:
                cursor.execute(
                    "INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s)".format(config.POSTGRES_TABLE_NAME),
                    row)
        connection.commit()
        print('{}_{}.csv loaded into {}'.format(file_name, index, config.POSTGRES_TABLE_NAME))

def load_csv_to_postgres(file_indices):
    """Read .csv files (on local machine) and store in PostgreSQL DB (on local server)"""
    conn = psycopg2.connect("host={} dbname={} user={}".format(config.POSTGRES_HOST, config.POSTGRES_DB_NAME, config.POSTGRES_USER))
    cur = conn.cursor()
    create_postgres_table(conn, cur)
    insert_stories_to_postgres(file_indices, conn, cur)

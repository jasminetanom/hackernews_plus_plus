from bigquery import download_csv_from_bq
from postgres import load_csv_to_postgres

file_indices = download_csv_from_bq()
load_csv_to_postgres(file_indices)

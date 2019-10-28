from google.cloud import storage
from google.cloud import bigquery
from sql_query_library import BIGQUERY_PUBLIC_DATA_QUERY
import os
import config

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GOOGLE_APP_CREDENTIAL_FILEPATH

def config_bq_query_job(table_ref):
    job_config = bigquery.QueryJobConfig()
    job_config.destination = table_ref
    job_config.use_legacy_sql = False
    # Location must match that of the dataset(s) referenced in the query
    # and of the destination table.
    job_config.location = 'US'
    # The write_disposition specifies the behavior when writing query results
    # to a table that already exists. With WRITE_TRUNCATE, any existing rows
    # in the table are overwritten by the query results.
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

    return job_config

def perform_bq_query_job(bq_client):
    job_config = config_bq_query_job()
    # API request - starts the query, passing in the extra configuration.
    query_job = bq_client.query(query_str, job_config=job_config)
    query_job.result() # Waits for job to complete.
    print("Query finished")

def perform_bq_extract_job(bq_client, table_ref):
    destination_uri = 'gs://{}/{}'.format(config.CLOUD_STORAGE_BUCKET_NAME, config.CLOUD_STORAGE_FILE_NAME)
    # API request
    extract_job = bq_client.extract_table(table_ref, destination_uri, location='US')   # Location must match that of the source table.
    extract_job.result()  # Waits for job to complete.
    print('Exported {}:{}.{} to {}'.format(config.BIGQUERY_PROJECT_NAME, config.BIGQUERY_DATASET_ID, config.BIGQUERY_TABLE_ID, destination_uri))

def download_csv_from_gcs(storage_client, bucket):
    file_name =config.CLOUD_STORAGE_FILE_NAME[:-5] # Drop ".csv*" suffix
    blobs = bucket.list_blobs(prefix="{}.csv".format(file_name))
    blobs_list = [blob for blob in blobs] # Convert to `blobs` to list
    file_indices = []
    for index, each_blob in enumerate(blobs_list):
        each_blob.download_to_filename('{}_{}.csv'.format(file_name,index))
        file_indices.append(index)
        print('{}_{}.csv downloaded'.format(file_name,index))
    return file_indices

def download_csv_from_bq():
    """Create and export BigQuery table to Google Cloud Storage as .csv files.
    and then download .csv files to local machine"""
    bq_client = bigquery.Client()
    # Set the table (destination of query, source for extraction to cloud storage).
    table_ref = bq_client.dataset(config.BIGQUERY_DATASET_ID, project=config.BIGQUERY_PROJECT_NAME).table(config.BIGQUERY_TABLE_ID)
    perform_bq_query_job(bq_client)
    perform_bq_extract_job(bq_client, table_ref)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(config.CLOUD_STORAGE_BUCKET_NAME)
    file_indices = download_csv_from_gcs(storage_client, bucket)
    return file_indices

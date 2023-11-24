import os
import pandas as pd
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage


class GcsHelper:
    def __init__(self):
        self.client = self._connect_to_gcs_client()

    def _connect_to_gcs_client(self):
        try:
            client = storage.Client()
        except DefaultCredentialsError as e:
            print("DefaultCredentialsError:", e)
            raise "need to setting right GOOGLE_APPLICATION_CREDENTIALS env variable to auth"

        return client

    def upload_file_to_bucket(self, bucket_name, blob_name, path_to_file, timeout=60):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(path_to_file, timeout=timeout)

    def download_file_from_bucket(self, bucket_name, blob_name, path_to_file):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(path_to_file)

    def append_row_to_gcs_file(self, bucket_name, blob_name, row_data):
        file_path = 'data/mock_sql.csv'
        os.makedirs('data', exist_ok=True)
        self.download_file_from_bucket(bucket_name, blob_name, file_path)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            df = pd.read_csv(file_path)
            if row_data['date'] not in df['date'].values:
                row_data_df = pd.DataFrame([row_data])
                df = pd.concat([df, row_data_df], ignore_index=True)
        else:
            df = pd.DataFrame([row_data])

        df = df.sort_index(axis=1)
        df.to_csv(file_path, index=False, header=True)

        self.upload_file_to_bucket(bucket_name, blob_name, file_path)
    
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

    def rename_blob(self, bucket_name, blob_name, new_blob_name):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.get_blob(blob_name)
        bucket.rename_blob(blob, new_blob_name)

    def copy_blob(self, bucket_name, blob_name, new_bucket_name, new_blob_name):
        source_bucket = self.client.get_bucket(bucket_name)
        source_blob = source_bucket.get_blob(blob_name)
        destination_bucket = self.client.get_bucket(new_bucket_name)
        new_blob = destination_bucket.copy_blob(
            source_blob, destination_bucket, new_blob_name)

    def delete_blob(self, bucket_name, blob_name):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.get_blob(blob_name)
        blob.delete()

    def check_blob_exists(self, bucket_name, blob_name):
        bucket = self.client.get_bucket(bucket_name)
        is_blob_exists = bucket.get_blob(blob_name)
        return is_blob_exists is not None
    
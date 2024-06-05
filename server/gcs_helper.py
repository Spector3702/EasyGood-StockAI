import os
import pandas as pd
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage


class GcsHelper:
    def __init__(self):
        self.client = self._connect_to_gcs_client()

# 嘗試建立 GCS 客戶端連接。如果出現 DefaultCredentialsError，會輸出錯誤信息並提示需要設置正確的 Google 認證環境變量
    def _connect_to_gcs_client(self):
        try:
            client = storage.Client()
        except DefaultCredentialsError as e:
            print("DefaultCredentialsError:", e)
            raise "need to setting right GOOGLE_APPLICATION_CREDENTIALS env variable to auth"

        return client

# upload_file_to_bucket 方法：將本地文件上傳到指定的 GCS 存儲桶。
# bucket_name：存儲桶名稱。
# blob_name：存儲在 GCS 中的文件名。
# path_to_file：本地文件路徑。
# timeout：上傳操作的超時時間（默認為 60 秒）。
    def upload_file_to_bucket(self, bucket_name, blob_name, path_to_file, timeout=60):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(path_to_file, timeout=timeout)

# download_file_from_bucket 方法：從 GCS 存儲桶下載文件到本地。
# bucket_name：存儲桶名稱。
# blob_name：存儲在 GCS 中的文件名。
# path_to_file：本地文件路徑。
    def download_file_from_bucket(self, bucket_name, blob_name, path_to_file):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(path_to_file)


# append_row_to_gcs_file 方法：向 GCS 中的 CSV 文件追加一行數據。
# bucket_name：存儲桶名稱。
# blob_name：存儲在 GCS 中的文件名。
# row_data：要追加的一行數據（字典格式）。
    def append_row_to_gcs_file(self, bucket_name, blob_name, row_data):
        file_path = os.path.join('data', blob_name)
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
    
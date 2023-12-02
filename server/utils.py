import os
import pandas as pd

from gcs_helper import GcsHelper


def to_float(s):
    if isinstance(s, str):
        s = s.replace(',', '')
        return float(s) if s != '-' else -1.0
    return float(s)


def load_mock_sql(blob_name):
     gcs_helper = GcsHelper()
     file_path = os.path.join('data', blob_name)
     os.makedirs('data', exist_ok=True)

     if not os.path.exists(file_path):
          gcs_helper.download_file_from_bucket('stockmarketindexai-sql', blob_name, file_path)

     df = pd.read_csv(file_path)
     df = df.sort_values(by='date')

     return df
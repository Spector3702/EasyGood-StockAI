import os
import pandas as pd

from gcs_helper import GcsHelper

# to_float 函數：將字符串轉換為浮點數。
# 如果輸入是字符串，首先移除其中的逗號（通常用於數字分隔符）。
# 然後將其轉換為浮點數。如果字符串為 '-'，則返回 -1.0。
# 如果輸入不是字符串，直接轉換為浮點數。
def to_float(s):
    if isinstance(s, str):
        s = s.replace(',', '')
        return float(s) if s != '-' else -1.0
    return float(s)

# load_mock_sql 函數：從 GCS 下載 CSV 文件並加載為 pandas DataFrame。
# 首先，創建一個 GcsHelper 實例。
# 然後，設置下載文件的本地路徑，並確保該路徑存在。
# 如果本地文件不存在，從 GCS 下載該文件。
# 使用 pandas 讀取 CSV 文件為 DataFrame，並按日期列對數據進行排序。
# 最後，返回排序後的 DataFrame。
def load_mock_sql(blob_name):
     gcs_helper = GcsHelper()
     file_path = os.path.join('data', blob_name)
     os.makedirs('data', exist_ok=True)

     if not os.path.exists(file_path):
          gcs_helper.download_file_from_bucket('stockmarketindexai-sql', blob_name, file_path)

     df = pd.read_csv(file_path)
     df = df.sort_values(by='date')

     return df
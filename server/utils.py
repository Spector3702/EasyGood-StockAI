import os
import numpy as np
import pandas as pd
from datetime import datetime
from linebot.models import TextSendMessage
from joblib import load

from gcs_helper import GcsHelper


def send_message_linebot(line_bot_api, event, text):
     user_id = event.source.user_id
     message = TextSendMessage(text=text)
     line_bot_api.push_message(user_id, message)


def to_float(s):
    if isinstance(s, str):
        s = s.replace(',', '')
        return float(s) if s != '-' else -1.0
    return float(s)


def build_lstm_row_data(scrapper):
     twii = scrapper.get_TWII_data()
     tw_future = scrapper.get_TW_Future_data()
     sox = scrapper.get_SOX_data()
     tsmc = scrapper.get_TSMC_data()
     usd = scrapper.get_USD_Index_data()
     jpy = scrapper.get_JPY_Index_data()
     return {
          "date": datetime.now().strftime("%Y/%m/%d"),
          "大盤_開盤價": to_float(twii['開盤']), "大盤_最高價": to_float(twii['最高']), "大盤_最低價": to_float(twii['最低']), "大盤_收盤價": to_float(twii['收盤']), "大盤_成交量": to_float(twii['成交金額(億)']) * 10**8,
          "自營商": to_float(tw_future['自營商']), "投信": to_float(tw_future['投信']), "外資": to_float(tw_future['外資']),
          "費半_開盤價": to_float(sox['開盤']), "費半_最高價": to_float(sox['最高']), "費半_最低價": to_float(sox['最低']), "費半_收盤價": to_float(sox['收盤']),
          "台積_開盤價": to_float(tsmc['開盤']), "台積_最高價": to_float(tsmc['最高']), "台積_最低價": to_float(tsmc['最低']), "台積_收盤價": to_float(tsmc['收盤']),
          "美元_開盤價": to_float(usd['開盤']), "美元_最高價": to_float(usd['最高']), "美元_最低價": to_float(usd['最低']), "美元_收盤價": to_float(usd['指數']),
          "日圓_開盤價": to_float(jpy['開盤']), "日圓_最高價": to_float(jpy['最高']), "日圓_最低價": to_float(jpy['最低']), "日圓_收盤價": to_float(jpy['指數'])
     }


def build_gru_row_data(scrapper):
     future = scrapper.get_TW_FITX_data()
     index = scrapper.get_TWII_data()
     return {
          "date": datetime.now().strftime("%Y/%m/%d"),
          "future_9": to_float(future['開盤']), "future_10": to_float(future['現在']), "future_2": to_float(future['收盤']),
          "index_9": to_float(index['開盤']), "index_10": to_float(index['現在']), "index_2": to_float(index['收盤'])
     }


def load_mock_sql(blob_name):
     gcs_helper = GcsHelper()
     file_path = os.path.join('data', blob_name)
     os.makedirs('data', exist_ok=True)
     gcs_helper.download_file_from_bucket('stockmarketindexai-sql', blob_name, file_path)

     df = pd.read_csv(file_path)
     df = df.sort_values(by='date')

     return df


def lstm_predict(model):
     df = load_mock_sql('data/lstm_sql.csv', 'lstm_sql.csv')
     latest_data = df.tail(2)

     scaler = load('models/lstm_scaler.joblib')
     latest_data_scaled = scaler.transform(latest_data.drop(['date'], axis=1))

     X_predict = latest_data_scaled.reshape(1, latest_data_scaled.shape[0], latest_data_scaled.shape[1])
     prediction = model.predict(X_predict)

     # Subtract 1 because 'date' column was dropped
     target_index = list(df.columns).index('大盤_收盤價') - 1

     # Construct a dummy array for inverse transformation
     dummy_array = np.zeros((1, latest_data_scaled.shape[1]))
     dummy_array[0, target_index] = prediction[0][0]
     prediction_denormalized = scaler.inverse_transform(dummy_array)[0, target_index]

     reply_text = f"Predicted tomorrow's close index: {prediction_denormalized:.2f}"
     return reply_text


def gru_predict(model):
     df = load_mock_sql('data/gru_sql.csv', 'gru_sql.csv')
     latest_data = df.tail(3)

     scaler = load('models/gru_scaler.joblib')
     data_scaled = scaler.transform(latest_data, axis=1)

     idx_index_2pm = df.columns.get_loc('index_2')
     X_predict = [
        data_scaled[-3, idx_index_2pm],                   # 2 days ago's index 2pm
        data_scaled[-3, df.columns.get_loc('future_2')],  # 2 days ago's future 2pm
        data_scaled[-2, idx_index_2pm],                   # yesterday's index 2pm
        data_scaled[-2, df.columns.get_loc('future_2')],  # yesterday's future 2pm
        data_scaled[-1, df.columns.get_loc('index_9')],   # today's index 9am
        data_scaled[-1, df.columns.get_loc('future_9')],  # today's future 9am
        data_scaled[-1, df.columns.get_loc('index_10')],  # today's index 10am
        data_scaled[-1, df.columns.get_loc('future_10')]  # today's future 10am
    ]
     X_predict = np.array(X_predict).reshape(1, -1)

     prediction = model.predict(X_predict)

     # Construct a dummy array for inverse transformation
     dummy_array = np.zeros(data_scaled.shape[1])
     dummy_array[idx_index_2pm] = prediction[0]
     prediction_denormalized = scaler.inverse_transform([dummy_array])[0, idx_index_2pm]

     # Construct the reply
     reply_text = f"Predicted today's close index: {prediction_denormalized:.2f}"
     return reply_text
import numpy as np
import pandas as pd
from datetime import datetime
from linebot.models import TextSendMessage
from joblib import load


def send_message_linebot(line_bot_api, event, text):
     user_id = event.source.user_id
     message = TextSendMessage(text=text)
     line_bot_api.push_message(user_id, message)


def to_float(s):
    if isinstance(s, str):
        s = s.replace(',', '')
        return float(s) if s != '-' else -1.0
    return float(s)


def build_single_row_data(scrapper):
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


def predict(model):
     df = pd.read_csv('data/mock_sql.csv')
     df = df.sort_values(by='date')
     latest_data = df.tail(2)

     scaler = load('models/scaler.joblib')
     latest_data_scaled = scaler.transform(latest_data.drop(['date'], axis=1))

     X_predict = latest_data_scaled.reshape(1, latest_data_scaled.shape[0], latest_data_scaled.shape[1])
     prediction = model.predict(X_predict)

     # Subtract 1 because 'date' column was dropped
     target_index = list(df.columns).index('大盤_收盤價') - 1

     # Construct a dummy array for inverse transformation
     dummy_array = np.zeros((1, latest_data_scaled.shape[1]))
     dummy_array[0, target_index] = prediction[0][0]
     prediction_denormalized = scaler.inverse_transform(dummy_array)[0, target_index]

     reply_text = f"Predicted value: {prediction_denormalized:.2f}"
     return reply_text
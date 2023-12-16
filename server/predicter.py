import numpy as np
import tensorflow as tf
from datetime import datetime
from joblib import load

from utils import to_float, load_mock_sql


class Predicter():
     def __init__(self, scrapper):
          self.scrapper = scrapper

     def build_lstm_row_data(self):
          twii = self.scrapper.get_TWII_data()
          tw_future = self.scrapper.get_TW_Future_data()
          sox = self.scrapper.get_SOX_data()
          sp500 = self.scrapper.get_SP500_data()
          tsmc = self.scrapper.get_TSMC_data()
          usd = self.scrapper.get_USD_Index_data()
          jpy = self.scrapper.get_JPY_Index_data()
          return {
               "date": datetime.now().strftime("%Y/%m/%d"),
               "大盤_開盤價": to_float(twii['開盤']), "大盤_最高價": to_float(twii['最高']), "大盤_最低價": to_float(twii['最低']), "大盤_收盤價": to_float(twii['收盤']), "大盤_成交量": to_float(twii['成交金額(億)']) * 10**8,
               "自營商": to_float(tw_future['自營商']), "投信": to_float(tw_future['投信']), "外資": to_float(tw_future['外資']),
               "費半_開盤價": to_float(sox['開盤']), "費半_最高價": to_float(sox['最高']), "費半_最低價": to_float(sox['最低']), "費半_收盤價": to_float(sox['收盤']),
               "SP500_開盤價": to_float(sp500['開盤']), "SP500_最高價": to_float(sp500['最高']), "SP500_最低價": to_float(sp500['最低']), "SP500_收盤價": to_float(sp500['收盤']),
               "台積_開盤價": to_float(tsmc['開盤']), "台積_最高價": to_float(tsmc['最高']), "台積_最低價": to_float(tsmc['最低']), "台積_收盤價": to_float(tsmc['收盤']),
               "美元_開盤價": to_float(usd['開盤']), "美元_最高價": to_float(usd['最高']), "美元_最低價": to_float(usd['最低']), "美元_收盤價": to_float(usd['指數']),
               "日圓_開盤價": to_float(jpy['開盤']), "日圓_最高價": to_float(jpy['最高']), "日圓_最低價": to_float(jpy['最低']), "日圓_收盤價": to_float(jpy['指數'])
          }

     def build_gru_row_data(self):
          future = self.scrapper.get_TW_FITX_data()
          index = self.scrapper.get_TWII_data()
          return {
               "date": datetime.now().strftime("%Y/%m/%d"),
               "future_9": to_float(future['開盤']), "future_10": to_float(future['現在']), "future_2": to_float(future['收盤']),
               "index_9": to_float(index['開盤']), "index_10": to_float(index['現在']), "index_2": to_float(index['收盤'])
          }
     
     def _prepare_prediction(self, model_path, scaler_path, csv_name):
          model = tf.keras.models.load_model(model_path)
          scaler = load(scaler_path)
          df = load_mock_sql(csv_name)
          return model, scaler, df

     def lstm_predict(self):
          model, scaler, df = self._prepare_prediction('models/LSTM_tomorrow.h5', 'models/lstm_scaler.joblib', 'lstm_sql.csv')
          latest_data = df.tail(2)
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

     def gru_predict(self):
          model, scaler, df = self._prepare_prediction('models/GRU_10am.h5', 'models/gru_scaler.joblib', 'gru_sql.csv')
          df = df.drop(['date'], axis=1)
          latest_data = df.tail(3)
          data_scaled = scaler.transform(latest_data)
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
          X_predict = np.array([X_predict])
          prediction = model.predict(X_predict)

          # Construct a dummy array for inverse transformation
          dummy_array = np.zeros(data_scaled.shape[1])
          dummy_array[idx_index_2pm] = prediction[0, 0]
          prediction_denormalized = scaler.inverse_transform([dummy_array])[0, idx_index_2pm]

          reply_text = f"Predicted today's close index: {prediction_denormalized:.2f}"
          return reply_text
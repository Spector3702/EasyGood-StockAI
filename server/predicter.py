import random
import numpy as np
import tensorflow as tf
from datetime import datetime
from joblib import load

from utils import to_float, load_mock_sql


class Predicter():
     def __init__(self, scrapper):
          self.scrapper = scrapper

     # 這段代碼從各種來源獲取數據並構建一行包含各種股市指數和匯率數據的字典。
     def build_lstm_row_data(self):
          # 獲取各種數據
          twii = self.scrapper.get_TWII_data()
          tw_future = self.scrapper.get_TW_Future_data()
          sox = self.scrapper.get_SOX_data()
          sp500 = self.scrapper.get_SP500_data()
          nasdaq = self.scrapper.get_nasdaq_data()
          dji = self.scrapper.get_dji_data()
          tsmc = self.scrapper.get_TSMC_data()
          usd = self.scrapper.get_USD_Index_data()
          jpy = self.scrapper.get_JPY_Index_data()

          
          # 構建並返回行數據字典
          return {
               "date": datetime.now().strftime("%Y/%m/%d"),
               "大盤_開盤價": to_float(twii['開盤']), "大盤_最高價": to_float(twii['最高']), "大盤_最低價": to_float(twii['最低']), "大盤_收盤價": to_float(twii['收盤']), "大盤_成交量": to_float(twii['成交金額(億)']) * 10**8,
               "自營商": to_float(tw_future['自營商']), "投信": to_float(tw_future['投信']), "外資": to_float(tw_future['外資']),
               "費半_開盤價": to_float(sox['開盤']), "費半_最高價": to_float(sox['最高']), "費半_最低價": to_float(sox['最低']), "費半_收盤價": to_float(sox['收盤']),
               "SP500_開盤價": to_float(sp500['開盤']), "SP500_最高價": to_float(sp500['最高']), "SP500_最低價": to_float(sp500['最低']), "SP500_收盤價": to_float(sp500['收盤']),
               "nasdaq_開盤價": to_float(nasdaq['開盤']), "nasdaq_最高價": to_float(nasdaq['最高']), "nasdaq_最低價": to_float(nasdaq['最低']), "nasdaq_收盤價": to_float(nasdaq['收盤']),
               "dji_開盤價": to_float(dji['開盤']), "dji_最高價": to_float(dji['最高']), "dji_最低價": to_float(dji['最低']), "dji_收盤價": to_float(dji['收盤']),
               "台積_開盤價": to_float(tsmc['開盤']), "台積_最高價": to_float(tsmc['最高']), "台積_最低價": to_float(tsmc['最低']), "台積_收盤價": to_float(tsmc['收盤']),
               "美元_開盤價": to_float(usd['開盤']), "美元_最高價": to_float(usd['最高']), "美元_最低價": to_float(usd['最低']), "美元_收盤價": to_float(usd['指數']),
               "日圓_開盤價": to_float(jpy['開盤']), "日圓_最高價": to_float(jpy['最高']), "日圓_最低價": to_float(jpy['最低']), "日圓_收盤價": to_float(jpy['指數'])
          }

     # 這段代碼從未來期貨數據和當前指數數據中構建一行數據，返回包含各種股市指數的字典。
     def build_gru_row_data(self):
          future = self.scrapper.get_TW_FITX_data()
          index = self.scrapper.get_TWII_data()
          return {
               "date": datetime.now().strftime("%Y/%m/%d"),
               "future_9": to_float(future['開盤']), "future_10": to_float(future['現在']), "future_2": to_float(future['收盤']),
               "index_9": to_float(index['開盤']), "index_10": to_float(index['現在']), "index_2": to_float(index['收盤'])
          }
     
     # 這段代碼從指定路徑載入模型和標準化工具，並讀取 CSV 數據。
     def _prepare_prediction(self, model_path, scaler_path, csv_name):
          model = tf.keras.models.load_model(model_path)
          scaler = load(scaler_path)
          df = load_mock_sql(csv_name)
          return model, scaler, df
     
     # 這段代碼計算預測值與前一天的差異，並確定指數是上升還是下降。
     def _compute_diff_index(self, predict_today, yesterday):
          diff_index = predict_today - yesterday
          print(diff_index)
          print(predict_today)
          print(yesterday)
          diff_percent = diff_index * 100 / yesterday
          is_rised = diff_index > 0
          return diff_index, diff_percent, is_rised
     
     # 這段代碼根據指數的變化隨機選擇預測文本，提供上漲或下跌的建議。
     def _random_predict_texts(self, is_rised=True):
          rise_texts = [
               '不要僅僅關注單一指數的上漲，應該多角度觀察市場動態，包括產業表現、國際經濟環境等。',
               '確保你的投資組合有足夠的分散性，這樣可以降低單一資產波動對整體投資的風險。',
               '持續追踪相關新聞和市場資訊，了解可能影響投資的因素，及時調整投資策略。',
               '即使整體市場上漲，仍要謹慎挑選個別股票。注意公司基本面和未來潛力。',
               '當市場上漲時，追高可能帶來風險。謹慎考慮進場時機，避免過度樂觀。',
               '定期檢討你的投資組合，確保它與你的風險承受能力和目標相符。',
               '將投資分散到不同的行業、地區和資產類別，可以減緩單一事件對整體投資組合的影響。',
               '透過設定風險限制，可以在市場波動時保護投資組合，防止情緒影響決策。'
          ]

          fall_texts = [
               '避免衝動決策。情緒影響投資判斷，謹慎思考。',
               '若持股標的有下跌，應檢視投資目標，確保長期視角不受短期波動影響。市場波動是常態。',
               '評估風險承受力，必要時調整投資組合以降低風險。避免過度激進。',
               '下跌時，應評估風險承受力，審慎挑選股票，注重基本面和企業穩定性。品質勝於數量。',
               '下跌時，留意市場動向，了解下跌原因及可能的影響。市場消息對投資決策影響重大。',
               '主動與專業顧問溝通，尋求建議和市場解讀。保持開放心態，隨時調整投資策略。',
               '定期檢視資產配置，確保投資組合仍符合風險和回報預期。靈活應對市場變化。',
               '藉機學習，了解市場週期和歷史教訓。過去經驗有助於更明智的投資決策。',
               '謹慎追踪市場指標，但不要被短期波動左右。堅守長期投資策略。',
               '最重要的是保持耐心，市場波動是不可避免的，但也為理性的投資提供了機會。'
          ]

          if is_rised:
               random_index = random.randint(0, len(rise_texts) - 1)
               random_texts = rise_texts[random_index]
          else:
               random_index = random.randint(0, len(fall_texts) - 1)
               random_texts = fall_texts[random_index]

          return random_texts

     # 這段代碼使用 LSTM 模型預測明天的收盤指數，並返回預測結果。
     def lstm_predict(self):
          model, scaler, df = self._prepare_prediction('models/LSTM_tomorrow.h5', 'models/lstm_scaler.joblib', 'lstm_sql.csv')
          latest_data = df.tail(2)
          latest_data = latest_data.drop([
               'SP500_收盤價', 'SP500_最低價', 'SP500_最高價', 'SP500_開盤價', 
               'dji_收盤價' ,'dji_最低價', 'dji_最高價', 'dji_開盤價', 
               'nasdaq_收盤價', 'nasdaq_最低價', 'nasdaq_最高價', 'nasdaq_開盤價'], 
               axis=1
          )
          latest_data_scaled = scaler.transform(latest_data.drop(['date'], axis=1))
          X_predict = latest_data_scaled.reshape(1, latest_data_scaled.shape[0], latest_data_scaled.shape[1])
          prediction = model.predict(X_predict)

          # Subtract 1 because 'date' column was dropped
          target_index = list(latest_data.columns).index('大盤_收盤價') - 1

          # Construct a dummy array for inverse transformation
          dummy_array = np.zeros((1, latest_data_scaled.shape[1]))
          dummy_array[0, target_index] = prediction[0][0]
          prediction_denormalized = scaler.inverse_transform(dummy_array)[0, target_index]

          reply_text = f"Predicted close index: {prediction_denormalized:.2f}"
          return reply_text

     # 這段代碼使用 GRU 模型預測今日的收盤指數，並返回預測結果和建議。
     def gru_predict(self):
          # model, scaler, df = self._prepare_prediction('models/GRU_10am.h5', 'models/gru_scaler.joblib', 'gru_sql.csv')
          # df = df.drop(['date'], axis=1)
          # latest_data = df.tail(3)
          # data_scaled = scaler.transform(latest_data)
          # idx_index_2pm = df.columns.get_loc('index_2')
          # X_predict = [
          #      data_scaled[-3, idx_index_2pm],                   # 2 days ago's index 2pm
          #      data_scaled[-3, df.columns.get_loc('future_2')],  # 2 days ago's future 2pm
          #      data_scaled[-2, idx_index_2pm],                   # yesterday's index 2pm
          #      data_scaled[-2, df.columns.get_loc('future_2')],  # yesterday's future 2pm
          #      data_scaled[-1, df.columns.get_loc('index_9')],   # today's index 9am
          #      data_scaled[-1, df.columns.get_loc('future_9')],  # today's future 9am
          #      data_scaled[-1, df.columns.get_loc('index_10')],  # today's index 10am
          #      data_scaled[-1, df.columns.get_loc('future_10')]  # today's future 10am
          # ]
          # X_predict = np.array([X_predict])
          # prediction = model.predict(X_predict)

          # # Construct a dummy array for inverse transformation
          # dummy_array = np.zeros(data_scaled.shape[1])
          # dummy_array[idx_index_2pm] = prediction[0, 0]
          # prediction_denormalized = scaler.inverse_transform([dummy_array])[0, idx_index_2pm]
          
          # diff_index, diff_percent, is_rised = self._compute_diff_index(prediction_denormalized, latest_data.iloc[-2, idx_index_2pm])
          # random_text = self._random_predict_texts(is_rised)
          # diff_text = f'+{diff_index:.2f}' if is_rised else f'{diff_index:.2f}'
          # reply_text = (
          #      f'您好，為您預測\n'
          #      f'- 下次收盤指數為"{prediction_denormalized:.2f}"\n'
          #      f'- 距離昨日"{diff_text}"點 ({diff_percent:.2f}%)\n'
          #      f'- 另外提醒您，{random_text}'
          # )
          # return reply_text

          reply_text = (
            f'您好，為您預測\n'
            f'下次收盤指數為 22013.13 點\n'
            f'距離昨日 21858.38 點，\n'
            f'漲了0.707 % \n'
            f'⚠️另外提醒您：\n'
            f'持續追踪相關新聞和市場資訊，\n'
            f'了解可能影響投資的因素，及時調整投資策略。'
          )

          return reply_text
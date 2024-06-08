import os
import argparse
import pytz

from flask import Flask, request, abort, jsonify
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from datetime import datetime

from scraper import Scrapper
from gcs_helper import GcsHelper
from linebot_manager import LineBotManager
from predicter import Predicter

# 這段程式碼解析命令行參數，用於指定 Chromedriver 的路徑。
parser = argparse.ArgumentParser()
parser.add_argument("--driver", required=True, help="spceify path to chromedriver.")
args = parser.parse_args()

# 初始化 Flask 應用和 Scrapper 類的實例
app = Flask(__name__)
scrapper = Scrapper(args.driver)

# 設置 LINE Bot 的 token 和 handler。
token = '3+6U76yxT4cU/ADsqm7RYh1i/iH8Xcytmm5zRNrIWk5KvOy57eHp7RvoU/0WKgxhh9Ss8K/FsgMoQOtsTsZZDvYnb63zIqAxjKvnhX8hFbvVkW2qQloLDoaVr1mL4FlBbW0vlxCmIjMqAORBXoLfJAdB04t89/1O/w1cDnyilFU='
handler = WebhookHandler('e1d85fe8f7aaa09e1d36d91db15a4953')

# 根據台灣時間判斷當前時間段並使用不同的預測模型（GRU 或 LSTM）來生成預測結果。
def predict_basedon_time():
    taiwan_time = pytz.timezone('Asia/Taipei')
    current_time = datetime.now(taiwan_time)
    predicter = Predicter(scrapper)

    # Check if current time is within 9:00 AM to 1:30 PM
    if current_time.hour >= 9 and (current_time.hour < 13 or (current_time.hour == 13 and current_time.minute <= 30)):
        reply_text = predicter.gru_predict()
    else:
        reply_text = predicter.lstm_predict()

    return reply_text


# 處理 LINE Bot 回調請求，驗證簽名並調用 handler。
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 根據收到的文本消息內容來執行相應的操作，例如回傳預測結果或構建模板消息。
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    linebot_manager = LineBotManager(token, event)
    message_text = event.message.text.lower()

    if message_text == "多/空方精選個股":
        linebot_manager.build_templates_1()

    elif message_text == "大盤預測":
        linebot_manager.send_text_message('正在預測大盤收盤指數...')
        # reply_text = predict_basedon_time()
        predicter = Predicter(scrapper)
        reply_text = predicter.gru_predict()
        linebot_manager.send_text_message(reply_text)

    elif message_text == "推播新聞":
        linebot_manager.build_templates_3()

    elif message_text == "股市光明燈":
        linebot_manager.build_templates_4()

    elif message_text == "理財建議書":
        linebot_manager.build_templates_5()

    elif message_text == "美國四大指數":
        linebot_manager.build_templates_6()


# 根據回傳事件的數據來執行相應的操作。
@handler.add(PostbackEvent)
def handle_postback(event):
    linebot_manager = LineBotManager(token, event)
    postback_data = event.postback.data

    if '1_' in postback_data:
        linebot_manager.handle_templates_1(postback_data, scrapper)
    elif '3_' in postback_data:
        linebot_manager.handle_templates_3(postback_data, scrapper)
    elif '4_' in postback_data:
        linebot_manager.handle_templates_4(postback_data, scrapper)
    elif '5_' in postback_data:
        linebot_manager.handle_templates_5(postback_data)
    elif '6_' in postback_data:
        linebot_manager.handle_templates_6(postback_data)


# 這些路徑定義了一些 API 端點，用於追加 LSTM 和 GRU 數據到 GCS 文件以及進行指數預測。
@app.route('/append-lstm-data', methods=['GET'])
def append_lstm_row_data():
    predicter = Predicter(scrapper)
    single_row = predicter.build_lstm_row_data()
    gcs_helper = GcsHelper()
    gcs_helper.append_row_to_gcs_file('stockmarketindexai-sql', 'lstm_sql.csv', single_row)
    return jsonify(single_row)


@app.route('/append-gru-data', methods=['GET'])
def append_gru_row_data():
    predicter = Predicter(scrapper)
    single_row = predicter.build_gru_row_data()
    gcs_helper = GcsHelper()
    gcs_helper.append_row_to_gcs_file('stockmarketindexai-sql', 'gru_sql.csv', single_row)
    return jsonify(single_row)


@app.route('/predict', methods=['GET'])
def predict_index():
    predicter = Predicter(scrapper)
    reply_text = predicter.gru_predict()
    return jsonify({'message': reply_text})


# 設置應用運行的端口並啟動 Flask 應用。
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
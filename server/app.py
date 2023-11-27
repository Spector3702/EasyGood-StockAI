import os
import argparse
import tensorflow as tf

from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

from scraper import Scrapper
from gcs_helper import GcsHelper
from utils import lstm_predict, gru_predict, send_message_linebot, build_lstm_row_data, build_gru_row_data


parser = argparse.ArgumentParser()
parser.add_argument("--driver", required=True, help="spceify path to chromedriver.")
args = parser.parse_args()

app = Flask(__name__)
scrapper = Scrapper(args.driver)

line_bot_api = LineBotApi('6pQcNXYxqu0Kwiu4gfZcDtkt/qHcfApZ3s0DSGG+ISNWTSUv+I4p4YRWkOVHVngVFf68pWJ09p04yqZtJkfUu4OipzWrr0vwJGqC/nlMzTPq4bPutXzBm/FUBgtMab67e+KfxlW0MR1aE/bAdxlbvQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ecfb9d5eefbcbb9f678a79a25af244d3')
# line_bot_api.push_message('U6e55546093da4b2e769f0edc16fec07f', TextSendMessage(text='你可以開始了'))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text.lower() == "after-hour predict":
        send_message_linebot(line_bot_api, event, '正在預測明日大盤收盤指數...')
        lstm = tf.keras.models.load_model('models/LSTM_tomorrow.h5')
        reply_text = lstm_predict(lstm)

    elif event.message.text.lower() == "in-hour predict":
        send_message_linebot(line_bot_api, event, '正在預測今日大盤收盤指數...')
        gru = tf.keras.models.load_model('models/GRU_10am.h5')
        reply_text = gru_predict(gru)

    elif event.message.text.lower() == "5與20日均線死亡交叉":
        send_message_linebot(line_bot_api, event, '正在查詢5與20日均線死亡交叉...')
        data = scrapper.get_stock_selection()
        reply_text = data['5與20日均線死亡交叉']

    elif event.message.text.lower() == "5與20日均線黃金交叉":
        send_message_linebot(line_bot_api, event, '正在查詢5與20日均線黃金交叉...')
        data = scrapper.get_stock_selection()
        reply_text = data['5與20日均線黃金交叉']

    elif event.message.text.lower() == "多頭吞噬":
        send_message_linebot(line_bot_api, event, '正在查詢多頭吞噬...')
        data = scrapper.get_stock_selection()
        reply_text = data['多頭吞噬']

    elif event.message.text.lower() == "爆量長紅":
        send_message_linebot(line_bot_api, event, '正在查詢爆量長紅...')
        data = scrapper.get_stock_selection()
        reply_text = data['爆量長紅']

    elif event.message.text.lower() == "爆量長黑":
        send_message_linebot(line_bot_api, event, '正在查詢爆量長黑...')
        data = scrapper.get_stock_selection()
        reply_text = data['爆量長黑']

    elif event.message.text.lower() == "空頭吞噬":
        send_message_linebot(line_bot_api, event, '正在查詢空頭吞噬...')
        data = scrapper.get_stock_selection()
        reply_text = data['空頭吞噬']

    elif event.message.text.lower() == "突破季線":
        send_message_linebot(line_bot_api, event, '正在查詢突破季線...')
        data = scrapper.get_stock_selection()
        reply_text = data['突破季線']

    elif event.message.text.lower() == "突破整理區間":
        send_message_linebot(line_bot_api, event, '正在查詢突破整理區間...')
        data = scrapper.get_stock_selection()
        reply_text = data['突破整理區間']

    elif event.message.text.lower() == "跌破季線":
        send_message_linebot(line_bot_api, event, '正在查詢跌破季線...')
        data = scrapper.get_stock_selection()
        reply_text = data['跌破季線']

    elif event.message.text.lower() == "跌破整理區間":
        send_message_linebot(line_bot_api, event, '正在查詢跌破整理區間...')
        data = scrapper.get_stock_selection()
        reply_text = data['跌破整理區間']

    elif event.message.text.lower() == "twii":
        send_message_linebot(line_bot_api, event, '正在查詢大盤指數...')
        data = scrapper.get_TWII_data()
        reply_text = '\n'.join(f"{key}: {value}" for key, value in data.items())

    elif event.message.text.lower() == "tw future":
        send_message_linebot(line_bot_api, event, '正在查詢三大法人...')
        data = scrapper.get_TW_Future_data()
        reply_text = '淨多單留倉(張):\n'
        reply_text += '\n'.join(f"{key}: {value}" for key, value in data.items())

    elif event.message.text.lower() == "sox":
        send_message_linebot(line_bot_api, event, '正在查詢費半指數...')
        data = scrapper.get_SOX_data()
        reply_text = '您好，今日費半指數為:\n'
        reply_text += '\n'.join(f"{key}: {value}" for key, value in data.items())

    elif event.message.text.lower() == "tsmc":
        send_message_linebot(line_bot_api, event, '正在查詢台積電指數...')
        data = scrapper.get_TSMC_data()
        reply_text = '您好，今日台積電股價為:\n'
        reply_text += '\n'.join(f"{key}: {value}" for key, value in data.items())

    elif event.message.text.lower() == "usd":
        send_message_linebot(line_bot_api, event, '正在查詢美元匯率...')
        data = scrapper.get_USD_Index_data()
        reply_text = '您好，今日美元/台幣匯率為:\n'
        reply_text += '\n'.join(f"{key}: {value}" for key, value in data.items())

    elif event.message.text.lower() == "jpy":
        send_message_linebot(line_bot_api, event, '正在查詢美元/日圓...')
        data = scrapper.get_JPY_Index_data()
        reply_text = '您好，今日美元/日幣匯率為:\n'
        reply_text += '\n'.join(f"{key}: {value}" for key, value in data.items())

    else:
        reply_text = event.message.text

    if not isinstance(reply_text, str):
        reply_text = str(reply_text)

    send_message_linebot(line_bot_api, event, reply_text)


@app.route('/lstm-predict', methods=['GET'])
def predict_lstm_endpoint():
    lstm = tf.keras.models.load_model('models/LSTM_tomorrow.h5')
    return {"prediction": lstm_predict(lstm)}


@app.route('/gru-predict', methods=['GET'])
def predict_gru_endpoint():
    gru = tf.keras.models.load_model('models/GRU_10am.h5')
    return {"prediction": gru_predict(gru)}


@app.route('/get-stock-selection', methods=['GET'])
def get_stock_selection_today():
    data = scrapper.get_stock_selection()
    return jsonify(data)


@app.route('/get-TWII', methods=['GET'])
def get_TWII_today():
    data = scrapper.get_TWII_data()
    return jsonify(data)


@app.route('/get-TW-Future', methods=['GET'])
def get_TW_Future_today():
    data = scrapper.get_TW_Future_data()
    return jsonify(data)


@app.route('/get-TW-FITX', methods=['GET'])
def get_TW_FITX_today():
    data = scrapper.get_TW_FITX_data()
    return jsonify(data)


@app.route('/get-SOX', methods=['GET'])
def get_SOX_today():
    data = scrapper.get_SOX_data()
    return jsonify(data)


@app.route('/get-TSMC', methods=['GET'])
def get_TSMC_today():
    data = scrapper.get_TSMC_data()
    return jsonify(data)


@app.route('/get-USD', methods=['GET'])
def get_USD_today():
    data = scrapper.get_USD_Index_data()
    return jsonify(data)


@app.route('/get-JPY', methods=['GET'])
def get_JPY_today():
    data = scrapper.get_JPY_Index_data()
    return jsonify(data)


@app.route('/append-lstm-data', methods=['GET'])
def append_lstm_row_data():
    single_row = build_lstm_row_data(scrapper)
    gcs_helper = GcsHelper()
    gcs_helper.append_row_to_gcs_file('stockmarketindexai-sql', 'lstm_sql.csv', single_row)
    return jsonify(single_row)


@app.route('/append-gru-data', methods=['GET'])
def append_gru_row_data():
    single_row = build_gru_row_data(scrapper)
    gcs_helper = GcsHelper()
    gcs_helper.append_row_to_gcs_file('stockmarketindexai-sql', 'gru_sql.csv', single_row)
    return jsonify(single_row)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
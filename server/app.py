import os
import argparse
import tensorflow as tf

from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

from scraper import Scrapper
from utils import predict, send_message_linebot, build_single_row_data, append_row_to_gcs_file


parser = argparse.ArgumentParser()
parser.add_argument("--driver", required=True, help="spceify path to chromedriver.")
args = parser.parse_args()

app = Flask(__name__)
model = tf.keras.models.load_model('models/LSTM_v1.h5')
scrapper = Scrapper(args.driver)

line_bot_api = LineBotApi('6pQcNXYxqu0Kwiu4gfZcDtkt/qHcfApZ3s0DSGG+ISNWTSUv+I4p4YRWkOVHVngVFf68pWJ09p04yqZtJkfUu4OipzWrr0vwJGqC/nlMzTPq4bPutXzBm/FUBgtMab67e+KfxlW0MR1aE/bAdxlbvQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ecfb9d5eefbcbb9f678a79a25af244d3')
line_bot_api.push_message('U6e55546093da4b2e769f0edc16fec07f', TextSendMessage(text='你可以開始了'))


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
    if event.message.text.lower() == "predict":
        reply_text = predict(model)

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


@app.route('/predict', methods=['GET'])
def predict_endpoint():
     return {"prediction": predict(model)}


@app.route('/get-TWII', methods=['GET'])
def get_TWII_today():
    data = scrapper.get_TWII_data()
    return jsonify(data)


@app.route('/get-TW-Future', methods=['GET'])
def get_TW_Future_today():
    data = scrapper.get_TW_Future_data()
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


@app.route('/append_data', methods=['GET'])
def append_row_data():
    single_row = build_single_row_data(scrapper)
    append_row_to_gcs_file('stockmarketindexai-sql', 'mock_sql.csv', single_row)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
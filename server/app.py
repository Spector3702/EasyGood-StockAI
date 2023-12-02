import os
import argparse
import tensorflow as tf

from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

from scraper import Scrapper
from gcs_helper import GcsHelper
from linebot_manager import LineBotManager
from utils import lstm_predict, gru_predict, build_lstm_row_data, build_gru_row_data


parser = argparse.ArgumentParser()
parser.add_argument("--driver", required=True, help="spceify path to chromedriver.")
args = parser.parse_args()

app = Flask(__name__)
scrapper = Scrapper(args.driver)

token = '6pQcNXYxqu0Kwiu4gfZcDtkt/qHcfApZ3s0DSGG+ISNWTSUv+I4p4YRWkOVHVngVFf68pWJ09p04yqZtJkfUu4OipzWrr0vwJGqC/nlMzTPq4bPutXzBm/FUBgtMab67e+KfxlW0MR1aE/bAdxlbvQdB04t89/1O/w1cDnyilFU='
handler = WebhookHandler('ecfb9d5eefbcbb9f678a79a25af244d3')
# line_bot_api.push_message('U6e55546093da4b2e769f0edc16fec07f', TextSendMessage(text='你可以開始了'))


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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    linebot_manager = LineBotManager(token, event)
    message_text = event.message.text.lower()

    if message_text == "多方精選個股":
        linebot_manager.build_template_1()

    elif message_text == "大盤預測":
        linebot_manager.send_text_message('正在預測今日大盤收盤指數...')
        gru = tf.keras.models.load_model('models/GRU_10am.h5')
        reply_text = gru_predict(gru)
        linebot_manager.send_text_message(reply_text)

    elif message_text == "空方精選個股":
        linebot_manager.send_text_message('正在查詢5與20日均線死亡交叉...')
        data = scrapper.get_stock_selection()
        reply_text = data['5與20日均線死亡交叉']
        linebot_manager.send_text_message(reply_text)

    elif message_text == "外匯市場":
        linebot_manager.send_text_message('正在查詢5與20日均線黃金交叉...')
        data = scrapper.get_stock_selection()
        reply_text = data['5與20日均線黃金交叉']
        linebot_manager.send_text_message(reply_text)

    elif message_text == "期貨未平倉":
        linebot_manager.send_text_message('正在查詢多頭吞噬...')
        data = scrapper.get_stock_selection()
        reply_text = data['多頭吞噬']
        linebot_manager.send_text_message(reply_text)

    elif message_text == "美股四大指數":
        linebot_manager.send_text_message('正在查詢爆量長紅...')
        data = scrapper.get_stock_selection()
        reply_text = data['爆量長紅']
        linebot_manager.send_text_message(reply_text)


@handler.add(PostbackEvent)
def handle_postback(event):
    linebot_manager = LineBotManager(token, event)
    postback_data = event.postback.data

    if postback_data == '突破整理區間':
        linebot_manager.send_text_message('正在查詢突破整理區間...')
        data = scrapper.get_stock_selection()
        reply_text = data['突破整理區間']
        linebot_manager.send_text_message(reply_text)




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
import os
import tensorflow as tf
from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

from scraper import Scrapper
from utils import predict


app = Flask(__name__)
model = tf.keras.models.load_model('models/LSTM_v1.h5')

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
        scrapper = Scrapper()
        data = scrapper.get_TWII_data()
        reply_text = jsonify(data)
    elif event.message.text.lower() == "tw future":
        scrapper = Scrapper()
        data = scrapper.get_TW_Future_data()
        reply_text = jsonify(data)
    else:
        reply_text = event.message.text

    message = TextSendMessage(text=reply_text)
    line_bot_api.reply_message(event.reply_token, message)


@app.route('/predict', methods=['GET'])
def predict_endpoint():
     return {"prediction": predict(model)}


@app.route('/get-TWII', methods=['GET'])
def get_TWII_today():
    scrapper = Scrapper()
    data = scrapper.get_TWII_data()
    return jsonify(data)


@app.route('/get-TW-Future', methods=['GET'])
def get_TW_Future_today():
    scrapper = Scrapper()
    data = scrapper.get_TW_Future_data()
    return jsonify(data)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
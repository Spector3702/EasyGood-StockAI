import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

app = Flask(__name__)

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
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token,message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
import sys
import google.generativeai as genai
from firebase import firebase
from linebot import LineBotApi
from linebot.models import *

class GeminiBot():
    def __init__(self, event, token):
        # 初始化 LineBotApi
        self.line_bot_api = LineBotApi(token)
        
        # 配置 Gemini AI
        genai.configure(api_key='AIzaSyA8--HjDOqj7LXf3u4EHUGeIkKZEtf1nKI')
        self.model = genai.GenerativeModel('gemini-pro')
        
        # 初始化 Firebase
        self.fdb = firebase.FirebaseApplication('https://gemini-b0270-default-rtdb.firebaseio.com/', None)
        self.user_chat_path = f'chat/{event.source.user_id}'
        
        self.handle_event(event)

    def handle_event(self, event):
        msg_type = event.message.type
        reply_token = event.reply_token
        chatgpt = self.fdb.get(self.user_chat_path, None)
        
        # 處理文字訊息
        if isinstance(event.message, TextMessage):
            user_message = event.message.text
            if user_message == '推播新聞':
                user_message = '請提供我最新最重要的三個財金新聞(只需要標題、不需要內文)，並且附上新聞的連結，中文'
            
            if chatgpt is None:
                messages = []
            else:
                messages = chatgpt

            if user_message == '!清空':
                reply_msg = TextSendMessage(text='對話歷史紀錄已經清空！')
                self.fdb.delete(self.user_chat_path, None)
            else:
                messages.append({'role': 'user', 'parts': [user_message]})
                response = self.model.generate_content(messages)
                messages.append({'role': 'model', 'parts': [response.text]})
                reply_msg = TextSendMessage(text=response.text)
                if event.message.text != '推播新聞':
                    # 更新 firebase 中的對話紀錄
                    self.fdb.put_async(self.user_chat_path, None, messages)
            
            # 回覆訊息
            self.line_bot_api.reply_message(reply_token, reply_msg)

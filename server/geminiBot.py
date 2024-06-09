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

    def generate_news(self):
        # 使用 Gemini AI 生成新聞標題和連結
        prompt = ("請提供我最新最重要的三個財金新聞(只需要標題、不需要內文)，並且附上新聞的連結，中文\n"
                  "各網域連結請依照下面範例:\n"
                  "ET : https://finance.ettoday.net/news/\n"
                  "經濟日報 : https://money.udn.com/money/story\n"
                  "MoneyDJ : https://www.moneydj.com/funddj\n"
                  "上述都是從這網址中抓新聞的URL前綴字語，只需要在後面加上其對應的新聞頁面即可")
        messages = [{'role': 'user', 'parts': [prompt]}]
        response = self.model.generate_content(messages)
        
        news_list = response.text.strip().split('\n')
        formatted_news = "\n".join([f"{news.strip()}" for news in news_list if news.strip()])     
        
        # 移除Markdown格式
        formatted_news = formatted_news.replace('**', '').replace('- [連結]', '').replace('(', ' ').replace(')', '')
        
        return formatted_news



    def handle_event(self, event):
        msg_type = event.message.type
        reply_token = event.reply_token
        chatgpt = self.fdb.get(self.user_chat_path, None)
        
        # 處理文字訊息
        if isinstance(event.message, TextMessage):
            user_message = event.message.text
            if user_message == '推播新聞':
                news_content = self.generate_news()
                reply_msg = TextSendMessage(text=news_content)
                self.line_bot_api.reply_message(reply_token, reply_msg)
                return
            
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
                    self.fdb.put(self.user_chat_path, None, messages)
            
            # 回覆訊息
            self.line_bot_api.reply_message(reply_token, reply_msg)

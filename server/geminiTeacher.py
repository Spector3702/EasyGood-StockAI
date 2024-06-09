import sys
import re
import google.generativeai as genai
from firebase import firebase
from linebot import LineBotApi
from linebot.models import *

class GeminiTeacher():
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
        reply_token = event.reply_token
        chatgpt = self.fdb.get(self.user_chat_path, None)
        user_message = event.message.text
        
        # 檢查顧客的輸入
        is_valid, message, extracted_data = self.validate_and_extract_input(user_message)
        if not is_valid:
           self.line_bot_api.reply_message(reply_token,f"回傳資料格式錯誤: {message}")
        else:
            if isinstance(event.message, TextMessage):
                if chatgpt is None:
                    messages = []
                else:
                    messages = chatgpt

                # messages.append({'role': 'user', 'parts': [user_message]})
                # response = self.model.generate_content(messages)
                #messages.append({'role': 'model', 'parts': [response.text]})
                response_text = self.generate_financial_plan(extracted_data)
                # response_text = self.generate_financial_plan(response.text)
                reply_msg = TextSendMessage(text=response_text)
                
                # 更新 firebase 中的對話紀錄
                self.fdb.put_async(self.user_chat_path, None, messages)
                
                # 回覆訊息
                self.line_bot_api.reply_message(reply_token, reply_msg)

    def validate_and_extract_input(self, input_text):
        # 定義每一項的正則表達式模式
        patterns = {
            "age": r"1\.年齡:\s*(\d+)",
            "monthly_income": r"2\.月收入:\s*(\d+)",
            "retirement_age": r"3\.預計退休年齡:\s*(\d+)",
            "savings": r"4\.存款:\s*(\d+)",
            "goal": r"5\.財務目標\(夢想\):\s*(.+)"
        }
        
        extracted_data = {}
        
        # 檢查每一項是否存在且格式正確
        for key, pattern in patterns.items():
            match = re.search(pattern, input_text)
            if not match:
                return False, f"缺少或格式錯誤: {key}", {}
            extracted_data[key] = match.group(1)
        
        # 將數字轉換為整數
        extracted_data['age'] = int(extracted_data['age'])
        extracted_data['monthly_income'] = int(extracted_data['monthly_income'])
        extracted_data['retirement_age'] = int(extracted_data['retirement_age'])
        extracted_data['savings'] = int(extracted_data['savings'])
        
        return True, "所有項目都已正確填寫", extracted_data
    
    def generate_financial_plan(self, user_response):
        # 解析用戶資料的邏輯
        #測試資料
        # user_data = self.extract_user_data(ai_response)
        user_data = user_response

        # 判斷資產等級
        asset_level = self.determine_asset_level(user_data)

        # 生成理財規劃建議
        if asset_level == 'low':
            plan = self.generate_low_asset_plan(user_data)
        elif asset_level == 'middle':
            plan = self.generate_middle_asset_plan(user_data)
        elif asset_level == 'high':
            plan = self.generate_high_asset_plan(user_data)

        return plan

    # def extract_user_data(self, response):
    #     # 模擬解析用戶資料的邏輯，這裡應該根據實際情況解析用戶的基本資料和財務目標
    #     # 示例資料
    #     return {
    #         'age': 30,
    #         'monthly_income': 50000,
    #         'retirement_age': 65,
    #         'savings': 100000,
    #         'goal': '環遊世界'
    #     }

    def determine_asset_level(self, user_data):
        # 模擬資產等級的判斷邏輯
        if user_data['savings'] < 500000:
            return 'low'
        elif user_data['savings'] < 2000000:
            return 'middle'
        else:
            return 'high'

    def generate_low_asset_plan(self, user_data):
        monthly_savings_needed = self.calculate_monthly_savings(user_data)
        plan = (
            f"根據您的資料，這是您的理財規劃建議：\n"
            f"請使用6(生活開銷)/3(投資與儲蓄)/1(保險)的原則分配您的收入。\n"
            f"例如：如果您的月收入為 {user_data['monthly_income']} 元，\n"
            f"則每月花 {user_data['monthly_income'] * 0.6} 元在生活開銷上，\n"
            f"每月儲蓄與投資 {user_data['monthly_income'] * 0.3} 元，\n"
            f"每月花 {user_data['monthly_income'] * 0.1} 元在保險上。\n"
            f"為了實現您的夢想 {user_data['goal']}，\n"
            f"您需要每年儲蓄 {monthly_savings_needed} 元。\n"
            f"使用我們的 LINE Bot 輔助投資策略，達成您的財務目標！"
        )
        return plan

    def generate_middle_asset_plan(self, user_data):
        monthly_savings_needed = self.calculate_monthly_savings(user_data)
        plan = (
            f"根據您的資料，這是您的理財規劃建議：\n"
            f"請使用4(生活開銷)/4(投資與儲蓄)/2(保險)的原則分配您的收入。\n"
            f"例如：如果您的月收入為 {user_data['monthly_income']} 元，\n"
            f"則每月花 {user_data['monthly_income'] * 0.4} 元在生活開銷上，\n"
            f"每月儲蓄與投資 {user_data['monthly_income'] * 0.4} 元，\n"
            f"每月花 {user_data['monthly_income'] * 0.2} 元在保險上。\n"
            f"記得不要因收入增加而讓生活開銷變大。\n"
            f"為了實現您的夢想 {user_data['goal']}，\n"
            f"您需要每年儲蓄 {monthly_savings_needed} 元。\n"
            f"使用我們的 LINE Bot 輔助投資策略，達成您的財務目標！"
        )
        return plan

    def generate_high_asset_plan(self, user_data):
        monthly_savings_needed = self.calculate_monthly_savings(user_data)
        plan = (
            f"根據您的資料，這是您的理財規劃建議：\n"
            f"請使用保險的規劃來合法節稅。\n"
            f"例如：如果您的月收入為 {user_data['monthly_income']} 元，\n"
            f"則每月花 {user_data['monthly_income'] * 0.3} 元在生活開銷上，\n"
            f"每月儲蓄與投資 {user_data['monthly_income'] * 0.5} 元，\n"
            f"每月花 {user_data['monthly_income'] * 0.2} 元在保險上。\n"
            f"為了實現您的夢想 {user_data['goal']}，\n"
            f"您需要每年儲蓄 {monthly_savings_needed} 元。\n"
            f"使用我們的 LINE Bot 輔助投資策略，達成您的財務目標！"
        )
        return plan

    def calculate_monthly_savings(self, user_data):
        # 假設的儲蓄計算邏輯
        years_to_save = user_data['retirement_age'] - user_data['age']
        total_savings_needed = 1000000  # 根據夢想計算
        monthly_savings_needed = total_savings_needed / (years_to_save * 12)
        return monthly_savings_needed

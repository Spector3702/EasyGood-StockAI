from linebot import LineBotApi
from linebot.models import *


class LineBotManager():
    def __init__(self, token, event):
        self.line_bot_api = LineBotApi(token)
        self.user_id = event.source.user_id

    def send_text_message(self, text):
        message = TextSendMessage(text=text)
        self.line_bot_api.push_message(self.user_id, message)

    def build_richmenu(self, image_path):
        new_rich_menu = RichMenu(
            size=RichMenuSize(width=2500, height=1686),
            selected=True,
            name="New rich menu",
            chat_bar_text="Tab to open",
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                    action=MessageAction(label="多方精選個股", text="多方精選個股")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=833, y=0, width=833, height=843),
                    action=MessageAction(label="大盤預測", text="大盤預測")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1666, y=0, width=834, height=843),
                    action=MessageAction(label="空方精選個股", text="空方精選個股")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=843, width=833, height=843),
                    action=MessageAction(label="外匯市場", text="外匯市場")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=833, y=843, width=833, height=843),
                    action=MessageAction(label="期貨未平倉", text="期貨未平倉")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1666, y=843, width=834, height=843),
                    action=MessageAction(label="美股四大指數", text="美股四大指數")
                )
            ]
        )
        
        rich_menu_id = self.line_bot_api.create_rich_menu(rich_menu=new_rich_menu)
        with open(image_path, 'rb') as f:
            self.line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg", f)
        self.line_bot_api.set_default_rich_menu(rich_menu_id)

    def send_template(self, titles, texts, actions_list):
        columns = []
        for title, text, actions in zip(titles, texts, actions_list):
            column = CarouselColumn(
                thumbnail_image_url='https://steam.oxxostudio.tw/download/python/line-template-message-demo.jpg',
                title=title,
                text=text,
                actions=actions
            )
            columns.append(column)

        self.line_bot_api.push_message(
            self.user_id, 
            TemplateSendMessage(
                alt_text='Carousel Template',
                template=CarouselTemplate(columns=columns)
            )
        )

    def build_templates_1(self):
        titles = ['突破整理區間', '爆量長紅', '突破季線', '多頭吞噬', '5與20日均線黃金交叉']
        texts = ['突破整理區間', '爆量長紅', '突破季線', '多頭吞噬', '5與20日均線黃金交叉']
        actions = [
            [
                PostbackAction(label='查詢', data='1_突破整理區間'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='1_爆量長紅'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='1_突破季線'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='1_多頭吞噬'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='1_5與20日均線黃金交叉'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ]
        ]

        self.send_template(titles, texts, actions)

    def handle_templates_1(self, postback_data, scrapper):
        key = postback_data.split('1_', 1)[1] if '1_' in postback_data else None
        self.send_text_message(f'正在查詢{key}...')
        data = scrapper.get_stock_selection()
        reply_text = data.get(key, '找不到相關資料')
        self.send_text_message(reply_text)

    def build_templates_3(self):
        titles = ['跌破整理區間', '爆量長黑', '跌破季線', '空頭吞噬', '5與20日均線死亡交叉']
        texts = ['跌破整理區間', '爆量長黑', '跌破季線', '空頭吞噬', '5與20日均線死亡交叉']
        actions = [
            [
                PostbackAction(label='查詢', data='3_跌破整理區間'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='3_爆量長黑'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='3_跌破季線'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='3_空頭吞噬'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='3_5與20日均線死亡交叉'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ]
        ]

        self.send_template(titles, texts, actions)

    def handle_templates_3(self, postback_data, scrapper):
        key = postback_data.split('3_', 1)[1] if '3_' in postback_data else None
        self.send_text_message(f'正在查詢{key}...')
        data = scrapper.get_stock_selection()
        reply_text = data.get(key, '找不到相關資料')
        self.send_text_message(reply_text)

    def build_templates_4(self):
        titles = ['美/台', '美/日']
        texts = ['美/台', '美/日']
        actions = [
            [
                PostbackAction(label='查詢', data='4_美/台')
            ],
            [
                PostbackAction(label='查詢', data='4_美/日')
            ]
        ]

        self.send_template(titles, texts, actions)

    def handle_templates_4(self, postback_data, scrapper):
        if postback_data == '4_美/台':
            self.send_text_message('正在查詢美元匯率...')
            data = scrapper.get_USD_Index_data()
            reply_text = '您好，今日美元/台幣匯率為:\n'
            reply_text += '\n'.join(f"{key}: {value}" for key, value in data.items())
        else:
            self.send_text_message('正在查詢美元/日圓...')
            data = scrapper.get_JPY_Index_data()
            reply_text = '您好，今日美元/日幣匯率為:\n'
            reply_text += '\n'.join(f"{key}: {value}" for key, value in data.items())
            
        self.send_text_message(reply_text)
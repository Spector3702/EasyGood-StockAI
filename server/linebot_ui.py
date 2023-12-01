from linebot import LineBotApi
from linebot.models import *


class LineBotUIManager():
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

    def build_template_1(self):
        titles = ['突破整理區間', '爆量長紅', '突破季線', '多頭吞噬', '5與20日均線黃金交叉']
        texts = ['突破整理區間', '爆量長紅', '突破季線', '多頭吞噬', '5與20日均線黃金交叉']
        actions = [
            [
                PostbackAction(label='查詢', data='突破整理區間'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='爆量長紅'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='突破季線'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='多頭吞噬'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ],
            [
                PostbackAction(label='查詢', data='5與20日均線黃金交叉'),
                URIAction(label='HiStock', uri='https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4')
            ]
        ]

        self.send_template(titles, texts, actions)
from linebot import LineBotApi
from linebot.models import *

from utils import load_mock_sql


class LineBotManager():
    # 初始化 LineBotManager 實例，設置 LINE Bot API 和用戶 ID，以及圖片基礎 URL。
    def __init__(self, token, event):
        self.line_bot_api = LineBotApi(token)
        self.user_id = event.source.user_id
        self.base_img_url = 'https://storage.cloud.google.com/stockmarketindexai-sql/imgs'

    # send_text_message 方法：構建並發送文本消息給用戶。
    def send_text_message(self, text):
        message = TextSendMessage(text=text)
        self.line_bot_api.push_message(self.user_id, message)

    # build_richmenu 方法：建立一個副menu，並設置相應的操作區域。
    def build_richmenu(self, image_path):
        new_rich_menu = RichMenu(
            size=RichMenuSize(width=2500, height=1686),
            selected=True,
            name="New rich menu",
            chat_bar_text="Tab to open",
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                    action=MessageAction(label="多/空方精選個股", text="多/空方精選個股")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=833, y=0, width=833, height=843),
                    action=MessageAction(label="大盤預測", text="大盤預測")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1666, y=0, width=834, height=843),
                    action=MessageAction(label="推播新聞", text="推播新聞")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=843, width=833, height=843),
                    action=MessageAction(label="股市光明燈", text="股市光明燈")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=833, y=843, width=833, height=843),
                    action=MessageAction(label="理財建議書", text="理財建議書")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1666, y=843, width=834, height=843),
                    action=MessageAction(label="美國四大指數", text="美國四大指數")
                )
            ]
        )
        
        rich_menu_id = self.line_bot_api.create_rich_menu(rich_menu=new_rich_menu)
        with open(image_path, 'rb') as f:
            self.line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg", f)
        self.line_bot_api.set_default_rich_menu(rich_menu_id)

    # send_template 方法：構建並發送一個旋轉木馬模板消息（Carousel Template）給用戶。
    def send_template(self, images, titles, texts, actions_list):
        columns = []
        for image, title, text, actions in zip(images, titles, texts, actions_list):
            column = CarouselColumn(
                thumbnail_image_url=image,
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

    def send_uri_action(self, uri):
        message = TextSendMessage(text=f"請點擊以下連結跳轉到指定頁面：\n{uri}")
        self.line_bot_api.push_message(self.user_id, message)

    def build_initial_templates(self):
        template_url = f'{self.base_img_url}/initial'
        images = [
            f'{template_url}/多方篩選股票.png',
            f'{template_url}/空方篩選股票.png'
        ]
        titles = ['多方篩選股票', '空方篩選股票']
        texts = ['選擇多方篩選股票', '選擇空方篩選股票']
        actions = [
            [
                PostbackAction(label='選擇', data='initial_多方篩選股票')
            ],
            [
                PostbackAction(label='選擇', data='initial_空方篩選股票')
            ]
        ]

        self.send_template(images, titles, texts, actions)


    # build_templates_1 方法：建立多方篩選股票的模板消息。
    # handle_templates_1 方法：處理多方篩選股票的查詢，根據回傳的數據查找並回應相應的信息。
    def build_templates_1(self):
        template_url = f'{self.base_img_url}/template1-多方篩選股票'
        images = [
            f'{template_url}/突破區間.png',
            f'{template_url}/爆量長紅.png',
            f'{template_url}/突破季線.png',
            f'{template_url}/多頭吞噬.png',
            f'{template_url}/黃金交叉.png'
        ]
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

        self.send_template(images, titles, texts, actions)

    def handle_templates_1(self, postback_data, scrapper):
        key = postback_data.split('1_', 1)[1] if '1_' in postback_data else None
        self.send_text_message(f'正在查詢{key}...')
        data = scrapper.get_stock_selection()
        reply_text = data.get(key, '找不到相關資料')
        self.send_text_message(reply_text)

    # 處理空方篩選股票的模板消息和查詢。
    def build_templates_3(self):
        template_url = f'{self.base_img_url}/template3-空方篩選股票'
        images = [
            f'{template_url}/跌破區間.png',
            f'{template_url}/爆量長黑.png',
            f'{template_url}/跌破季線.png',
            f'{template_url}/空頭吞噬.png',
            f'{template_url}/死亡交叉.png'
        ]
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

        self.send_template(images, titles, texts, actions)

    def handle_templates_3(self, postback_data, scrapper):
        key = postback_data.split('3_', 1)[1] if '3_' in postback_data else None
        self.send_text_message(f'正在查詢{key}...')
        data = scrapper.get_stock_selection()
        reply_text = data.get(key, '找不到相關資料')
        self.send_text_message(reply_text)

    # # 處理外匯市場的模板消息和查詢。
    # def build_templates_4(self):
    #     template_url = f'{self.base_img_url}/template4-外匯市場'
    #     images = [
    #         f'{template_url}/美元兌台幣.png',
    #         f'{template_url}/美元兌日圓.png'
    #     ]
    #     titles = ['美元/台幣', '美元/日圓']
    #     texts = ['看透美元匯率，市場強弱，捕捉股市資金變化。', '日幣避險巧妙，智選投資，穩守風險，掌握未來。']
    #     actions = [
    #         [
    #             PostbackAction(label='查詢', data='4_美元/台幣'),
    #             URIAction(label='美元/台幣 - StockQ', uri='https://www.stockq.org/forex/USDTWD.php')
    #         ],
    #         [
    #             PostbackAction(label='查詢', data='4_美元/日圓'),
    #             URIAction(label='美元/日圓 - StockQ', uri='https://www.stockq.org/forex/USDJPY.php')
    #         ]
    #     ]

    #     self.send_template(images, titles, texts, actions)

    # def handle_templates_4(self, postback_data, scrapper):
    #     if postback_data == '4_美元/台幣':
    #         self.send_text_message('正在查詢美元/台幣...')
    #         data = scrapper.get_USD_Index_data()
    #         reply_text = '您好，今日美元/台幣匯率為:\n'
    #         reply_text += '\n'.join(f"{key}: {value}" for key, value in data.items())
    #     else:
    #         self.send_text_message('正在查詢美元/日圓...')
    #         data = scrapper.get_JPY_Index_data()
    #         reply_text = '您好，今日美元/日幣匯率為:\n'
    #         reply_text += '\n'.join(f"{key}: {value}" for key, value in data.items())
            
    #     self.send_text_message(reply_text)

    # 處理期貨未平倉的模板消息和查詢。
    def build_templates_5(self):
        template_url = f'{self.base_img_url}/template5-期貨未平倉'
        images = [
            f'{template_url}/外資.png',
            f'{template_url}/投信.png',
            f'{template_url}/自營商.png'
        ]
        titles = ['外資', '投信', '自營商']
        texts = [
            '外資暗潮洶湧，牽動臺股風向。劇烈波動，風險挑戰，同時帶來投資機會與成長活力。', 
            '投信穩定力，深耕臺股田野。資金活水，推動市場穩健成長~', 
            '自營商專業避險。穩健操作，緩衝風險，保值增值，投資無憂。'
        ]
        actions = [
            [
                PostbackAction(label='查詢', data='5_外資'),
                URIAction(label='操作建議', uri='https://rich01.com/foreign-investment-overbought-oversold/')
            ],
            [
                PostbackAction(label='查詢', data='5_投信'),
                URIAction(label='操作建議', uri='https://rich01.com/securities-investment-trust-verbought-oversold/')
            ],
            [
                PostbackAction(label='查詢', data='5_自營商'),
                URIAction(label='操作建議', uri='https://rich01.com/dealer-overbought-oversold/#%E8%87%AA%E7%87%9F%E5%95%86%E6%8C%81%E8%82%A1%E6%AF%94%E4%BE%8B%E6%9C%83%E5%A6%82%E4%BD%95%E5%BD%B1%E9%9F%BF%E8%82%A1%E5%83%B9%EF%BC%9F')
            ],
        ]

        self.send_template(images, titles, texts, actions)

    def handle_templates_5(self, postback_data):
        key = postback_data.split('5_', 1)[1] if '5_' in postback_data else None
        self.send_text_message(f'正在查詢{key}期貨未平倉...')
        
        df = load_mock_sql('lstm_sql.csv')
        latest_data = df.iloc[-3:][['date', key]]
        reply_text = f'您好，近三日{key}期貨未平倉為:\n'

        for _, row in latest_data.iterrows():
            date = row['date']
            value = row[key]
            reply_text += f"{date}: {value}\n"

        reply_text = reply_text.rstrip('\n')
        self.send_text_message(reply_text)

    # 處理美股四大指數的模板消息和查詢。
    def build_templates_6(self):
        template_url = f'{self.base_img_url}/template6-美國四大指數'
        images = [f'{template_url}/費半&SP500.png', f'{template_url}/NSQ&道瓊.png']
        titles = ['費半 & S&P500', '那斯達克 & 道瓊']
        texts = ['洞悉美股四大指數，如同洞悉光明未來!', '洞悉美股四大指數，如同洞悉光明未來!']
        actions = [
            [
                PostbackAction(label='費半', data='6_費半'),
                PostbackAction(label='S&P500', data='6_SP500')
            ],
            [
                PostbackAction(label='那斯達克', data='6_nasdaq'),
                PostbackAction(label='道瓊', data='6_dji')
            ]
        ]

        self.send_template(images, titles, texts, actions)

    def handle_templates_6(self, postback_data):
        key = postback_data.split('6_', 1)[1] if '6_' in postback_data else None
        self.send_text_message(f'正在查詢{key}指數...')

        df = load_mock_sql('lstm_sql.csv')
        columns = ['date', f'{key}_開盤價', f'{key}_最高價', f'{key}_最低價', f'{key}_收盤價']
        latest_data = df.iloc[-3:][columns]
        reply_text = f'您好，近三日{key}指數為:\n'

        for _, row in latest_data.iterrows():
            date = row['date']
            open_price = row[f'{key}_開盤價']
            high_price = row[f'{key}_最高價']
            low_price = row[f'{key}_最低價']
            close_price = row[f'{key}_收盤價']
            reply_text += (
                f"{date}:\n"
                f"  - 開盤價 {open_price}\n"
                f"  - 最高價 {high_price}\n"
                f"  - 最低價 {low_price}\n"
                f"  - 收盤價 {close_price}\n"
            )

        reply_text = reply_text.rstrip('\n')
        self.send_text_message(reply_text)
        
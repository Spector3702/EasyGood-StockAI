import requests
from bs4 import BeautifulSoup
from lxml import html


class Scrapper():
    def __init__(self) :
        pass

    def get_content_tree(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        tree = html.fromstring(str(soup))
        return tree

    def get_TWII_data(self):
        url = "https://tw.stock.yahoo.com/quote/%5ETWII"
        tree = self.get_content_tree(url)

        xpaths = {
            "成交金額(億)": "/html/body/div[1]/div/div/div/div/div[5]/div/div[1]/div/div[3]/div/section[1]/div[2]/div[2]/div/ul/li[6]/span[2]",
            "開盤": "/html/body/div[1]/div/div/div/div/div[5]/div/div[1]/div/div[3]/div/section[1]/div[2]/div[2]/div/ul/li[2]/span[2]",
            "最高": "/html/body/div[1]/div/div/div/div/div[5]/div/div[1]/div/div[3]/div/section[1]/div[2]/div[2]/div/ul/li[3]/span[2]",
            "最低": "/html/body/div[1]/div/div/div/div/div[5]/div/div[1]/div/div[3]/div/section[1]/div[2]/div[2]/div/ul/li[4]/span[2]",
            "收盤": "/html/body/div[1]/div/div/div/div/div[5]/div/div[1]/div/div[3]/div/section[1]/div[2]/div[2]/div/ul/li[7]/span[2]"
        }

        data = {}
        for key, path in xpaths.items():
            element = tree.xpath(path)
            if element:
                data[key] = element[0].text
            else:
                print(f"No element found for XPath: {path}")

        return data
    
    def get_TW_Future_data(self):
        url = "https://www.taifex.com.tw/cht/3/futContractsDate"
        tree = self.get_content_tree(url)

        xpaths = {
            "自營商": "/html/body/div[1]/div[4]/div[2]/div/div[4]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[11]/div[1]/font",
            "投信": "/html/body/div[1]/div[4]/div[2]/div/div[4]/table/tbody/tr[2]/td/table/tbody/tr[5]/td[11]/div[1]/font",
            "外資": "/html/body/div[1]/div[4]/div[2]/div/div[4]/table/tbody/tr[2]/td/table/tbody/tr[6]/td[11]/div[1]/font"
        }

        data = {}
        for key, path in xpaths.items():
            element = tree.xpath(path)
            if element:
                cleaned_value = element[0].text.replace("\r", "").replace("\t", "").strip()
                data[key] = cleaned_value
            else:
                print(f"No element found for XPath: {path}")

        return data



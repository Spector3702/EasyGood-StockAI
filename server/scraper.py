import requests
from bs4 import BeautifulSoup
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Scrapper():
    def __init__(self, driver_path) :
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")
        self.service = Service(executable_path=driver_path)

    def get_content_tree(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        tree = html.fromstring(str(soup))
        return tree

    def get_TWII_data(self):
        url = "https://tw.stock.yahoo.com/quote/%5ETWII"
        tree = self.get_content_tree(url)

        xpaths = {
            "成交金額(億)": "//li[contains(@class, 'price-detail-item')]//span[contains(text(), '成交金額(億)')]/following-sibling::span",
            "開盤": "//li[contains(@class, 'price-detail-item')]//span[contains(text(), '開盤')]/following-sibling::span",
            "最高": "//li[contains(@class, 'price-detail-item')]//span[contains(text(), '最高')]/following-sibling::span",
            "最低": "//li[contains(@class, 'price-detail-item')]//span[contains(text(), '最低')]/following-sibling::span",
            "收盤": "//li[contains(@class, 'price-detail-item')]//span[contains(text(), '昨收')]/following-sibling::span"
        }

        data = {}
        for key, path in xpaths.items():
            element = tree.xpath(path)
            if element:
                data[key] = element[0].text_content().strip()
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
    
    def get_SOX_data(self):
        url = "https://www.google.com/search?q=%E8%B2%BB%E5%8D%8A&oq=%E8%B2%BB%E5%8D%8A&aqs=chrome..69i57j69i59l2.3056j0j1&sourceid=chrome&ie=UTF-8"
        driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        driver.get(url)

        xpaths = {
            "開盤": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[1]/table/tbody/tr[1]/td[2]/div",
            "最高": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[1]/table/tbody/tr[2]/td[2]/div",
            "最低": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[2]/table/tbody/tr[1]/td[2]/div",
            "收盤": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[2]/table/tbody/tr[2]/td[2]/div"
        }

        data = {}
        for key, path in xpaths.items():
            input_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, path))
            )
            if input_element:
                text_content = input_element.text
                data[key] = text_content
            else:
                print(f"No element found for XPath: {path}")

        driver.quit()

        return data



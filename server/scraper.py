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
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

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
            "收盤": "//li[contains(@class, 'price-detail-item')]//span[contains(text(), '成交')]/following-sibling::span",
            "現在": "/html/body/div[1]/div/div/div/div/div[4]/div/div[1]/div/div[1]/div/div[2]/div[1]/div/span[1]"
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
    
    def get_TW_FITX_data(self):
        url = "https://histock.tw/index-tw/FITX"
        self.driver.get(url)

        xpaths = {
            "開盤": "/html/body/form/div[4]/div[5]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div/ul/li[2]/div[2]/span",
            "收盤": "/html/body/form/div[4]/div[5]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div/ul/li[5]/div[2]/span",
            "現在": "/html/body/form/div[4]/div[3]/div/div[1]/div[1]/div[2]/div[1]/div[2]/ul/li[1]/span/span/span"
        }

        data = {}
        for key, path in xpaths.items():
            input_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, path))
            )
            if input_element:
                text_content = input_element.text
                data[key] = text_content
            else:
                print(f"No element found for XPath: {path}")

        return data
    
    def get_USD_Index_data(self):
        url = "https://www.stockq.org/forex/USDTWD.php"
        tree = self.get_content_tree(url)

        xpaths = {
            "開盤": "//table[@class='indexpagetable']/tr[@class='row2']/td[6]",
            "最高": "//table[@class='indexpagetable']/tr[@class='row2']/td[4]",
            "最低": "//table[@class='indexpagetable']/tr[@class='row2']/td[5]",
            "指數": "//table[@class='indexpagetable']/tr[@class='row2']/td[1]"
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
    
    def get_JPY_Index_data(self):
        url = "https://www.stockq.org/forex/USDJPY.php"
        tree = self.get_content_tree(url)

        xpaths = {
            "開盤": "//table[@class='indexpagetable']/tr[@class='row2']/td[6]",
            "最高": "//table[@class='indexpagetable']/tr[@class='row2']/td[4]",
            "最低": "//table[@class='indexpagetable']/tr[@class='row2']/td[5]",
            "指數": "//table[@class='indexpagetable']/tr[@class='row2']/td[1]"
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
        self.driver.get(url)

        xpaths = {
            "開盤": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[1]/table/tbody/tr[1]/td[2]/div",
            "最高": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[1]/table/tbody/tr[2]/td[2]/div",
            "最低": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[2]/table/tbody/tr[1]/td[2]/div",
            "收盤": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/g-card-section/div/g-card-section/div[2]/div[1]/span[1]/span/span"
        }

        data = {}
        for key, path in xpaths.items():
            input_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, path))
            )
            if input_element:
                text_content = input_element.text
                data[key] = text_content
            else:
                print(f"No element found for XPath: {path}")

        return data
    
    def get_SP500_data(self):
        url = "https://www.google.com/search?q=SP500&rlz=1C1VDKB_zh-TWTW1019TW1019&oq=SP500&gs_lcrp=EgZjaHJvbWUyDwgAEEUYORiDARixAxiABDINCAEQABiDARixAxiABDINCAIQABiDARixAxiABDIHCAMQABiABDINCAQQABiDARixAxiABDIHCAUQABiABDIHCAYQABiABDIHCAcQABiABDIHCAgQABiABDIHCAkQABiABNIBBzM2N2owajeoAgCwAgA&sourceid=chrome&ie=UTF-8"
        self.driver.get(url)

        xpaths = {
            "開盤": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[1]/table/tbody/tr[1]/td[2]/div",
            "最高": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[1]/table/tbody/tr[2]/td[2]/div",
            "最低": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[2]/table/tbody/tr[1]/td[2]/div",
            "收盤": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/g-card-section/div/g-card-section/div[2]/div[1]/span[1]/span/span"
        }

        data = {}
        for key, path in xpaths.items():
            input_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, path))
            )
            if input_element:
                text_content = input_element.text
                data[key] = text_content
            else:
                print(f"No element found for XPath: {path}")

        return data
    
    def get_TSMC_data(self):
        url = "https://www.google.com/search?q=%E5%8F%B0%E7%A9%8D%E9%9B%BB%E8%82%A1%E5%83%B9"
        self.driver.get(url)

        xpaths = {
            "開盤": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[1]/table/tbody/tr[1]/td[2]/div",
            "最高": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[1]/table/tbody/tr[2]/td[2]/div",
            "最低": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/div/g-card-section[2]/div/div/div[1]/table/tbody/tr[3]/td[2]/div",
            "收盤": "/html/body/div[5]/div/div[10]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div[3]/g-card-section/div/g-card-section/div[2]/div[1]/span[1]/span/span"
        }

        data = {}
        for key, path in xpaths.items():
            input_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, path))
            )
            if input_element:
                text_content = input_element.text
                data[key] = text_content
            else:
                print(f"No element found for XPath: {path}")

        return data
    
    def get_stock_selection(self):
        url = "https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4"
        self.driver.get(url)

        input_element_xpath = '//*[@id="form1"]/div[4]/div[5]/div[2]/div[2]/div[1]/div[2]/table'
        input_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, input_element_xpath))
        )

        rows = input_element.find_elements(By.TAG_NAME, "tr")

        data_dict = {}
        for row in rows:
            header = row.find_element(By.TAG_NAME, "th").text
            cells = row.find_elements(By.TAG_NAME, "td")
            cell_data = [cell.text for cell in cells]

            # If there's only one td, store it directly; otherwise, store the list
            data_dict[header] = cell_data[0] if len(cell_data) == 1 else cell_data

        return data_dict

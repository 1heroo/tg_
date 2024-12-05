import asyncio
import time

from bs4 import Tag
import bs4
# import nodriver as uc
import undetected_chromedriver as uc
from nodriver.core.config import Config
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class BaseUtils:
    pass


class ParsingUtils(BaseUtils):

    @staticmethod
    def parse_products_from_category_page_ozon(html: str) -> list[dict]:
        soup = bs4.BeautifulSoup(html, features='lxml')
        products = soup.find_all('div', class_='tile-root')

        output_data = []
        for product in products:
            a_tags = product.find_all('a')

            if not a_tags:
                continue

            title = a_tags[-1].text
            uri = a_tags[-1].get('href')
            output_data.append({
                'title': title,
                'link': f'https://www.ozon.ru{uri}'
            })

        return output_data

    async def get_ozon_category_products(self, category_url: str) -> list[dict]:
        browser = uc.Chrome()

        products = []
        for page_index in range(1, 2, 3):
            url = category_url + f'&page={page_index}'
            browser.get(url)
            time.sleep(3)
            browser.execute_script("window.scrollBy(0, 1000);")
            browser.execute_script("window.scrollBy(0, 1000);")
            browser.execute_script("window.scrollBy(0, 1000);")
            browser.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)
            products += self.parse_products_from_category_page_ozon(html=browser.page_source)
            time.sleep(1)

        browser.quit()
        return products

    def extract_seller_link(self, html) -> str:
        soup = bs4.BeautifulSoup(html, features='lxml')
        seller_div = soup.find('div', {'data-widget': 'webCurrentSeller'})

        if seller_div:
            links = [link.get('href') for link in seller_div.find_all('a')]
            for link in links:
                if '/seller/' in link:
                    return link

    async def seller_links(self, products: list[dict]) -> list[dict]:
        browser = uc.Chrome()

        for product in products[:]:

            try:
                url = product.get('link')

                browser.get(url)
                time.sleep(4)
                browser.execute_script("window.scrollBy(0, 1000);")
                time.sleep(3)

                seller_link = self.extract_seller_link(browser.page_source)
                if seller_link:
                    product.update({'seller_link': seller_link})
                time.sleep(1)
                print(products.index(product), 'index getting seller link')
            except Exception as e:
                print('seller parsing', e)

        browser.quit()
        return products

    def extract_info(self, html: str) -> str:
        soup = bs4.BeautifulSoup(html, features='lxml')
        seller_div = soup.find_all('div', {'data-widget': 'textBlock'})

        seller_info = soup.find('div', {'data-widget': 'shopInfo'})
        works_with_ozon = None

        if seller_info:
            w_text = 'Работает с Ozon'
            for i in seller_info:
                if w_text in i.text:
                    works_with_ozon = i.text.replace(w_text, '')

        if seller_div:
            text = seller_div[-1].find('span')
            text_content: str = text.get_text(separator="\n", strip=True)
            print(text_content)

            ogrn = None
            for line in text_content.splitlines():
                if line.isdigit():
                    ogrn = line

            return text_content, ogrn, works_with_ozon

    async def extract_info_from_seller_page(self, products: list[dict]) -> list[dict]:
        browser = uc.Chrome()

        for product in products[:]:
            try:
                url = product.get('seller_link')
                if not url:
                    continue

                browser.get(url)
                time.sleep(4)

                btn = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'О магазине')]"))
                )
                print(btn.text)
                btn.click()
                print(btn, 'clicked')

                time.sleep(5)
                info, ogrn, works_with_ozon = self.extract_info(browser.page_source)
                product.update({'info': info, 'ogrn': ogrn, 'works_with_ozon': works_with_ozon})
                time.sleep(3)
                print(products.index(product), 'index getting seller info')
            except Exception as e:
                print('seller_data parsing error', str(e)[:300])

        browser.quit()
        return products


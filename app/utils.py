import asyncio

from bs4 import Tag
import bs4
import nodriver as uc
from nodriver.core.config import Config


class BaseUtils:
    pass


class ParsingUtils(BaseUtils):

    @staticmethod
    def parse_products_from_category_page_ozon(html: str) -> list[dict]:
        soup = bs4.BeautifulSoup(html, features='lxml')
        products = soup.find_all('div', class_='tile-root')
        print(products)
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
        browser = await uc.start()

        products = []
        for page_index in range(1, 2, 3):
            url = category_url + f'&page={page_index}'
            page = await browser.get(url)
            await page.sleep(5)
            await page.scroll_down(100)
            await page.scroll_down(100)
            await page.scroll_down(100)
            await page.scroll_down(100)
            await page.sleep(4)

            products += self.parse_products_from_category_page_ozon(html=await page.get_content())
            await asyncio.sleep(2)

        browser.stop()
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
        browser = await uc.start()

        for product in products[:]:

            try:
                url = product.get('link')

                page = await browser.get(url)
                await page.sleep(4)
                await page.scroll_down(100)
                await page.sleep(3)

                seller_link = self.extract_seller_link(await page.get_content())
                if seller_link:
                    product.update({'seller_link': seller_link})
                await asyncio.sleep(2)
                print(products.index(product), 'index getting seller link')
            except Exception as e:
                print('seller parsing', e)

        try:
            browser.stop()
        except: pass
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
        browser = await uc.start()

        for product in products[:]:
            try:
                url = product.get('seller_link')

                if not url:
                    continue

                page = await browser.get(url)
                await page.sleep(4)

                btn = await page.find(text='О магазине', timeout=15)
                await page.sleep(2)

                await btn.click()
                await btn.click()
                print(btn, 'clicked')

                await page.sleep(5)
                info, ogrn, works_with_ozon = self.extract_info(await page.get_content())
                product.update({'info': info, 'ogrn': ogrn, 'works_with_ozon': works_with_ozon})
                await page.sleep(3)
                print(products.index(product), 'index getting seller info')
            except Exception as e:
                print('seller_data parsing error', e)

        try:
            browser.stop()
        except: pass
        return products


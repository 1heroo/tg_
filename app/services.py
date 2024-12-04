from app.utils import ParsingUtils


class Services:

    def __init__(self):
        self.parsing_utils = ParsingUtils()

    async def launch_parsing(self, category_url: str) -> list[dict]:
        category_url = category_url.split('?')[0]
        category_url += '?sorting=new'

        products = await self.parsing_utils.get_ozon_category_products(category_url)
        products = products[:5]
        products = await self.parsing_utils.seller_links(products)

        print(len(products))
        products = {
            product.get('seller_link'): product
            for product in products
        }
        print(products)
        products = list(products.values())
        products = await self.parsing_utils.extract_info_from_seller_page(products)
        print(products)
        return [
            {
                'Наименование': product.get('title'),
                'Информация': product.get('info'),
                'ОГРН': product.get('ogrn'),
                'Продавец': product.get('seller_link'),
                'Товар': product.get('link'),
                'Работает с озон': product.get('works_with_ozon')
            }
            for product in products if product.get('ogrn')
        ]


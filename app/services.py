from app.utils import ParsingUtils


class Services:

    def __init__(self):
        self.parsing_utils = ParsingUtils()

    async def launch_parsing(self, category_url: str) -> list[dict]:
        category_url = category_url.split('?')[0]
        category_url += '?sorting=new'

        # products = await self.parsing_utils.get_ozon_category_products(category_url)
        # products = products[:1]
        # print(products)
        # products = await self.parsing_utils.seller_links(products)
        #
        # print(len(products))
        # products = {
        #     product.get('seller_link'): product
        #     for product in products
        # }
        # print(products)
        products = {'https://www.ozon.ru/seller/magazin-krossovok-1875173/': {'title': 'Толстовка Frenemy', 'link': 'https://www.ozon.ru/product/tolstovka-frenemy-1768299839/?asb2=XOlT28N4KZw6CoKzN8ZKUhgD251dPkDrcYMQ8BpwNDh_xMYcEU3YIZuUJipBrv-4&avtc=1&avte=4&avts=1733384088', 'seller_link': 'https://www.ozon.ru/seller/magazin-krossovok-1875173/'}}
        products = list(products.values())
        products = await self.parsing_utils.extract_info_from_seller_page(products)

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


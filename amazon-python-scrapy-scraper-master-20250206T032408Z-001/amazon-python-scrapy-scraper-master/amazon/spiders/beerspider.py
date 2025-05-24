import scrapy
from scrapy_splash import SplashRequest

class BeerSpider(scrapy.Spider):
    name = 'abeer'
    start_urls = ["https://beerwulf.com/collections/beer-kegs"]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url, 
                self.parse,             
                args={
                'wait': 2,  # 等待时间增加到2秒
                'timeout': 90,
                'render_all': 1  # 确保渲染完整页面
                }
            )

    def parse(self, response):
        print("正在处理URL:", response.url)
        products = response.css("#load-previous-products + div")
        print("products 选择器结果:", products)

        product_names =products.css("h2::text").getall()

        for product_name in product_names:
            print("提取到的商品名称:", product_name) # 打印提取到的商品名称，查看是否提取成功
            yield {"product_name": product_name}

import scrapy

class TestWebsiteSpider(scrapy.Spider):

    name = "test_website_01"

    def start_requests(self):
        
        #每电影单独网页链接for循环
        for index in range(1, 101):
            search_url = f"https://ssr1.scrape.center/detail/{index}"
            yield scrapy.Request(url=search_url, callback=self.scrape_item, meta={"index" : index})
    
    

    def scrape_item(self, response):

        index = response.meta['index']

        #"rating"，"introduction"的xpath结果中有换行符，在这里去掉，并把结果存入变量
        rating = (response.xpath('//p[@class="score m-t-md m-b-n-sm"]/text()').getall())[0].strip()
        introduction = (response.xpath('//div[@id="detail"]// div[@class="drama"]/p/text()').getall())[0].strip()

        yield{
            "index" : index,
            "name" : response.xpath('(//div[@id="detail"]//h2/text())[1]').getall(),
            "categories" : response.xpath('//div[@id="detail"]//div[@class="categories"]//span/text()').getall(),
            "release_time" : response.xpath('(//div[@id="detail"]//div[@class="m-v-sm info"])[2]/span/text()').getall(),
            "rating" : rating,
            "introduction" : introduction,
        }

#待做："rating"，"introduction"需去掉换行符。

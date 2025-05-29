import json
import scrapy
from urllib.parse import urljoin
import re
import logging

class AmazonSearchProductSpider(scrapy.Spider):
    name = "amazon_search_product"



    def start_requests(self):
        keyword_list = ['ipad']
        for keyword in keyword_list:
            amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page=1'

            self.logger.info("开始爬取网页")
            self.logger.in

            yield scrapy.Request(url=amazon_search_url, callback=self.discover_product_urls, meta={'keyword': keyword, 'page': 1})

    def discover_product_urls(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword'] 

        ## Discover Product URLs
        search_products = response.css("div.s-result-item[data-component-type=s-search-result]")
        for product in search_products:
            relative_url = product.xpath('.//h2/parent::*/@href').get()
            product_url = urljoin('https://www.amazon.com/', relative_url).split("?")[0]
            yield scrapy.Request(url=product_url, callback=self.parse_product_data, meta={'keyword': keyword, 'page': page})
            
        ## Get All Pages
        if page == 1:

            for page_num in range(2, 3):
                amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page={page_num}'
                yield scrapy.Request(url=amazon_search_url, callback=self.discover_product_urls, meta={'keyword': keyword, 'page': page_num})


    def parse_product_data(self, response):
        yield {
            "name": response.css("#productTitle::text").get("").strip(),
            "stars": response.css("#acrPopover::attr(title)").get("").strip(),
            "rating_count": response.css("div[data-hook=total-review-count] ::text").get("").strip(),
        }
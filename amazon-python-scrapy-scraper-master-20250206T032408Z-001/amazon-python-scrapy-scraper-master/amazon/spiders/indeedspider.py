#疑问一：Line60,proxy_url需要修改
#疑问二：Line97,search_url需不需要检查一下？
#疑问三：Line114,询问AI.
#看到Line114
# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode, urljoin
from scrapy_splash import SplashRequest
import logging # 导入 logging 模块

# 设置日志级别，减少 Scrapy 的冗余输出，聚焦于爬虫本身的信息
logging.getLogger('scrapy').setLevel(logging.WARNING)
logging.getLogger('scrapy.core.scraper').setLevel(logging.INFO)
logging.getLogger('scrapy.middleware').setLevel(logging.WARNING)
logging.getLogger('scrapy.extensions').setLevel(logging.WARNING)
logging.getLogger('scrapy.statscollectors').setLevel(logging.WARNING)


class IndeedJobSpider(scrapy.Spider):
    """
    一个 Scrapy 爬虫，用于抓取 Indeed 印度网站上指定地区和职位的招聘信息。

    Attributes:
        name (str): 爬虫的唯一名称。
        locations (list): 需要爬取的地区列表。
        job_titles (list): 需要爬取的职位名称列表。
        proxy_url (str): 用于请求的代理服务器 URL (需要时请替换为有效地址)。
        base_url (str): Indeed 搜索的基础 URL。
    """
    name = 'indeed_jobs'
    allowed_domains = ['in.indeed.com'] # 限制爬虫只在 Indeed 印度域名下活动

    # ================== 用户配置区域 ==================
    # 需要爬取的地区列表
    locations = [
        "Ahmedabad",
        "Gandhinagar",
        "Baroda (Vadodara)",
        "Gujarat" # 注意： "Gujarat (India)" 中的 "(India)" 可能不需要，Indeed 通常只用地名
                  # 如果 "Gujarat" 效果不好，可以尝试只用 "Gujarat" 或检查 Indeed 上实际使用的地名
    ]

    # 需要爬取的职位名称列表
    job_titles = [
        "MERN Stack Developer", "React Developer", "Node.js Developer", "PHP Developer",
        "Python Developer", "Power BI Analyst", "Data Analyst", "Tableau Specialist",
        "Cybersecurity Analyst", "Security Operations Center (SOC) Analyst",
        "Network Security Analyst", "IT Security Administrator",
        "Penetration Testing Intern / Junior Penetration Tester",
        "Ethical Hacker (Entry-Level)", "Cloud Security Associate",
        "Application Security Analyst", "Information Security Specialist",
        "Junior Security Consultant", "Junior DevOps Engineer", "DevOps Trainee",
        "Junior or Trainee Cloud Architect", "Cloud Consultant", "Cloud Network Engineer",
        "Solutions Architect", "Cloud Security Specialist", "Cloud Administrator",
        "Cloud Infrastructure Expert", "Cloud Engineer", "Cloud Software Engineer",
        "Cloud Automation Engineer", "Cloud Database Manager"
    ]

    # 代理服务器设置 (如果需要，请取消注释并替换为您的有效代理地址)
    # proxy_url = "http://YOUR_PROXY_USERNAME:YOUR_PROXY_PASSWORD@YOUR_PROXY_ADDRESS:PORT"
    proxy_url = "http://ok04pcttn3gbd5l:p07fjq63s61u7pb@rp.scrapegw.com:6060"

    # Splash 服务地址 (确保 Splash 服务正在运行并监听此地址)
    splash_url = 'http://localhost:32769' # 默认本地 Splash 地址

    # ================== 爬虫内部变量 ==================
    base_url = "https://in.indeed.com/jobs?"

    # ================== 核心方法 ==================

    def start_requests(self):
        """
        生成初始请求。
        遍历所有地区和职位组合，为每个组合的第一页搜索结果生成 SplashRequest。
        """

        #log内容
        self.log(f"爬虫 '{self.name}' 开始启动...", level=logging.INFO)
        if not self.locations or not self.job_titles:
            self.log("错误：地区列表或职位列表为空，无法开始爬取。", level=logging.ERROR)
            return

        if self.proxy_url:
             self.log(f"将使用代理: {self.proxy_url.split('@')[-1]}", level=logging.INFO) # 仅显示地址和端口
        else:
             self.log("不使用代理", level=logging.INFO)
        #以上
        
        #内外for循环， 外循环location, 内循环jobTitle
        request_count = 0
        for location in self.locations:
            for job_title in self.job_titles:
                request_count += 1

                #构建查询参数，通过查询参数、构建searchUrl    
                # 构建查询参数
                params = {
                    'q': job_title,
                    'l': location,
                    'radius': 0, # 根据用户提供的 URL 结构
                    'start': 0   # 始终从第一页 (start=0) 开始
                }

                # 构建完整的 URL
                search_url = self.base_url + urlencode(params)
                #log
                self.log(f"为 '{job_title}' 在 '{location}' (第 1 页) 生成请求: {search_url}", level=logging.DEBUG)

                #yield SplashRequest本体
                yield SplashRequest(
                    url=search_url,
                    callback=self.parse_search_results,
                    endpoint='render.html', # 显式指定 endpoint

                    args={
                        'wait': 3,  # 等待时间增加到 3 秒，给 Indeed 更多加载时间
                        'timeout': 90,
                        'render_all': 1, # 尝试渲染完整页面
                        'html': 1, # 确保返回 HTML
                        'proxy': self.proxy_url
                        # 'images': 0, # 可以禁用图片加载以加快速度 (可选)
                        # 'response_body': 1 # 确保返回响应体
                    }, # 直接传递 args

                    meta={
                        'search_location': location,
                        'search_job_title': job_title,
                        'start': 0, # 传递当前页的 start 值
                    },
                )
        #log
        self.log(f"共生成 {request_count} 个初始请求。", level=logging.INFO)


    def parse_search_results(self, response):
        """
        解析 Indeed 搜索结果页面。
        提取当前页面的所有招聘信息的 Designation 和 City，并生成下一页的请求。
        """
        search_location = response.meta['search_location']
        search_job_title = response.meta['search_job_title']
        start = response.meta['start']
        current_page = (start // 10) + 1
        items_yielded_on_page = 0 # 确保计数器已初始化

        #log
        self.log(f"正在解析: '{search_job_title}' 在 '{search_location}' - 第 {current_page} 页 (URL: {response.url})", level=logging.INFO)
        #进度页在001活页本第一页

        # --- 提取数据 ---
        # 首先定位包含单个工作信息的卡片/容器

        #job_cards的xpath
        job_cards = response.xpath('//*[@id="mosaic-provider-jobcards"]/ul/li')
        #这个job_cards的元素、多数是工作帖子卡，但有少数几个元素、不是工作帖子卡

        #从job_cards中选择是*真工作帖子卡*的元素
        #筛选方法：这个元素包含职位名称文本，则是；不包含，则不是。
        #用职位名称文本的xpath进行筛选
        filtered_job_cards = [
            card for card in job_cards
            if card.xpath('.//h2[contains(@class, "jobTitle")]//span/text()').get() and card.xpath('.//h2[contains(@class, "jobTitle")]//span/text()').get().strip()
        ]

        #找到真工作帖子卡元素后，对每个真帖子卡提取Designation和City文本，用for循环
        for card in filtered_job_cards:

            #提取Designation文本 - 使用 get(default='') 避免 None，并 strip()
            designation = card.xpath('.//h2[contains(@class, "jobTitle")]//span/text()').get(default='').strip()
            #提取City文本 - 使用 get(default='') 避免 None，并 strip()
            city = card.xpath('.//div[contains(@class, "company_location")]//div[@data-testid="text-location"]/text()').get(default='').strip()

            # 确保提取到了有效的 designation 才 yield
            if designation:
                items_yielded_on_page += 1
                yield {
                    'Designation': designation,
                    'City': city, # city 可能为空，但仍然 yield
                    'Searched_Job': search_job_title,
                    'Searched_Location': search_location,
                    'Source_Page': current_page,
                    'Source_URL': response.url # 添加来源 URL 便于调试
                }
            else:
                 # 如果在这个被认为是 job card 的元素中找不到 designation，记录一下
                 self.log(f"警告: 在第 {current_page} 页的一个卡片中未找到 Designation。卡片 HTML 片段: {card.get()[:200]}...", level=logging.WARNING)


        self.log(f"在第 {current_page} 页成功提取并输出了 {items_yielded_on_page} 条职位信息。", level=logging.INFO)

        # --- 处理分页 ---
        # 只有在当前页面成功提取到了数据时 (items_yielded_on_page > 0)，才尝试请求下一页
        if items_yielded_on_page > 0:
            # 计算下一页的 start 值
            next_start = start + 10

            # 构建下一页的查询参数
            next_params = {
                'q': search_job_title,
                'l': search_location,
                'radius': 0,
                'start': next_start
            }
            next_page_url = self.base_url + urlencode(next_params)

            self.log(f"为 '{search_job_title}' 在 '{search_location}' 生成下一页 (第 {current_page + 1} 页) 请求: {next_page_url}", level=logging.DEBUG)

            yield SplashRequest(
                url=next_page_url,
                callback=self.parse_search_results,
                endpoint='render.html', # 显式指定 endpoint

                args={
                    'wait': 3,  # 等待时间增加到 3 秒，给 Indeed 更多加载时间
                    'timeout': 90,
                    'render_all': 1, # 尝试渲染完整页面
                    'html': 1, # 确保返回 HTML
                    'proxy': self.proxy_url
                    # 'images': 0, # 可以禁用图片加载以加快速度 (可选)
                    # 'response_body': 1 # 确保返回响应体
                }, # 直接传递 args

                meta={
                    'search_location': search_location,
                    'search_job_title': search_job_title,
                    'start': next_start, # 传递当前页的 start 值
                },
            )
        else:
            # 如果当前页面没有提取到任何项目 (items_yielded_on_page == 0)，停止分页。
            # 细化日志信息
            if not job_cards:
                 self.log(f"在 '{search_job_title}' / '{search_location}' 第 {current_page} 页未找到任何 job card 元素。停止此分支的分页。", level=logging.INFO)
            elif not filtered_job_cards:
                 self.log(f"在 '{search_job_title}' / '{search_location}' 第 {current_page} 页找到 job card 元素，但未能通过筛选（可能不是有效职位）。停止此分支的分页。", level=logging.INFO)
            else:
                 # 找到了卡片并通过了筛选，但未能提取出有效的 Designation
                 self.log(f"在 '{search_job_title}' / '{search_location}' 第 {current_page} 页未成功提取任何有效的职位信息 (Designation 为空)。停止此分支的分页。", level=logging.INFO)


    def closed(self, reason):
        """爬虫关闭时调用的方法"""
        self.log(f"爬虫 '{self.name}' 已关闭。原因: {reason}", level=logging.INFO)
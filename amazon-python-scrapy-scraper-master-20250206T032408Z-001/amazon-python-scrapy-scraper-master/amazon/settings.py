# Scrapy settings for amazon project
# ... (optional comments) ...

BOT_NAME = 'amazon' # 假设你的项目名称是 'amazon'

SPIDER_MODULES = ['amazon.spiders'] # 指定包含爬虫的模块

FEED_EXPORT_ENCODING = 'utf-8'  # 确保使用UTF-8编码
FEED_EXPORT_INDENT = 2  # 可选，美化输出

#Splash_setup
SPLASH_URL = 'http://localhost:32769/'

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

REQUEST_FINGERPRINTER_CLASS = 'scrapy_splash.SplashRequestFingerprinter'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

LOG_LEVEL = 'INFO'



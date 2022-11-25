import imp
import os

os.environ.setdefault('ENABLE_SPIDERKEEPER_SUPPORT', 'True')
os.environ.setdefault('SPIDERKEEPER_APPID', 'APPID-5-12')
os.environ.setdefault('SPIDERKEEPER_HOST_ADDR', '127.0.0.1:8000')


from scrapy.cmdline import execute

execute(['scrapy', 'crawl', 'example'])

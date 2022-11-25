import time

import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['example.com']

    def get_mocker_server(self):
        host = self.settings.get('MOCK_SERVER_HOST')
        port = self.settings.get('MOCK_SERVER_PORT')
        try:
            port = int(port)
        except Exception as e:
            self.logger.error(e)
            port = None
        if all([host, port]):
            return f'{host}:{port}'
        else:
            return None

    def start_requests(self):
        url = 'http://httpbin.iclouds.work/uuid'
        urls = [
            f'{url}' for _ in range(0, 100)
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        time.sleep(1)
        self.logger.info(response)
        return {"url": response.url}

import logging
from multiprocessing import Process

from scrapy import signals

from .mock import app

logger = logging.getLogger(__name__)


class MockServer(object):
    def __init__(self, host, port):

        self.host = host
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        default_host, default_port = crawler.settings.get('DEFAULT_MOCK_SERVER').split(':')
        host = crawler.settings.get('MOCK_SERVER_HOST', default_host)
        port = crawler.settings.get('MOCK_SERVER_PORT', default_port)
        try:
            port = int(port)
        except Exception as e:
            logger.error(f'Mocker server port type error {port}, use default port {default_port}')
            logger.error(e)
            port = default_port
        ext = cls(host, port)

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        # return the extension object
        return ext

    def spider_opened(self, spider):
        logger.info("opened spider %s", spider.name)
        self.server = Process(target=app.run, kwargs={'host': self.host, 'port': self.port})
        logger.debug(f'Start mocker server in pid: {self.server.pid}')
        self.server.start()

    def spider_closed(self, spider):
        logger.info("closed spider %s", spider.name)
        self.server.kill()
        logger.debug(f'Stop mocker server.')

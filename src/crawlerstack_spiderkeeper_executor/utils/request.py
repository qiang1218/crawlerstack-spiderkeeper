"""request api"""
import logging
import time

from requests import Session
from requests.exceptions import JSONDecodeError, RequestException

from crawlerstack_spiderkeeper_executor.utils import SingletonMeta

logger = logging.getLogger(__name__)


class BaseRequest(metaclass=SingletonMeta):
    """Base request"""
    NAME: str
    DELAY = 1
    MAX_RETRY = 3

    def request(self, *args, **kwargs):
        raise NotImplementedError


class RequestWithSession(BaseRequest):  # noqa
    """base spider with session"""
    NAME = 'session'

    def __init__(self, *args, **kwargs):
        super(RequestWithSession, self).__init__(*args, **kwargs)
        self.session = Session()
        self.session.headers.update({
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/89.0.4389.114 Safari/537.36',
        })

    def request(self, method, url, **kwargs) -> dict:
        """
        request
        :param method:
        :param url:
        :param kwargs:
        :return:
        """
        try:
            for i in range(self.MAX_RETRY):
                time.sleep(self.DELAY)
                response = self.session.request(method, url, **kwargs)
                status_code = response.status_code
                if status_code == 200:
                    logger.debug('Got response from "%s", status code is %d', url, status_code)
                    try:
                        resp_json = response.json()
                        return resp_json
                    except JSONDecodeError:
                        logger.warning('Json decode error, response data is %s', response.text)
                logger.warning('Got response from "%s", status code is %d', url, status_code)
        except RequestException as ex:
            logger.warning('Request exception, request url is %s', url)
            logger.warning('%s', ex)
        return {}

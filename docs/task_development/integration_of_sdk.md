# 集成sdk

采集任务集成sdk是推荐的一种做法，用户可使用到采集平台的所有功能。

## 安装包

```bash
pip install crawlerstack-spiderkeeper-sdk
```

## 用例

```python
import asyncio
import requests

from crawlerstack_spiderkeeper_sdk.repeater import SpiderkeeperSDK

# todo 默认情况下，通过采集平台调度的任务，环境变量中会包含自动以下变量，可直接获取:
TASK_NAME = ''
DATA_URL=''
LOG_URL=''
METRICS_URL=''
STORAGE_ENABLED=''
SNAPSHOT_ENABLED=''

class DemoCrawlers:
    """DemoCrawlers"""
    url = 'http://localhost:8000/api/v1/example'

    def __init__(self):
        self.metrics_task = None
        self.sdk = SpiderkeeperSDK(
            task_name=TASK_NAME,
            data_url=DATA_URL,
            log_url=LOG_URL,
            metrics_url=METRICS_URL,
            storage_enabled=self.parse_enabled_config(STORAGE_ENABLED),
            snapshot_enabled=self.parse_enabled_config(SNAPSHOT_ENABLED),
        )

    @staticmethod
    def parse_enabled_config(config) -> bool:
        """
        Enable
        系统环境变量中的 bool类型参数可能表示为字符串
        因此在爬虫程序中需将状态参数进行过滤
        :param config:
        :return:
        """
        if isinstance(config, str):
            config = config.lower()
        if config == 'true' or config is True:
            return True
        return False

    async def init_metrics_collector_task(self):
        """
        由爬虫程序初始化监控指标收集任务
        :return:
        """
        loop = asyncio.get_running_loop()
        self.metrics_task = loop.create_task(self.sdk.metrics())
        await asyncio.sleep(3)

    async def crawlers(self):
        """crawlers"""
        # 发送日志
        await self.sdk.logs(f'Crawler {self.url}')
        # todo 如果需要设置指标，可以通过对请求设置装饰器实现
        res = requests.get(self.url)
        await self.init_metrics_collector_task()
        # 发送数据
        await self.send_data(res.json())
        # 爬虫结束后由爬虫程序关闭指标收集任务
        self.metrics_task.cancel()
        await asyncio.sleep(5)

    async def send_data(self, data):
        """send data"""
        await self.sdk.send_data(data=data)
```

设置指标的方式：

```python
from prometheus_client import Counter

req_count = Counter(
    'spiderkeeper_downloader_request_count',
    'Number of requests'
)

# todo 根据需要，设置指标的值
req_count.inc()
```

详细内容请参考：[crawlerstack-spiderkeeper-sdk](https://github.com/crawlerstack/crawlerstack-spiderkeeper-sdk)

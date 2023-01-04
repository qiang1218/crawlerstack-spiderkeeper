"""k8s"""
from crawlerstack_spiderkeeper_executor.executor import BaseExecutor


class K8SExecutor(BaseExecutor):
    NAME = 'k8s'

    async def stop(self, *args, **kwargs):
        pass

    async def delete(self, *args, **kwargs):
        pass

    async def status(self, *args, **kwargs) -> str:
        pass

    async def log(self, *args, **kwargs):
        pass

    async def run(self, *args, **kwargs):
        pass

"""
Test
"""
import os

from furl import furl

os.environ.setdefault('SPIDERKEEPER_ENV', 'test')


def update_test_db():
    """
    创建测试环境的 sqlite 数据库文件。

    由于操作系统适配问题，不建议在 settings.yml 配置中写具体路径。
    """
    from crawlerstack_spiderkeeper.config import settings
    db_settings = settings.DATABASE
    url = furl(db_settings)
    if not url.path:
        local_path = settings.LOCALPATH
        db_file = local_path / 'spiderkeeper.db'
        settings.DATABASE = f'{url.scheme}:///{db_file}'


update_test_db()

"""
config
"""

import os
from pathlib import Path

from dynaconf import Dynaconf

base_dir = Path(__file__).parent.parent

local_path = base_dir / '.local'
os.makedirs(local_path, exist_ok=True)

settings_files = [
    Path(__file__).parent / 'settings.yml',
]  # 指定绝对路径加载默认配置

settings = Dynaconf(
    envvar_prefix="SPIDERKEEPER_FORWARDER",  # 环境变量前缀。设置`SPIDERKEEPER_FOO='bar'`，使用`settings.FOO`
    settings_files=settings_files,
    lowercase_read=False,  # 禁用小写访问， settings.name 是不允许的
    includes=['/etc/spiderkeeper_forwarder/settings.yml'],  # 自定义配置覆盖默认配置
    base_dir=base_dir,  # 编码传入配置
    localpath=local_path
)


if not os.path.isabs(settings.LOGPATH):
    settings.set('LOGPATH', local_path / settings.LOGPATH)
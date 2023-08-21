"""
config
"""

import os
import sys
from pathlib import Path

from dynaconf import Dynaconf

base_dir = Path(__file__).parent.parent

local_path = base_dir / '.local'
os.makedirs(local_path, exist_ok=True)
data_path = Path('/tmp', 'spiderkeeper', 'server', 'datas')
os.makedirs(data_path, exist_ok=True)

_settings_files = [
    Path(__file__).parent / 'settings.yml',
]  # 指定绝对路径加载默认配置

_external_files = [
    Path(sys.prefix, 'etc', 'SPIDERKEEPER', 'server', 'settings.yml')
]

settings = Dynaconf(
    envvar_prefix="SPIDERKEEPER_SERVER",  # 环境变量前缀。设置`SPIDERKEEPER_FOO='bar'`，使用`settings.FOO`
    settings_files=_settings_files,
    # environments=True,  # 启用多层次日志，支持 dev, pro
    load_dotenv=True,  # 加载 .env
    # env_switcher="SPIDERKEEPER_SERVER_ENV",  # 用于切换模式的环境变量名称 SPIDERKEEPER_ENV=production
    lowercase_read=False,  # 禁用小写访问， settings.name 是不允许的
    includes=_external_files,  # 自定义配置覆盖默认配置
    base_dir=base_dir,  # 编码传入配置
    localpath=local_path
)

if not os.path.isabs(settings.LOGPATH):
    settings.set('LOGPATH', local_path / settings.LOGPATH)

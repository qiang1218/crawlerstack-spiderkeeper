import os
from pathlib import Path

from dynaconf import Dynaconf

base_dir = Path(__file__).parent.parent

user_local = Path(os.getenv('HOME')) / '.local'

os.makedirs(user_local, exist_ok=True)

user_local_path = user_local / 'spiderkeeper'

settings_files = [
    Path(__file__).parent / 'settings.yaml',
]  # 指定绝对路径加载默认配置

settings = Dynaconf(
    envvar_prefix="SPIDERKEEPER",  # 环境变量前缀。设置`SPIDERKEEPER_FOO='bar'`，使用`settings.FOO`
    settings_files=settings_files,
    environments=True,  # 启用多层次日志，支持 dev, pro
    load_dotenv=True,  # 加载 .env
    env_switcher="SPIDERKEEPER_ENV",  # 用于切换模式的环境变量名称 SPIDERKEEPER_ENV=production
    lowercase_read=False,  # 禁用小写访问， settings.name 是不允许的
    includes=['/etc/spiderkeeper/settings.yaml'],  # 自定义配置覆盖默认配置
    base_dir=base_dir,  # 编码传入配置
)

# 环境变量的优先级比配置文件要低，所以环境变量会覆盖配置文件。


if not settings.LOGPATH:
    settings.set('LOGPATH', user_local_path / 'logs')

if not os.path.isabs(settings.LOGPATH):
    settings.set('LOGPATH', user_local_path / settings.LOGPATH)

if not settings.ARTIFACT_PATH:
    settings.set('ARTIFACT_PATH', user_local_path / 'artifacts')

if not os.path.isabs(settings.ARTIFACT_PATH):
    settings.set('ARTIFACT_PATH', settings.ARTIFACT_PATH)

"""
配置中心。
使用 Dynaconf 提供配置对象。
项目会加载该目录下的 `settings.yml` 作为默认配置，你也可以在该目录下创建一个 `settings.local.yma` 的本地配置，
用来覆盖默认配置，本地配置文件不会被 git 追踪。
如果项目是以 pip 安装的则会在系统目录中生成默认配置，你可以修改系统配置达到覆盖项目配置的目的。
你可以通过设置以 `SPIDERKEEPER` 为开头的环境变量，来修改项目的默认配置。当你通过容器部署项目的时候，这种方式就很方便来。
你还可以在启动的时候通过命令行覆盖部分已暴露在命令行参数中的配置选项。
上述的配置方式，从上到下，优先级越来越高。就是说如果一个配置你既通过命令行传递，又通过环境变量传递，则只有命令行传入的配置
会生效。
"""

import os
from pathlib import Path

from dynaconf import Dynaconf

base_dir = Path(__file__).parent.parent

user_local = Path(os.getenv('HOME')) / '.local'

os.makedirs(user_local, exist_ok=True)

user_local_path = user_local / 'spiderkeeper'

settings_files = [
    Path(__file__).parent / 'settings.yml',
]  # 指定绝对路径加载默认配置

settings = Dynaconf(
    envvar_prefix="SPIDERKEEPER",  # 环境变量前缀。设置`SPIDERKEEPER_FOO='bar'`，使用`settings.FOO`
    settings_files=settings_files,
    environments=True,  # 启用多层次日志，支持 dev, pro
    load_dotenv=True,  # 加载 .env
    env_switcher="SPIDERKEEPER_ENV",  # 用于切换模式的环境变量名称 SPIDERKEEPER_ENV=production
    lowercase_read=False,  # 禁用小写访问， settings.name 是不允许的
    includes=['/etc/spiderkeeper/settings.yml'],  # 自定义配置覆盖默认配置
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

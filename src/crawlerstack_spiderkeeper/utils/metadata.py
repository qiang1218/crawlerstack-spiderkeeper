import os
from datetime import datetime

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.utils import constants

"""
.
├── artifacts
│   ├── artifact
│   │   └── demo-20191215152202.zip
│   ├── workspaces
│   │   └── demo-20191215152202
│   └── virtual_env
│   │   └── demo-20191215152202
│   └── logs
│       └── demo-20191215152202
│           └── out.log

优点：
    - 使用场景独立，不会因为使用源代码而考虑忽略其他目录
    - 针对像使用 virtualenv 的用户，直接配置目标路径即可直接使用开发中的源码
缺点：
    - 需要多次删除
    - 针对使用 pipenv 或者 virtualenvwrapper 的用户不是很友好，无法直接读取虚拟环境目录
      特别是像 pipenv 创建的目录带 hash
=============================================

.
├── spiderkeeper-artifact
│   ├── demo
│   │   ├── demo-20191215152202
│   │   │   ├── demo-20191215152202.zip
│   │   │   └── demo-20191215152202
│   │   │       ├── boot.py
│   │   │       ├── setup.py
│   │   │       ├── log
│   │   │       │   ├── out.log
│   │   │       │   └── err.log
│   │   │       └── venv
│   │   │           └── bin
│   │   │               ├── python
│   │   │               └── pip
│   │   ├── demo-20201215152202

有点：
    - 便于管理，一次删除归档下的所有东西
    - 所有东西放在一起，方便用户直接配置开发代码路径
缺点：
    - docker 构建的时候需要忽略不需要的文件夹
"""

"""
settings.ARTIFACT_PATH 为设置的归档目录

当前使用第一种目录格式。
"""


class Metadata:
    obj = None

    def __new__(cls):
        # 关键在于这，每一次实例化的时候，我们都只会返回这同一个instance对象

        if not hasattr(cls, '__instance'):
            cls.__instance = super(Metadata, cls).__new__(cls)
            cls.artifact_path = settings.ARTIFACT_PATH
            cls.artifact_files_path = os.path.join(settings.ARTIFACT_PATH, constants.ARTIFACT_FILE_PATHNAME)
            cls.artifact_source_code_path = os.path.join(
                settings.ARTIFACT_PATH,
                constants.ARTIFACT_SOURCE_CODE_PATHNAME
            )
            cls.artifact_virtualenvs_path = os.path.join(settings.ARTIFACT_PATH, constants.ARTIFACT_VIRTUALENV_PATHNAME)
            os.makedirs(cls.artifact_path, exist_ok=True)
            os.makedirs(cls.artifact_files_path, exist_ok=True)
            os.makedirs(cls.artifact_source_code_path, exist_ok=True)
            os.makedirs(cls.artifact_virtualenvs_path, exist_ok=True)
            return cls.__instance


# TODO  增加格式支持

class ArtifactMetadata:
    """
    归档文件元信息。
    将归档文件所对应元信息的规则独立出来，当调整规则时，不影响相关引用逻辑。
    """

    ARTIFACT_PATH = settings.ARTIFACT_PATH

    @classmethod
    def from_project(cls, project_name: str) -> 'ArtifactMetadata':
        return cls(f'{project_name}-{datetime.now().timestamp()}.zip')

    def __init__(self, filename: str):
        """
        :param filename:    project filename
        """
        self._filename = filename
        self.metadata = Metadata()

    def __repr__(self):
        return self.file_basename

    __str__ = __repr__

    @property
    def filename(self) -> str:
        """
        filename
        :return:
        """
        return self._filename

    @property
    def project_name(self) -> str:
        """
        Project name
        :return:
        """
        return self._filename.split('-')[0]

    @property
    def timestamp(self) -> float:
        timestamp = float(self._filename.split('-')[1].rstrip('.zip'))
        return timestamp

    @property
    def file_basename(self):
        """
        not contain file format
        :return:
        """
        return f'{self.project_name}-{self.timestamp}'

    @property
    def file(self) -> str:
        """
        Artifact 文件目录
        :return:
        """
        return os.path.join(self.metadata.artifact_files_path, self._filename)

    @property
    def source_code(self) -> str:
        """
        Artifact 解压目录
        :return:
        """
        return os.path.join(
            self.metadata.artifact_source_code_path,
            self.file_basename
        )

    @property
    def virtualenv(self) -> str:
        """
        Artifact 的虚拟环境目录
        :return:
        """
        artifact_virtualenv_path = os.path.join(
            self.metadata.artifact_virtualenvs_path,
            self.file_basename
        )
        return artifact_virtualenv_path

    @property
    def image_tag(self) -> str:
        """
        Docker Image tag
        :return:
        """
        return f'{self.project_name}:{self.timestamp}'

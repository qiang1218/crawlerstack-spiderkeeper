"""
Local executor.
"""
import asyncio
import functools
import logging
import os
import shutil
import signal
from asyncio import AbstractEventLoop, create_subprocess_shell, subprocess
from functools import partial
from pathlib import Path
from typing import AsyncIterable, Dict, List, Optional

import aiofiles
import toml
from psutil import NoSuchProcess, Process, TimeoutExpired
from virtualenv import cli_run

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.executor.base import (BaseExecuteContext,
                                                     BaseExecutor)
from crawlerstack_spiderkeeper.executor.subprocess import \
    create_subprocess_shell as customs_create_subprocess_shell
from crawlerstack_spiderkeeper.utils import Tail, kill_proc_tree
from crawlerstack_spiderkeeper.utils.exceptions import (
    ExecutorStopError, PKGInstallError, RequirementFileNotFound)
from crawlerstack_spiderkeeper.utils.metadata import ArtifactMetadata
from crawlerstack_spiderkeeper.utils.states import States

logger = logging.getLogger(__name__)


# TODO change build context cmd use env.
# 增加构建环境的时候传入 env ，通过增加 PATH 使用虚拟环境下的默认 python 。

class LocalExecuteContext(BaseExecuteContext):
    """
    local execute context.
    """

    def __init__(self, artifact: ArtifactMetadata, loop: Optional[AbstractEventLoop] = None):
        super().__init__(artifact, loop)

        self.virtualenv = Virtualenv(self.artifact, loop)

    async def build(self) -> None:
        """
        Build execute context.
        :return:
        """
        await self.unpack_artifact()
        await self.virtualenv.init()
        logger.debug('%s context build successfully.', self.artifact.project_name)

    async def delete(self) -> None:
        """
        Delete execute context.
        :return:
        """
        await self.loop.run_in_executor(None, shutil.rmtree, self.artifact.source_code, True)
        logger.debug('Delete artifact source code path: %s', self.artifact.source_code)
        await self.loop.run_in_executor(None, shutil.rmtree, self.artifact.virtualenv, True)
        logger.debug('Delete artifact virtualenv path: %s', self.artifact.virtualenv)

    async def exist(self) -> bool:
        """
        Check if context is exist.
        :return:
        """
        has_source_code = os.path.exists(self.artifact.source_code)
        has_virtualenv = os.path.exists(self.artifact.virtualenv)
        if has_source_code and has_virtualenv:
            return True


class Virtualenv:
    """
    Execute virtual environment.
    """

    def __init__(self, artifact: ArtifactMetadata, loop: Optional[AbstractEventLoop] = None):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.loop = loop or asyncio.get_running_loop()
        self.artifact = artifact
        self.__python_path = None

    async def get_requirements_from_pipfile(self, pipfile: str) -> List[str]:
        """
        Get artifact requirements from pipfile.
        :param pipfile:
        :return:
        """
        requirements = []
        async with aiofiles.open(pipfile, 'r') as f_obj:
            txt = await f_obj.read()
            pipenv = toml.loads(txt)
            packages: Dict[str, str] = pipenv.get('packages')

        for key, value in packages.items():
            if value == "*":
                req = f'{key}'
            else:
                req = f'{key}=="{value}"'
            requirements.append(req)
        self.logger.debug('Read requirement from %s. requirements: %s', pipfile, requirements)
        return requirements

    async def get_requirements_from_txt(self, file: str) -> List[str]:
        """
        Get requirements from requirements.txt
        :param file:
        :return:
        """
        requirements = []
        async with aiofiles.open(file, 'r') as f_obj:
            for line in await f_obj.readlines():
                line = line.strip().replace('\n', '').replace('\r', '')
                if line:
                    requirements.append(line)
            self.logger.debug('Read requirement from %s, requirements: %s', file, requirements)
        return requirements

    async def get_requirements(self) -> List[str]:
        """
        获取归档文件中的依赖包，返回对应的依赖，然后通过 `pip install ` 安装。
        return eg: ['aiohttp=="*"', 'fastapi=="0.58.1"']
        :return:
        """
        pipenv_file = os.path.join(self.artifact.source_code, 'Pipfile')
        requirements_txt = os.path.join(self.artifact.source_code, 'requirements.txt')
        if os.path.isfile(pipenv_file):
            requirements = await self.get_requirements_from_pipfile(pipenv_file)
        elif os.path.isfile(requirements_txt):
            requirements = await self.get_requirements_from_txt(requirements_txt)
        else:
            raise RequirementFileNotFound(self.artifact.source_code)

        return requirements

    @property
    def python_path(self) -> str:
        """
        虚拟环境 python 脚本的位置。
        :return:
        """
        if self.__python_path:
            return self.__python_path
        return os.path.join(self.artifact.virtualenv, 'bin', 'python')

    async def create(self) -> None:
        """
        创建虚拟环境
        :return:
        """
        partial_cli_run = functools.partial(cli_run, setup_logging=False)

        session = await self.loop.run_in_executor(
            None,
            partial_cli_run,
            self.artifact.virtualenv.split()
        )
        self.__python_path = session.creator.exe
        logger.debug('Create virtualenv in %s', self.artifact.virtualenv)

    async def install(self, requirement, *requirements) -> None:
        """
        安装 requirement 。
        使用异步创建子进程，调用虚拟环境中的 python -m pip install xxx 。如果返回代码不是 0，
        则说明安装过程出现错误，直接抛出异常
        :param requirement:
        :param requirements:
        :return:
        """
        reqs = [requirement, *requirements]
        req = ' '.join(reqs)
        self.logger.debug('Installing pkg: %s, please waiting...', ", ".join(reqs))
        process = await create_subprocess_shell(
            cmd=f'{self.python_path} '
                f'-m pip install '
                f'--index-url http://repo.tendata.com.cn/repository/pypi-all/simple '
                f'--trusted-host repo.tendata.com.cn '
                f'{req}',
            # cmd=f'python -m pip install {req}',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        code = await process.wait()
        (stdout_data, stderr_data) = await process.communicate()
        if code:
            raise PKGInstallError(stderr_data.decode(), code)
        self.logger.debug(
            'Install pkg: %s success. \nDetail: %s',
            ", ".join(reqs),
            stdout_data.decode("utf-8")
        )

    async def init(self) -> None:
        """
        初始化虚拟环境目录，然后安装虚拟环境。
        :return:
        """
        self.logger.debug('Init virtualenv ...')
        await self.create()
        requirements = await self.get_requirements()
        await self.install(*requirements)
        self.logger.debug('Virtualenv inited.')


std_log_path = Path(settings.LOGPATH) / 'containers'
os.makedirs(std_log_path, exist_ok=True)


class LocalExecutor(BaseExecutor):
    """
    Local executor.
    """
    _executor_context_cls = LocalExecuteContext

    @property
    def _process(self):
        """
        Local process
        :return:
        """
        return Process(int(self.pid))

    @classmethod
    async def run(
            cls,
            artifact: ArtifactMetadata,
            cmdline: List[str],
            env: Dict[str, str],
            target: Optional[str] = None,
            loop: Optional[AbstractEventLoop] = None
    ) -> 'LocalExecutor':
        """
        使用 cmdline 创建子进程运行程序。
        考虑到 cmdline 可能需要在源码目录的相对路径下运行，所以在创建子进程的时候先切换目录到源码目录
        然后再运行 cmdline 。
        :param artifact:
        :param cmdline:
        :param env:
        :param target:
        :param loop:
        :return:
        """
        executor_context = cls._executor_context_cls(artifact, loop)
        if not await executor_context.exist():
            await executor_context.build()
        cwd = os.getcwd()
        os.chdir(artifact.source_code)

        env.update({
            'ARTIFACT_FILENAME': artifact.filename,
            'VIRTUAL_ENV': artifact.virtualenv,
            'PATH': f'{artifact.virtualenv}/bin:{os.environ.get("PATH")}'
        })

        process = await customs_create_subprocess_shell(
            cmd=' '.join(cmdline),
            std_path=std_log_path,
            back_count=10,
            max_bytes=1024 * 1024 * 20,
            loop=loop,
            env=env
        )
        os.chdir(cwd)
        logger.debug('Run subprocess %s. Artifact: %s', process.pid, artifact)
        return cls(artifact, str(process.pid), loop)

    async def stop(self) -> None:
        """
        Stop executor.
        :return:
        """
        func = partial(
            kill_proc_tree,
            pid=int(self.pid),
            sig=signal.SIGTERM,
            include_parent=True,
            timeout=10,
            on_terminate=None
        )
        self.logger.debug('Stopping process %s', self.pid)
        try:
            (_, alive) = await self.loop.run_in_executor(None, func)
            if alive:
                alive_pid = [process.pid for process in alive]
                self.logger.error(
                    'Stop process %s error, some pid is alive: %s',
                    self.pid, alive_pid
                )
                raise ExecutorStopError(self.pid, alive_pid)
        except NoSuchProcess as ex:
            self.logger.warning(ex)

    async def delete(self) -> None:
        """
        Delete executor
        :return:
        """
        self.logger.debug('Stop local process %s ...', self.pid)
        await self.stop()

    async def running(self) -> bool:
        """
        Run executor.
        :return:
        """
        try:
            await self.loop.run_in_executor(None, self._process.wait, 2)
            return False
        except TimeoutExpired:
            if self._process.is_running():
                return True

    async def status(self) -> Dict:
        """
        Get executor status.
        :return:
        """
        if self._process.is_running():
            detail = 'Process %s is running', self.pid
            state = States.RUNNING
        else:
            exit_code = await self.loop.run_in_executor(None, self._process.wait, 0)
            if exit_code < 0:
                detail = 'Process %s terminated by a signal', self.pid
                state = States.STOPPED
            elif exit_code > 0:
                detail = 'Process %s exit, code: %s', self.pid, exit_code
                state = States.STOPPED
            else:
                detail = 'Process %s finished.', self.pid
                state = States.FINISH
        self.logger.debug(*detail)
        return {
            'state': state,
            'detail': detail
        }

    async def log(self, follow=False) -> AsyncIterable[str]:
        """
        Get executor log.
        :param follow:
        :return:
        """
        tail = Tail(std_log_path / f'pid-{self.pid}.log')
        if follow:
            return tail.follow()
        return tail.last()

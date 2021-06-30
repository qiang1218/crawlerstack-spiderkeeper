"""
Test local executor.
"""
import logging
import os

import psutil
import pytest
from virtualenv import cli_run

from crawlerstack_spiderkeeper.executor.local import (LocalExecuteContext,
                                                      LocalExecutor,
                                                      Virtualenv)
from crawlerstack_spiderkeeper.utils.exceptions import (
    PKGInstallError, RequirementsFileNotFound)


def write(file, data):
    """Write data to file."""
    with open(file, 'w') as f_obj:
        f_obj.write(data)


class TestVirtualenv:
    """Test virtualenv."""

    @pytest.fixture()
    async def venv_path(self, temp_dir, event_loop):
        """Fixture virtualenv path"""
        venv_path = os.path.join(temp_dir, 'venv')
        await event_loop.run_in_executor(None, cli_run, [venv_path])
        yield venv_path

    @pytest.fixture()
    async def pipfile(self, temp_dir, event_loop):
        """Fixture pipenv file."""
        pipfile = os.path.join(temp_dir, 'Pipfile')
        data = """
[[source]]
url = "https://mirrors.aliyun.com/pypi/simple/"
verify_ssl = true
name = "aliyun"

[packages]
setuptools = "*"
six = "1.15.0"
        """
        await event_loop.run_in_executor(None, write, pipfile, data)
        yield pipfile

    @pytest.fixture()
    async def req_file(self, temp_dir, event_loop):
        """Fixture requirements file."""
        req_file = os.path.join(temp_dir, 'requirements.txt')
        data = """setuptools
six=="1.15.0"
    """
        await event_loop.run_in_executor(None, write, req_file, data)
        yield req_file

    @pytest.mark.asyncio
    async def test_get_requirement_from_pipfile(self, mocker, pipfile):
        """Test get requirements from pipfile"""
        virtualenv = Virtualenv(mocker.MagicMock())
        requirements = await virtualenv.get_requirements_from_pipfile(pipfile)
        assert requirements == ['setuptools', 'six=="1.15.0"']

    @pytest.mark.asyncio
    async def test_get_requirements_from_txt(self, mocker, req_file):
        """Test get requirements from requirements.txt"""
        virtualenv = Virtualenv(mocker.MagicMock())
        requirements = await virtualenv.get_requirements_from_txt(req_file)
        assert requirements == ['setuptools', 'six=="1.15.0"']

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ('req_name', 'raise_exception'),
        [
            ('pipfile', False),
            ('req_file', False),
            (None, True)
        ]
    )
    async def test_get_requirements(self, mocker, req_file, pipfile, req_name, raise_exception):
        """Test get requirements."""
        artifact = mocker.MagicMock()
        if req_name == 'pipfile':
            artifact.source_code = os.path.dirname(pipfile)
        elif req_name == 'req_file':
            os.remove(pipfile)
            artifact.source_code = os.path.dirname(req_file)
        else:
            artifact.source_code = '/tmp/foo'
        virtualenv = Virtualenv(artifact)
        if raise_exception:
            with pytest.raises(RequirementsFileNotFound):
                await virtualenv.get_requirements()
        else:
            requirements = await virtualenv.get_requirements()
            assert requirements == ['setuptools', 'six=="1.15.0"']

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ('reqs', 'raise_exception'),
        [
            (['setuptools', 'six=="1.15.0"'], False),
            (['_xxx_test', 'six=="1.15.0"'], True)
        ]
    )
    async def test_install(self, mocker, venv_path, reqs, raise_exception, caplog):
        """Test install requirements."""
        with caplog.at_level(logging.DEBUG):
            artifact = mocker.MagicMock()
            artifact.virtualenv = venv_path
            virtualenv = Virtualenv(artifact)

        if raise_exception:
            with pytest.raises(PKGInstallError):
                await virtualenv.install(*reqs)
        else:
            await virtualenv.install(*reqs)
            assert ', '.join(reqs) in caplog.text

    @pytest.mark.asyncio
    async def test_init(self, mocker, temp_dir, pipfile):
        """Test init virtualenv."""
        artifact = mocker.MagicMock()
        artifact.source_code = os.path.dirname(pipfile)
        artifact.virtualenv = os.path.join(temp_dir, 'venv')
        virtualenv = Virtualenv(artifact)
        await virtualenv.init()


@pytest.fixture()
def local_ctx(artifact_metadata, event_loop):
    """Fixture local context."""
    ctx = LocalExecuteContext(artifact_metadata, event_loop)
    yield ctx


class TestLocalExecuteContext:
    """Test local execute context."""

    @pytest.mark.asyncio
    async def test_build(self, local_ctx, caplog):
        """Test build context."""
        with caplog.at_level(logging.DEBUG):
            await local_ctx.build()
            assert os.path.isfile(local_ctx.artifact.file)
            assert os.path.exists(local_ctx.artifact.source_code)
            assert os.path.exists(local_ctx.artifact.virtualenv)
            assert 'context build successfully' in caplog.text

    @pytest.mark.asyncio
    async def test_delete(self, local_ctx, caplog):
        """Test delete context."""
        with caplog.at_level(logging.DEBUG):
            await local_ctx.build()
            await local_ctx.delete()
            assert not os.path.exists(local_ctx.artifact.source_code)
            assert not os.path.exists(local_ctx.artifact.virtualenv)
            assert 'Delete artifact source code path' in caplog.text
            assert 'Delete artifact virtualenv path' in caplog.text

    @pytest.mark.asyncio
    async def test_exist(self, local_ctx):
        """Test if context is exist."""
        await local_ctx.build()
        exist = await local_ctx.exist()
        assert exist


@pytest.mark.asyncio
async def test_delete(artifact_metadata):
    """Test delete local executor."""
    executor = await LocalExecutor.run(
        artifact=artifact_metadata,
        cmdline='scrapy crawl example'.split(),
        env={},
    )
    await executor.delete()
    assert not int(executor.pid) in psutil.pids()

"""
Test job service.
"""
import asyncio
import logging

import pytest
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import greenlet_spawn

from crawlerstack_spiderkeeper.db.models import Artifact, Job, Task
from crawlerstack_spiderkeeper.services import JobService
from crawlerstack_spiderkeeper.utils.states import States


async def update_artifact_state(session: AsyncSession, job_id: int, state: States):
    """Update artifact state."""
    async with session.begin():
        job = await session.get(Job, job_id)
        stmt = update(Artifact).where(Artifact.id == job.artifact_id).values(state=state)
        await session.execute(stmt)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ['executor_context_exist', 'artifact_state', 'expect_value'],
    [
        (True, States.FINISH.value, 'skip'),
        (False, States.FINISH.value, 'finish'),
    ]
)
async def test_run_with_no_run_job(
        mocker,
        init_job,
        session,
        factory_with_session,
        executor_context_exist,
        artifact_state,
        expect_value,
        caplog,
):
    """Test run a not exist job."""
    async with session.begin():
        job: Job = await session.scalar(select(Job))
        artifact_id = job.artifact_id
    await update_artifact_state(session, job.id, artifact_state)

    async with factory_with_session(JobService) as service:
        mocker.patch.object(
            service.executor_cls._executor_context_cls,  # pylint: disable=protected-access
            'exist',
            return_value=executor_context_exist,
            new_callable=mocker.AsyncMock
        )
        mocker.patch.object(
            service.executor_cls._executor_context_cls,  # pylint: disable=protected-access
            'build',
            new_callable=mocker.AsyncMock
        )
        async_mocker = mocker.AsyncMock
        async_mocker.pid = 'foo'
        mocker.patch.object(service.executor_cls, 'run', new_callable=async_mocker)

        with caplog.at_level(level=logging.DEBUG, logger='crawlerstack_spiderkeeper.services.job'):
            await service.run(job.id)
            assert expect_value in caplog.text

    async with session.begin():
        # 注意：这里使用了 greenlet_spawn 对底层的同步 session 对象做了缓存的数据全部过期。
        # 由于创建 session 使用了 expire_on_commit=False ，所以对象会被缓存下来
        # 另外需要说明一点的是： sessionmaker 创建出来的 session 对象不包含 expire_all
        # 这个方法是 async_scoped_session 代理的。
        await greenlet_spawn(session.sync_session.expire_all)
        artifact = await session.get(Artifact, artifact_id)

    assert artifact.state == States.FINISH.value


@pytest.fixture()
async def init_job_have_no_running_task(init_job, session):
    """Test init a job, that have no running task."""
    async with session.begin():
        result = await session.execute(select(Job))
        jobs = result.scalars().all()
        tasks = [
            Task(job_id=jobs[0].id, state=States.STOPPED.value),
            Task(job_id=jobs[1].id, state=States.RUNNING.value, container_id='001'),
        ]
        session.add_all(tasks)


@pytest.mark.asyncio
async def test_run_with_run_job(init_task, session, caplog, factory_with_session):
    """Test run a running job."""
    stmt = select(Job).join(Job.tasks.and_(Task.state == States.RUNNING.value))
    job = await session.scalar(stmt)
    async with factory_with_session(JobService) as service:
        res = await service.run(job.id)
    assert res == 'Job already run.'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ['have_running_task', 'stop_error'],
    [
        (False, None),
        (False, Exception('xxx')),
        (True, None),
        (True, Exception('xxx')),
    ]
)
async def test_stop(
        mocker,
        session,
        factory_with_session,
        init_job_have_no_running_task,
        have_running_task,
        stop_error,
        caplog
):
    """Test stop a job."""
    state = States.RUNNING.value if have_running_task else States.STOPPED.value
    stmt = select(Job).join(Job.tasks.and_(Task.state == state))
    job = await session.scalar(stmt)

    async with factory_with_session(JobService) as service:
        mocker.patch.object(
            service.executor_cls,
            'stop',
            new_callable=mocker.AsyncMock,
            side_effect=stop_error
        )

        with caplog.at_level(level=logging.DEBUG, logger='crawlerstack_spiderkeeper.services.job'):
            res = await service.stop(job.id)
            if have_running_task:
                assert res == 'Stopped'
            else:
                assert res == 'No task run.'

            if have_running_task and stop_error:
                assert 'Stop fail' in caplog.text
            else:
                assert 'Stop fail' not in caplog.text

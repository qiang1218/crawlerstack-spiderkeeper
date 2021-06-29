"""
Test job service.
"""
import logging

import pytest

from crawlerstack_spiderkeeper.db import SessionFactory
from crawlerstack_spiderkeeper.db.models import Artifact, Job, Task
from crawlerstack_spiderkeeper.services import job_service
from crawlerstack_spiderkeeper.utils.mock import AsyncMock
from crawlerstack_spiderkeeper.utils.states import States


def update_artifact_state(job_id: int, state: States):
    """Update artifact state."""
    session = SessionFactory()
    job = session.query(Job).get(job_id)
    artifact = job.artifact
    setattr(artifact, 'state', state.value)
    session.add(artifact)
    session.commit()
    session.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ['executor_context_exist', 'artifact_state', 'expect_value'],
    [
        (True, States.FINISH, 'skip'),
        (False, States.FINISH, 'finish'),
        (False, States.CREATED, 'finish'),
    ]
)
async def test_run_with_no_run_job(
        mocker,
        init_job,
        session,
        executor_context_exist,
        artifact_state,
        expect_value,
        caplog,
):
    """Test run a not exist job."""
    mocker.patch.object(
        job_service.executor_cls._executor_context_cls,  # pylint: disable=protected-access
        'exist',
        return_value=executor_context_exist,
        new_callable=AsyncMock
    )
    mocker.patch.object(
        job_service.executor_cls._executor_context_cls,  # pylint: disable=protected-access
        'build',
        new_callable=AsyncMock
    )
    async_mocker = AsyncMock
    async_mocker.pid = 'foo'
    mocker.patch.object(job_service.executor_cls, 'run', new_callable=async_mocker)

    with caplog.at_level(level=logging.DEBUG, logger='crawlerstack_spiderkeeper.services.job'):
        job: Job = session.query(Job).first()
        artifact_id = job.artifact_id
        update_artifact_state(job.id, artifact_state)
        await job_service.run(job.id)
        assert expect_value in caplog.text
        artifact: Artifact = session.query(Artifact).get(artifact_id)
        assert artifact.state == States.FINISH.value


@pytest.fixture()
def init_job_have_no_running_task(init_job):
    """Test init a job, that have no running task."""
    session = SessionFactory()
    jobs = session.query(Job).all()
    tasks = [
        Task(job_id=jobs[0].id, state=States.STOPPED.value),
        Task(job_id=jobs[1].id, state=States.RUNNING.value, container_id='001'),
    ]
    session.add_all(tasks)
    session.commit()
    session.close()


@pytest.mark.asyncio
async def test_run_with_run_job(init_task, session, caplog):
    """Test run a running job."""
    job = session.query(Job).join(Task).filter(Task.state == States.RUNNING.value).first()
    res = await job_service.run(job.id)
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
        init_job_have_no_running_task,
        have_running_task,
        stop_error,
        caplog
):
    """Test stop a job."""
    mocker.patch.object(
        job_service.executor_cls,
        'stop',
        new_callable=AsyncMock,
        side_effect=stop_error
    )
    state = States.RUNNING.value if have_running_task else States.STOPPED.value
    job = session.query(Job).join(Task).filter(Task.state == state).first()
    with caplog.at_level(level=logging.DEBUG, logger='crawlerstack_spiderkeeper.services.job'):
        res = await job_service.stop(job.id)
        if have_running_task:
            assert res == 'Stopped'
        else:
            assert res == 'No task run.'

        if have_running_task and stop_error:
            assert 'Stop fail' in caplog.text
        else:
            assert 'Stop fail' not in caplog.text

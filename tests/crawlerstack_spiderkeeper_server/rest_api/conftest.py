"""rest api"""
import pytest
from fastapi_sa.database import db
from crawlerstack_spiderkeeper_server.models import Project, Artifact, StorageServer, Job, Task, TaskDetail
from fastapi import Response


@pytest.fixture()
async def init_project():
    """Init project fixture."""
    async with db():
        projects = [
            Project(name="test1", desc="test1"),
            Project(name="test2", desc="test2"),
        ]
        db.session.add_all(projects)
        await db.session.flush()


@pytest.fixture()
async def init_artifact(init_project):
    """Init artifact fixture."""
    async with db():
        artifacts = [
            Artifact(name="test1", desc="test1", image='test1', version='latest', project_id=1),
            Artifact(name="test2", desc="test2", image='test2', version='latest', project_id=2),
        ]
        db.session.add_all(artifacts)
        await db.session.flush()


@pytest.fixture()
async def init_storage_server():
    """Init storage server fixture."""
    async with db():
        storage_servers = [
            StorageServer(name="test1", url="mysql://root:root@localhost:3306/spiderkeeper_server",
                          storage_class='mysql'),
            StorageServer(name="test2", url="mysql://root:root@localhost:3306/spiderkeeper_server",
                          storage_class='mysql'),
        ]
        db.session.add_all(storage_servers)
        await db.session.flush()


@pytest.fixture()
async def init_job(init_artifact, init_storage_server):
    """Init job fixture."""
    async with db():
        jobs = [
            Job(name="test1", trigger_expression="0 0 * * *", storage_enable=True, executor_type='docker',
                storage_server_id=1, artifact_id=1, enabled=False, pause=False),
            Job(name="test2", trigger_expression="0 1 * * *", storage_enable=False, executor_type='docker',
                artifact_id=1, enabled=True, pause=False),
            Job(name="test3", trigger_expression="0 1 * * *", storage_enable=False, executor_type='docker',
                artifact_id=1, enabled=True, pause=True),
        ]
        db.session.add_all(jobs)
        await db.session.flush()


@pytest.fixture()
async def init_task(init_job):
    """Init task fixture."""
    async with db():
        tasks = [
            Task(name="test1", job_id=1),
            Task(name="test2", job_id=2),
        ]
        db.session.add_all(tasks)
        await db.session.flush()


@pytest.fixture()
async def init_task_detail(init_task):
    """Init task detail fixture."""
    async with db():
        task_details = [
            TaskDetail(item_count=0, task_id=1),
            TaskDetail(item_count=1, task_id=2),
        ]
        db.session.add_all(task_details)
        await db.session.flush()


def assert_status_code(response: Response, code=200) -> None:
    """Check state code is ok."""
    assert response.status_code == code

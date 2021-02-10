import pytest

from crawlerstack_spiderkeeper.db.models import Artifact, Job


def test_migrate(migrate, session):
    table_names = session.bind.table_names()
    print(table_names)
    assert table_names


@pytest.mark.asyncio
async def test_db(session, init_artifact, init_job):
    artifact: Artifact = session.query(Artifact).first()
    job = Job(name='xxx', artifact_id=artifact.id)
    session.add(job)
    jobs = session.query(Artifact).all()
    assert len(jobs) == 2

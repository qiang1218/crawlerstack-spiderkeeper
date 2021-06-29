"""Test server dao"""
from crawlerstack_spiderkeeper.dao import server_dao
from crawlerstack_spiderkeeper.db.models import Job


def test_get_server_by_job_id(init_job, session):
    """test get_server_by_job_id"""
    job = session.query(Job).first()
    server = server_dao.get_server_by_job_id(job_id=job.id)
    assert job.server_id == server.id

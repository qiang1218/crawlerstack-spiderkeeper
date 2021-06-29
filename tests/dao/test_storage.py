"""Test storage dao"""
from crawlerstack_spiderkeeper.dao import storage_dao
from crawlerstack_spiderkeeper.db.models import Storage
from crawlerstack_spiderkeeper.utils.states import States


def test_increase_storage_count(init_storage, session):
    """test increase_storage_count"""
    before = session.query(Storage).first()
    after = storage_dao.increase_storage_count(pk=before.id)
    assert after.count == before.count + 1


def test_running_storage(init_storage, session):
    """test running_storage"""
    objs = storage_dao.running_storage()
    assert len(objs) == session.query(Storage).filter_by(
        state=States.RUNNING.value
    ).count()

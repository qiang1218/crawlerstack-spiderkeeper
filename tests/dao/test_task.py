"""Test task dao"""

from crawlerstack_spiderkeeper.dao import task_dao
from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.utils.states import States


def test_get_running(init_task, session):
    """test get_running"""
    tasks = task_dao.get_running()
    assert len(tasks) == session.query(Task).filter_by(
        state=States.RUNNING.value).count()
    tasks = task_dao.get_running(job_id=100)
    assert not tasks


def test_count_running_task(init_task, session):
    """test count_running_task"""
    count = task_dao.count_running_task()
    assert count == session.query(Task).filter_by(
        state=States.RUNNING.value
    ).count()

    count = task_dao.count_running_task(job_id=100)
    assert not count


def test_increase_item_count(init_task, session):
    """test increase_item_count"""
    before = session.query(Task).first()
    after = task_dao.increase_item_count(before.id)
    assert after.item_count == before.item_count + 1

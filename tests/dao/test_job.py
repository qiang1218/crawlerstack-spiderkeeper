"""Test job dao"""
import pytest

from crawlerstack_spiderkeeper.dao import job_dao
from crawlerstack_spiderkeeper.db.models import Job, Task


@pytest.mark.parametrize(
    'exist',
    [True, False]
)
def test_job_state(init_task, session, exist):
    """test job_state"""
    if exist:
        obj = session.query(Job).first()
        state = job_dao.state(pk=obj.id)
        task = session.query(Task).first()
        assert task.state == state.value
    else:
        state = job_dao.state(pk=100)
        assert not state

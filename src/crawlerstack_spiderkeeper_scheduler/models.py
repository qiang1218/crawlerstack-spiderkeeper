"""db models"""
from datetime import datetime

import inflection
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from crawlerstack_spiderkeeper_scheduler.utils.status import Status


class CustomBase:
    """
    Customs DB base class
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return inflection.underscore(cls.__name__)  # pylint: disable=no-member


BaseModel = declarative_base(cls=CustomBase)


class Executor(BaseModel):
    """
    Project model.
    """
    name = Column(String(200), nullable=False, comment='执行器名称')
    selector = Column(String(200), nullable=False, comment='自定义选择器')
    url = Column(String(200), nullable=False, comment='api url')
    type = Column(String(200), nullable=False, comment='类型')
    status = Column(Integer, default=Status.ONLINE.value, comment='在线或离线')
    memory = Column(Integer, nullable=False, comment='内存G')
    cpu = Column(Integer, nullable=False, comment='cpu占用%')

    # Cascade delete artifacts when delete project.
    executor_detail = relationship(
        'ExecutorDetail',
        backref='executor_detail',
        passive_deletes=True  # 在删除父记录的时候检查子记录的约束。如果 ON DELETE 为 RESTRICT 则抛出异常。对于非数据库
    )
    task = relationship(
        'Task',
        backref='task',
        passive_deletes=True
    )


class ExecutorDetail(BaseModel):
    """
    Artifact model.
    """
    task_count = Column(Integer, nullable=False, comment='任务个数')
    executor_id = Column(
        Integer,
        ForeignKey('executor.id', ondelete='CASCADE'),
        nullable=False
    )  # 级联删除


class Task(BaseModel):
    """
    StorageService model
    """

    name = Column(String(200), nullable=False, comment='任务名称', unique=True)
    url = Column(String(200), nullable=False, comment='任务调度位置')
    type = Column(String(200), nullable=False, comment='任务类型')
    status = Column(Integer, default=Status.CREATED.value, comment='任务状态')
    executor_id = Column(
        Integer,
        ForeignKey('executor.id', ondelete='CASCADE'),
        nullable=False
    )  # 级联删除
    container_id = Column(String(200), nullable=False, comment='容器ID')
    task_start_time = Column(DateTime, default=datetime.now, comment='任务创建时间')
    task_end_time = Column(DateTime, nullable=True, default=None, comment='任务结束时间')

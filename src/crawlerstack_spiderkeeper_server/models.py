"""db models"""
from datetime import datetime

import inflection
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from crawlerstack_spiderkeeper_server.utils.status import Status


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


class Project(BaseModel):
    """
    Project model.
    """
    name = Column(String(200), nullable=False, comment='项目名称')
    desc = Column(String(200), nullable=False, comment='项目描述')

    # Cascade delete artifacts when delete project.
    artifacts = relationship(
        'Artifact',
        backref='project',
        passive_deletes=True  # 在删除父记录的时候检查子记录的约束。如果 ON DELETE 为 RESTRICT 则抛出异常。对于非数据库
    )


class Artifact(BaseModel):
    """
    Artifact model.
    """
    name = Column(String(200), nullable=False, comment='归档名称')
    desc = Column(String(2000), nullable=False, comment='归档描述')
    image = Column(String(200), nullable=False, comment='镜像名称')
    tag = Column(String(200), nullable=True, comment='归档标签')
    version = Column(String(20), nullable=True, comment='镜像版本')
    project_id = Column(
        Integer,
        ForeignKey('project.id', ondelete='CASCADE'),
        nullable=False
    )  # 级联删除

    # Restrict delete jobs when delete project.
    jobs = relationship('Job', backref='artifact', passive_deletes=True)


class StorageServer(BaseModel):
    """
    StorageService model
    """

    name = Column(String(200), nullable=False, comment='存储服务名称', unique=True)
    url = Column(String(200), nullable=False, comment='地址')
    storage_class = Column(String(200), nullable=False, comment="存储实现")

    jobs = relationship(
        'Job',
        backref='storage_server',
        passive_deletes=False  # 在删除父记录的时候检查子记录的约束。如果 ON DELETE 为 RESTRICT 则抛出异常。对于非数据库
    )


class Job(BaseModel):
    """
    Job model
    """
    name = Column(String(200), nullable=False, comment='job名称')
    cmdline = Column(String(500), nullable=True, comment='执行命令')
    environment = Column(String(2000), nullable=True, comment='环境变量')
    volume = Column(String(2000), nullable=True, comment='目录挂载')
    trigger_expression = Column(String(100), nullable=False, comment='crontab表达式')
    storage_enable = Column(Boolean, default=False, comment='是否开启存储')

    storage_server_id = Column(
        Integer,
        ForeignKey('storage_server.id', ondelete='SET NULL'),
        nullable=True,
        comment='存储服务id'
    )  # 级联删除
    executor_type = Column(String(100), nullable=False, comment='执行器类型')
    enabled = Column(Boolean, default=False, comment='job状态')
    pause = Column(Boolean, default=False, comment='任务暂停状态')
    executor_selector = Column(String(100), nullable=True, comment='执行器选择器')
    artifact_id = Column(
        Integer,
        ForeignKey('artifact.id', ondelete='RESTRICT')
    )

    # Restrict delete when delete job.
    tasks = relationship("Task", backref="job", cascade="all, delete-orphan", passive_deletes=True)


class Task(BaseModel):
    """
    Task model
    """
    name = Column(String(200), nullable=False, comment='任务名称')
    status = Column(Integer, default=Status.CREATED.value, comment='任务状态')
    job_id = Column(
        Integer,
        ForeignKey('job.id', ondelete='SET NULL'),
        nullable=True,
        comment='job id'
    )
    task_details = relationship('TaskDetail', backref='task', cascade='all, delete-orphan', passive_deletes=True)


class TaskDetail(BaseModel):
    """
    TaskDetail model
    """
    item_count = Column(Integer, default=0, nullable=False, comment='写入数据量')
    detail = Column(String(100), nullable=True, comment='任务失败值存储')
    task_id = Column(
        Integer,
        ForeignKey('task.id', ondelete='CASCADE'),
        nullable=False,
        comment='task id'
    )

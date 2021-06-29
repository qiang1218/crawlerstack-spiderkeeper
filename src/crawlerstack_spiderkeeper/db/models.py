"""
DB models.
"""
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from crawlerstack_spiderkeeper.utils.states import States


class CustomBase:
    """
    Customs DB base class
    """
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return cls.__name__.lower()  # pylint: disable=no-member


BaseModel = declarative_base(cls=CustomBase)


class Server(BaseModel):
    """
    Server model.
    """
    name = Column(String(45), unique=True, comment='服务器名称')
    type = Column(String(45), comment='服务器类型')  # 服务器类型
    uri = Column(String(100), comment='URI')
    enable = Column(Boolean, default=False, comment='是否启用配置')

    jobs = relationship('Job', backref='server')


class Project(BaseModel):
    """
    Project model.
    """
    name = Column(String(200), nullable=False, comment='项目名称')
    slug = Column(String(200), unique=True, nullable=False)
    desc = Column(Text, nullable=True, comment='项目描述')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # Cascade delete artifacts when delete project.
    artifacts = relationship(
        "Artifact",
        backref="project",
        passive_deletes=True  # 在删除父记录的时候检查子记录的约束。如果 ON DELETE 为 RESTRICT 则抛出异常。对于非数据库
    )


class Artifact(BaseModel):
    """
    Artifact model.
    """
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    filename = Column(String(200), comment='文件名称')
    interpreter = Column(String(500), default='python', nullable=True, comment='解释器')
    tag = Column(String(100), nullable=True, comment='Tag')
    execute_path = Column(String(100), nullable=True, comment='执行路径')
    state = Column(Integer, default=States.CREATED.value, comment='状态')
    project_id = Column(
        Integer,
        ForeignKey("project.id", ondelete='CASCADE'),
        nullable=False
    )  # 级联删除

    # Restrict delete jobs when delete project.
    jobs = relationship("Job", backref="artifact", passive_deletes=True)


class Job(BaseModel):
    """
    Job mode.
    """
    name = Column(String(200), nullable=False)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cmdline = Column(String(200), nullable=True, comment='执行命令')

    storage_enable = Column(Boolean, default=False, comment='是否开启存储')

    artifact_id = Column(Integer, ForeignKey('artifact.id', ondelete='RESTRICT'))
    server_id = Column(Integer, ForeignKey('server.id', ondelete='SET NULL'), nullable=True)

    # Restrict delete when delete job.
    tasks = relationship("Task", backref="job", cascade="all, delete-orphan", passive_deletes=True)
    reports = relationship(
        'Storage',
        backref='job',
        cascade='all, delete-orphan',
        passive_deletes=True,
        uselist=False
    )


class Task(BaseModel):
    """
    Task model.
    """
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    state = Column(Integer, default=States.CREATED.value, comment='任务状态')
    item_count = Column(Integer, default=0, comment='写入数据数量')
    detail = Column(Text, nullable=True, comment='任务详情')
    container_id = Column(String(120), comment='容器 ID')

    job_id = Column(Integer, ForeignKey("job.id", ondelete='RESTRICT'))


class Storage(BaseModel):
    """
    Storage model
    """
    create_time = Column(DateTime, default=datetime.now, comment='开始时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    count = Column(Integer, default=0, comment='导出数据量')
    state = Column(Integer, default=States.CREATED.value, comment='存储任务状态')
    detail = Column(String(1000), nullable=True, comment='存储任务详情，失败后的值可以存在这里，便于诊断')

    job_id = Column(Integer, ForeignKey('job.id', ondelete='CASCADE'))


class Audit(BaseModel):
    """
    Audit model
    """
    datetime = Column(DateTime, default=datetime.now)
    url = Column(String(300), comment='URL')
    method = Column(String(10), comment='HTTP 方法')
    client = Column(String(150), comment='客户端地址')
    detail = Column(Text, comment='详细内容')

    user_id = Column(Integer, nullable=True, comment='用户')

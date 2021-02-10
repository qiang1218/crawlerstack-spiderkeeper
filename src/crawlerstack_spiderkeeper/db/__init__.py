from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from crawlerstack_spiderkeeper.config import settings

engine: Engine = create_engine(
    settings.DATABASE,
    # echo=True,
)

SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=True)

# https://docs.sqlalchemy.org/en/13/orm/contextual.html#using-thread-local-scope-with-web-applications
# 在使用此 ScopedSession 的时候需要先初始化 ScopedSession() 注册 session 对象。然后直接使用 ScopedSession.query(User).all()
# 因为 ScopedSession 具有代理功能
# 使用结束后调用 session.remove() 删除前面注册的对象
ScopedSession = scoped_session(SessionFactory)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    from sqlite3 import Connection

    if isinstance(dbapi_connection, Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

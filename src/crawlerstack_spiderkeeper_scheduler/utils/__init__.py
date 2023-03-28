"""utils"""


class SingletonMeta(type):
    """
    单例元类

    example:
        class Foo(metaclass=SingletonMeta):...
    """
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
        return cls.__instances[cls]

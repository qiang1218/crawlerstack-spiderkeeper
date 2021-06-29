"""
Exceptions.
"""
from typing import List, Optional

from fastapi import HTTPException
from starlette import status


class SpiderkeeperError(Exception):
    """SpiderkeeperError"""


class ObjectDoesNotExist(HTTPException):
    """
    Object does not exist.
    """

    # TODO 增加传入 model 参数，异常返回对应 model.id=1 不存在。
    def __init__(
            self,
            detail: Optional[str] = 'Object does not exist!',
    ):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class DeleteConstraintError(HTTPException):
    """
    406 Not Acceptable.
    """

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=detail or 'Delete error, some children node exist.'
        )


class RequirementFileNotFound(Exception):
    """Requirement file not found error"""

    def __init__(self, path: Optional[str] = None):
        super().__init__()
        self.path = path

    def __repr__(self):
        """Return fmt str."""
        return f'Requirement file not found in {self.path}, ' \
               f'your artifact should contain "Pipfile" or "requirement.txt"'


class PKGInstallError(Exception):
    """Pkg install error"""

    def __init__(self, detail: Optional[str] = None, exit_code: Optional[int] = None):
        self.detail = detail
        self.exit_code = exit_code
        super().__init__()

    def __repr__(self):
        """Return fmt str."""
        return f'Install pkg failure, ' \
               f'exit code: {self.exit_code}. \nDetail: {self.detail}'


class ExecutorStopError(Exception):
    """Executor stop error"""

    def __init__(self, pid: str, alive: List[int]):
        self.pid = pid
        self.alive = alive
        super().__init__()

    def __repr__(self):
        """Return fmt str."""
        return f'Stop pid: {self.pid} error, some pid is alive: {self.alive}'

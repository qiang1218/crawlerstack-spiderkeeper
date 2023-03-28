"""
Exceptions.
"""
from pathlib import Path
from typing import List, Optional, Union


class SpiderkeeperError(Exception):
    """SpiderkeeperError"""

    def __init__(self, detail: str):
        """
        :param detail:
        """
        self.detail = detail
        super().__init__(detail)

    def __repr__(self):
        """repr"""
        return f'{self.__class__.__name__}("detail"={self.detail})'


class ObjectDoesNotExist(SpiderkeeperError):
    """
    Object does not exist.

    http code: 404
    """

    def __init__(
            self,
            detail: Optional[str] = 'Object does not exist!',
    ):
        super().__init__(detail)


class UnprocessableEntityError(SpiderkeeperError):
    """
    Unprocessable entity error

    http code: 422
    """

    def __init__(
            self,
            detail: str | list | dict = 'Unprocessable entity error',
    ):
        super().__init__(detail)


class DeleteConstraintError(SpiderkeeperError):
    """
    406 Not Acceptable.
    """

    def __init__(
            self,
            detail: Optional[str] = 'Delete error, some children node exist.'
    ):
        super().__init__(detail)


class RequirementsFileNotFound(SpiderkeeperError):
    """Requirement file not found error"""

    def __init__(self, path: Optional[Union[str, Path]] = None):
        detail = f'Requirement file not found in {path}, ' \
                 f'your artifact should contain "Pipfile" or "requirement.txt"'
        super().__init__(detail)


class PKGInstallError(SpiderkeeperError):
    """Pkg install error"""

    def __init__(self, output: Optional[str] = None, exit_code: Optional[int] = None):
        detail = ['Install pkg failure, ']
        if exit_code:
            detail.append(f'exit code: {exit_code}.')
        if output:
            detail.append(f'\n    Detail: {output}')

        super().__init__(''.join(detail))


class ExecutorStopError(SpiderkeeperError):
    """Executor stop error"""

    def __init__(self, pid: str, alive: List[int]):
        detail = f'Stop pid: {pid} error, some pid is alive: {alive}'

        super().__init__(detail)

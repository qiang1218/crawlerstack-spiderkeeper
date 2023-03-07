"""
Exceptions.
"""
from typing import Optional


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


class CreateConnectionError(SpiderkeeperError):
    """Create connection error"""

    def __init__(
            self,
            detail: str | list | dict = 'Create connection error',
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


class JobStoppedError(SpiderkeeperError):
    """
    Job stopped error
    """

    def __init__(
            self,
            detail: Optional[str] = 'Job had stopped'
    ):
        super().__init__(detail)


class JobRunError(SpiderkeeperError):
    """
    Job run error
    """

    def __init__(
            self,
            detail: Optional[str] = 'Job repeated calls or status error'
    ):
        super().__init__(detail)


class JobPauseError(SpiderkeeperError):
    """
    Job pause error
    """

    def __init__(
            self,
            detail: Optional[str] = 'Job repeated pause or status error'
    ):
        super().__init__(detail)


class JobUnpauseError(SpiderkeeperError):
    """
    Job unpause error
    """

    def __init__(
            self,
            detail: Optional[str] = 'Job repeated unpause or status error'
    ):
        super().__init__(detail)


class TaskActionError(SpiderkeeperError):
    """
    Task action error
    """

    def __init__(
            self,
            detail: Optional[str] = 'Task action error'
    ):
        super().__init__(detail)

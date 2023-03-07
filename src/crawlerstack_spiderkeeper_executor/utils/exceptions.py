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
            detail: str | list | dict = 'Unprocessable entity error.',
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


class RequestError(SpiderkeeperError):
    """
    RequestError
    """

    def __init__(
            self,
            detail: Optional[str] = 'Get Server api info error.'
    ):
        super().__init__(detail)


class RemoteTaskGetError(SpiderkeeperError):
    """
    RemoteTaskRunError
    """

    def __init__(
            self,
            detail: Optional[str] = 'Remote task get failed.'
    ):
        super().__init__(detail)


class RemoteTaskRunError(SpiderkeeperError):
    """
    RemoteTaskRunError
    """

    def __init__(
            self,
            detail: Optional[str] = 'Remote task run failed.'
    ):
        super().__init__(detail)


class RemoteTaskCheckError(SpiderkeeperError):
    """
    RemoteTaskCheckError
    """

    def __init__(
            self,
            detail: Optional[str] = 'Remote task check failed.'
    ):
        super().__init__(detail)


class ContainerRmError(SpiderkeeperError):
    """
    ContainerRmError
    """

    def __init__(
            self,
            detail: Optional[str] = 'Container rm failed.'
    ):
        super().__init__(detail)


class ContainerStopError(SpiderkeeperError):
    """
    ContainerStopError
    """

    def __init__(
            self,
            detail: Optional[str] = 'Container stop failed.'
    ):
        super().__init__(detail)

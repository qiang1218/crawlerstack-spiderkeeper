"""project"""
from crawlerstack_spiderkeeper_server.models import Project
from crawlerstack_spiderkeeper_server.repository.project import \
    ProjectRepository
from crawlerstack_spiderkeeper_server.schemas.project import (ProjectCreate,
                                                              ProjectSchema,
                                                              ProjectUpdate)
from crawlerstack_spiderkeeper_server.services.base import EntityService


class ProjectService(EntityService[Project, ProjectCreate, ProjectUpdate, ProjectSchema]):
    """
    Project service.
    """
    REPOSITORY_CLASS = ProjectRepository

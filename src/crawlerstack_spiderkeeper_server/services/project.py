"""project"""
from crawlerstack_spiderkeeper_server.services.base import EntityService
from crawlerstack_spiderkeeper_server.models import Project
from crawlerstack_spiderkeeper_server.schemas.project import ProjectCreate, ProjectUpdate, ProjectSchema
from crawlerstack_spiderkeeper_server.repository.project import ProjectRepository


class ProjectService(EntityService[Project, ProjectCreate, ProjectUpdate, ProjectSchema]):
    """
    Project service.
    """
    REPOSITORY_CLASS = ProjectRepository

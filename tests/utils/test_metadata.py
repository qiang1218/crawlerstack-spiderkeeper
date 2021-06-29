"""Test metadata"""
from pathlib import Path

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.utils import ArtifactMetadata


def test():
    """test init ArtifactMetadata"""
    kwargs = {
        'filename': 'foo-1624505096.557897.zip',
        'project_name': 'foo',
        'timestamp': 1624505096.557897,
        'file': Path(settings.ARTIFACT_PATH, 'artifacts', 'foo-1624505096.557897.zip'),
        'source_code': Path(settings.ARTIFACT_PATH, 'workspaces', 'foo-1624505096.557897'),
        'virtualenv': Path(settings.ARTIFACT_PATH, 'virtualenvs', 'foo-1624505096.557897'),
        'image_tag': 'foo:1624505096.557897',
    }
    metadata = ArtifactMetadata(kwargs.get('filename'))
    for key, value in kwargs.items():
        assert getattr(metadata, key) == value

    assert str(metadata) == metadata.file_basename


def test_from_project(mocker):
    """test ArtifactMetadata from_project"""
    datetime_mocker = mocker.patch('crawlerstack_spiderkeeper.utils.metadata.datetime')
    datetime_mocker.now.return_value = datetime_mocker
    datetime_mocker.timestamp.return_value = 123
    metadata = ArtifactMetadata.from_project('foo')
    assert metadata.timestamp == 123

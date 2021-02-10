from enum import Enum

DEFAULT_CHARACTER = 'utf-8'

ARTIFACT_VIRTUALENV_PATHNAME = 'virtualenvs'
ARTIFACT_FILE_PATHNAME = 'artifacts'
ARTIFACT_SOURCE_CODE_PATHNAME = 'workspaces'
SPIDER_LOG_PATHNAME = 'logs'

ARTIFACT_TIME_FORMAT = '%Y%m%d%H%M%S'

# Mode
LOCAL_MODE = 'local'
DOCKER_MODE = 'docker'

LOG_TOPIC = 'topic-log'
METRIC_TOPIC = 'topic-metric'

LOG_CONSUMER_GROUP_ID = 'log'
METRIC_CONSUMER_GROUP_ID = 'metric'


class JsonRpcErrors(Enum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


class ArtifactStatus(Enum):
    building = 'building'


class StageStatus(Enum):
    running = 'running'

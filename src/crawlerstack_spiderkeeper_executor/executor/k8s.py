"""k8s"""
import logging
from typing import Any

from kubernetes import client, config

from crawlerstack_spiderkeeper_executor.executor.base import BaseExecutor
from crawlerstack_spiderkeeper_executor.schemas.base import (ExecutorSchema,
                                                             SpiderSchema,
                                                             TaskSchema)
from crawlerstack_spiderkeeper_executor.utils.exceptions import \
    SpiderkeeperError

logger = logging.Logger(__name__)


class K8SExecutor(BaseExecutor):
    """K8S executor"""
    NAME = 'k8s'

    def __init__(self, settings):
        super().__init__(settings)
        self.namespace = self.settings.NAMESPACE
        self.executor_config = self.settings.EXECUTOR_CONFIG or '~/.kube/config'
        self.api = self.init_api()

    def init_api(self):
        """Init api"""
        logger.debug('Start init k8s client')
        try:
            # 默认通过集群内部连接
            config.load_incluster_config()
        except Exception as ex:
            logger.debug('Non-cluster internal, initialization failed, exception info: %s', ex)
            # 通过集群外部连接，当使用容器化部署时，进行目录挂载
            try:
                logger.info('Try to initialize with config')
                config.load_kube_config(config_file=self.executor_config)
            except Exception as e:
                logger.debug('Config init failed, exception info: %s', e)

        try:
            api = client.CoreV1Api()
            api.list_namespace()
            logger.info('successfully inited k8s client')
        except Exception as ex:
            logger.warning('Failed to connect to k8s api, exception info: %s', ex)
            raise SpiderkeeperError(detail='K8s client Init Failed, exit') from ex
        else:
            return api

    async def get(self, *args, **kwargs):
        """
        Get pod with label in k8s
        :param args:
        :param kwargs:
        :return:
        """
        jobs = self.api.list_namespaced_pod(namespace=self.namespace, label_selector="category=spiderkeeper").items
        datas = []
        for job in jobs:
            container_id = job.metadata.name
            status = job.status.phase
            task_name = job.metadata.labels.get('task_name')
            datas.append(dict(container_id=container_id, status=status, task_name=task_name))

        return datas

    async def run(self, obj_in: TaskSchema, **_):
        """
        Run
        :param obj_in:
        :param _:
        :return:
        """
        # 1 参数拆分
        executor_params = obj_in.executor_params
        spider_params = obj_in.spider_params
        container_name = f'{self._prefix}{spider_params.TASK_NAME}'.replace('_', '-')
        # 2 执行器的参数组装
        pod = self.gen_pod(executor_params, spider_params, container_name)
        self.api.create_namespaced_pod(namespace=self.namespace, body=pod)
        return container_name

    def gen_pod(self, executor_params: ExecutorSchema, spider_params: SpiderSchema,
                container_name: str) -> client.V1Pod:
        """
        Merge executor params
        :param executor_params:
        :param spider_params:
        :param container_name:
        :return:
        """
        environment = executor_params.environment or []
        environment.extend(self._convert_env(spider_params.dict()))
        volumes = executor_params.volume
        # 针对多组volume时，基于task_name与源volume进行组装，生成多组的volume_mount进行挂载，防止多个job同时访问同一路径下的pvc导致冲突
        if volumes:
            claim_name = self.settings.PVC_CLAIM_NAME
            volume_mounts = [client.V1VolumeMount(name="my-pvc",
                                                  mount_path=volume.split(':')[1],
                                                  sub_path=f'./{spider_params.TASK_NAME}' + volume.split(':')[0],
                                                  read_only=False
                                                  ) for volume in volumes]
            volume_pvc = client.V1Volume(name="my-pvc",
                                         persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                             claim_name=claim_name))
        else:
            volume_mounts = None
            volume_pvc = None

        pod = client.V1Pod()
        pod.metadata = client.V1ObjectMeta(
            name=container_name,
            labels={"category": "spiderkeeper", 'task_name': spider_params.TASK_NAME}
        )
        pod.spec = client.V1PodSpec(
            containers=[
                client.V1Container(
                    name=container_name,
                    image=executor_params.image,
                    image_pull_policy='IfNotPresent',
                    args=executor_params.cmdline,
                    env=[client.V1EnvVar(name=item.split('=')[0], value=item.split('=')[1]) for item in environment],
                    volume_mounts=volume_mounts if volume_mounts else None,
                    # 参数传递，控制上限，下限默认
                    resources=client.V1ResourceRequirements(
                        limits={"cpu": f"{executor_params.cpu_limit}m", "memory": f"{executor_params.memory_limit}Mi"},
                        requests={"cpu": "200m", "memory": "100Mi"}
                    )
                )
            ],
            volumes=[volume_pvc] if volume_pvc else None,
            restart_policy="Never",
        )
        return pod

    @staticmethod
    def _convert_env(env: dict[str, Any]) -> list[str]:
        """
        Convert env to pass docker.
        :param env:
        :return:
        """
        envs = []
        for key, value in env.items():
            envs.append(f'{key}={value}')
        return envs

    async def stop(self, *args, **kwargs):
        """Stop pod"""
        # 无停止内容，stop 表示直接删除
        await self.delete(*args, **kwargs)

    async def delete(self, pod_name: str, **kwargs):
        """
        Delete pod
        :param pod_name:
        :param kwargs:
        :return:
        """
        # 删除job
        logger.debug('Start delete a pod: %s', pod_name)
        self.api.delete_namespaced_pod(
            name=pod_name,
            namespace=self.namespace,
            body=client.V1DeleteOptions(propagation_policy="Foreground", grace_period_seconds=5),
        )
        logger.debug('Delete a pod: %s success.', pod_name)
        return 'delete successful'

    async def status(self, pod_name: str, **_) -> str:
        """
        Status
        已知的 status:
            - Pending
            - Running
            - Succeeded
            - Failed
            - Unknown
        :param pod_name:
        :param _:
        :return:
        """

        # 查看job的状态
        pod_status = self.api.read_namespaced_pod_status(name=pod_name, namespace=self.namespace)
        logger.debug('Inspect k8s pod: %s, response: %s', pod_name, pod_status.status)
        return pod_status.status.phase

    async def log(self, pod_name: str, **_):
        """Log"""
        # 日志查看需要从pod中获取
        logs = self.api.read_namespaced_pod_log(name=pod_name, namespace='default', tail_lines=50)
        yield logs

    async def close(self, *args, **kwargs):
        """Close"""

    async def resource(self, *args, **kwargs) -> dict:
        """Resource"""
        return {'cpu': 1000 * 48, 'memory': 1024 * 8}

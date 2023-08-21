# 执行器

执行器作为采集任务真正被调度的位置，用来管理任务的调度和销毁工作。

## 支持类型

- docker
- k8s

### docker执行器

要启动docker执行器，仅需要修改配置文件：

```yml
EXECUTOR_TYPE: docker
EXECUTOR_REMOTE_URL: 'unix://var/run/docker.sock'
EXECUTOR_NAME: 'docker-local'
EXECUTOR_SELECTOR: 'local'
DOCKER_NETWORK: app
```

参数说明：

- EXECUTOR_TYPE：执行器类型，目前支持2种，docker\k8s
- EXECUTOR_REMOTE_URL: 执行器远程地址，可为docker套接字或tcp链接（docker特有参数）
- EXECUTOR_NAME：执行器名称，又来区分不同执行器，需唯一
- EXECUTOR_SELECTOR：执行器选择器参数，结合作业任务，可指定同标签执行器作为作业触发位置
- DOCKER_NETWORK：docker网络，将调度任务统一置于相同网络中（docker特有参数）

### k8s执行器

要启动k8s执行器，仅需要修改配置文件:

```shell
EXECUTOR_TYPE: k8s
EXECUTOR_NAME: 'k8s-local'
EXECUTOR_SELECTOR: 'local'
EXECUTOR_CONFIG: '~/.kube/config'
NAMESPACE: default
PVC_CLAIM_NAME: spiderkeeper-executor-pod-pvc
```

参数说明：

- EXECUTOR_TYPE：执行器类型，目前支持2种，docker\k8s
- EXECUTOR_NAME：执行器名称，又来区分不同执行器，需唯一
- EXECUTOR_SELECTOR：执行器选择器参数，结合作业任务，可指定同标签执行器作为作业触发位置
- EXECUTOR_CONFIG：k8s的token文件位置，如果在集群中执行，可为空（k8s特有参数）
- NAMESPACE：作业的命名空间（k8s特有参数）
- PVC_CLAIM_NAME：pvc名称，作业中的挂载内容，需提前创建（k8s特有参数）

# docker-compose

## 要求

- 主机资源 2 CPU 核心 和 2 GB 内存
- docker
- docker-compose

## 下载

部署文件分为主服务和外部关联服务，
详见[docker-compose部署文件](https://github.com/crawlerstack/crawlerstack-spiderkeeper/tree/main/docker-compose)。

通过`git clone` 命令获取代码：

```shell
git clone https://github.com/crawlerstack/crawlerstack-spiderkeeper.git
```

或者下载：

```shell
https://github.com/crawlerstack/crawlerstack-spiderkeeper/archive/refs/heads/main.zip
```

其中： `docker-compose/main_server` 目录为 采集平台的部署脚本和配置， `docker-compose/other_server` 目录为 外部依赖的部署脚本。

## 安装前

安装服务前，需要进行网络的创建。外部服务配置默认运行在名为 `app` 的网络名称下，运行以下命令：

```shell
docker network create app
```

## 外部依赖安装

- 数据库 支持mysql,如果选用其他的存储，检查依赖安装
- 消息队列 例如：rabbitmq

项目中默认提供mysql和rabbitmq两个服务的部署脚本，如果用户环境中已经包含，则无需安装。

切换到`other_server`中，运行以下命令完成`mysql`和`rabbitmq`的启动：

```shell
docker pull
docker-compose up -d
```

## 采集平台服务安装

### 镜像拉取

采集平台服务分为：前端和后端服务，包含2个镜像，执行以下命令完成镜像拉取操作：

```shell
docker pull quay.io/crawlerstack/spiderkeeper:v4.0.1
docker tag quay.io/crawlerstack/spiderkeeper:v4.0.1 spiderkeeper:v4.0.1

docker pull quay.io/crawlerstack/spiderkeeper-web:v4.0.1
docker tag quay.io/crawlerstack/spiderkeeper-web:v4.0.1 spiderkeeper-web:v4.0.1
```

亦可使用源码构建镜像，根目录下执行 `docker build -t spiderkeeper:v4.0.1 .`命令构建后端镜像。  
切换到 `frontend` 下执行 `docker build -t spiderkeeper-web:v4.0.1 .` 命令构建前端镜像。

### 配置修改

根据具体环境，修改以下文件中配置参数(其中： `<>` 中的内容需要替换)：

- settings_server.yml

```yaml
MQ: amqp://<user>:<password>@<host>:<port>/
DATABASE: mysql+aiomysql://<user>:<password>@<host>:<port>/spiderkeeper_server?charset=UTF8MB4
```

- settings_scheduler.yml

```yaml
DATABASE: mysql+aiomysql://<user>:<password>@<host>:<port>/spiderkeeper_scheduler?charset=UTF8MB4
SCHEDULER_JOB_STORE_DEFAULT: mysql://<user>:<password>@<host>:<port>/spiderkeeper_scheduler
```

- settings_forwarder.yml

```yaml
MQ: amqp://<user>:<password>@<host>:<port>/
```

- settings_executor.yml

```yaml
EXECUTOR_REMOTE_URL: 'tcp://<host>:<port>'
```

说明：EXECUTOR_REMOTE_URL的连接为docker远程连接，需要在docker中开启。

### 初始化数据库

默认数据库为mysql，初始化库，连接mysql命令行，运行以下命令(如自定义时，修改数据库名称，上述配置一同修改)：

```shell
create database if not exist spiderkeeper_scheduler;
create database if not exist spiderkeeper_server;
```

### 启动服务

运行以下命令完成服务启动：

```shell
docker-compose up -d
```

如需要修改，运行以下命令：

```shell
docker-compose down
```

## 查看

待各服务启动成功后，打开浏览器，输入[http://localhost:5000](http://localhost:5000) 查看web页面


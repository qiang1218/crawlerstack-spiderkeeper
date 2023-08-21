# kubernetes

## 要求

- helm 参考[helm安装指南](https://helm.sh/zh/docs/intro/install/)
- kubernetes
- 消息队列服务 例如：rabbitmq
- 数据库服务 例如：mysql

## 下载

详见[helm_chart部署文件](https://github.com/crawlerstack/crawlerstack-spiderkeeper/tree/main/helm_chart)。

通过`git clone` 命令获取代码：

```shell
git clone https://github.com/crawlerstack/crawlerstack-spiderkeeper.git
```

或者下载：

```shell
https://github.com/crawlerstack/crawlerstack-spiderkeeper/archive/refs/heads/main.zip
```

其中 `helm_chart/spiderkeeper` 目录下内容为本地chart包。

## 安装前

采集平台服务依赖外部服务： 消息队列（如：rabbitmq）、数据库（如：mysql），需根据系统环境自行安装。

## 采集平台安装

根据具体环境，修改以下文件中配置参数(其中： `<>` 中的内容需要替换，未写出的配置不做更改)：

### 配置修改

- values.yml

```yaml

# web
web:
  repository: quay.io/crawlerstack/spiderkeeper-web

# server
server:
  repository: quay.io/crawlerstack/spiderkeeper
  configMap:
    configOverrides:
      - name: settings.yml
        data: |
          MQ: amqp://<user>:<password>@<host>:<port>/
          DATABASE: mysql+aiomysql://<user>:<password>@<host>:<port>/spiderkeeper_server?charset=UTF8MB4

# scheduler
scheduler:
  repository: quay.io/crawlerstack/spiderkeeper
  configMap:
    configOverrides:
      - name: settings.yml
        data: |
          DATABASE: mysql+aiomysql://<user>:<password>@<host>:<port>/spiderkeeper_scheduler?charset=UTF8MB4
          SCHEDULER_JOB_STORE_DEFAULT: mysql://<user>:<password>@<host>:<port>/spiderkeeper_scheduler

# forwarder
forwarder:
  repository: quay.io/crawlerstack/spiderkeeper
  configMap:
    configOverrides:
      - name: settings.yml
        data: |
          MQ: amqp://<user>:<password>@<host>:<port>/
# executor
executor:
  repository: quay.io/crawlerstack/spiderkeeper
```

### 初始化数据库

根据上述配置中的数据库设置参数，进行对应库的创建。

### 启动服务

运行以下命令完成服务启动：

```shell
helm install -f values.yaml --create-namespace --namespace spiderkeeper spiderkeeper .
```

说明： values.yaml文件配置应与启动命令一致，例如 `helm install <name>` 指定名称时，
需同步修改`configMap`中配置参数，例如：`SCHEDULER_URL: http://<name>-scheduler:8081/api/v1`。

如需要卸载，运行以下命令：

```shell
helm uninstall --namespace spiderkeeper spiderkeeper
```

## 查看

待各服务启动成功后，打开浏览器，输入[www.spiderkeeper.com](http://www.spiderkeeper.com) 查看web页面。

说明：如果访问不通，请检查 `dns` 。

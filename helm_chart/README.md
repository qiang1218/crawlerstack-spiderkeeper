# 部署流程

## 准备

- helm  参考[helm安装指南](https://helm.sh/zh/docs/intro/install/)
- kubernetes
- 消息队列服务 例如：rabbitmq
- 数据库服务 例如：mysql

## 配置修改

根据需要修改`values.yaml`文件中中各服务的configmap，其中url、mq、database连接按需修改

## 部署

使用 `spiderkeeper\README.md`中的命令进行安装或者卸载

## 注意

- values.yaml文件配置应与启动命令一致，例如 `helm install <name>` 指定名称时，需同步修改配置参数，
`SCHEDULER_URL: http://<name>-scheduler:8081/api/v1`
- 外部消息队列和数据库服务安装完成后，需同步修改配置文件

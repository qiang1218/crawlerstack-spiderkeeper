# 项目部署流程

## 项目打包
项目总共分为4个服务, 分为核心服务、调度服务、转发服务、执行器服务，采用统一的Dockerfile进行镜像构建。  
拉取代码，执行 `docker build -t crawlerstack-spiderkeeper:latest .`，完成镜像构建

## 数据迁移
需要数据迁移的包含：核心服务和调度服务，进入对应的目录，修改配置文件或环境变量提供如下参数：  
`DATABASE: mysql+aiomysql://root:1qazZAQ!@192.168.6.15:3306/spiderkeeper_server?charset=UTF8MB4`  
执行 `alembic upgrade head` 完成数据的迁移工作。

## 配置管理
正式环境下，查看对应的 `_external_files`参数，在对应目录下进行settings.yml设置，将默认配置进行替换，完成配置设置。

## 任务调度
考虑任务的相互依赖，任务启动顺序为：  
核心服务 ->  调度服务  -> 执行器服务 ->  转发器服务 

## 注意事项
1. 项目中的任务交互采用api的形式，故要进行配置文件中响应的链接进行设置，防止调度过程中的异常。

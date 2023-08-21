# 部署流程

## 前端要点

- 镜像构建  
  前端文件位于 frontend 目录下，执行 `docker build -t spiderkeeper-web:v4.0.1 .` 命令进行构建

## 后端要点

- 镜像构建
  后端文件位于根据路下，执行`docker build -t spiderkeeper:v4.0.1 .`命令进行构建
- 服务启动顺序
  后端分为4个服务，按照 `scheduler` -> `executor` -> `server` 的顺序启动， `forwarder`不区分顺序，

## 其他

- 配置文件  
  使用 `docker-compose` 文件中的 `volumns` 进行配置的设置，亦可以使用环境变量的形式传递（遵循 `dynaconf` 设置）
- 外部依赖
    - 数据库 支持mysql,如果选用其他的存储，检查依赖安装
    - 消息队列 MQ: memory://localhost 需要修改对应的外部存储
    - 执行器 执行器分为：docker执行器和k8s执行器，需要自定义配置文件

## 部署

1. 创建网络，执行命令`docker network create app`，如果已经存在，可忽略
2. 启动关联依赖 `other_server` ，执行命令 `docker-compose up -d`，如果已经存在相关服务，可忽略
3. 数据库创建，连接mysql client,执行 `create database spiderkeeper_scheduler;create database spiderkeeper_server;`
4. 部署前后端 `mian_server` ，根据相关要点，修改对应配置文件，完成服务启动 `docker-compose up -d`
5. 打开浏览器，输入`http://localhost:5000` 查看web页面

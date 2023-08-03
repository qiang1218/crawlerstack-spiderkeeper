# 核心服务

## 业务模块

业务模块主要完成任务的crud操作，通过web页面和api交互，完成任务的管理和执行器查看功能。

## 收集器模块

收集器作为采集项目的最后一个环节，承担着最终数据的存储、统计和可视化。

目前，收集器模块提供日志、指标、数据的收集功能：

- 日志、指标
    - 实现 `otel` 规范，接入到第三方的监控可视化工具
- 数据
    - 实现 `mysql` 、 `mongo` 、 `s3` 的存储和 `pulsar` 消息的转发
    - 数据条数统计

其中，在存储选取方面，推荐使用数据的pulsar发送功能，运用三方抽取工具，可灵活的进行数据的持久化操作。
配置存储时，请遵循以下格式：

- mysql
    - `mysql://root:root@localhost:3306/spiderkeeper_server?charset=utf8`

- mongodb
    - `mongodb://user:password@example.com/default_db?authSource=admin`
- s3
    - `s3://access_key:secret_key@example.com:port/bucket`
- pulsar
    - `pulsar://localhost:6650?token=aaa.bbb.ccc&topic_prefix=clusterId/namespace`
    - 其中 clusterId/namespace/Topic 为创建topic所需要的内容,除topic外,其余指定

# 采集平台sdk

采集平台sdk完成日志、指标、数据的校验、收集和转发功能。其中监控为自动发送，其余信息均通过api触发。

## 设计

采集平台sdk针对日志、指标和数据，采用不同的方式进行收集，分别如下：

- 日志
    - 日志内容，调用日志方法即可
- 指标
    - 采用 `prometheus_client`的形式
    - 定义好要上报的指标，由后台任务持续获取
    - 指标按照指定格式筛选，仅上报符合要求的内容
    - 指标设置格式，通常为 `Counter`, sdk在转发前会计算差值，增量更新
- 数据
    - 数据内容分为数据和快照两部分
    - 数据收集后，仅校验通过数据进行后续操作

收集到的结果，分别采用对应的异步请求来完成数据上传。

## 采集数据流格式

### 指标

- 格式

```json
{
  "spiderkeeper_downloader_request_count": 5,
  "spiderkeeper_downloader_request_bytes": 342,
  "spiderkeeper_downloader_request_method_count_GET": 0,
  "spiderkeeper_downloader_response_count": 0,
  "spiderkeeper_downloader_response_status_count_200": 5,
  "spiderkeeper_downloader_response_status_count_302": 0,
  "spiderkeeper_downloader_response_bytes": 1024,
  "spiderkeeper_downloader_exception_count": 0
}
```

- 说明  
  使用`prometheus`客户端进行定义数据，提供api`/metrics`接口对外提供
  前缀 spiderkeeper_，第二层使用 downloader、parser之类，作为过滤type的参数

### 日志

- 格式

```json
[
  "line1",
  "line2",
  "line3"
]
```

- 说明  
  日志以行的形式提供，保存到server中的目录中，通过接口`/logs`提供到web页面

### 数据

- 格式

```json
{
  "title": "user",
  "fields": [
    "name",
    "age",
    "gender"
  ],
  "datas": [
    [
      "zhangSan",
      10,
      0
    ],
    [
      "liHua",
      25,
      1
    ]
  ]
}
```

- 说明  
  数据以结构化为主，`fields` 与 `data` 形成映射关系，通过对应数据实现进行存储

### 快照

- 格式

```json
{
  "title": "snapshot",
  "fields": [
    "file_name",
    "content"
  ],
  "datas": [
    [
      "test1.html",
      "test1"
    ],
    [
      "test2.html",
      "test2"
    ]
  ]
}
```

- 说明  
  快照以结构化为主，`fields` 与 `data` 形成映射关系，`file_name`为文件名，`content`
  为对应的内容，通过对应快照实现进行存储。（现有功能满足html等数据，文件流不在范围）

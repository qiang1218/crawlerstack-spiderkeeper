# 最佳实践

## 数据目录标准

### S3文件目录

- 桶
    - 格式
        - spiderkeeper
    - 说明
        - spiderkeeper指代数据由平台存入
- 文件
    - 格式
        - /data/项目分类/项目名/文件名[日期].json
        - /snapshot/项目分类/项目名/自定义分区/文件名[.后缀]
    - 说明
        - /data 为数据存储，例如：/data/项目分类/项目名/user20230309.json
        - /snapshot 为快照存储，例如： /snapshot/项目分类/项目名/shenzhen/company/1200.html

### 数据库目录

- 数据库|集合
    - 格式
        - spiderkeeper_data
        - spiderkeeper_snapshot
    - 说明
        - 数据采用_data后缀
        - 快照采用_snapshot后缀
        - spiderkeeper表示数据由平台入库
- 数据表|文档
    - 格式
        - 项目分类_项目名_表名
    - 说明
        - 例如： 工商数据_顺企网_公司详情

## 数据格式标准

### 字段

- 必须字段
    - mysql
        - id 自增
        - create_time 自动生成 | 传递
    - mongo
        - _id 自动生成 object_id
        - create_time 传递
    - s3文件
        - create_time 传递
- 可选字段
    - task_name 任务名称 环境传递 可作为批次号
    - batch_id 批次id uuid自行生成
- 其他字段
    - 同一类型的采集项目，字段需统一
    - 同一类型的采集项目，因历史问题，需设置字段映射表

### 格式

- 小写字母 + 下划线

### 命名

- 见名知意
- 同类型数据存储时，命名统一
- 同类型数据存储时，提供历史数据与新映射字段规则关系表
- 考虑部分数据库不区分大小写，故采用小写字母+下划线的格式


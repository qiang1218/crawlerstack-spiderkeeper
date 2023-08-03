# crawlerstack-spiderkeeper-web

## 使用 docker 部署

在 [docker-compose.yml](../../docker-compose/docker-compose-web.yml) 的 `environment` 参数中通过环境变量配置后端服务地址

构建容器, 启动容器

```bash
docker compose build
docker compose up
```

## 本地 mock 数据

```bash
npm run mocks
```

## prettier 格式化代码

```bash
yarn prettier --write .
```

## eslint 代码检测

```bash
yarn eslint src
```

## jest 测试

```bash
yarn test
```

FROM python:3.10 AS build

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/

WORKDIR /app

RUN python -m pip install -U pip  \
    && pip install --no-cache-dir -U poetry

COPY . ./

RUN poetry build

FROM python:3.10

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/

WORKDIR /app

COPY --from=0 /app/dist /tmp

RUN python -m pip install -U pip \
    && pip install --no-cache-dir /tmp/*.whl

EXPOSE 8080 8081 8082 8083

CMD ["crawlerstack_spiderkeeper_server", "api"]
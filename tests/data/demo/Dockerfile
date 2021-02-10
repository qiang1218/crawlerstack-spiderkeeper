FROM python:3.7

ENV PIP_INDEX_URL="https://mirrors.aliyun.com/pypi/simple/"

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

CMD ["scrapy", "crawl"]
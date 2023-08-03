FROM node:19

WORKDIR /app

COPY *.json  ./
COPY yarn.lock ./

RUN yarn install

COPY . ./

RUN yarn build

FROM caddy:2.6

EXPOSE 80

COPY --from=0 /app/build /usr/share/caddy
COPY Caddyfile /etc/caddy/

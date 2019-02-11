FROM busybox:1.30.0 as base

RUN wget -O /tmp/dockerize-alpine-linux-amd64-v0.5.0.tar.gz https://github.com/jwilder/dockerize/releases/download/v0.5.0/dockerize-alpine-linux-amd64-v0.5.0.tar.gz
RUN tar xvfz /tmp/dockerize-alpine-linux-amd64-v0.5.0.tar.gz -C /tmp/

FROM alpine as ssl-container

RUN apk update \
  && apk add --no-cache openssl \
  && rm -rf /var/cache/apk/* \
  && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /tmp/server.key -out /tmp/server.crt  -subj "/C=PT/ST=Lisboa/L=Lisboa/O=Dev/CN=dev.elri-nrs.eu"

FROM nginx:1.15.5

ENV ELRI_HOSTNAME="dev" \
    ELRI_DOMAINNAME="elri-nrs.eu" \
    ELRI_NODES=test-node1:8000 \
    ELRI_CERT="server.crt" \
    ELRI_KEY="server.key"

COPY --from=base /tmp/dockerize /usr/local/bin/
COPY --from=ssl-container /tmp/server.crt /etc/ssl/certs/server.crt
COPY --from=ssl-container /tmp/server.key /etc/ssl/private/server.key
COPY resources/env_secrets_expand.sh /
COPY resources/startup.sh /
COPY resources/vhost.tmpl /tmp/

RUN chmod +x /startup.sh /env_secrets_expand.sh \
    && echo "daemon off;" >> /etc/nginx/nginx.conf \
    && mkdir -p /www/data/static \
    && chown 8283:8283 /www/data/static

VOLUME [ "/www/data/static" ]

EXPOSE 80 443

CMD [ "/startup.sh" ]

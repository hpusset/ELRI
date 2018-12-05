FROM busybox:1.29.3 as base

RUN wget -O /tmp/dockerize-alpine-linux-amd64-v0.5.0.tar.gz https://github.com/jwilder/dockerize/releases/download/v0.5.0/dockerize-alpine-linux-amd64-v0.5.0.tar.gz
RUN tar xvfz /tmp/dockerize-alpine-linux-amd64-v0.5.0.tar.gz -C /tmp/

FROM nginx:1.15.5

ENV ELRI_HOSTNAME="nrs" \
    ELRI_DOMAINNAME="dev.elri.com" \
    ELRI_NODES=test-node1:8000

COPY --from=base /tmp/dockerize /usr/local/bin/
COPY resources/env_secrets_expand.sh /
COPY resources/startup.sh /startup.sh
COPY resources/vhost.tmpl /etc/nginx/conf.d/

RUN chmod +x /startup.sh /env_secrets_expand.sh \
    && echo "daemon off;" >> /etc/nginx/nginx.conf

CMD [ "/startup.sh" ]
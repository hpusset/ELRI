FROM debian:stretch as base

ARG RELEASE="trunk"
#ARG RELEASE="branches/R2"

ENV GIT_URL="https://github.com/ELDAELRA/ELRI/${RELEASE}/solr"

RUN apt-get update \
    && apt-get install -y subversion \
    && svn --trust-server-cert export ${GIT_URL} /tmp/solr

FROM openjdk:8u181-jre-slim-stretch

COPY --from=base /tmp/solr /solr

RUN useradd solr \
    && usermod --shell /bin/false --uid 7273 --expiredate 1 --lock solr \
    && groupmod --gid 7273 solr \
    && chown -R solr:solr /solr

USER solr
WORKDIR /solr
EXPOSE 8983

ENTRYPOINT [ "java", "-jar", "-Djetty.port=8983", "start.jar"]
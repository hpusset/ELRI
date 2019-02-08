FROM busybox:1.29.3 as base

RUN wget -O /tmp/dockerize-alpine-linux-amd64-v0.5.0.tar.gz https://github.com/jwilder/dockerize/releases/download/v0.5.0/dockerize-alpine-linux-amd64-v0.5.0.tar.gz
RUN tar xvfz /tmp/dockerize-alpine-linux-amd64-v0.5.0.tar.gz -C /tmp/

FROM python:2.7.15-stretch

#ARG RELEASE="trunk"
ARG RELEASE="tags/R2"
#ARG RELEASE="branches/VIC"
ENV DB_HOST="postgres-server" \
    DB_PORT="5432" \
    SOLR_HOST="solr" \
    SOLR_PORT="8983" \
    DBELRI_USER="elri" \
    DBELRI_PASS="elri_pass" \
    DBELRI_NAME="elri_metashare" \
    ELRI_TIMEZONE="Europe/Lisbon" \
    ELRI_LANGUAGE="pt-pt" \
    ELRI_SUP_LANGUAGES='[("English", "English"), ("French", "French"), ("German", "German"), ("Italian", "Italian"), ("Irish", "Irish"), ("Spanish; Castilian", "Spanish"), ("Portuguese", "Portuguese")]' \
    ELRI_COUNTRY="Portugal" \
    ELRI_SALT="e07fc77c1ecd3" \
    ELRI_ALERT_MAILS="noreply@elri.com" \
    GIT_URL="https://github.com/ELDAELRA/ELRI/${RELEASE}"

COPY --from=base /tmp/dockerize /usr/local/bin/
COPY resources/env_secrets_expand.sh \
     resources/startup.sh \
     resources/create_super_user.sh \
     resources/gettext.patch \ 
     resources/manage.py /elri/

RUN svn export ${GIT_URL}/metashare /elri/metashare \
    && svn export ${GIT_URL}/project_management /elri/project_management \
    && svn export ${GIT_URL}/elri_resources /elri/elri_resources \
    && svn export ${GIT_URL}/requirements.txt /elri/requirements.txt \
    && mkdir -p /elri/metashare/unprocessed \
             /elri/metashare/processed \
    && patch /usr/local/lib/python2.7/gettext.py < /elri/gettext.patch \
    && pip install -r /elri/requirements.txt \
    && chmod +x /elri/startup.sh \
                /elri/env_secrets_expand.sh \
                /elri/create_super_user.sh
# Workaround to allow elri_resources persistence without overriding shared volume with toolchains image
RUN svn export ${GIT_URL}/elri_resources/config/web_service.cfg /elri/web_service.cfg

COPY resources/local_settings.py \
     resources/maintainers.dat \
     resources/wsgi.py /elri/metashare/

#COPY /elri/elri_resources/config/web_service.cfg /elri/

EXPOSE 8000

WORKDIR /elri

RUN useradd django \
    && usermod --shell /bin/false --uid 8283 --expiredate 1 --lock django \
    && groupmod --gid 8283 django \
    && chown -R django:django /elri \
    && chmod -R 774 /elri/elri_resources

VOLUME [ "/certificates", "/elri/elri_resources" ]

USER django

ENTRYPOINT [ "/elri/startup.sh" ]

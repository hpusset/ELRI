FROM postgres:11.0

ENV POSTGRES_USER="pgres_user" \
    POSTGRES_PASSWORD="pgres_pass" \
    DBELRI_USER="elri" \
    DBELRI_PASS="elri" \
    DBELRI_NAME="elri_metashare"

COPY resources/env_secrets_expand.sh /env_secrets_expand.sh
COPY resources/startup.sh /startup.sh
COPY resources/base.sh /docker-entrypoint-initdb.d/
COPY resources/postgresql.conf resources/pg_hba.conf /usr/share/postgresql/11/

RUN usermod --shell /bin/false --uid 6263 --lock --expiredate 1 postgres \
    && groupmod --gid 6263 postgres \
    && chmod +x /startup.sh /env_secrets_expand.sh

VOLUME [ "/var/lib/postgresql/data" ]

ENTRYPOINT [ "/startup.sh" ]
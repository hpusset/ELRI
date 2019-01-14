#!/bin/bash
set -e

# Create a user and assign to it a password. The one you will add to the local_settings.py file.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE $DBELRI_USER;
    ALTER USER $DBELRI_USER WITH ENCRYPTED PASSWORD '$DBELRI_PASS';
EOSQL

# Create a database to this user
createdb -U $POSTGRES_USER $DBELRI_USER
# And allow this user to login to the psql service:
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    GRANT ALL PRIVILEGES ON DATABASE $DBELRI_USER TO $DBELRI_USER;
    ALTER ROLE "$DBELRI_USER" WITH LOGIN;
EOSQL

# Create a database. The one you will add to the local_settings.py file. 
createdb -U $POSTGRES_USER $DBELRI_NAME
# And grant permissions to the user you created before.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    GRANT ALL PRIVILEGES ON DATABASE $DBELRI_NAME to $DBELRI_USER ;
EOSQL
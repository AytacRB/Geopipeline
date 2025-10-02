#!/bin/bash

# Nominatim DB storage
DB_DIR=~/NII/geocoding/nominatim_db
mkdir -p "$DB_DIR"

# Location of Nominatim pbf
PBF_FILE=/mnt/d/nominatim/planet-admin.osm.pbf

# Check if database already exists
if [ -z "$(ls -A "$DB_DIR" 2>/dev/null)" ]; then
    echo "No existing Nominatim DB found. Running fresh import."

    docker run -it \
      --name nominatim \
      -p 8080:8080 \
      -e PBF_PATH=/nominatim/data.osm.pbf \
      -e NOMINATIM_IMPORT_STYLE=admin \
      -e NOMINATIM_NO_UPDATE=1 \
      --shm-size=12g \
      -v "$DB_DIR":/var/lib/postgresql/16/main \
      -v "$PBF_FILE":/nominatim/data.osm.pbf \
      mediagis/nominatim:5.1
else
    echo "Existing Nominatim DB found. Starting container..."

    docker run -it \
      --name nominatim \
      -p 8080:8080 \
      --shm-size=12g \
      -v "$DB_DIR":/var/lib/postgresql/16/main \
      mediagis/nominatim:5.1 \
      bash -c "nominatim setup --indexing-only --threads 8 && service postgresql start && apache2ctl -D FOREGROUND"
fi

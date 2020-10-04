#!/bin/bash

docker-compose up -d --build
echo "Waiting for containers to finalize..."
docker exec -u postgres df_database bash -c "sleep 90 && bash /data/restore.sh"
echo "Database restored."
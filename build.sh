#!/bin/bash

docker-compose up -d --build
echo " use docker exec -u postgres df_database bash -c \"bash /data/restore.sh\" to restore database dump"
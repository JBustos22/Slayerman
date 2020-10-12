#!/bin/bash

docker-compose up -d --build
echo " use docker exec -u postgres df_database bash -c \"sleep 90 && bash /data/restore.sh\ restore database dump"
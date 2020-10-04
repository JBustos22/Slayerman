#!/bin/bash

pg_restore -U postgres -h 0.0.0.0 -d Defrag -1 /data/df.db
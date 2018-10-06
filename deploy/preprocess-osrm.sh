#!/usr/bin/env bash
cp ../osm-files/moscow.osm.pbf ../osrm
docker-compose -f ../docker-compose.yml run osrm osrm-extract -p /opt/car.lua /data/moscow.osm.pbf
docker-compose -f ../docker-compose.yml run osrm osrm-partition /data/moscow.osrm
docker-compose -f ../docker-compose.yml run osrm osrm-customize /data/moscow.osrm
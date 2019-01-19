#!/usr/bin/env bash
set -e
python processor.py --fr mos_data/markets.json --to mos-markets.json --provider mos --cat market
python processor.py --fr mos_data/parks.json --to mos-parks.json --provider mos --cat park --upsert_brands
python processor.py --fr parsed_data/small_raw.json --to google-small.json --provider google --upsert_brands
python processor.py --fr osm-files/moscow-nodes.osm --to osm-all.json --provider osm  --upsert_brands

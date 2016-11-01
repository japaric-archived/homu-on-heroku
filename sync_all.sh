#!/bin/bash
set -euo pipefail
IFS=$'\n\t'
set -vx

curl -X "POST" "$APP_URL/admin" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d "{\"secret\":\"$HOMU_WEB_SECRET\",\"cmd\":\"sync_all\"}"

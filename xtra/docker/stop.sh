#!/bin/bash

echo "Stop ADUN Web GUI"
docker rm -f -v adun_webgui
echo ""

echo "Stop ADUN Engine"
docker rm -f -v adun_engine
echo ""

echo "Stop ADUN Database"
docker rm -f -v adun_db
echo ""
echo "Completed"
echo ""

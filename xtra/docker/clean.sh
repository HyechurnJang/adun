#!/bin/bash

docker rm -f -v adun_webgui
docker rm -f -v adun_engine
docker rm -f -v adun_db

docker rmi adun/webgui
docker rmi adun/engine
docker rmi adun/db

#!/bin/bash

sudo apt update
sudo apt install docker.io -y
sudo systemctl enable docker
sudo systemctl restart docker

echo "Build Database"
sudo docker build -t adun/db:latest -f ./resource/database.docker .
echo ""

echo "Build Engine"
sudo docker build -t adun/engine:latest -f ./resource/engine.docker .
echo ""

echo "Build WebGUI"
sudo docker build -t adun/webgui:latest -f ./resource/webgui.docker .
echo ""

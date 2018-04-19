#!/bin/bash

echo "Build Database"
sudo docker build -t adun/database:latest -f ./resource/database.docker .

echo "Build Engine"
sudo docker build -t adun/engine:latest -f ./resource/engine.docker .

echo "Build WebGUI"
sudo docker build -t adun/webgui:latest -f ./resource/webgui.docker .


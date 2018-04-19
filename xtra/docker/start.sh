#!/bin/bash

echo "Start ADUN Database"
sudo docker run --name adun_db -d adun/db
echo "Wait Database 10 Seconds"
echo ""
sleep 10

echo "Start ADUN Engine"
sudo docker run --name adun_engine --link adun_db:adun_db -e APIC_IP=10.72.86.21 -e APIC_USERNAME=admin -e APIC_PASSWORD=1234Qwer -e QUARANTINE_VLAN=114 -d adun/engine
echo ""

echo "Start ADUN Web GUI"
sudo docker run --name adun_webgui -p 80:80 --link adun_engine:adun_engine -d adun/webgui
echo ""

echo "OK Let's Start ADUN !!!"
echo ""

echo "### Engine Logs ###"
echo ""
sudo docker logs -f adun_engine


#!/bin/sh

echo "Cleaning..."
docker stop cnt_ups
docker rm cnt_ups

echo "Building..."
docker build -t img_ups .

echo "Running"
docker run -d --restart unless-stopped \
           --device=/dev/ttyACM0 \  # Substitua pelo caminho da sua porta serial
           --name cnt_ups img_ups

ip r
echo "Service started"

docker logs cnt_ups -f

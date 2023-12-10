#! /bin/sh

echo "Cleaning..."
docker stop cnt_ups
docker rm cnt_ups

echo "Building..."
docker build -t img_ups .

echo "Running"
docker run -d --restart unless-stopped \
           -p 5000:5000 \
           --name cnt_ups img_ups

ip r
echo "service started on 5000"

docker logs cnt_ups -f

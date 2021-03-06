#!/bin/sh

sshpass -p "pwd" ssh -o StrictHostKeyChecking=no pi@domain -p 2000 << EOF
	cd RSFM
	./script_init.sh &
EOF
python3 /home/pi/Python/subscriber.py &

python3 /home/pi/Python/publisher.py &

ffmpeg -f v4l2 -i /dev/video0 -c:v libx264 -preset ultrafast -tune zerolatency -b:v 600k -f rtsp -rtsp_transport tcp rtsp://domain/video &



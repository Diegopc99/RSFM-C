import paho.mqtt.client as mqtt
import subprocess
import os
import signal

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker. Status code: ", str(rc))
    client.subscribe("warnings/#")

def on_message(client, userdata, msg):
    payload_string = str(msg.payload.decode('UTF-8'))
    print("Message received: " + msg.topic + " " + payload_string)

    if msg.topic == 'warnings/turn_off_engine' and payload_string == 'true':
        client.publish('warnings/pop_up_engine','true',qos=2,retain=False)
        
    if msg.topic == "warnings/stream_delay" and payload_string == "true":
        print("RETRASO EN EL STREAM")
        # Reiniciar camara o bajar resolucion o tasa de frames (?)
        for line in os.popen("ps ax | grep ffmpeg | grep -v grep"):
            fields = line.split()
            # extracting Process ID from the output
            pid = fields[0]
            # terminating process
            os.kill(int(pid), signal.SIGKILL)

        os.popen("ffmpeg -f v4l2 -i /dev/video0 -c:v libx264 -preset ultrafast -tune zerolatency -b:v 600k -f rtsp -rtsp_transport tcp rtsp://diego1432.duckdns.org:7000/video")

        #p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        #out, err = p.communicate()
        #for line in out.splitlines():
        #        if 'ffmpeg' in line:
        #                pid = int(line.split(None, 1)[0])
        #                os.kill(pid, signal.SIGKILL)
        #subprocess.Popen(args=["ffmpeg","-f","v4l2","-i","/dev/video0","-c:v","libx264","-preset","ultrafast","-tune","zerolatency","-b:v","600k","-f","rtsp","-rtsp_transport","tcp","rtsp://diego1432.duckdns.org:7000/video"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, encoding='utf8')
	

            
    if msg.topic == "warnings/data_delay" and payload_string == "true":
        print("RETRASO EN EL ENVIO DE DATOS")
        # Apagar camara
        #shell_response = subprocess.run(["pkill","ffmpeg"],shell=True,check=True,text=True)
        for line in os.popen("ps ax | grep ffmpeg | grep -v grep"):
            fields = line.split()
            # extracting Process ID from the output
            pid = fields[0]
            # terminating process
            os.kill(int(pid), signal.SIGKILL)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("diego1432.duckdns.org", 9000, 60)
print("Starting connection")
#battery = psutil.sensors_battery()
#percent = str(battery.percent)
#print(percent)
#print(battery.power_plugged)
client.loop_forever()

# mosquitto_pub -d -h localhost -p 1883 -t "warnings/stream_delay" -m "true"

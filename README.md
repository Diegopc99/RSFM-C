# BOAT SOFTWARE

BitBucket repo that stores the needed scripts to run a telemetry software in a hydrofoil boat. Data is sent throught MQTT, thus a broker is needed to be deployed

# INSTALLATION
1. Copy in /home/pi the folder named **Python** 
2. Follow the instructions of **crontab_config.txt**
3. Set up a MQTT broker and change the global variables of the python scripts to the ip destination or dns name of the broker.
4. Deploy the Node-RED flow from the file **node-red-flow.txt**

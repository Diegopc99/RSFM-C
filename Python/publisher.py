import serial,time
import paho.mqtt.publish as publish
import json
import paho.mqtt.client as mqtt

from datetime import datetime

destino = "ip"
puerto = 9000

client = mqtt.Client("client")
client.connect(destino, puerto)

if __name__ == '__main__':
    
    print('Running. Press CTRL-C to exit.')
    
    # Modificar ttyUSB0 por el puerto al que conectemos la arduino (en terminal ejecutar: dmesg | grep "tty")
    with serial.Serial("/dev/ttyUSB0", 9600, timeout=1) as arduino: 
        
        time.sleep(0.1)
        
        if arduino.isOpen():
            
            # Obtenemos el puerto al que esta conectada la arduino (normalmente USB0)
            print("{} conectado".format(arduino.port)) 
            try:
                while True:
                    # Comprobamos si hay datos en el buffer serie
                    while arduino.inWaiting()==0: 
                        pass 
                        
                    if  arduino.inWaiting()>0:

                        #resp = "1-18.00|2.1-10.00,16.00,13.02|2.2-0.48,0.05,0.92|2.3-1.09,0.51,0.63|2.4-11.09,3.34,11.02"
 
                        respuesta=arduino.readline()
                        print("Mensaje recibido: "+respuesta.decode('utf-8').strip())
                        resp = respuesta.decode('utf-8').strip()
                        
                        # Limpiamos el buffer despues de obtener los datos
                        
                        print("Enviamos al broker")
            
                        now = time.time()
                        client.publish("barco/timestamp", str(now))
            
           
                         ######################################################

                        index_list = [pos for pos, char in enumerate(resp) if char == "|"]
                        print(index_list)
                        
                        data = resp[2:(index_list[0])]
                        print(data)
                        dataJSON = json.dumps({"distancia":data})
                        print(dataJSON)
                        client.publish("barco/ultrasonidos",dataJSON)
                        

                
                        data_array = resp[(index_list[0]+5):(index_list[1])].split(",")
                        print("Data_array: ",data_array)
                        x = data_array[0]
                        y = data_array[1]
                        z = data_array[2]
                
                        dataJSON = json.dumps({"x":x,
                                               "y":y,
                                               "z":z})
                        print(dataJSON)
                        client.publish("barco/acelerometro/calibration",dataJSON)
                           
                
                        data_array = resp[(index_list[1]+5):(index_list[2])].split(",")
                        print(data_array)
                        x = data_array[0]
                        y = data_array[1]
                        z = data_array[2]
                
                        dataJSON = json.dumps({"x":x,
                                               "y":y,
                                               "z":z})
                        print(dataJSON)
                        client.publish("barco/acelerometro/acceleration",dataJSON)
                    

                        data_array = resp[(index_list[2]+5):(index_list[3])].split(",")
                        print(data_array)
                        x = data_array[0]
                        y = data_array[1]
                        z = data_array[2]
                
                        dataJSON = json.dumps({"x":x,
                                               "y":y,
                                               "z":z})
                        print("Gyroscopio: "+dataJSON)
                
                        client.publish("barco/acelerometro/gyro",dataJSON)

                        data_array = resp[(index_list[3]+5):].split(",")
                        print(data_array)
                        x = data_array[0]
                        y = data_array[1]
                        z = data_array[2]
                
                        dataJSON = json.dumps({"x":x,
                                               "y":y,
                                               "z":z})
                        print("Gyroscopio: "+dataJSON)
                
                        client.publish("barco/acelerometro/compass",dataJSON)

             
                    #arduino.flushInput()
                        
            except KeyboardInterrupt:
                print("Capturada interrupcion de teclado.")
        
            except ValueError as ve:
                print(ve)
                print("Otra interrupcion")

            except TimeoutError as e:
                print(e)

            finally:
                arduino.close()

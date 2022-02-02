import serial,time
import paho.mqtt.publish as publish
import json

from datetime import datetime

#destino = "88.18.247.162"
destino = "diego1432.duckdns.org"
puerto = 9000

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
                        respuesta=arduino.readline()
                        print("Mensaje recibido: "+respuesta.decode('utf-8'))
                        resp = respuesta.decode('utf-8')
                        
                        # Limpiamos el buffer despues de obtener los datos
                        
                        print("Enviamos al broker")
                        
                        now = time.time()
                        publish.single("barco/timestamp", str(now), hostname=destino, port=puerto)
                        
                        if(resp[0] == '1'):
                            
                            data = resp[2:-2]
                            
                            dataJSON = json.dumps({"distancia":data})
                            print(dataJSON)
                            
                            publish.single("barco/ultrasonidos",dataJSON,hostname=destino, port=puerto)
                            
                        if(resp[0] == '2'):
                            
                            if(resp[2] == '1'):
                                
                                data = resp[4:-2].split(",")
                            
                                x = data[0]
                                y = data[1]
                                z = data[2]
                            
                                dataJSON = json.dumps({"x":x,
                                                       "y":y,
                                                       "z":z})
                                print(dataJSON)
                            
                                publish.single("barco/acelerometro/calibration",dataJSON,hostname=destino, port=puerto)
                                
                            if(resp[2] == '2'):
                                
                                data = resp[4:-2].split(",")
                            
                                x = data[0]
                                y = data[1]
                                z = data[2]
                            
                                dataJSON = json.dumps({"x":x,
                                                       "y":y,
                                                       "z":z})
                                print("Acelerometro:"+dataJSON)
                            
                                publish.single("barco/acelerometro/acceleration",dataJSON,hostname=destino, port=puerto)
                                
                            if(resp[2] == '3'):
                                
                                data = resp[4:-2].split(",")
                            
                                x = data[0]
                                y = data[1]
                                z = data[2]
                            
                                dataJSON = json.dumps({"x":x,
                                                       "y":y,
                                                       "z":z})
                                print("Gyroscopio: "+dataJSON)
                            
                                publish.single("barco/acelerometro/gyro",dataJSON,hostname=destino, port=puerto)
                                
                            if(resp[2] == '4'):
                                
                                data = resp[4:-2].split(",")
                            
                                x = data[0]
                                y = data[1]
                                z = data[2]
                            
                                dataJSON = json.dumps({"x":x,
                                                       "y":y,
                                                       "z":z})
                                print("Compass: "+dataJSON)
                            
                                publish.single("barco/acelerometro/compass",dataJSON,hostname=destino,port=puerto)
                                
                            #if(resp[2] == '5'):
                                
                            #    data = resp[4:-2]
                            
                             #   dataJSON = json.dumps({"angle":data})
                              #  print(dataJSON)
                            
                               # publish.single("barco/acelerometro/angle-mag-x",dataJSON,hostname=destino)
                                
                            #if(resp[2] == '6'):
                                
                             #   data = resp[4:-2]
                            
                              #  dataJSON = json.dumps({"angle":data})
                              #  print(dataJSON)
                            
                              #  publish.single("barco/acelerometro/angle-mag-projx",dataJSON,hostname=destino)
                                
                            
                    arduino.flushInput()
                        
            except KeyboardInterrupt:
                print("Capturada interrupcion de teclado.")
                
            except ValueError as ve:
                print(ve)
                print("Otra interrupcion")
                
            finally:
                arduino.close()

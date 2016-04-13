# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 11:24:53 2016

@author: gonzalo
"""

import threading, serial, time, struct
import matplotlib.pyplot as plt

'''class numGenerator(threading.Thread):
    def __init__(self,num):
        threading.Thread.__init__(self)
        self.num=num
    def run(self):
        pass'''#Esto de momento nada



'''Esta clase permite obtener datos de una comunicacion serie
En la creación del objeto debe indicarse la cabecera y la cola de cada dato recibido'''

class serialPortSensor():
    def __init__(self,header='\n',ender='\r'): # SI no se le indica nada, toma estos valores por defecto
        self.header=header
        self.ender=ender
        
    def initCom(self, baudr=9600): #Tras la creación, debe iniciarse la comunicación. Por defecto a 9600 baudios
        try:
            self.ser=serial.Serial('/dev/ttyUSB0',baudrate=baudr, timeout=2) # Se intentará crear una conexión a través de los puertos ttyUSB1 y tty USB0
            print("Using port", self.ser.port, "@", self.ser.baudrate)
        except:
            try:
                self.ser=serial.Serial('/dev/ttyUSB1',baudrate=baudr, timeout=2)
                print("Using port", self.ser.port, "@", self.ser.baudrate)
            except:
                print("Neither ttyUSB0 nor ttyUSB1 ports are available.")

    def getData(self,n=1): # Este método retorna una tupla con dos listas.
        if n<1:
            print("Number of samples must be positive.")
            return False
        data=[]
        timeaxis=[]
               
        while n>0:
            cur_data=""
            got_header=False
            got_data=False
            while not got_header:
                if chr(struct.unpack('B',self.ser.read(1))[0])==self.header: #se convierte el byte leido a str y se compara con el caracter '\n' que indica el final de la trama
                    got_header=True
            while not got_data:
                cur_byte=chr(struct.unpack('B',self.ser.read(1))[0])
                if cur_byte==self.ender: #El caracter '\r' indica el inicio de la trama
                    got_data=True
                else:
                    cur_data=cur_data+cur_byte
            try:
                data.append(float(cur_data))
                timeaxis.append(time.clock())
                n-=1
            except ValueError:
                print ("Data format not valid.")      
        
        return data, timeaxis # Una de las listas contiene los valores leídos (float) y la otra los instantes de tiempo correspondientes (float)
            

'''INICIO DEL PROGRAMA'''
if __name__ == "__main__":
    arduino=serialPortSensor()
    arduino.initCom()
    y=[]
    t=[]
    while True: #arduino.ser.inWaiting()>0:
        if arduino.ser.inWaiting()==0:
            time.sleep(0.5)    
        elif arduino.ser.inWaiting()>50:
            data_rcv=arduino.getData(50)
        else:
            data_rcv=arduino.getData(arduino.ser.inWaiting())
        for i in range(0,len(data_rcv[0])):
            y.append(data_rcv[0][i])
            t.append(data_rcv[1][i])
        plt.plot(t,y)
        plt.show()
        
        
    print("No hay más datos que leer.")    











     
        
        
        
        

# -*- coding: utf-8 -*-
"""
Created on Thu May  5 12:23:45 2016

@author: gonzalo
"""

'''Esta clase maneja una trama de datos procedente de una conexión serie. La trama tiene que tener un header y un ender.
Cada dato debe ir precedido de un identificador y de un '=' y cada uno de ellos debe ir separado del resto por '/'.
Ejemplo: "'\n's0=23/s1=45'\r'". La función getSingleData() devuelve un array con los valores numéricos obtenidos.'''

import serial, struct

class lightsensormatrix():
    def __init__(self,header='\n',ender='\r',baud=9600, tout=1):
        self.header=header
        self.ender=ender
        self.frame=[]
        try:        
            self.ser = serial.Serial(port='/dev/ttyUSB0', baudrate=baud, timeout=tout)
            print("Using port", self.ser.port, "@", self.ser.baudrate)
        except serial.SerialException:
            try:
                self.ser = serial.Serial(port='/dev/ttyUSB1', baudrate=baud, timeout=tout)
                print("Using port", self.ser.port, "@", self.ser.baudrate)
            except serial.SerialException:
                print("Neither ttyUSB0 nor ttyUSB1 ports are available.")
                
    def getSingleData(self):
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
        cur_data=cur_data.split('/')
        for i in range(0,len(cur_data)):
            cur_data[i]=cur_data[i].split('=')
            cur_data[i]=float(cur_data[i][1])
         
        return cur_data
        
        
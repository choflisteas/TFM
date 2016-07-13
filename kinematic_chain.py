# -*- coding: utf-8 -*-
"""
Created on Fri May  6 12:44:07 2016

@author: gonzalo
"""

#import numpy as np
#import matplotlib.pyplot as plt
#import mpl_toolkits.mplot3d.axes3d as p3
#import matplotlib.animation as animation
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_qt4agg import (
#    FigureCanvasQTAgg as FigureCanvas,
#    NavigationToolbar2QT as NavigationToolbar)
import math
from mathutils import Quaternion

#import time
import threading

class kinematic_chain:
    def __init__(self, driverXbus, framesnames=['clavicula','brazo', 'antebrazo', 'mano'], frameslenghts=[0.2,0.35, 0.25, 0.1],
                 joints=['hombro','codo','munyeca']):
        # framesnames continen los nombres y el orden en el que están conectados los eslabones
        # frameslenghts contiene las longitudes de los eslabones que forman la cadena
        # Se comprueba si las dimensiones de los arrays pasados son correctos y si las longitudes son positivas
        self.__dataok=False
        
        if len(framesnames)<1 or len(framesnames)!=len(frameslenghts):
            raise ValueError (">>>ERROR: Los datos introducidos para crear el objeto kinematic_chain\
                                son incorrectos")
        elif self.__checkFrames(driverXbus, framesnames) == False:
            raise ValueError (">>>ERROR: los eslabones introducidos para crear el objeto\
                               'kinematic_chain' no se encuentran en los datos.")
        elif len(framesnames)-len(joints) !=1:
            print("El número de articulaciones no es correcto, debería ser de %d." %(framesnames-1))
        
        elif all(i>0 for i in frameslenghts):            
            self.mod = frameslenghts
            self.frames = framesnames
            self.nframes = len(self.frames)
            self.v = []
            self.joints = joints
            self.driver = driverXbus
            self.data = driverXbus.datos #Esto sobra si se sustituye self.data por self.driver.datos en toooooda la clase
            for i in range (0,self.nframes):
                self.v.append(Quaternion((0.0, 0.0, 0.0, 1.0))) # Todos los eslabones se definen igual

            self.__dataok=True
        
        if self.__dataok:
            self.__setOrigin()
                                 
            # Se inicializan los datos necesarios
            self.__initData()
            # Se establecen las posiciones de calibración
            self.__setCalibPositions()
            
            # Se defin el tiempo de calibración
            self.setCalibTime()
            
            # Se crean los Locks para restringir el acceso simultaneo a determinadas vbles.
            self.__initLocks()
            
            # Se crea un objeto que lanza la conversión a Quaternions de forma periódica
            self.procThread = recurringTimer(0.1, self.processData)
            self.procThread.start_timer()
            
            print ('La cadena cinemática', self.frames,'se ha creado correctamente.')
            
    def __initData(self):
        self.latestQuat = {}
        self.ang = {}
        axis = ['X', 'Y', 'Z']
        for frame in self.frames:
            self.ang[frame] = {}
            for ax in axis:
                self.ang[frame][ax] = 0
        return True
    
    def __setCalibPositions(self):
        self.qrot = []
        self.vCalib = {}
        for i in range(0,self.nframes):            
            self.vCalib[self.frames[i]] = Quaternion((0,0,0,-1))
        return True
    
    def calibPosition(self,frame,qComponents):
        self.vCalib[frame] = Quaternion((qComponents[0],
                                         qComponents[1],
                                         qComponents[2],
                                         qComponents[3]))            
        
    def __initLocks(self):
        self.coordinatesLock = threading.Lock()
        self.anglesLock = threading.Lock()    
        return True
            
    def __checkFrames(self, driverXbus, framesnames):
        for frame in framesnames:
            if frame not in driverXbus.sensores:
                return False
        return True        

    def rotateFrames(self, q=None): #q es un diccionario de quaterniones, p.ej.:{'mano':Quaternion((0.0,1.0,0.0,0.0)),...}
        if q==None:
            q = self.latestQuat
        if len(q)!=self.nframes:
            raise ValueError ("El número de quaternions no se corresponde con el número\
                               de eslabones de la cadena.")
        else:
            self.v_ = [] #vectores resultantes tras el giro.
            self.coordinatesLock.acquire()
            self.coordinates = [] #coordinadas de los puntos que definen cada eslabón.
            for i in range (0,self.nframes):
                self.v_.append(q[self.frames[i]][0]*self.v[i]*q[self.frames[i]][0].conjugated())
                '''if len(self.qrot) is 0:
                    pass
                else:
                    self.v_[i] = self.qrot[i]*self.v_[i]*self.qrot[i].conjugated()'''
                if i==0:
                    self.coordinates.append(((self.origin[0], self.origin[0]+self.v_[i][1]*self.mod[i]),
                                        (self.origin[1], self.origin[1]+self.v_[i][2]*self.mod[i]),
                                        (self.origin[2], self.origin[2]+self.v_[i][3]*self.mod[i])))
                else:
                    self.coordinates.append(((self.coordinates[i-1][0][1],self.coordinates[i-1][0][1]+self.v_[i][1]*self.mod[i]),
                                        (self.coordinates[i-1][1][1],self.coordinates[i-1][1][1]+self.v_[i][2]*self.mod[i]),
                                        (self.coordinates[i-1][2][1],self.coordinates[i-1][2][1]+self.v_[i][3]*self.mod[i])))
            
        
        self.coordinates = dict(list(zip(self.frames,self.coordinates)))
        self.coordinatesLock.release()        
         
    def processData(self):
        # Este método se lanzará en un hilo para que se realice continuamente
        # la conversión de datos "crudos" a Quaternions.
        keys = list(self.data.keys())
        if len(self.data[keys[0]]) == 0: #se chequea la longitud de una lista cualquiera de los datos para ver si está vacía.
            print (">>> AVISO: Se ha descartado una lectura. No se han podido convertir datos a Quaternions.")
            return False
        else:
            self.latestQuat = self.driver.getQuaternionsFromData(self.driver.getLatestData())
            self.rotateFrames()
            self.getAnglesFromQuaternions()#<<<<<---------------------OJO!!!!!¿¿¿¿¿¿???????????******----------------*****************ÇÇÇÇÇÇÇÇÇ
            return True

    def getAnglesFromQuaternions(self):
        self.anglesLock.acquire()
        self.ang = {}
        axis = ['X', 'Y', 'Z']
        for i in range(0,self.nframes-1): #narticulaciones = neslabones-1
            self.ang[self.joints[i]]={}
            qdif = self.latestQuat[self.frames[i]][0].rotation_difference(self.latestQuat[self.frames[i+1]][0])
            for j in range(0,3): #para cada uno de los ejes
                self.ang[self.joints[i]][axis[j]] = math.degrees(qdif.to_euler()[j])
        self.anglesLock.release()
        
    def getAnglesFromQuaternions3(self):
        # Esta función convierte los datos almacenados en self.data a objetos
        # de la clase Quaternion y borra aquellos datos ya usados.
        self.anglesLock.acquire()
        self.ang = {}
        axis = ['X', 'Y', 'Z']
        for i in range(0,self.nframes-1): #narticulaciones = neslabones-1
            self.ang[self.joints[i]]={}
            qdif = self.v_[i].rotation_difference(self.v_[i+1])
            sqw = qdif[0]*qdif[0]
            sqx = qdif[1]*qdif[1]
            sqy = qdif[2]*qdif[2]
            sqz = qdif[3]*qdif[3]
            #for j in range(0,3):
                #self.ang[frame][axis[i]] = math.degrees(self.latestQuat[frame][0].to_euler()[i])
                #self.ang[self.joints[i]][axis[j]] = math.degrees(qdif[j+1]/s)
            self.ang[self.joints[i]][axis[0]] = math.degrees(math.atan2(2*qdif[2]*qdif[0]-2*qdif[1]*qdif[3], sqx-sqy-sqz-sqw))
            self.ang[self.joints[i]][axis[1]] = math.degrees(math.asin(2*(qdif[1]*qdif[2]+qdif[3]*qdif[0])/(sqx+sqy+sqz+sqw)))
            self.ang[self.joints[i]][axis[2]] = math.degrees(math.atan2(2*qdif[1]*qdif[0]-2*qdif[2]*qdif[3],-sqx+sqy-sqz+sqw))
        self.anglesLock.release()    

    def getAnglesFromQuaternions2(self):
        self.anglesLock.acquire()
        self.ang = {}
        axis = ['X', 'Y', 'Z']
        for i in range(0,self.nframes-1): #narticulaciones = neslabones-1
            self.ang[self.joints[i]]={}
            qdif = self.v_[i].rotation_difference(self.v_[i+1])
            for j in range(0,3): #para cada uno de los ejes
                self.ang[self.joints[i]][axis[j]] = math.degrees(qdif.to_euler()[j])
        self.anglesLock.release()
   
    def __setOrigin(self):
        self.origin = (0, 0, sum(self.mod))
        return True
        
    def setCalibTime(self,tcalib=5):
        if tcalib<2 or tcalib>15:
            print (">>> ERROR: debe indicar un tiempo de calibración entre 2 y 15 segundos.")
            return False
        else:
            self.tcalib = tcalib
            return True        
    
    def beginSetInitPos(self):
        print ("Calibrando...")
        setPosThread = threading.Timer(self.tcalib,self.__setInitPos)
        setPosThread.start()
    
    def __setInitPos(self):
        #se tomarán 10 muestras de los últimos tcalib segundos        
        samples = []
        t = self.data['tiempo'][-1] - self.data['tiempo'][-2]
        sps = 1.0 / round(t,2)
        step = int(sps/10)
        for i in range(0,10*self.tcalib):
            samples.append(-1-i*step)
        self.qoffset = self.driver.getQuaternionsFromData(self.driver.getSortedData(samples), mean=True)
        self.newV = {}
        self.new_v = []
        self.qrot = []
        # Ahora se modifican los frames para la representación sea correcta
        for i in range(0, self.nframes):
            #qact = self.qoffset[self.frames[i]]*self.vCalib[self.frames[i]]*self.qoffset[self.frames[i]].conjugated()
            self.qrot.append(self.qoffset[self.frames[i]].rotation_difference(self.vCalib[self.frames[i]]))
            self.newV[i] = self.qrot[i]*self.vCalib[self.frames[i]]*self.qrot[i].conjugated()
            self.new_v.append(self.qrot[i]*self.vCalib[self.frames[i]]*self.qrot[i].conjugated())#<-----------------
        self.v = self.newV#<------------------------------------------------------------------------
        print("Calibración completada correctamente.")
        
#------------------------------------------------------------------------------            
class recurringTimer(threading.Timer):
    # Implementación de una clase que permite la invocación de un método de forma periódica
     
    def __init__ (self, *args, **kwargs):
        threading.Timer.__init__ (self, *args, **kwargs) 
        self.setDaemon (True)
        self._running = 0
        self._destroy = 0
        self.start()
 
    def run (self):
        while True:
            self.finished.wait (self.interval)
            if self._destroy:
                return;
            if self._running:
                self.function (*self.args, **self.kwargs)
 
    def start_timer (self):
        self._running = 1
 
    def stop_timer (self):
        self._running = 0
 
    def is_running (self):
        return self._running
 
    def destroy_timer (self):
        self._destroy = 1;



    

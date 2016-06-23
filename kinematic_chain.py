# -*- coding: utf-8 -*-
"""
Created on Fri May  6 12:44:07 2016

@author: gonzalo
"""

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import math
from mathutils import Quaternion

import time
import threading

class kinematic_chain:
    def __init__(self, driverXbus, framesnames=['brazo', 'antebrazo', 'mano'], frameslenghts=[0.35, 0.25, 0.1]):
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
        
        elif all(i>0 for i in frameslenghts):            
            self.mod = frameslenghts
            self.frames = framesnames
            self.nframes = len(self.frames)
            self.v = []
            self.driver = driverXbus
            self.data = driverXbus.datos #Esto sobra si se sustituye self.data por self.driver.datos en toooooda la clase
            for i in range (0,self.nframes):
                self.v.append(Quaternion((0.0, 0.0, 0.0, 1.0))) # Todos los eslabones se definen igual

            self.__dataok=True
        
        if self.__dataok:
            self.__setOrigin()
            print ('La cadena cinemática', self.frames,'se ha creado correctamente.')
                        
            # Se inicializan los datos necesarios
            self.__initData()
            
            # Se crea un objeto que lanza la conversión
            self.coordinatesLock = threading.Lock()
            self.anglesLock = threading.Lock()            
            
            self.procThread = recurringTimer(0.1, self.processData)
            self.procThread.start_timer()
            
            
    def __initData(self):
        self.latestQuat = {}
        self.ang = {}
        axis = ['X', 'Y', 'Z']
        for frame in self.frames:
            self.ang[frame] = {}
            for ax in axis:
                self.ang[frame][ax] = 0
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
        
    """def getQuaternionsFromData (self, subdata, mean=False):
        ''' 'subdata' will contain the whole data and 'mean' parameter indicates whether the data used
        for calculating the Quaternion is:
               - a single value -> mean = False
               - the average of all the values -> mean = True'''
        quat = {}
        sufix = ['_q0', '_q1', '_q2', '_q3']
        
        for name in self.frames:
            quat[name] = []
            for suf in sufix:
                if not name+suf in subdata.keys():
                    raise ValueError ('>>>ERROR: señal no encontrada en los datos.')
                elif mean:
                    avg = sum(subdata[name+suf])/len(subdata[name+suf])
                    quat[name].append(avg)                
                else:
                    quat[name].append(subdata[name+suf][0])
                    
            quat[name] = Quaternion((quat[name][0], quat[name][1], quat[name][2], quat[name][3]))
        return quat"""

            
    def processData(self):
        # Este método se lanzará en un hilo para que se realice continuamente
        # la conversión de datos "crudos" a Quaternions.
        keys = list(self.data.keys())
        if len(self.data[keys[0]]) == 0: #se chequea la longitud de una lista cualquiera de los datos para ver si está vacía.
            print (">>> AVISO: no se han podido convertir datos a Quaternions.\
 La base de datos está vacía.")
            return False
        else:
            self.latestQuat = self.driver.getQuaternionsFromData(self.driver.getLatestData())
            self.rotateFrames()
            self.getAnglesFromQuaternions()
            return True

    def getAnglesFromQuaternions(self):
        # Esta función convierte los datos almacenados en self.data a objetos
        # de la clase Quaternion y borra aquellos datos ya usados.
        self.anglesLock.acquire()
        self.ang = {}
        axis = ['X', 'Y', 'Z']
        for frame in self.frames:
            self.ang[frame] = {}
            for i in range(0,3):
                self.ang[frame][axis[i]] = math.degrees(self.latestQuat[frame][0].to_euler()[i])
        self.anglesLock.release()                
    
    """def getLatestData (self, n=1):
        '''Retorna los ultimos n datos contenidos en data
        y los retorna en un diccionario con el mismo formato.'''
        subdata = {}
        for signal in self.data.keys():
            subdata[signal] = []
            for i in range(-n,0):
                subdata[signal].append(self.data[signal][i])
        return subdata       
        
    def getSortedData (self, t):
        '''Retorna los datos contenidos en los indices marcados por t[]
        y los retorna en un diccionario con el mismo formato.'''
        subdata = {}
        for signal in self.data.keys():
            subdata[signal] = []
            for i in t:
                subdata[signal].append(self.data[signal][i])
        return subdata"""
    
    def __setOrigin(self):
        self.origin = (0, 0, sum(self.mod))
    
    def __setOffset(self, tcalib=3, n=4):
        while(self.getLatestData(self.data)['tiempo'][-1]<tcalib):
            pass
        # En t[] se guardarán los indices de los datos que vamos a usar.        
        t = []
        step = len(self.data['tiempo'])//(tcalib*n)
        for i in range(1,tcalib*n+1):
            t.append(step*i)
        subdata = self.getSortedData(t)
        self.qoffset = self.getQuaternionsFromData(subdata, mean=True)
        # Ahora se modifican los frames para la representación sea correcta
        for i in range(0, self.nframes):
           self.v[i] = self.qoffset[self.frames[i]]*self.v[i]*self.qoffset[self.frames[i]].conjugated()
           
    """# Las funciones de representación se han trasladado a una clase específica
    def updatePlot(self,i):
        # se actualizan los valores de las lineas
        for name in self.frames:
            self.lines[name][0].set_data(self.coordinates[name][0], self.coordinates[name][1])
            self.lines[name][0].set_3d_properties(self.coordinates[name][2])


    def plot3d(self, widget):
        # 'widget' será dónde se quiera mostrar el gráfico
        # Creación de la figura
        self.fig3d = Figure()
        # y enlace con el canvas.
        self.canvas3d = FigureCanvas(self.fig3d)
        # Creación los ejes 3D
        self.ax3d = p3.Axes3D(self.fig3d)
        # Establecimiento de los límites de los ejes
        self.ax3d.set_xlim3d([-0.5, 0.5])
        self.ax3d.set_xlabel('X')
        self.ax3d.set_ylim3d([-0.5, 0.5])
        self.ax3d.set_ylabel('Y')
        self.ax3d.set_zlim3d([0.0, 1.0])
        self.ax3d.set_zlabel('Z')
        self.ax3d.set_title('3D View')     
        
        # Creación de la lista de colores
        col = ['red','blue','green', 'black', 'yellow', 'pink', 'orange']  
        colors = {}
        for i in range(0,self.nframes):
            j = i
            if i>6:
                j=i%6
            colors[self.frames[i]] = col[j]
       
        # Definición de las coordenadas iniciales
        self.coordinates = [((0,0),(0,0),(0,0)),((0,0),(0,0),(0,0)),((0,0),(0,0),(0,0))]
        self.coordinates = dict(list(zip(self.frames, self.coordinates)))

        # Creación de las 3DLines
        self.lines = {}
        for name in self.frames:
            self.lines[name] = self.ax3d.plot(self.coordinates[name][0],self.coordinates[name][1],self.coordinates[name][2],'-o',markersize=4,markerfacecolor="orange",linewidth=3, color=colors[name])
        # Se llama a ax.hold para que borre lo que estaba antes y dibuje todo nuevo.                            
        self.ax3d.hold(False)                        
        # Enlace del canvas con el widget
        widget.addWidget(self.canvas3d)
        self.canvas3d.draw()
        # Creación de la animación.
        self.anim = animation.FuncAnimation(self.fig3d, self.updatePlot,interval=100, blit=False)"""
        
        
#------------------------------------------------------------------------------
        
class plot3DChain:
    def __init__(self, chain, widget):
        # 'widget' será dónde se quiera mostrar el gráfico
        # 'chain' es la cadena cinemática a representar
        self.chain = chain
        # Creación de la figura
        self.fig3d = Figure()
        # y enlace con el canvas.
        self.canvas3d = FigureCanvas(self.fig3d)
        # Creación los ejes 3D
        self.ax3d = p3.Axes3D(self.fig3d)
        # Establecimiento de los límites de los ejes
        self.ax3d.set_xlim3d([-0.5, 0.5])
        self.ax3d.set_xlabel('X')
        self.ax3d.set_ylim3d([-0.5, 0.5])
        self.ax3d.set_ylabel('Y')
        self.ax3d.set_zlim3d([0.0, 1.0])
        self.ax3d.set_zlabel('Z')
        self.ax3d.set_title('3D View')     
        
        # Creación de la lista de colores
        col = ['red','blue','green', 'black', 'yellow', 'pink', 'orange']  
        colors = {}
        for i in range(0,self.chain.nframes):
            j = i
            if i>6:
                j=i%6
            colors[self.chain.frames[i]] = col[j]
       
        # Definición de las coordenadas iniciales
        coordinates = [((0,0),(0,0),(0,0)),((0,0),(0,0),(0,0)),((0,0),(0,0),(0,0))]
        coordinates = dict(list(zip(self.chain.frames, coordinates)))

        # Creación de las 3DLines
        self.lines = {}
        for name in self.chain.frames:
            self.lines[name] = self.ax3d.plot(coordinates[name][0],coordinates[name][1],coordinates[name][2],'-o',markersize=4,markerfacecolor="orange",linewidth=3, color=colors[name])
        # Se llama a ax.hold para que borre lo que estaba antes y dibuje todo nuevo.                            
        self.ax3d.hold(False)                        
        # Enlace del canvas con el widget
        widget.addWidget(self.canvas3d)
        self.canvas3d.draw()
        # Creación de la animación.
        self.anim = animation.FuncAnimation(self.fig3d, self.updatePlot,interval=100, blit=False)   

    def updatePlot(self,i):
        # se actualizan los valores de las lineas
        for name in self.chain.frames:
            self.lines[name][0].set_data(self.chain.coordinates[name][0], self.chain.coordinates[name][1])
            self.lines[name][0].set_3d_properties(self.chain.coordinates[name][2]) 
            
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


# Ejemplo de uso, generando unos cadena de 3 eslabones          
if __name__ == "__main__":
    
    datos = {'antebrazo_q0': [0.9766144156455994,
  0.9806947112083435,
  0.9840761423110962,
  0.9868678450584412,   
  0.9890149235725403,
  0.9897510409355164,
  0.9907563328742981,
  0.9900298714637756,
  0.9901557564735413,
  0.9888587594032288],
 'antebrazo_q1': [0.06301222741603851,
  0.06560635566711426,
  0.06812159717082977,
  0.07454560697078705,
  0.07732219994068146,
  0.09018727391958237,
  0.09313075989484787,
  0.10617543756961823,
  0.10893853008747101,
  0.11889593303203583],
 'antebrazo_q2': [0.19692927598953247,
  0.17882686853408813,
  0.16139303147792816,
  0.14254118502140045,
  0.12596653401851654,
  0.10967134684324265,
  0.09434773772954941,
  0.08207018673419952,
  0.06819313019514084,
  0.05820736289024353],
 'antebrazo_q3': [-0.058903519064188004,
  -0.044176895171403885,
  -0.030046921223402023,
  -0.014619911089539528,
  -0.0003834260278381407,
  0.015109376050531864,
  0.028706805780529976,
  0.042767610400915146,
  0.05541304498910904,
  0.06805115193128586],
 'brazo_q0': [0.705383837223053,
  0.7059023380279541,
  0.7022340893745422,
  0.7022221088409424,
  0.7011651396751404,
  0.7000548243522644,
  0.6981678605079651,
  0.6952747702598572,
  0.6925674080848694,
  0.6889120936393738],
 'brazo_q1': [-0.06097843497991562,
  -0.07369398325681686,
  -0.08750403672456741,
  -0.09996135532855988,
  -0.11095015704631805,
  -0.12076032161712646,
  -0.13037042319774628,
  -0.13967910408973694,
  -0.14809101819992065,
  -0.15887293219566345],
 'brazo_q2': [0.33254316449165344,
  0.3139199912548065,
  0.2950935363769531,
  0.27503153681755066,
  0.256795734167099,
  0.2373957484960556,
  0.21979627013206482,
  0.2054857313632965,
  0.18916013836860657,
  0.1770317703485489],
 'brazo_q3': [0.6230010390281677,
  0.6306546926498413,
  0.641973614692688,
  0.6490373611450195,
  0.6558303833007812,
  0.6625582575798035,
  0.6687710881233215,
  0.6744318604469299,
  0.6801748871803284,
  0.6847037672996521],
 'mano_q0': [0.9494596123695374,
  0.9505110383033752,
  0.9511004686355591,
  0.950128436088562,
  0.9494195580482483,
  0.9450922608375549,
  0.9434089064598083,
  0.9379281401634216,
  0.9355869889259338,
  0.9306087493896484],
 'mano_q1': [0.27108797430992126,
  0.2708302140235901,
  0.27047452330589294,
  0.2734314203262329,
  0.27308931946754456,
  0.28322553634643555,
  0.2831001877784729,
  0.2940271198749542,
  0.29384222626686096,
  0.30159610509872437],
 'mano_q2': [0.1463419497013092,
  0.13079585134983063,
  0.11552000790834427,
  0.09900124371051788,
  0.0848308652639389,
  0.07049769163131714,
  0.05728470906615257,
  0.047475557774305344,
  0.03563529625535011,
  0.0283622145652771],
 'mano_q3': [0.060201164335012436,
  0.07793911546468735,
  0.09438667446374893,
  0.11266032606363297,
  0.12973326444625854,
  0.14702489972114563,
  0.16295623779296875,
  0.17772798240184784,
  0.1925257295370102,
  0.20543880760669708],
 'tiempo': [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 4]}    
    
    brazo=kinematic_chain(datos)


    

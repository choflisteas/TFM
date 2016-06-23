import math
from mathutils import Quaternion

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation


from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

import threading

import random #solamente usado para hacer las pruebas del plot

def getGlobalAngles(q0):
    ang = [0.0, 0.0, 0.0]
    v = Quaternion((0.0,0.0,0.0,1.0))
    q = q0*v*q0.conjugated()
    
    ang[0] = math.degrees(math.atan(q[3]/q[2]))

    ang[1] = math.degrees(math.atan(q[1]/q[3])) 
    
    ang[2] = math.degrees(math.atan(q[2]/q[1]))
    
    return ang

def getAnglesFromQuaternions(q):
    #q is a dictionary with quaternions and whose keys are the frames
    ang = {}
    axis = ['X', 'Y', 'Z']
    for frame in list(q.keys()):
        ang[frame] = {}
        for ax in axis:
            ang[frame][axis] = math.degrees(q[frame][0].to_euler()[i])
    return ang
    
def getEulerAngles(q0):
    ang = [0.0,0.0,0.0]
    v = Quaternion((0,0,0,1))
    q = q0*v*q0.conjugated()

    for i in range(0,3):
        ang[i] = math.degrees(q.to_euler()[i])
    
    return ang

def getDifAngles(q0,q1):
    angA = [0.0, 0.0, 0.0]
    angB = [0.0, 0.0, 0.0]
    v0 = Quaternion((0.0,0.0,0.0,1.0))
    v1 = Quaternion((0.0,0.0,0.0,1.0))    
    qA = q0*v0*q0.conjugated()
    qB = q1*v1*q1.conjugated()    
    
    angA[0] = math.degrees(math.atan(qA[3]/qA[2]))
    angB[0] = math.degrees(math.atan(qA[3]/qA[2]))

    angA[1] = math.degrees(math.atan(qA[1]/qA[3]))    
    angB[1] = math.degrees(math.atan(qA[1]/qA[3]))
    
    angA[2] = math.degrees(math.atan(qA[2]/qA[1]))
    angB[2] = math.degrees(math.atan(qA[2]/qA[1]))
    
    return [sum(i) for i in zip(angA,angB)]
    

    
#-----------------------------------------------------------------------------#
    
class tempGraph():
    def __init__(self, kinem_chain, name, frames, axis, inf_limit, sup_limit):
        # kinem_chain es un objeto de la clase 'kinematic_chain' que contiene los datos a representar
        # inf_limit and sup limit are the values used to plot the red lines
        # widget is where the graph will be plotted
        self.name = name
        self.chain = kinem_chain
        lim = self.defLimits(inf_limit, sup_limit)
        fra = self.__checkFrames(frames)
        ax = self.__checkAxis(axis)
        if lim and fra and ax:
            print (">>> La gráfica %s se ha creado correctamente. Mostrará el ángulo entre \
%s y %s en el eje %s" %(self.name,self.frames[0], self.frames[1], self.axis))
        else:
            print ("-->No se ha podido crear la gráfica %s." %name)
    
    def defLimits(self, inf_limit,sup_limit):
        if inf_limit<-180 or sup_limit>180 or sup_limit<inf_limit:
            raise ValueError(">>> ERROR: Los límites introducidos no son válidos", self.name )
        else:
            self.inf_limit = inf_limit
            self.sup_limit = sup_limit
            return True
    
    def __checkFrames(self, frames):
        # el número de frames debe ser 2.
        if len(frames) != 2:
            print(">>> ERROR: El número de eslabones no es correcto")
            return False
        # las frames indicadas deben estar en la base de datos del objeto kinem_chain
        for frame in frames:
            if frame not in self.chain.ang:
                print(">>> ERROR: No se han encontrado los eslabones en la estructura de datos")
                return False
        self.frames = frames
        return True
        
    def __checkAxis(self,axis):
        if axis not in ['X','Y','Z','x','y','z']:
            return False
        else:
            self.axis = str.capitalize(axis)
            return True
    
    def setColor(self,color='blue'):
        if color not in ['blue', 'green', 'red', 'black', 'orange', 'yellow']:
            return False
        else:
            self.color=color      

    def updatePlot(self,i):
        
        # Actualizar los datos
        if len(self.chain.ang) == 0: #Esto se produciría cuando aún no se hubiera calculado ningún ángulo        
            pass
        else:
            self.angle.pop(0)
            ang = self.chain.ang[self.frames[0]][self.axis]-self.chain.ang[self.frames[1]][self.axis]
            #ang = random.random()*10            
            print ("Dato nuevo %f" %ang)
            self.angle.append(ang)
            self.line.set_ydata(self.angle)
        

    def plotGraph(self, widget):
        # 'widget' será dónde se quiera mostrar el gráfico
        # Creación de la figura
        self.fig = Figure()
        # y enlace con el canvas.
        self.canvas = FigureCanvas(self.fig)
        # Creación los ejes 3D
        self.ax = self.fig.add_subplot('111')
        # Establecimiento de los límites de los ejes
        self.ax.set_ylim(self.inf_limit, self.sup_limit)
        self.ax.set_title(self.name)
        
        self.setColor()
        
        self.angle = []
       
        for i in range(0,100):
            self.angle.append(0)
        self.line, = self.ax.plot(self.angle, color=self.color)

        self.ax.hold(False)                        
        # Enlace del canvas con el widget
        widget.addWidget(self.canvas)
        self.canvas.draw()
        # Creación de la animación.
        self.anim = animation.FuncAnimation(self.fig, self.updatePlot,interval=100, blit=False)
        
    
    
    
        
        
    

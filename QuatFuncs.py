import math
from mathutils import Quaternion

#import numpy as np
#import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation


from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

import threading

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
    
#------------------------------------------------------------------------------
        
class plot3DChain:
    def __init__(self, chain, layout):
        # 'widget' será dónde se quiera mostrar el gráfico
        # 'chain' es la cadena cinemática a representar
        self.chain = chain
        # Variable para controlar la representación gráfica del objeto
        self.plotting = True
        # Creación de la figura
        self.fig = Figure()
        # y enlace con el canvas.
        self.canvas = FigureCanvas(self.fig)
        # se hace propio el layout para poder ocultar/mostrar el gráfico
        self.layout = layout        
        # Creación los ejes 3D
        self.ax3d = p3.Axes3D(self.fig)
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
       
        # Definición de las coordenadas iniciales ya que no se pueden crear lineas vacías.
        coordinates = []
        for j in range(0,self.chain.nframes): #para cada uno de los eslabones        
            coordinates.append([])
            for i in range(0,3): #para cada uno de los ejes
                coordinates[j].append((0,0))

        #coordinates = [((0,0),(0,0),(0,0)),((0,0),(0,0),(0,0)),((0,0),(0,0),(0,0))]
        coordinates = dict(list(zip(self.chain.frames, coordinates)))

        # Creación de las 3DLines
        self.lines = {}
        for name in self.chain.frames:
            self.lines[name] = self.ax3d.plot(coordinates[name][0],coordinates[name][1],coordinates[name][2],'-o',markersize=4,markerfacecolor="orange",linewidth=3, color=colors[name])
        # Se llama a ax.hold para que borre lo que estaba antes y dibuje todo nuevo.                            
        self.ax3d.hold(False)                        
        layout.addWidget(self.canvas) #con esta opción se inserta en un layout.
        #self.canvas3d.setParent(widget)
        self.canvas.draw()
        # Creación de la animación.
        self.anim = animation.FuncAnimation(self.fig, self.updatePlot,interval=100, blit=False)   

    def updatePlot(self,i):
        # Se comprueba si la visualización está activada:
        if self.plotting == True:

        # y se actualizan los valores de las lineas:
            for name in self.chain.frames:
                self.lines[name][0].set_data(self.chain.coordinates[name][0], self.chain.coordinates[name][1])
                self.lines[name][0].set_3d_properties(self.chain.coordinates[name][2])

    def togglePlot(self):
        self.plotting = not self.plotting

#------------------------------------------------------------------------------

class chainGraphs():
    def __init__(self, kinem_chain, layout):
        # kinem_chain es un objeto de la clase 'kinematic_chain' que contiene los datos a representar
        # inf_limit and sup limit are the values used to plot the red lines
        # widget is where the graph will be plotted
        self.chain = kinem_chain

        # Variable para controlar la representación gráfica del objeto
        self.plotting = True
        
        self.layout = layout
        self.__initData()
        self.__initPlots()

 
        self.plotThread = recurringTimer(0.1, self.updatePlots)
        self.plotThread.start_timer()
        
    def __initData(self):
        # Articulación que se muestra por defecto:
        self.activeJoint = self.chain.joints[0] #por defecto
        # Datos para este ejemplo en concreto:
        self.graphData = {'munyeca':{'X':{'name':'Desviación radial(-)/cubital(+)','max':15,'min':-20,'plot':True,'offset':0},
                        'Y':{'name':'Flexión(+)/Extensión(-)','max':45,'min':-45,'plot':True,'offset':0},
                        'Z':{'name':' ','max':30,'min':-10,'plot':False,'offset':0}},
                        'codo':{'X':{'name':'Flexión(-)/Extensión(+)','max':120,'min':60,'plot':True,'offset':0},
                        'Y':{'name':'','max':40,'min':-35,'plot':False,'offset':0},
                        'Z':{'name':'Pronación(-)/Supinación(+)','max':60,'min':-60,'plot':True,'offset':0}},
                        'hombro':{'X':{'name':'Flexión(-)/Extensión(+)','max':10,'min':-10,'plot':True,'offset':0},
                        'Y':{'name':'Abducción(+)/Adducción(-)','max':45,'min':-20,'plot':True,'offset':0},
                        'Z':{'name':'Rotación int.(-)/ext(+)','max':30,'min':-30,'plot':True,'offset':0}}}    
    
    def checkJointAngles(self,joint,axis):
        if self.plotData[joint][axis][-1]>self.graphData[joint][axis]['max'] or\
        self.plotData[joint][axis][-1]<self.graphData[joint][axis]['min']:
            return True
        else:
            return False                 
        
    
    def getCurrentJoint(self):
        pass
    
    def togglePlot(self):
        self.plotting = not self.plotting
        if self.plotting == True:
            self.plotThread.start_timer()
        else:
            self.plotThread.stop_timer()

    def updatePlots(self):
        # Actualizar los datos si self.plotting está activado
        if self.plotting == True:
            for joint in self.chain.joints:
                for axis in ['X','Y','Z']:
                    self.plotData[joint][axis].pop(0)
                    self.plotData[joint][axis].append(self.chain.ang[joint][axis]+self.graphData[joint][axis]['offset'])
                
        for axis in ['X','Y','Z']:
            if self.firstPlot == True:
                self.firstPlot = False
                self.selectJoint('hombro')
            
            if self.graphData[self.activeJoint][axis]['plot'] == False:
                pass
            else:
                self.plotStuff[axis]['line'].set_ydata(self.plotData[self.activeJoint][axis])
    
                self.plotStuff[axis]['ax'].draw_artist(self.plotStuff[axis]['ax'].patch)
                self.plotStuff[axis]['ax'].draw_artist(self.plotStuff[axis]['line'])
                self.plotStuff[axis]['ax'].draw_artist(self.plotStuff[axis]['limits'])
    
                if (self.checkJointAngles(self.activeJoint,axis)==True) and (self.plotStuff[axis]['ax'].get_axis_bgcolor() is not 'r'):
                    self.plotStuff[axis]['ax'].set_axis_bgcolor('r')
                elif (self.checkJointAngles(self.activeJoint,axis)==False) and (self.plotStuff[axis]['ax'].get_axis_bgcolor()is not 'w'):
                    self.plotStuff[axis]['ax'].set_axis_bgcolor('w')
                
                self.plotStuff[axis]['fig'].canvas.update()
                self.plotStuff[axis]['fig'].canvas.flush_events()
                   

    def __initPlots(self):

        initLine = []
        for i in range (0,100):
            initLine.append(0)
        
        colors = {'X':'green','Y':'blue','Z':'orange'}        
        
        self.plotStuff = {}           
        for axis in ['X','Y','Z']:
            self.plotStuff[axis] = {}
            self.plotStuff[axis]['fig'] = Figure()
            self.plotStuff[axis]['canvas'] = FigureCanvas(self.plotStuff[axis]['fig'])
            self.plotStuff[axis]['ax'] = self.plotStuff[axis]['fig'].add_subplot('111')
            self.plotStuff[axis]['ax'].hold(False)            
            self.plotStuff[axis]['line'], = self.plotStuff[axis]['ax'].plot(initLine, color = colors[axis], linewidth = 2)
            minAngle = self.graphData[self.activeJoint][axis]['min']
            maxAngle = self.graphData[self.activeJoint][axis]['max']
            self.plotStuff[axis]['limits'] = self.plotStuff[axis]['ax'].hlines([minAngle,maxAngle],0,99,colors = 'red',linestyles='dashed')
            
            self.layout.addWidget(self.plotStuff[axis]['canvas'])
            self.plotStuff[axis]['canvas'].draw()
            #self.plotStuff[axis]['ax'].set_ylim(-180,180)
            
            self.firstPlot = True
            
            #title = 'Eje'+axis
            #self.plotStuff[axis]['ax'].set_title(title)
            
        self.plotData = {}
        for joint in self.chain.joints:
            self.plotData[joint]={}
            self.plotData[joint]['plotting'] = False
            for axis in ['X', 'Y', 'Z']:
                self.plotData[joint][axis] = initLine.copy()

    def __changePlotLimits(self):
        for axis in ['X','Y','Z']:
            minAngle = self.graphData[self.activeJoint][axis]['min']
            maxAngle = self.graphData[self.activeJoint][axis]['max']
            self.plotStuff[axis]['limits'] = self.plotStuff[axis]['ax'].hlines([minAngle,maxAngle],0,99,colors = 'red',linestyles='dashed')
            
    def __hideSomePlots(self):
        for axis in ['X','Y','Z']:
            if self.graphData[self.activeJoint][axis]['plot'] == False:
                self.plotStuff[axis]['ax'].set_axis_bgcolor('grey')
                self.plotStuff[axis]['ax'].clear()
            else:
                self.plotStuff[axis]['ax'].set_ylim(-180,180)
    
    def __changePlotTitles(self):
        for axis in ['X','Y','Z']:
            title = self.graphData[self.activeJoint][axis]['name']
            title = self.plotStuff[axis]['ax'].set_title(title)
            self.plotStuff[axis]['canvas'].draw()

    def selectJoint(self,joint):
        if joint not in self.chain.joints:
            print("La articulación no se encuentra.")
            return False
        else:
            self.activeJoint = joint
            self.__changePlotLimits()
            self.__hideSomePlots()
            self.__changePlotTitles()
            return True
        
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

        
    
    
    
        
        
    

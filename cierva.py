from PyQt4.uic import loadUiType
 
import matplotlib.animation as animation
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
    

Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui')

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        #Configuración de señales
        self.qDetener.clicked.connect(stopPlots)
 
    '''def addmpl(self, fig):# no usada por el momento.
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()'''

def stopPlots(kinem_chain):
    kinem_chain.procThread.destroy_timer()        
        
if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui
    
    import numpy as np
    import threading
    import time
    
    from kinematic_chain import *
    from driverXbus import *
    from QuatFuncs import *
        
    app = QtGui.QApplication(sys.argv)
    main = Main()
    
    # Inicialización de los objetos encargados de la captura y representación de datos.
    bus=simurdriver(freq=100 , modo=1, buff=0.1)
    # Adición de sensores:
    bus.addsensor('brazo',sensor(1323366,0))
    bus.addsensor('antebrazo',sensor(1323357,1))
    bus.addsensor('mano',sensor(1323356,2))   
    
    bus.gotoconfig()
    bus.configura()
   
    # Comienzo de la captura de datos.
    bus.gotomeasurement()
    # Se hace una pequeña pausa para acumular los primeros datos    
    time.sleep(0.1)
    
    brazo = kinematic_chain(bus)
    # Creación del gráfico 3D
    brazoPlot = plot3DChain(brazo,main.verticalLayout)
    # Creación de la gráfica temporal 'codoX'
    codoX = tempGraph(brazo,'Codo X',['brazo','antebrazo'], 'X', -30, 30)
    codoX.plotGraph(main.verticalLayout)
    
    codoY = tempGraph(brazo,'Codo Y',['brazo','antebrazo'], 'Y', -45, 45)
    codoY.plotGraph(main.verticalLayout)
      
    main.show()
    sys.exit(app.exec_())
    

        
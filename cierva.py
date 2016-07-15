from PyQt4.uic import loadUiType
#from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('mainwindow2.ui')

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, kinem_chain):
        super(Main, self).__init__()
        self.setupUi(self)
        self.chain = kinem_chain
        
        #Configuración de señales
        self.qHombro.clicked.connect(self.Hombro)        
        self.qCodo.clicked.connect(self.Codo)
        self.qMunyeca.clicked.connect(self.Munyeca)
        
        self.qToggle.clicked.connect(self.togglePlotting)
        self.qPosicion.clicked.connect(self.setInitPos)
        self.qSalir.clicked.connect(self.exitApp)
        
        # Variables para control de la respresentación gráfica
        #self.plotting = False
 
    def togglePlotting(self):
        brazoTemp.togglePlot()
        brazo3D.togglePlot()
           
    def setInitPos(self):
        self.chain.beginSetInitPos()
    
    def exitApp(self):
        bus.gotoconfig()
        self.close()
        
    def Hombro(self):
        main.qLabelArt.setText('Hombro')
        brazoTemp.selectJoint('hombro')
        brazoTemp.updatePlots()


    def Codo(self):
        main.qLabelArt.setText('Codo')        
        brazoTemp.selectJoint('codo')
        brazoTemp.updatePlots()
        
    def Munyeca(self):
        main.qLabelArt.setText('Muñeca')
        brazoTemp.selectJoint('munyeca')
        brazoTemp.updatePlots()
        
        
if __name__ == '__main__':
    
    import sys
    from PyQt4 import QtGui
    
    #import numpy as np
    #import threading
    #import time

    from kinematic_chain import *
    from driverXbus import *
    from QuatFuncs import *
    
    # Inicialización de los objetos encargados de la captura y representación de datos.
    bus=simurdriver(freq=100 , modo=1, buff=0.1)
    # Adición de sensores:
    bus.addsensor('clavicula',sensor(323868,0))
    bus.addsensor('brazo',sensor(1323366,1))
    bus.addsensor('antebrazo',sensor(1323357,2))
    bus.addsensor('mano',sensor(1323356,3))   
    
    bus.gotoconfig()
    bus.configura()
   
    # Comienzo de la captura de datos.
    bus.gotomeasurement()
    # Se hace una pequeña pausa para acumular los primeros datos    
    time.sleep(0.1)
    
    brazo = kinematic_chain(bus,['clavicula','brazo','antebrazo','mano'],[0.2,0.35,0.3,0.2],['hombro','codo','munyeca'])
    brazo.calibPosition('clavicula',(0,1,0,0))
    
    #Creación de la interfaz            
    app = QtGui.QApplication(sys.argv)
    main = Main(brazo)
    
    # Variables para el control de la representación gráfica
    
    
    # Creación del gráfico 3D
    brazo3D = plot3DChain(brazo,main.layout3D)

    # Creación de las gráficas temporales
    brazoTemp = chainGraphs(brazo,main.layoutGraphs)
             
    main.show()
    sys.exit(app.exec_())
    

        

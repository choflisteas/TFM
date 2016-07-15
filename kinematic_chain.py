#!/usr/bin/python
# -*- coding: utf-8 -*-
import serial	
import struct
import time
import threading
from mathutils import Quaternion
#import pysimur

verbose=True

def SendMessage(puerto,codigo):
  """Envia un mensaje al puerto, conteniendo los caracteres cuyos
  codigos ascii estan en la lista codigo, mas su correspondiente checksum
  """
  #Se calcula el cheksum y se coloca al final
  checksum=0
  msg=struct.pack('B',codigo[0])
  for tmp in codigo[1:]:
    checksum=checksum+tmp
    msg=msg+struct.pack('B',tmp)
  msg=msg+struct.pack('B',256-checksum%256)
  #Se envia por el puerto serie 
  while (puerto.inWaiting()>0): #Vaciar el puerto
    if verbose:
      print ('>>> AVISO: Se descartaran ', puerto.inWaiting() , ' datos')
    puerto.flushInput()
  puerto.write(msg)
  
def CheckError(puerto,numero):
  """Comprueba si se ha recibido un mensaje enviado,
    analizando el cheksum
  """
  reply=puerto.read(5)
  reply=struct.unpack('BBBBB',reply)
  checksum=sum(reply[1:])
  error=False
  if checksum%256!=0:
    raise ValueError ('Error de checksum')
  elif reply[2]!=numero:
    raise ValueError ('Error en la secuencia de mensajes')

#------------------------------------------------------------------------------
    
class sensor():
    def __init__(self,sn,did):
        self.opt=sn
        self.kID=did


#------------------------------------------------------------------------------

class simurdriver():
  """clase para gestionar la captura de datos del Xbus Master"""
  def __init__(self,freq=100,buff=1,modo=0,opt=None):
    """Crea un objeto BusMaster para controlar la captura de
    datos. 
    Input parameters:
      datos->   objeto con los datos a modificar
      freq->    Frecuencia de muestreo (por defecto 100Hz)
      buffer->  Tamaño del bloque de captura en segundos (por defecto 1 s)
      opt -> opciones de este driver concreto
        puerto->  Cadena con el nombre del puerto serie(por defecto '/dev/ttyUSB0')
        bps->     Velocidad de transferencia (por defecto 115200 bps)
    """
    if opt==None:
      opt=['/dev/ttyUSB0',115200]
    puerto=opt[0]
    bps=opt[1]

    self.freq=freq
    self.sensores={}
    self.datos={}
    # Número de muestras almacenadas en el buffer
    self.buffer=buff*freq
    self.modo=modo
    #Matrices de rotación de los datos de las IMU's
    self.rot_matrix = {}
    # Lock para gestionar el acceso exclusivo a self.datos
    self.lock= threading.Lock()

    #Creamos el objeto serial asociado al puerto de comunicaciones  
    try:
      self.puerto=serial.Serial(puerto,bps,timeout=0.1)
      self.puerto.setRTS(1)
    except serial.SerialException:
      print ('--> No se ha podido abrir el puerto de comunicaciones.')
    self.puerto.stopbits=serial.STOPBITS_TWO
    self.bps=bps
    self.thread_read=None
    self.capturando=0
  def __str__(self):
    cadena='Driver para lectura de fichero\n'
    cadena+='\t nombre: '+self.name+'\n'
    cadena+='\t frecuencia: '+str(self.freq)+'\n'
    cadena+='\t sensores: '+str(self.sensores.keys())+'\n'
    cadena+='\t puerto: '+str(self.puerto)+'\n'
    cadena+='\t bps: '+str(self.bps)+'\n'
    return cadena

  def addsensor(self,name,sensor):
    """Añade un sensor al driver
    """
    self.sensores[name]=sensor

  def gotoconfig(self):
    """Pasa a modo de configuracion
    """
    if self.thread_read!=None:
      self.capturando=0
      self.thread_read.join()
    codigo=[250,255,48,0]#Cuerpo del mensaje (excepto el byte de checksum)
    SendMessage(self.puerto,codigo)
    time.sleep(0.1)
    while (self.puerto.inWaiting()>0): #Vaciar el puerto
      if verbose:
        print ('>>> AVISO: Se descartaran '+str(self.puerto.inWaiting())+' datos')
      self.puerto.flushInput()
    self.puerto.setRTS(1)
    codigo=[250,255,48,0]#Cuerpo del mensaje (excepto el byte de checksum)
    SendMessage(self.puerto,codigo)
    CheckError(self.puerto,codigo[2]+1)

  def configura(self):
    """Se configura el dispositivo a la frecuencia y modo pedidos
    También se da nombre a las señales que se generaran y se insertan
    las claves en los datos
    """
    timeout, self.puerto.timeout = self.puerto.timeout,1
    self.__InitBus()
    self.__SetPeriod(self.freq)
    if self.modo==0 or self.modo==1:
      self.__SetMTOutputMode(self.modo);
    else:
      raise ValueError ('El Xbus solo soporta los modos 0 y 1.')
    self.puerto.timeout = timeout
    
    if self.modo==0:
        self.datos['tiempo']=[]        
        for name in self.sensores:
          for sufijo in ['_ax','_ay','_az','_wx','_wy','_wz','_bx','_by','_bz']:
            if not (name+sufijo) in self.datos:
              self.datos[name+sufijo]=[]
              if verbose:
                print('añadida la señal: ' +name+sufijo)
            else:
              raise ValueError ('la señal '+name+sufijo+' está duplicada')
    if self.modo==1:
        self.datos['tiempo']=[]
        for name in self.sensores:
          for sufijo in ['_q0','_q1','_q2','_q3']:
            if not (name+sufijo) in self.datos:
              self.datos[name+sufijo]=[]
              if verbose:
                print('añadida la señal: ' +name+sufijo)
            else:
              raise ValueError ('la señal '+name+sufijo+' está duplicada')              

  def gotomeasurement(self):
    """Pasa el dispositivo al estado measurement.
    """
    #Se manda el mensaje
    codigo=[250,255,16,0]
    SendMessage(self.puerto,codigo)
    CheckError(self.puerto,codigo[2]+1)
    self.thread_read = threading.Thread(target=self.__leerxbusdata)
    self.capturando=1
    self.puerto.setRTS(1)
    self.time_start=time.time()
    self.thread_read.start()    

  def __leerxbusdata(self):
    """Lee datos desde el dispositivo Xbus Master. 
    """
    while self.capturando:
      try:
        t, self.puerto.timeout = self.puerto.timeout, 1.2 #Voy a leer maximo 1 segundo
        data=self.puerto.read(int(self.DataLength*self.buffer))
        self.puerto.timeout=t #Recupero timeout standar
        #Separar los mensajes
        formato=''
        formato=formato+'B'*self.DataLength
        for tmp in range(int(self.buffer)):
          #muestras=float(tmp)          
          mensaje=data[tmp*self.DataLength:(tmp+1)*self.DataLength]
          reply=struct.unpack(formato,mensaje)
          if (sum(reply[1:])%256!=0):
            raise ValueError ('ERROR de checksum')
          if (reply[2]!=50):
            raise ValueError ('ERROR de tipo de mensaje')
          #procesar la informacion
          if self.modo==0:
            muestra=struct.unpack('>H',mensaje[4:6])
            muestra=float(muestra[0])
            self.datos['tiempo'].append(muestra/self.freq)
            DL=36 #Longitud de los datos en el modo 0
            for s in self.sensores:
              k=self.sensores[s].kID
              ax=struct.unpack('>f',mensaje[6+k*DL:10+k*DL])
              ay=struct.unpack('>f',mensaje[10+k*DL:14+k*DL])
              az=struct.unpack('>f',mensaje[14+k*DL:18+k*DL])
              wx=struct.unpack('>f',mensaje[18+k*DL:22+k*DL])
              wy=struct.unpack('>f',mensaje[22+k*DL:26+k*DL])
              wz=struct.unpack('>f',mensaje[26+k*DL:30+k*DL])
              bx=struct.unpack('>f',mensaje[30+k*DL:34+k*DL])
              by=struct.unpack('>f',mensaje[34+k*DL:38+k*DL])
              bz=struct.unpack('>f',mensaje[38+k*DL:42+k*DL])
              self.lock.acquire()
              self.datos[s+'_ax'].append(ax[0])
              self.datos[s+'_ay'].append(ay[0])
              self.datos[s+'_az'].append(az[0])
              self.datos[s+'_wx'].append(wx[0])
              self.datos[s+'_wy'].append(wy[0])
              self.datos[s+'_wz'].append(wz[0])
              self.datos[s+'_bx'].append(bx[0])
              self.datos[s+'_by'].append(by[0])
              self.datos[s+'_bz'].append(bz[0])
              self.lock.release()
          elif self.modo==1:
            muestra=struct.unpack('>H',mensaje[4:6]) #SC, SampleCounter
            muestra=float(muestra[0])
            self.datos['tiempo'].append(muestra/self.freq)
            DL=16 #Longitud de los datos en el modo 1
            for s in self.sensores:
              k=self.sensores[s].kID
              q0=struct.unpack('>f',mensaje[6+k*DL:10+k*DL])
              q1=struct.unpack('>f',mensaje[10+k*DL:14+k*DL])
              q2=struct.unpack('>f',mensaje[14+k*DL:18+k*DL])
              q3=struct.unpack('>f',mensaje[18+k*DL:22+k*DL])
              self.lock.acquire()              
              self.datos[s+'_q0'].append(q0[0])
              self.datos[s+'_q1'].append(q1[0])
              self.datos[s+'_q2'].append(q2[0])
              self.datos[s+'_q3'].append(q3[0])
              self.lock.release()                
      except:
        #probably got disconnected
        if self.lock.locked():
          self.lock.release()
        break

  def __InitBus(self):
    """Envia el mensaje initbus al dispositivo, y recupera la
    informacion sobre los IMUS conectados al mismo. Numero y numeros de serie
    """
    codigo=[250,255,2,0]
    SendMessage(self.puerto,codigo)
    #Primero se leen 4 bytes para concer la longitud total del mensaje
    reply=self.puerto.read(4)
    reply=struct.unpack('BBBB',reply)
    if reply[2]!=3:
      raise ValueError ('Error en la secuencia de mensajes')
    #de momento no se ha detectado ningun error y se continua con la lectura
    #del resto del mensaje ack1(end)+1 bytes
    reply2=self.puerto.read(reply[-1]+1)
    #for tmp in reply2:
    #  reply=reply+struct.unpack('B',tmp)
    reply=reply+struct.unpack('B'*len(reply2),reply2)    
    checksum=sum(reply[1:])
    if checksum%256!=0:
      raise ValueError ('Error de checksum')
    #Numero de sensores conectados. No tiene porque coincidir con ns, que son los usados
    self.ndisp=reply[3]//4
    #Idenfiticadores de los sensores
    ID_sensores=reply[4:-1]
    self.ID_sensores=[]
    for tmp in range(int(len(ID_sensores)/4)):
      numserie=''
      for tmp2 in range(4):
        numserie=numserie+"%02X"%ID_sensores[tmp*4+tmp2]
      self.ID_sensores=self.ID_sensores+[int(numserie)]
    #Comprobamos que los solicitados están en la lista
    # y les asignamos el ID    
    for sensorname in self.sensores:
      for k in range(len(self.ID_sensores)):
        if self.sensores[sensorname].opt==self.ID_sensores[k]:
          self.sensores[sensorname].kID=k
          break
      else:
        raise ValueError ('no se ha encontrado el sensor: '+str(sensorname)+' ID:'+str(self.sensores[sensorname].opt))
        
    #Fijamos el tamaño de los datos
    if self.modo==0 :
      self.DataLength=self.ndisp*36+2
      self.Data=1+9*self.ndisp
    elif self.modo==1:
      self.DataLength=self.ndisp*16+2
      self.Data=1+4*self.ndisp
        
    if self.DataLength>254:
      self.DataLength=self.DataLength+7 # se incluye la cabecera y el checksum
    else:
      self.DataLength=self.DataLength+5 # Se incluye la cabecera y el checksum
    

  def __SetPeriod(self,freq=100):
    """Envia el mensaje __SetPeriod al objeto XBusMaster
    y lo fija para trabajar a la frecuencia indicada 
    """
    #Calcular la frecuencia de muestreo
    freq=int(freq)
    fm=[int(115200/freq//256), int(115200/freq%256)]
    #Cuerpo del mensaje (excepto el byte de checksum)
    codigo=[250,255,4,2]+fm
    SendMessage(self.puerto,codigo)
    CheckError(self.puerto,codigo[2]+1)

  def __SetMTOutputMode(self, format=0):
    # Envia el mensaje SetOutputMode a cada IMU
    # Input parameters: 
    #  format -> 0 datos calibrados
    #            1 Quaternions
    #            2 Quaternions + datos calibrados (no esta listo)
    #            2 Angulos de Euler(no esta listo)
    #            3 Matriz de rotacion (no esta listo)
    
    if format==0:
      outmode=[0,2]
      outsett=[0,0,0,0]
    elif format==1:
      outmode=[0,4]
      outsett=[0,0,0,0]      
    elif format==2:
      outmode=[0,6]
      outsett=[0,0,0,0]
    elif format==3:
      outmode=[0,6]
      outsett=[0,0,0,4]
    elif format==4:
      outmode=[0,6]
      outsett=[0,0,0,8]
    for k in range(1,self.ndisp+1):
      # Cuerpo del mensaje (excepto el checksum)
      codigo=[250,k,208,2]+outmode
      SendMessage(self.puerto,codigo)
      CheckError(self.puerto,codigo[2]+1)
      codigo=[250,k,210,4]+outsett
      SendMessage(self.puerto,codigo)
      CheckError(self.puerto,codigo[2]+1)
  
  def setObjectAlignment(self, sensorname, zdir=0):
      #sensor es un parámetro que contiene una cadena de caracteres con el nombre del sensor a configurar
      #zdir puede tomar los siguientes valores en relación al dibujo en relieve del sensor:
      #    - 0: la orientación de los datos es como marca el dibujo en relieve.
      #    - 1: newX=Z, newY=Y, newZ=-X
          
      if zdir:
          rotmatrix = [0.0,0.0,1.0,0.0,1.0,0.0,-1.0,0.0,0.0]
      else:
          rotmatrix = [1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0]
     
      data = []
      for i in range(0,len(rotmatrix)):
          data = data + list(struct.pack('>f',rotmatrix[i]))
      datalenght = len(data)
      
      codigo=[250, self.sensores[sensorname].kID+1, 224, datalenght] + data
      SendMessage(self.puerto, codigo)
      CheckError(self.puerto, codigo[2]+1)
      return True

  def requestObjectAlignment(self, sensorname):
      # sensor es un parámetro que contiene una cadena de caracteres con el nombre del sensor a configurar
      codigo = [250, self.sensores[sensorname].kID+1, 224, 0]
      # Se envia el codigo al XBus
      SendMessage(self.puerto, codigo)
      # En reply se almacenan los campos DATA y CS. Si hubiera algún fallo en la recepción, se detectaría.
      reply = self.__checkLenghtAndCS(codigo[2])    
      # DATA contiene la matriz de rotación en formato [a,b,c,d,e,f,g,h,i]. Cada elemento es un float.
      self.rot_matrix[sensorname], remaining = self.__readDataFromReply(reply,9,4,'>f')
      # remaining contendrá el resto del mensaje no transformado. En este caso, el CS.
      return self.rot_matrix[sensorname]
  
  def __readDataFromReply(self, reply, ndata, datalenght, dataformat):
      #reply: bytes object
      #    ndata: number of single data in reply
      #    datalenght: number of bytes that belongs to every single data
      #    dataformat: '>f', 'B',...
      msg = []
      for i in range(0,ndata*datalenght,datalenght):
          msg.append(struct.unpack(dataformat, reply[i:i+datalenght])[0])
      # data will contain the desired info and reply will contain the remaining bytes of the reply
      return msg, reply
      
  def __checkLenghtAndCS(self, MID):
      #Primero se leen 4 bytes para concer la longitud total del mensaje
      reply=self.puerto.read(4)
      reply=struct.unpack('BBBB',reply)
      if reply[2]!=225:
          raise ValueError ('Error en la secuencia de mensajes')
      #de momento no se ha detectado ningun error y se continua con la lectura
      #del resto del mensaje ack1(end)+1 bytes
      reply2=self.puerto.read(reply[-1]+1)
      #for tmp in reply2:
      #  reply=reply+struct.unpack('B',tmp)
      reply=reply+struct.unpack('B'*len(reply2),reply2)    
      checksum=sum(reply[1:])
      if checksum%256!=0:
          raise ValueError ('Error de checksum')
      return reply2

  def deleteOldestData(self, n=1):
      '''Elimina los primeros n datos de cada una de las señales contenidas
      en self.datos'''
      dimChecked = False      
      for signal in self.datos.keys():
          #Se comprueba si el número de datos a elminiar es menor que la dimensión
          #de las señales contenidas en self.datos
          if not dimChecked:
              dimChecked = True
              if len(datos[signal])<n:
                  raise ValueError ('El número de elementos a eliminar es superior a la dimensión de la señal')

          for i in range(0,n):
                  self.datos[signal].pop(0)

  #ESTAS FUNCIONES ESTABAN ORIGINALMENTE EN kinematic_chain.py. ---------------
      
  def getLatestData (self, n=1):
      '''Retorna los ultimos n datos contenidos en el self.datos
      y los retorna en un diccionario con el mismo formato.'''
      subdata = {}
      for signal in self.datos.keys():
          subdata[signal] = []
          for i in range(-n,0):
              self.lock.acquire() 
              subdata[signal].append(self.datos[signal][i])
              self.lock.release()
      return subdata       
        
  def getSortedData (self, t):
      '''Retorna los datos contenidos en los indices marcados por t[]
      y los retorna en un diccionario con el mismo formato.'''
      subdata = {}
      for signal in self.datos.keys():
          subdata[signal] = []
          for i in t:
              self.lock.acquire() 
              subdata[signal].append(self.datos[signal][i])
              self.lock.release()
      return subdata 

  def getQuaternionsFromData (self, subdata, mean=False):
      ''' 'subdata' will contain the whole data and 'mean' parameter indicates whether the data used
      for calculating the Quaternion is:
             - a single value -> mean = False
             - the average of all the values -> mean = True'''    
      quat = {}
      sufix = ['_q0', '_q1', '_q2', '_q3']
      keys = list(self.sensores.keys())
      nquat = len(subdata[keys[0]+sufix[0]])
      
      # Checking signals in subdata
      
      for name in self.sensores:
          quat[name] = [] #---ESTO ES PARA INICIALIZAR EL DICCIONARIO Y QUE CONTENGA LAS CLAVES
          for suf in sufix:
              if not name+suf in subdata.keys():
                  raise ValueError ('Signal not found in data dictionary. Operation aborted.')              
          
      if mean:
          for name in self.sensores:
              q = []
              for suf in sufix:
                  avg = sum(subdata[name+suf])/len(subdata[name+suf])
                  q.append(avg)
              quat[name]=Quaternion((q[0],q[1],q[2],q[3]))
          return quat
          
      else:
          for i in range(0,nquat):
              for name in self.sensores:
                  q = []
                  for suf in sufix:
                      q.append(subdata[name+suf][i])
                  q = Quaternion((q[0],q[1],q[2],q[3]))
                  quat[name].append(q)
          return quat 
  #----------------------------------------------------------------------------

if __name__=='__main__':   
    from QuatFuncs import *
    from kinematic_chain import *
    
    #Definición de la frecuencia de muestreo
    sampFreq = 100
    
    bus=simurdriver(freq=sampFreq,modo=1,buff=0.1)

    bus.addsensor('clavicula',sensor(323868,0))
    bus.addsensor('brazo',sensor(1323366,1))
    bus.addsensor('antebrazo',sensor(1323357,2))
    bus.addsensor('mano',sensor(1323356,3))       

    bus.gotoconfig()
    bus.configura()
    
    brazo = kinematic_chain(bus,['clavicula','brazo','antebrazo','mano'],[0.2,0.35,0.3,0.1],['hombro','codo','munyeca'])
    
    bus.gotomeasurement()

    time.sleep(0.5)
    bus.gotoconfig()
    
    

        

    
    

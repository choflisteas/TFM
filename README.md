# TFM
Proyecto fin de master

  - mtdef.py y mtdevice.py son los drivers del sensor Xsens MTi. Están escritos para Python 2.

  - SerialPortSensor.py
      Es una clase que permite capturar datos de una conexión serie. El dato va intercalado entre dos caracteres definidos.
  
  - kinematic_chain.py
      Es una clase que permite crear objetos que simulan cadenas cinemáticas. Tiene un método para realizar giros sobre los
      elabones de la misma.
  
  - lightSensorMatrix.py
      Es una clase que permite obtener los datos de una trama recibida por una conexión serie. Se ha creado para emular una
      IMU a partir de unos fotorresistores y un Arduino UNO.
  
  - Animation3D.py
      Programa que usa la clase lightSensorMatrix.py con el objetivo de plotear dos eslabones de una cadena cinemática.
      
  - Plot3D.py
      Programa realizado previamente para implementar la clase kinematic_chain.py.
      
      
  

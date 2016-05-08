# -*- coding: utf-8 -*-
"""
Created on Fri May  6 12:44:07 2016

@author: gonzalo
"""

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
import mathutils as mu
import math

class kinematic_chain:
    def __init__(self,modules):
        # Se comprueba si las dimensiones de los arrays pasados son correctos.
        self.datavalid=False
        if len(modules)<1:
            print("Introduzca una matriz de módulos válida.")
            return False
        else:
            self.mod=modules
            self.nframes = len(modules)
            self.set_origin()
            self.datavalid=True
                        
    def rotate_frames(self, q):
        if len(q)!=self.nframes:
            print("El número de quaternions no se corresponde con el número de eslabones:")
            return False
        else:
            v = []
            v_ = []
            coordinates = []            
            for i in range (0,self.nframes):
                v.append(mu.Quaternion((0.0, 0.0, 0.0, 1.0))) #aquí, en su momento, es donde tendremos que definir los eslabones
                v_.append(q[i]*v[i]*q[i].conjugated())
                if i==0:
                    coordinates.append(((self.origin[0], self.origin[0]+v_[i][1]*self.mod[i]),
                                        (self.origin[1], self.origin[1]+v_[i][2]*self.mod[i]),
                                        (self.origin[2], self.origin[2]+v_[i][3]*self.mod[i])))
                else:
                    coordinates.append(((coordinates[i-1][0][1],coordinates[i-1][0][1]+v_[i][1]*self.mod[i]),
                                        (coordinates[i-1][1][1],coordinates[i-1][1][1]+v_[i][2]*self.mod[i]),
                                        (coordinates[i-1][2][1],coordinates[i-1][2][1]+v_[i][3]*self.mod[i])))
            return coordinates
    
    
    def set_origin(self, x0=0, y0=0, z0=0):
        self.origin = (x0, y0, z0)
        
# Ejemplo de uso, generando unos cadena de 3 eslabones y realizando el giro de los mismos sobre un solo eje.            
if __name__ == "__main__":
    brazo=kinematic_chain((2,1.5,0.5))
    a = []
    a.append(mu.Quaternion((1.0,0.0,0.0),math.radians(30)))            
    a.append(mu.Quaternion((1.0,0.0,0.0),math.radians(45)))
    a.append(mu.Quaternion((0.0,1.0,0.0),math.radians(60)))
    
    res=brazo.rotate_frames(a)
    
    fig = plt.figure()
    ax = p3.Axes3D(fig)
    
    ax.set_xlim3d([-1.0, 1.0])
    ax.set_xlabel('X')
    ax.set_ylim3d([-2.5, 0.5])
    ax.set_ylabel('Y')
    ax.set_zlim3d([0.0, 2.0])
    ax.set_zlabel('Z')
    ax.set_title('Brazo')
    
    for i in range(0,brazo.nframes):
        ax.plot3D(res[i][0], res[i][1], res[i][2])
    plt.show()
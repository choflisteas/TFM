import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
import lightsensormatrix


import mathutils
import math

def update_vector(i):
    global v
    
    # Borramos los anterior ejes y se dibujan de nuevo. (TARDA DEMASIADO)
    plt.cla()
    ax.set_xlim3d([-1.0, 1.0])
    ax.set_xlabel('X')
    ax.set_ylim3d([-0.5, 0.5])
    ax.set_ylabel('Y')
    ax.set_zlim3d([0.0, 2.0])
    ax.set_zlabel('Z')
    ax.set_title('3D Test')
    
    # Creación de los quaterniones que van a provocar el giro
    q=[]    
    q.append(mathutils.Quaternion((1.0,0.0,0.0), math.radians(90-arduino.getSingleData()[0])))
    q.append(mathutils.Quaternion((1.0,0.0,0.0), math.radians(90-arduino.getSingleData()[1])))
    
    #
    v_= []    
    v_.append(q[0]*v[0]*q[0].conjugated())
    ax.plot3D((0,v_[0][1]),(0,v_[0][2]),(0,v_[0][3]),'o-', markersize=1, markerfacecolor="orange", linewidth = 1, color='blue')   
    v_.append(q[1]*v[1]*q[1].conjugated())
    ax.plot3D((v_[0][1],v_[0][1]+v_[1][1]),(v_[0][2],v_[0][2]+v_[1][2]),(v_[0][3],v_[0][3]+v_[1][3])
    ,'o-', markersize=1, markerfacecolor="orange", linewidth = 1, color='blue')

# Enlazamos los ejes a la figura
fig = plt.figure()
ax=fig.add_subplot(111, projection='3d')

# Creamos el objeto para obtener los datos
arduino=lightsensormatrix.lightsensormatrix()

# Definición del vector original
v = []
v.append(mathutils.Quaternion((0.0,0.0,0.0,1.0)))
v.append(mathutils.Quaternion((0.0,0.0,0.0,1.0)))

# Creación del objeto Animation
line_ani = animation.FuncAnimation(fig, update_vector, frames=1, interval=50, blit=False)

plt.show()
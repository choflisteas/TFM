import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation 

import mathutils
import math

fig = plt.figure()
ax = p3.Axes3D(fig)

origin = (0.0,0.0,0.0)

mod = []
ang = []
q = []
v = []
v_ = []
coordinates = []
colors=['g', 'r', 'b', 'w', 'y']

for i in range (0,5):
    mod.append(1+i*1.5)
    ang.append(i*15)
    q.append(mathutils.Quaternion((1.0, 0.0, 0.0),math.radians(ang[i])))
    v.append(mathutils.Quaternion((0.0, 0.0, 0.0, 1.0)))
    v_.append(q[i]*v[i]*q[i].conjugated())
    if i==0:
        coordinates.append(((origin[0],v_[i][1]*mod[i]), (origin[1],v_[i][2]*mod[i]), (origin[2],v_[i][3]*mod[i])))
    else:
        coordinates.append(((coordinates[i-1][0][1],coordinates[i-1][0][1]+v_[i][1]*mod[i]),
                            (coordinates[i-1][1][1],coordinates[i-1][1][1]+v_[i][2]*mod[i]),
                            (coordinates[i-1][2][1],coordinates[i-1][2][1]+v_[i][3]*mod[i])))

    ax.plot3D(coordinates[i][0], coordinates[i][1], coordinates[i][2], color=colors[i])
    
plt.show()








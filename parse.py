# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from scipy.spatial.transform import Rotation as R

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

raw = np.loadtxt('imu-logs.txt',
                 dtype={'names': ('ax', 'ay', 'az', 'gx',                                  'gy', 'gz'), 'formats': ('i4', 'i4', 'i4', 'i4', 'i4', 'i4')}, delimiter=',')

gyro = np.array(list(map(lambda r: [r[3], r[4], r[5]], raw)))
gyro = gyro  * (2000.0/32768.0) * 0.0174532925199 * 0.01

rotations = R.from_euler('xyz', gyro)

vectors = np.zeros((gyro[:,0].size, 3))
vectors[0] = [1, 0, 0]
for i in range(1, gyro[:,0].size) :
    vectors[i] = rotations[i].apply(vectors[i-1])

z = np.zeros(gyro[:,0].size)
def getArrow(i):
    return 0, 0, 0, gyro[i,0:2]



fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))

ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_zlim(-2, 2)

#ax.quiver(z, z, z, gyro[:,0], gyro[:,1], gyro[:,2])
#q = ax.quiver(z, z, z, vectors[:,0], vectors[:,1], vectors[:,2])

q = ax.quiver(0, 0, 0, -1, 0, 0)

def update(frame):
    global q
    q.remove()
    q = ax.quiver(0, 0, 0, frame[0], frame[1], frame[2])


ani = animation.FuncAnimation(fig, update, vectors, interval=1)

plt.show()
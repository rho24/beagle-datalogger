# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from scipy.spatial.transform import Rotation as R

import sys
import fileinput
from functools import reduce
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

def main():

    fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
    plt.ion()
    plt.show()

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-2, 2)
    xLabel = ax.set_xlabel('X')
    yLabel = ax.set_ylabel('Y')
    zLabel = ax.set_zlabel('Z')

    started = False
    for line in fileinput.input():
        if line.rstrip() == 'starting': started = True
        elif not started: continue
        else:
            d = line.rstrip().split(',')
            update(d,ax)

    sys.exit()

def rawToDv(f: float):
    return f * 9.80665*8.0/32768.0

def rawToDr(f: float):
    return f * (2000.0/32768.0) * 0.0174532925199

def update(d, ax):
    dt = float(d[0]) * 1e-9
    dv = list(map(compose(float, rawToDv), d[1:4]))
    dr = list(map(compose(float, rawToDr), d[4:7]))
    ax.quiver(0,0,0,*dv)
    plt.draw()
    plt.pause(0.001)
    print(dt)

def compose(*fargs):
    def inner(arg):
        if not arg:
            raise ValueError("Invalid argument")
        if not all([callable(f) for f in fargs]):
            raise TypeError("Function is not callable")
        return reduce(lambda arg, func: func(arg), fargs, arg)
    return inner

if __name__ == '__main__': main()






raw = np.loadtxt('imu-data2.txt',
                 dtype={'names': ('ax', 'ay', 'az', 'gx',                                  'gy', 'gz'), 'formats': ('i4', 'i4', 'i4', 'i4', 'i4', 'i4')}, delimiter=',')

dt = 0.0125

gyro = np.array(list(map(lambda r: [r[3], r[4], r[5]], raw)))
gyro = gyro  * (2000.0/32768.0) * 0.0174532925199 * dt

sampleCount = gyro[:,0].size

rotations = R.from_euler('xyz', gyro)
vectors = np.zeros((sampleCount, 3))
vectors[0] = [1, 0, 0]
for i in range(1, sampleCount) :
    vectors[i] = rotations[i].apply(vectors[i-1])


accRotations = np.empty(sampleCount, dtype=object)
accRotations[0] = R.from_euler('zyx', [0, 0, 0])
for i in range(1, sampleCount) :
    accRotations[i] = accRotations[i-1] * rotations[i]


arrows = np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
def getArrows(i):
    a = [0, 0, 0], [0, 0, 0], [0, 0, 0], * accRotations[i].apply(arrows).tolist()
    return a

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))

ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_zlim(-2, 2)
xLabel = ax.set_xlabel('X')
yLabel = ax.set_ylabel('Y')
zLabel = ax.set_zlabel('Z')

#ax.quiver(z, z, z, gyro[:,0], gyro[:,1], gyro[:,2])
#q = ax.quiver(z, z, z, vectors[:,0], vectors[:,1], vectors[:,2])

q = ax.quiver(*getArrows(0))

def update(i):
    global q
    q.remove()
    q = ax.quiver(*getArrows(i), colors=['r', 'g', 'b'])
    r = accRotations[i].as_euler('xyz')
    ax.set_xlabel('X - {:06.3f}'.format(r[0]))
    ax.set_ylabel('Y - {:06.3f}'.format(r[1]))
    ax.set_zlabel('Z - {:06.3f}'.format(r[2]))

ani = animation.FuncAnimation(fig, update, sampleCount, interval=3)

plt.show()
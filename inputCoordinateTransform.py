"""
@Author:    Pramod Kumar Yadav
@email:     
@Date:      May, 2023
@Credit:    
@status:    development
@Version:   python3
@Function:  Script to run coordinate transformation
"""

import sys

PYTHONTOOLSDIR = r'K:\Users\pramod.kumar\Sandbox\pythonProjects'
sys.path.append(PYTHONTOOLSDIR)

import coordinate_mapper as cm

# ******* Input Transformation Setting *******#
order = 'TXYZ'  # Order/sequence of transformation
Tra = [1, 1, 1]  # Translation in x,y,z direction
a_x = 180  # Rotation along x axis
a_y = 45  # Rotation along y axis
a_z = 90  # Rotation along z axis
typ = 1  # 1: Coordinate Transformation, 2:Point Transformation

# ******* Input List of Coordinates *******#
ini_coord = [
    [5.2345, 6, 7],
    [0.0024, -4375.8124, 471.8651],
    [4, 6, 7],
    [1, 2, 3],
    [7, 8, 9],
    # [4, 6, 7],
    # [1, 2, 3],
    # [7, 8, 9],
]

point_in = []
point_out = []
for p in ini_coord:
    print("Initial Coordinate:\t", str(p))
    point_f = ['%.5f' % elem for elem in p]
    # point_f=["{0:06.5f}".format(elem) for elem in p]
#     print("Initial Coordinate:\t", point_f)
#     point_in.append(point_f)
    point_in.append(p)
    pout = cm.coordinateTransform(order, Tra, a_x, a_y, a_z, p, typ)
    print("Coordinate After Transformations:\t", str(pout))
    pout_round = [round(elem, 4) for elem in pout]
    point_out.append(pout_round)

with open('OutputCoordTransf.txt', 'w') as f:
    f.write("Order of transformation:\t{}\n".format(order))
    f.write("Translation in x, y,z:\t{}\n".format(Tra))
    f.write("Rotation along x:\t{}\n".format(a_x))
    f.write("Rotation along y:\t{}\n".format(a_y))
    f.write("Rotation along z:\t{}\n".format(a_z))
    if typ == 1:
        f.write("Type of transformation:\tCoordinate Transformation\n\n")
    elif typ == 2:
        f.write("Type of transformation:\tPoint Transformation\n\n")
    f.write("------------------\t\t\t\t\t\t\t\t\t-------------------------------\n")
    f.write("Initial Coordinate\t\t\t\t\t\t\t\t\tCoordinate After Transformation\n")
    f.write("------------------\t\t\t\t\t\t\t\t\t-------------------------------\n")

    for i in range(len(ini_coord)):
        f.write("{}{}\n".format(str(point_in[i]).ljust(52), point_out[i]))

print("Data written as text file\n")
# input("Enter to Exit")

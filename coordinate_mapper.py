"""
@Author:    Pramod Kumar Yadav
@email:     pkyadav01234@gmail.com
@Date:      April, 2023
@Credit:    
@status:    development
@PythonVersion: python3

"""

# *********** importing all the required library***********
import numpy as np
import pandas as pd
# *********** Function for coordinate transform ***********
def orderMult(order, Tr, Rx, Ry, Rz, typ):
    """Function to perform multiplication in required order or sequence

    Args:
        order ([str]): [order of transformation and rotation]
        Tr ([list]): [Translation of a coordinate or point]
        Rx ([float]): [anti-clockwise rotation along the x-axis]
        Ry ([float]): [anti-clockwise rotation along the y-axis]
        Rz ([float]): [anti-clockwise rotation along the z-axis]
        typ ([int]): [1 & 2 (1: for coordinate transformation, 2: for point transformation with fix coordinate)]

    Returns:
        [matrix]: [Transformation matrix]
    """
    MatDict = {char: ord(char) for char in order}
    MatDict['T'] = Tr
    MatDict['X'] = Rx
    MatDict['Y'] = Ry
    MatDict['Z'] = Rz
    keys = list(MatDict.keys())
    val1 = MatDict[keys[0]]
    val2 = MatDict[keys[1]]
    val3 = MatDict[keys[2]]
    val4 = MatDict[keys[3]]

    if typ == 1:
        RotMat = val4 @ val3 @ val2 @ val1
        # RotMat=np.matmul(np.matmul(val4, val3), np.matmul(val2, val1))
        # RotMat=np.matmul(val2, val3)
    elif typ == 2:
        RotMat = val1 @ val2 @ val3 @ val4
        # RotMat=np.matmul(np.matmul(val1, val2), np.matmul(val3, val4))
    return RotMat


def coordinateTransform(order='TXYZ', Tra=[0, 0, 0], a_x=0, a_y=0, a_z=0, point=[0, 0, 0], typ=1):
    """Function to perform coordinate transformation(typ-1) or point transformation(typ-2)
            typ=1: Coordinate changing but point fix
            typ-2: Point changing with respect to fix coordinate

    Args:
        order (str): [order of transformation and rotation]. Defaults to 'TXYZ'.
        Tra (list):  [Translation of a coordinate or point]. Defaults to [0,0,0].
        a_x (float):   [anti-clockwise rotation along the x-axis]. Defaults to 0.
        a_y (float):   [anti-clockwise rotation along the y-axis]. Defaults to 0.
        a_z (float):   [anti-clockwise rotation along the z-axis]. Defaults to 0.
        point (list): [point to be transformed]. Defaults to [0,0,0].
        typ (int, optional): [1 & 2 (1: for coordinate transformation, 2: for point transformation with fix coordinate)].Defaults to 1.

    Returns:
        [List]: point coordinate after transformation
    """

    Xc = np.matrix([[point[0]], [point[1]], [point[2]], [1]])
    theta_x = np.deg2rad(a_x)
    theta_y = np.deg2rad(a_y)
    theta_z = np.deg2rad(a_z)

    if typ == 2:
        tx = Tra[0]
        ty = Tra[1]
        tz = Tra[2]
    elif typ == 1:
        tx = Tra[0] * -1
        ty = Tra[1] * -1
        tz = Tra[2] * -1
        theta_x = np.deg2rad(a_x) * -1
        theta_y = np.deg2rad(a_y) * -1
        theta_z = np.deg2rad(a_z) * -1
    else:
        print("Enter typ=1: for coordinate transformation & typ=2: for point transformation")

    Tr = np.matrix([[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]])
    Rx = np.matrix([[1, 0, 0, 0], [0, np.cos(theta_x), -np.sin(theta_x), 0], [0, np.sin(theta_x), np.cos(theta_x), 0],
                    [0, 0, 0, 1]])
    Ry = np.matrix([[np.cos(theta_y), 0, np.sin(theta_y), 0], [0, 1, 0, 0], [-np.sin(theta_y), 0, np.cos(theta_y), 0],
                    [0, 0, 0, 1]])
    Rz = np.matrix([[np.cos(theta_z), -np.sin(theta_z), 0, 0], [np.sin(theta_z), np.cos(theta_z), 0, 0], [0, 0, 1, 0],
                    [0, 0, 0, 1]])

    RotMat = orderMult(order, Tr, Rx, Ry, Rz, typ)
    Xf = RotMat @ Xc

    Xf = Xf[0:3].tolist()
    return [Xf[0][0], Xf[1][0], Xf[2][0]]

import numpy as np

def dcm2rotation(R, sequence="XYZ"):
    
    """
    Converts a Direction Cosine Matrix (DCM) to Euler angles.

    Parameters:
        R (numpy.ndarray): 3x3 rotation matrix representing the DCM.
        sequence (str): String specifying the desired rotation sequence. Defaults to 'TXYZ'.
                        

    Returns:
        tuple: Tuple of three Euler angles (theta1, theta2, theta3) in radians.

    Raises:
        TypeError: If an invalid sequence is provided. Implemented for "XYZ","ZXY","YZX","ZYX","YXZ","XZY" only
        
    Notes:
        - The function uses the numpy library for array operations and trigonometric functions.

    """
    
    available = ["XYZ","ZXY","YZX","ZYX","YXZ","XZY"] 
    avail_posi = ["XYZ","ZXY","YZX"]
    
    if sequence in available:
        i= -1 if sequence in avail_posi else 1
        
        MatDict = {char: ord(char) for char in sequence}

        MatDict['X'] = 0
        MatDict['Y'] = 1
        MatDict['Z'] = 2

        keys = list(MatDict.keys())

        a = MatDict[keys[0]]
        b = MatDict[keys[1]]
        c = MatDict[keys[2]] 

        R1 = np.arctan2(i*R[c, b], R[c, c])
        R2 = np.arcsin(i*-R[c, a])
        R3 = np.arctan2(i*R[b, a], R[a, a])

        return R1, R2, R3
    else:
        raise TypeError('Sorry,Implemented for this sequence only "XYZ","ZXY","YZX","ZYX","YXZ","XZY"')
        
if __name__ == '__main__':

    lmn= np.array([[0.5,0.090524305,0.861281226],
               [-0.06041,0.995745059,-0.069586667],
               [-0.86392,-0.017237422,0.503341182]])
              
    sequence = 'XYZ'
    angles = dcm2rotation(lmn, sequence)
    print(np.degrees(angles)) 
    input()

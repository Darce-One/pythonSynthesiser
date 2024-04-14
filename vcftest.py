import math
from typing import List
import numpy as np
from numpy.fft import fft
from numpy.linalg import inv
import matplotlib.pyplot as plt

def main():
    Sr = 44100
    Tf = 0.2
    f0 = 700
    r = 0.8

    nf = math.floor(Sr * Tf)
    k = 1/Sr
    om0 = 2*math.pi*f0

    eye = np.eye(4)
    matrix_A = om0 * np.array([[-1,0,0,-4*r],[1,-1,0,0],[0,1,-1,0],[0,0,1,-1]])
    # print(matrix_A)
    vector_b = om0 * np.array([1,0,0,0]).reshape(4,1)
    # print(vector_b)
    vector_c = np.array([1,0,0,0]).reshape(1,4)
    # print(vector_c)
    matrix_B = eye - k*matrix_A
    # print(matrix_B)
    matrix_B_inv = np.linalg.inv(matrix_B)

    vector_x = np.array([0,0,0,0], dtype=np.float32).reshape(4,1)
    # print(vector_x)

    vector_y = np.zeros((nf,1))

    vector_u = np.zeros((nf,1))
    vector_u[0] = 1
    # print(vector_u)

    tvec = np.linspace(0, nf, nf).reshape(nf,1)*k
    fvec = np.linspace(0, nf, nf).reshape(nf,1)*Sr/nf
    svec = 2*np.pi*1j*fvec

    hs = np.zeros((nf,1))

    for i in range(nf):
        # vector_x = np.linalg.solve(matrix_B, (vector_x + k*vector_b*vector_u[i]))
        vector_x = matrix_B_inv @ (vector_x + k*vector_b*vector_u[i])
        vector_y[i] = vector_c @ vector_x
        hs[i] = vector_c @ np.linalg.inv(svec[i]*eye - matrix_A) @ vector_b

    vector_Y = fft(vector_y)
    plt.loglog(fvec, np.abs(vector_Y))
    plt.loglog(fvec, np.abs(hs))
    plt.xlim(20,20000)
    plt.show()

if __name__ == "__main__":
    main()

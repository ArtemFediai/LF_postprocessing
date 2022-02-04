'''
from the trajectory file, takes the last frame and computed coulomb interactions
'''
import numpy as np


global EPS_0, EPS_R, Q0, ANGSTROME
EPS_0 = 8.8541878128E-12  # [SI]
EPS_R = 4
Q0 = 1.6E-19  # [Si]
ANGSTROME = 1E-10
PATH_TO_TRAJECTORY = \
    '/home/artem/Desktop/1E5_0_0_no_exper/dop_0/r_0/r_0_manual/results/experiments/trajectories/trajec_0.xyz'


with open(PATH_TO_TRAJECTORY) as fid:
    first_line = fid.readline()  # 1401
    num_sites = int(first_line)
    num_particles = num_sites // 3
    next_line = num_sites
    frame_number = 0
    while next_line:
        second_line = fid.readline()
        print(second_line)
        #
        idx_C, idx_N, idx_O = 0, 0, 0
        XYZ_C = np.zeros((num_particles, 3))
        XYZ_N = np.zeros((num_particles, 3))
        XYZ_O = np.zeros((num_particles, 3))
        #
        for i in range(num_sites):
            line = fid.readline()
            letter = line.split()[0]
            xyz = [float(i) for i in line.split()[1:4]]
            if letter == 'C':
                XYZ_C[idx_C, :] = xyz
                idx_C += 1
            if letter == 'N':
                XYZ_N[idx_N, :] = xyz
                idx_N += 1
            if letter == 'O':
                XYZ_O[idx_O, :] = xyz
                idx_O += 1
        frame_number = frame_number + 1
        print(f'frame number is: {frame_number}')
        next_line = fid.readline()
        print(f'next line is: {next_line}')


# last frame remains


def coulomb_low(r, q1=1, q2=-1):
    global Q0, EPS_0, EPS_R
    '''

    :param r: distance in A!
    :param q1: in in Q0
    :param q2: in Q0
    :return: V_C in eV
    '''

    # return q1*q2*Q0*Q0*(4*np.pi*EPS_0*EPS_R*(r*ANGSTROME)**2)**(-1)  # Joule
    return q1*q2*Q0*(4*np.pi*EPS_0*EPS_R*r*ANGSTROME)**(-1)  # eV

coulomb_low(10)

print(f'This is the h-e Coulomb interaction at 1 nm and eps=4: {coulomb_low(10)}. '
      f'It should be close to -0.36 eV, then the function is correct')

# N-O
r_NO = []
for n1 in range(num_particles):
    for n2 in range(num_particles):
            r = np.linalg.norm(XYZ_N[n1, :] - XYZ_O[n2, :])
            r_NO.append(r)

v_NO = [coulomb_low(r, q1=1, q2=-1) for r in r_NO]
V_NO = np.sum(v_NO)
# N-N
r_NN = []
for n1 in range(num_particles):
    for n2 in range(num_particles):
        if n1 > n2:
            r = np.linalg.norm(XYZ_N[n1, :] - XYZ_N[n2, :])
            r_NN.append(r)

v_NN = [coulomb_low(r, q1=1, q2=1) for r in r_NN]
V_NN = np.sum(v_NN)

# O-O
r_OO = []
for n1 in range(num_particles):
    for n2 in range(num_particles):
        if n1 > n2:
            r = np.linalg.norm(XYZ_O[n1, :] - XYZ_O[n2, :])
            r_OO.append(r)

v_OO = [coulomb_low(r, q1=-1, q2=-1) for r in r_OO]
V_OO = np.sum(v_OO)


total_v = V_OO + V_NN + V_NO

print(f'total VC is {total_v} [eV]')

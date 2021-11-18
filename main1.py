import os

import numpy as np
import yaml
from lightforge.lightforge import main as main_lf
# from lightforge.lightforge import prep_signal_handlers

# try:
#     import mpi4py
#     mpi4py.rc.recv_mprobe = False
#     from mpi4py import MPI
# except ImportError as e:
#     pass

#/home/hk-project-virtmat/bh5670/QP_installation_V4/nanomatch/V4/lightforge/lightforge/lightforge.py

def consts():
  global a, SETTINGS_FILENAME, DOP, N_R, N_DOP, N_CPUs  
  SETTINGS_FILENAME = 'settings_dop'
  N = 1
  N_DOP = 10
  DOP = np.array(np.logspace(np.log10(1E-2), np.log10(2E-1), N_DOP))
  N_R = 30  # try not using this!
  N_CPUs = 1  # TODO if the replica is inside, change to that number

  # a for each doping
  Np_I_wish = 500
  a = np.array((Np_I_wish / DOP) ** (1.0 / 3.0), dtype=np.int)
  for i in range(len(a)):
      if a[i] < 15:
          a[i] = 15.0


def run_kmc(i_dop, i_r):
    consts()
    #print('I am here 1')
    SETTINGS_FILENAME = 'settings_dop'
    with open(SETTINGS_FILENAME, 'r') as fid:
        settings = yaml.load(fid)
    dir_name = f'dop_{i_dop}/r_{i_r}'
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    ###########
    settings["layers"][0]["thickness"] = np.int(a[i_dop])
    settings["morphology_width"] = np.int(a[i_dop])
    settings['layers'][0]['molecule_species'][0]['concentration'] = float(1.0 - DOP[i_dop])
    settings['layers'][0]['molecule_species'][1]['concentration'] = float(DOP[i_dop])
    ###########

    with open(f'{dir_name}/{SETTINGS_FILENAME}', 'w') as fid:
        yaml.dump(settings, fid)
    os.chdir(dir_name)
    #print("I am here 2")
    # os.system(f'lightforge.py -{SETTINGS_FILENAME}')
    # prep_signal_handlers()
    main_lf(load=False, replay=None,
         settings_file=SETTINGS_FILENAME,
         morphology_only=False,
         num_iterations=None,
         collect_current_density=False,
         collect_density_plots_only=False,
         Tools=None,
         analysis_autorun=False)

def main():
    consts()
    num_part_after = np.array(a * a * a * DOP, dtype=np.float)
    np.savetxt('a.txt', a)
    np.savetxt('doping.txt', DOP, fmt='%2.3E')
    np.savetxt('n_r_n_dop.txt', [N_R, N_DOP], fmt='%i')
    with open("joblist", 'w') as fid:
        for i_dop in range(0, len(DOP)):
            for i_r in range(0, N_R):
                fid.write("%i main1.run_kmc %i %i\n" % (N_CPUs, i_dop, i_r))
    print('num of doping points = %s' % N_DOP)
    print('a = %s' % a)
    print('actual dopant number =  %s' % np.array(num_part_after, dtype=np.int))
    print('doping = %s' % DOP)
    # print('n_cpus_vs_dop = %s' % n_cpu_vs_dop)
    # print('N_CPUS = %s' % N_CPUS)
    # print('number of nodes = %s' % (N_CPUS // 20))
    print(f'num replicas = {N_R}')

if __name__ == '__main__':
    main()



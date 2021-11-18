import os
import numpy as np
import yaml
import inspect

global a, SETTINGS_FILENAME, DOP, N_R, N_DOP, N_CPUs, YAML_FILENAME
#if I want sh file to be generated -->
GENERATE_SH_FILE = True
#<-- if I want sh file to be generated

SETTINGS_FILENAME = 'settings_dop'  # LF settings file
YAML_FILENAME = f'{__file__.split(".")[0]}.yaml'  #
N_DOP = 10
N_R = 30  # try not using this!
N_CPUs = 1
DOP = np.array(np.logspace(np.log10(1E-2), np.log10(2E-1), N_DOP))
Np_I_wish = 500  # number of dopants I wish
a = np.array((Np_I_wish / DOP) ** (1.0 / 3.0), dtype=np.int)
for i in range(len(a)):
    if a[i] < 15:
        a[i] = 15.0


def generate_sh_file(file_name = 'run_lf_from_threadfarm.sh', 
                     nodes=1, 
                     time='0-24:00:00', 
                     partition='accelerated',
                     email='artem.fedyay@gmail.com',
                     NANOMATCH='/home/hk-project-virtmat/bh5670/QP_installation_V4/nanomatch',
                     NANOVER='V4',
                     THREADFARM='/home/hk-project-virtmat/bh5670/QP_installation_V4/nanomatch/V4/QuantumPatch/mpithreadfarm/bin',
                     ):
    """
    writes sh file to be run at horeka
    :param file_name: sh file name tp generate
    :param nodes: number nodes to use
    :param time: sim time XX-XX:XX:XX
    :param partition:
    :param email:
    :param NANOMATCH: path to nm env
    :param NANOVER: version of it
    :param THREADFARM: path to threadfarm
    :return:
    """
    with open(file_name, 'a') as sh_file:
        sh_file.write(f'#!/bin/bash'
                      f'\n'
                      f'# SBATCH --nodes={nodes}'
                      f'\n'
                      f'# SBATCH --time={time}'
                      f'\n'
                      f'# SBATCH --mem-per-cpu=2000mb'
                      f'\n'
                      f'# SBATCH --job-name=Lightforge'
                      f'\n'
                      f'# SBATCH --partition={partition}'
                      f'\n'
                      f'# SBATCH --mail-type=ALL'
                      f'\n'
                      f'# SBATCH --mail-user={email}'
                      f'\n'
                      f'# SBATCH --error out_%j.err'
                      f'\n'
                      f'# SBATCH --output out_%j.out'
                      f'\n'
                      f'\n'
                      f'export NANOMATCH={NANOMATCH}'
                      f'\n'
                      f'export NANOVER={NANOVER}'
                      f'\n'
                      f'source $NANOMATCH/$NANOVER/configs/lightforge.config'
                      f'\n'
                      f'\n'
                      f'export THREADFARM={THREADFARM}'
                      f'\n'
                      f'export THREADFARMBIN={THREADFARM}/bin'
                      f'\n'
                      f'export PYTHONPATH=$THREADFARM:$PYTHONPATH'
                      f'\n'
                      f'export PATH=$THREADFARM:$PATH'
                      f'\n'
                      f'module load compiler/gnu/11'
                      f'\n'  # <-- load additional module. Needed?
                      f'cd SLURM_SUBMIT_DIR'
                      f'\n'
                      f'ulimit -s unlimited'
                      f'\n'
                      f'export KMP_AFFINITY=none'
                      f'\n'
                      f'\n'
                      f'MPI_PATH/bin/mpirun --bind-to none --mca btl self,vader,tcp python $THREADFARMBIN/thread_mpi_exe.py joblist'
                      f'\n')


def run_kmc(i_dop, i_r):
    """
    function that spawns lightforge. intended to be run from threadfarm
    :param i_dop:
    :param i_r:
    :return:
    """
    from lightforge.lightforge import main as main_lf
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
    main_lf(load=False, replay=None,
            settings_file=SETTINGS_FILENAME,
            morphology_only=False,
            num_iterations=None,
            collect_current_density=False,
            collect_density_plots_only=False,
            Tools=None,
            analysis_autorun=False)


def lf_wrapper():
    """
    creates joblist for threadfarm
    save simulation "hyper"parameters into __name__.yaml
    :return:
    """
    name_of_this_fun = inspect.stack()[0][3]

    num_part_after = np.array(a * a * a * DOP, dtype=np.float)
    with open("joblist", 'w') as fid:
        for i_dop in range(0, len(DOP)):
            for i_r in range(0, N_R):
                fid.write(f"%i {name_of_this_fun}.run_kmc %i %i\n" % (N_CPUs, i_dop, i_r))

    main_settings_dict = {'system size': a.tolist(),  # nm
                          'number of doping points': N_DOP,
                          'number of replicas': N_R,
                          'doping molar rate': DOP.tolist(),  # 0 < DOP < 1
                          'actual dopants number': np.array(num_part_after, dtype=np.int).tolist(),
                          'number of simulations': N_R*N_DOP}
    with open(YAML_FILENAME, 'w') as fid:
        yaml.dump(data=main_settings_dict, stream=fid)
    print(f"\nhyper-settings saved as {YAML_FILENAME}")

    print("\nSettings hyperparameters:")
    for key, value in main_settings_dict.items():
        print(f'{key} \t-->\t {value}')

    if GENERATE_SH_FILE:
        generate_sh_file()


if __name__ == '__main__':
    lf_wrapper()  # <-- this must be a function to create jobfile

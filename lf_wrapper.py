import os
import numpy as np
import pandas as pd
import yaml
import inspect

global a, SETTINGS_FILENAME, DOP, N_R, N_DOP, N_CPUs, YAML_FILENAME, BASE_PATH
# if I want sh file to be generated -->
GENERATE_SH_FILE = True  # sh file for SLURM (horeka)
# <-- if I want sh file to be generated

BASE_PATH = '/home/artem/Desktop/LF_data_from_hk/dis_0_1_node'
SETTINGS_FILENAME = 'settings_dop'  # LF settings file
YAML_FILENAME = f'{__file__.split(".")[0]}.yaml'  # yaml file with LF hyperparameters that will be generated
N_DOP = 10  # number of doping points
N_R = 30  # try not using this!
N_CPUs = 1  # number of cpus used per replica. 1 if enough RAM
DOP = np.array(np.logspace(np.log10(1E-2), np.log10(2E-1), N_DOP))  # list of doping values
Np_I_wish = 500  # number of dopants I wish in a replica
a = np.array((Np_I_wish / DOP) ** (1.0 / 3.0), dtype=np.int)  # size of the system. system is a cube, volume = a * a * a
for i in range(len(a)):
    if a[i] < 15:
        a[i] = 15.0  # system size will not be < 15 nm


def generate_sh_file(file_name='run_lf_from_threadfarm.sh',
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


def write_joblist():
    """
    creates joblist for threadfarm and writes it down
    save simulation "hyper"parameters into __name__.yaml
    :return:
    """
    # name_of_this_fun = inspect.stack()[0][3]  # returns name of the current function

    num_part_after = np.array(a * a * a * DOP, dtype=np.float)
    with open("joblist", 'w') as fid:
        for i_dop in range(0, len(DOP)):
            for i_r in range(0, N_R):
                fid.write(f"%i {__file__.split('.')[0].split('/')[-1]}.run_kmc %i %i\n" % (N_CPUs, i_dop, i_r))

    main_settings_dict = {'system size': a.tolist(),  # nm
                          'number of doping points': N_DOP,
                          'number of replicas': N_R,
                          'doping molar rate': DOP.tolist(),  # 0 < DOP < 1
                          'actual dopants number': np.array(num_part_after, dtype=np.int).tolist(),
                          'number of simulations': N_R * N_DOP}
    with open(YAML_FILENAME, 'w') as fid:
        yaml.dump(data=main_settings_dict, stream=fid)
    print(f"\nhyper-settings saved as {YAML_FILENAME}")

    print("\nSettings hyperparameters:")
    for key, value in main_settings_dict.items():
        print(f'{key} \t-->\t {value}')

    if GENERATE_SH_FILE:
        generate_sh_file()


def load_all_dipoles(path=BASE_PATH,
                     path_to_dipole='results/experiments/trajectories',
                     total_dipole_time_fname='trajec_0.dip_t',
                     dipole_xyz_fname='trajec_0.dip_vec',
                     test=True
                     ):
    """
    not used
    :return:
    """
    df_columns = ['time', 'total dipole', 'dip_x', 'dip_y', 'dip_z', 'doping', 'replica']
    outer_level = "dop_"  # TODO: save to yaml file
    inner_level = "r_"
    print('Load Dipoles...')



    df = pd.DataFrame(
        columns=df_columns
    )  # empty

    global DOP, N_R  # will not compile unless I make it

    if test:
        DOP = DOP[0:2]
        N_R = 2

    for i_dop, dop in enumerate(DOP):
        print(i_dop)
        for i_r in range(N_R):
            print(str(i_r))
            var_path = outer_level + str(i_dop) + '/' + inner_level + str(i_r)
            time_and_total_dipole = os.path.join(path, var_path, path_to_dipole, total_dipole_time_fname)
            xyz_dipole_components = os.path.join(path, var_path, path_to_dipole, dipole_xyz_fname)
            _ = np.loadtxt(time_and_total_dipole)
            __ = np.loadtxt(xyz_dipole_components)
            dwel_time = _[:, 0]
            total_dipole = _[:, 1]
            dipole_x = __[:, 0]
            dipole_y = __[:, 1]
            dipole_z = __[:, 2]
            print(i_dop, i_r)
            print(xyz_dipole_components)
            # i=0

            def create_df(df_columns=df_columns, current_i_dop=0, current_i_r=0):
                df = pd.DataFrame(
                            list(zip(dwel_time,
                                     total_dipole,
                                     dipole_x,
                                     dipole_y,
                                     dipole_z,
                                     np.ones(number_of_frames)*current_i_dop,
                                     np.ones(number_of_frames)*current_i_r)),
                            columns=['time', 'total dipole', 'dip_x', 'dip_y', 'dip_z', 'doping', 'replica'],
                            )
                return df.astype({'replica': int})
            number_of_frames = len(dwel_time)
            incremental_df = create_df(current_i_dop=i_dop,
                                    current_i_r=i_r)
            df = df.append(incremental_df)
    print('...Dipoles loaded')
    df.to_csv(os.path.join(path, 'dipoles.csv'))
    mem_of_df = df.memory_usage()
    print(f'Dataframe with dipole -- memory usage [Gb]: {mem_of_df* 1E-9}')
    print('done')
    pass


def return_mobility(path=BASE_PATH,
                    path_to_mobility='results/experiments/current_characteristics/mobilities_0.dat',
                    path_to_current_density='results/experiments/current_characteristics/all_data_points/current_density_0.dat',
                    path_to_yaml='lf_wrapper.yaml'):

    """

    :param path:
    :param path_to_mobility:
    :param path_to_yaml:
    :return:
    pd_mobility: pandas data frame mit doping / field / mobility
    """

    outer_level = "dop_"  # TODO: save to yaml file
    inner_level = "r_"
    # <-- dop_XX/r_XX

    with open(file=path_to_yaml, mode='r') as fid:
        hypersettings_dict = yaml.load(fid, Loader=yaml.SafeLoader)

    DOP = hypersettings_dict['doping molar rate']
    N_R = hypersettings_dict['number of replicas']

    pd_mobility = pd.DataFrame(
        columns=['doping', 'field', 'mobility [cm^2/(V*sec)]', 'current density [A/m^2]', 'voltage [V]']
    )

    for i_dop, dop in enumerate(DOP):
        print(i_dop)
        for i_r in range(N_R):
            print(str(i_r))
            var_path = outer_level + str(i_dop) + '/' + inner_level + str(i_r)
            current_path_to_mobility = os.path.join(path, var_path, path_to_mobility)
            current_path_to_current_density = os.path.join(path, var_path, path_to_current_density)
            print(current_path_to_mobility)
            _ = np.loadtxt(current_path_to_mobility)
            __ = np.loadtxt(current_path_to_current_density)
            pd_mobility = pd_mobility.append({'doping': dop,
                                              'field': _[0],
                                              'mobility [cm^2/(V*sec)]': _[1],
                                              'current density [A/m^2]': __[1],
                                              'voltage [V]': __[0]},
                                             ignore_index=True)

    pd_mobility['conductivity [Sm/m]'] = pd_mobility['current density [A/m^2]'] / (pd_mobility['field'] * 1E9)
    print(pd_mobility)

    pd_mobility.to_csv(os.path.join(path, 'mobility.csv'))
    print("I save mobility, conductivity etc. to mobility.png")

    return pd_mobility


if __name__ == '__main__':
    # return_mobility()
    load_all_dipoles()
    # write_joblist()  # <-- this must be a function to create jobfile

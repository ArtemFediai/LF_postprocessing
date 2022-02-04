"""
visualize lightforge simulations: currents, mobilities, etc.
"""
import copy
import os.path
import yaml
import matplotlib.pyplot as plt
import numpy as np

from lf_wrapper import return_mobility, save_dipoles_to_csv, save_coulomb_energy_to_csv
import pandas as pd
import seaborn as sns
import matplotlib

matplotlib.use('Agg')
matplotlib.style.use('ggplot')
sns.set_style('whitegrid')


with open('CONFIG.yaml', 'r') as fid:
    CONFIG = yaml.load(fid, Loader=yaml.SafeLoader)
BASE_PATH = CONFIG['BASE_PATH']  # LF simulation directory
OUT_PATH = os.path.join(BASE_PATH, 'postprocessing')  # everything will be saved here
OUT_SUBPATH_MOBILITIES = os.path.join(OUT_PATH, 'mobilities')
OUT_SUBPATH_RAW_DIPOLES = os.path.join(OUT_PATH, 'dipoles_vs_t')
OUT_SUBPATH_COULOMB = os.path.join(OUT_PATH, 'coulomb')



# EVERYTHING-->
path_to_csv = os.path.join(BASE_PATH, 'dipoles_and_vc.csv')
if os.path.exists(path_to_csv):
    print('\nI load dipoles and vc from dipoles_and_vc.csv ...')
    dipoles_and_vc_df = pd.read_csv(path_to_csv)
    print('...dipoles and vc loaded.')
else:
    print(f'\nI will read dipoles and vc from the raw simulation data, save it to {path_to_csv} and then read them therefrom.'
          f' This takes some time...')
    save_dipoles_to_csv()
    dipoles_and_vc_df = pd.read_csv(path_to_csv)
    print('...dipoles and vc are loaded')
# dipoles_df.dtypes.



# #
# # DIPOLES-->
# path_to_csv = os.path.join(BASE_PATH, 'dipoles.csv')
# if os.path.exists(path_to_csv):
#     print('\nI load dipoles from dipoles.csv ...')
#     dipoles_df = pd.read_csv(path_to_csv)
#     print('...dipoles loaded.')
# else:
#     print(f'\nI will read dipoles from the raw simulation data, save it to {path_to_csv} and then read them therefrom.'
#           f' This takes some time...')
#     save_dipoles_to_csv()
#     dipoles_df = pd.read_csv(path_to_csv)
#     print('...dipoles are loaded')
# # dipoles_df.dtypes.
#
# #
# # --> Coulomb energy
# path_to_csv = os.path.join(BASE_PATH, 'coulomb_energy.csv')
#
# print(f'\nI will read coulomb energy from the raw simulation data, save it to {path_to_csv} and then read them therefrom.'
#       f' This takes some time...')
# save_coulomb_energy_to_csv(debug_mode=True)
# coulomb_energy_df = pd.read_csv(path_to_csv)
# print('...coulomb energy is loaded')

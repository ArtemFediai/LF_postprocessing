"""
visualize lightforge simulations: currents, mobilities, etc.
"""
import copy
import os.path

import matplotlib.pyplot as plt
import numpy as np

from lf_wrapper import return_mobility
import pandas as pd
import seaborn as sns
import matplotlib

matplotlib.use('Agg')
matplotlib.style.use('ggplot')
sns.set_style('whitegrid')

# PATH to folder with lf simulations
PATH_TO_SIM_FOLDER = '/home/artem/Desktop/LF_data_from_hk/dis_0_1_node'

df_mobility = return_mobility(path=PATH_TO_SIM_FOLDER)


def lineplot(data,
             save_to='mobility.png',
             x='doping',
             y='mobility [cm^2/(V*sec)]',
             base_path=None,
             hue=None,
             style='field',
             xscale='log',
             yscale='log'):
    sns_plot = sns.lineplot(data=data,
                            x=x,
                            y=y,
                            markers='o',
                            style=style,
                            hue=hue)
    sns_plot.set(xscale=xscale)
    sns_plot.set(yscale=yscale)
    plt.savefig(os.path.join(base_path, save_to), dpi=600)
    plt.close()


# 1

lineplot(data=df_mobility,
         base_path=PATH_TO_SIM_FOLDER,
         save_to='mobility.png',
         y='mobility [cm^2/(V*sec)]')  # mobility

# 2

lineplot(data=df_mobility,
         base_path=PATH_TO_SIM_FOLDER,
         save_to='current_density.png',
         y='current density [A/m^2]')  # current density
# 3

lineplot(data=df_mobility,
         base_path=PATH_TO_SIM_FOLDER,
         save_to='conductivity.png',
         y='conductivity [Sm/m]')  # conductivity


print('I load dipoles from dipoles.csv ...')
path_to_csv = os.path.join(PATH_TO_SIM_FOLDER, 'dipoles.csv')
dipoles_df = pd.read_csv(path_to_csv)
print('...dipoles loaded')
dipoles_df.dtypes

lineplot(data=dipoles_df,
         base_path=PATH_TO_SIM_FOLDER,
         save_to='dipoles.png',
         x='time',
         y='dip_x',
         hue='doping',
         style=None,
         xscale='linear',
         yscale='linear')

# plot several instances replicas, etc.

dipoles_df = dipoles_df[dipoles_df['doping'] == 0]

#
N_DOP = 10  # number of doping points
N_R = 30  # try not using this!
#

print('done')

for i_dop in np.unique(dipoles_df['doping']):
    for i_r in np.unique(dipoles_df['replica']):
        df_per_r_per_dop = dipoles_df[(dipoles_df['replica'] == i_r) & (dipoles_df['doping'] == i_dop)]
        time_series = df_per_r_per_dop['time'] - df_per_r_per_dop['time'][0]
        df_per_r_per_dop.loc[:, 'time0'] = list(time_series)
        plt.figure()
        plt.plot()
        plt.savefig(f'r_d_{i_r}_{i_dop}.png')
        plt.close()
        del df_per_r_per_dop, time_series
        # print(f'i_r, i_dop --> {i_r}, {i_dop}')

# time_starts_from_0 = dipoles_df['time'] - dipoles_df['time'][0]
# dipoles_df['time_starts_from_0'] = time_starts_from_0
#
# lineplot(data=dipoles_df,
#          base_path=PATH_TO_SIM_FOLDER,
#          save_to='dipoles.png',
#          x='time_starts_from_0',
#          y='dip_x',
#          hue='replica',
#          style=None,
#          xscale='linear',
#          yscale='linear')
#
print('done')


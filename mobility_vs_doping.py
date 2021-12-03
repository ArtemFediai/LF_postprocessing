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

BASE_PATH = '/home/artem/Desktop/LF_data_from_hk/dis_0_1_node' # PATH to folder with lf simulations
OUT_PATH = os.path.join(BASE_PATH, 'postprocessing')  # everything will be saved here

if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)
    print(f'I create {OUT_PATH} where all results will be saved')
else:
    print(f'path {OUT_PATH} where all results will be saved exists.')

print('\nI load mobilities ...')
df_mobility = return_mobility(path=BASE_PATH)  # read in mobilities and related quantities
print('... mobilities are loaded\n')


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
                            style=style,
                            hue=hue)
    sns_plot.set(xscale=xscale)
    sns_plot.set(yscale=yscale)
    plt.savefig(os.path.join(base_path, save_to), dpi=600)
    plt.close()


# 1

lineplot(data=df_mobility,
         base_path=OUT_PATH,
         save_to='mobility.png',
         y='mobility [cm^2/(V*sec)]')  # mobility

# 2

lineplot(data=df_mobility,
         base_path=OUT_PATH,
         save_to='current_density.png',
         y='current density [A/m^2]')  # current density
# 3

lineplot(data=df_mobility,
         base_path=OUT_PATH,
         save_to='conductivity.png',
         y='conductivity [Sm/m]')  # conductivity

# <-- end of mobilities plots


#
#
# DIPOLES-->
print('I load dipoles from dipoles.csv ...')
path_to_csv = os.path.join(BASE_PATH, 'dipoles.csv')
dipoles_df = pd.read_csv(path_to_csv)
print('...dipoles loaded')
# dipoles_df.dtypes

# raw data at one plot -->
lineplot(data=dipoles_df,
         base_path=OUT_PATH,
         save_to='dipoles.png',
         x='time',
         y='dip_x',
         hue='doping',
         style='replica',
         xscale='linear',
         yscale='linear')

#
# plot for every doping and multiple replicas separate plot

for i_dop in np.unique(dipoles_df['doping']):
    plt.figure()
    for i_r in np.unique(dipoles_df['replica']):
        df_per_r_per_dop = dipoles_df[(dipoles_df['replica'] == i_r) & (dipoles_df['doping'] == i_dop)]
        x = df_per_r_per_dop['time']
        y = x[min(x.index)]
        time_series = x - y
        z = list(time_series)  # z is time referred to the starting time
        plt.plot(z, df_per_r_per_dop['dip_x'], color=f'C{i_r}')
        mean_dip_x = np.mean(df_per_r_per_dop['dip_x'])
        plt.plot(z, np.ones(len(z))*mean_dip_x, linestyle=':', color=f'C{i_r}')
    plt.savefig(f'{OUT_PATH}/d_{i_dop}.png')
    plt.close()

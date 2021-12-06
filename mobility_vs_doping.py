"""
visualize lightforge simulations: currents, mobilities, etc.
"""
import copy
import os.path
import yaml
import matplotlib.pyplot as plt
import numpy as np

from lf_wrapper import return_mobility, save_dipoles_to_csv
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
OUT_SUBPATH_t_minus_t0_DIPOLES = os.path.join(OUT_PATH, 'dipoles_vs_t_minus_t0')

OUT_SUBPATHS = [OUT_SUBPATH_MOBILITIES, OUT_SUBPATH_RAW_DIPOLES, OUT_SUBPATH_t_minus_t0_DIPOLES]
for sub_path in OUT_SUBPATHS:
    if not os.path.exists(sub_path):
        os.makedirs(sub_path)

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
             x_axis='doping',
             y_axis='mobility [cm^2/(V*sec)]',
             base_path=None,
             hue=None,
             style='field',
             xscale='log',
             yscale='log'):
    sns_plot = sns.lineplot(data=data,
                            x=x_axis,
                            y=y_axis,
                            style=style,
                            hue=hue)
    sns_plot.set(xscale=xscale)
    sns_plot.set(yscale=yscale)
    plt.savefig(os.path.join(base_path, save_to), dpi=600, bbox_inches='tight')
    plt.close()


cols_vs_filenames = {
    'mobility [cm^2/(V*sec)]': 'mobility.png',
    'current density [A/m^2]': 'current_density.png',
    'conductivity [Sm/m]': 'conductivity.png',
}  # this will be plotted vs doping and saved to respecting files in OOT_PATH folder

# plot mobilities, etc as in cols_vs_filenames -->
print("\nI plot mobilities, etc. ...")
for col_name, fig_name in cols_vs_filenames.items():
    # print(f'col_name, figure_name {col_name, fig_name}')
    lineplot(data=df_mobility,
             base_path=os.path.join(OUT_PATH, OUT_SUBPATH_MOBILITIES),
             save_to=fig_name,
             y_axis=col_name)
    print(f'{col_name} plotted at {os.path.join(BASE_PATH, fig_name)}')
# <-- end of mobilities plots


# DIPOLES-->
path_to_csv = os.path.join(BASE_PATH, 'dipoles.csv')
if os.path.exists(path_to_csv):
    print('\nI load dipoles from dipoles.csv ...')
    dipoles_df = pd.read_csv(path_to_csv)
    print('...dipoles loaded.')
else:
    print(f'\nI will read dipoles from the raw simulation data, save it to {path_to_csv} and then read them therefrom.'
          f' This takes some time...')
    save_dipoles_to_csv()
    dipoles_df = pd.read_csv(path_to_csv)
    print('...dipoles are loaded')
# dipoles_df.dtypes.

# dipoles vs time at one plot for every doping -->
for i_dop in np.unique(dipoles_df['doping']):
    df_per_dop = dipoles_df[dipoles_df['doping'] == i_dop]
    plt.figure()
    lineplot(data=df_per_dop,
             base_path=os.path.join(OUT_PATH, OUT_SUBPATH_RAW_DIPOLES),
             save_to=f'dipoles_raw_dop_{i_dop}.png',
             x_axis='time',
             y_axis='dip_x',  # x is the field direction
             hue='replica',
             style=None,
             xscale='linear',
             yscale='linear')
    plt.close()

# dipoles vs (time - t_0) where t_0 is the time when I start recording data.
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
        plt.plot(z, np.ones(len(z)) * mean_dip_x, linestyle=':', color=f'C{i_r}')
    plt.savefig(os.path.join(OUT_SUBPATH_t_minus_t0_DIPOLES, 'd_{i_dop}.png'))
    plt.close()

"""
visualize lf simulations
"""
import copy
import matplotlib.pyplot as plt
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
             y='mobility [cm^2/(V*sec)]'):

    sns_plot = sns.lineplot(data=data,
                            x='doping',
                            y=y,
                            markers='o',
                            style='field')
    sns_plot.set(xscale='log')
    sns_plot.set(yscale='log')
    plt.savefig(save_to, dpi=600)
    plt.close()

# 1

lineplot1 = copy.deepcopy(lineplot)
lineplot1(data=df_mobility)  # mobility
del lineplot1

# 2

lineplot1 = copy.deepcopy(lineplot)
lineplot1(data=df_mobility,
         save_to='current_density.png',
         y='current density [A/m^2]')  # current density

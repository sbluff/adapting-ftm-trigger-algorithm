#EXECUTE export_simulations_csv before running this script!


import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json


parameters_configuration = [ f.path for f in os.scandir('./') if f.is_dir() ]
for parameter_config in parameters_configuration:
    parameters = parameter_config.replace('./', '')
    parameters = parameters.split('-')
    # print(parameters)
    df = pd.read_csv('../meassurements.csv')
    df = df.loc[(df.meassurement_type == "fix_position") & (df.real_distance % 10 == 0) & (df.min_delta_ftm == int(parameters[0])) & (df.burst_period == int(parameters[1])) & (df.burst_exponent == int(parameters[2])) & (df.burst_duration == int(parameters[3]))& (df.ftm_per_burst == int(parameters[4]))]
    boxplot = df.boxplot(by ='real_distance', column =['meassured_distance'], grid = False)
    boxplot.set_title(parameters[0] + '-'  + parameters[1] + '-' + parameters[2] + '-'  + parameters[3] + '-'  + parameters[4])
    plt.savefig('./' + str(parameters[0]) +  '-' + str(parameters[1]) + '-' + str(parameters[2]) + '-' + str(parameters[3]) + '-' + str(parameters[4]) + '/' + "boxplot.pdf")

# df = df.groupby('real_distance')
# df.mean('meassured_distance')
# # print(df.to_string())
# line = df.plot('real_distance', 'meassured_distance')
# plt.savefig('./' + str(parameters[0]) +  '-' + str(parameters[1]) + '-' + str(parameters[2]) + '-' + str(parameters[3]) + '-' + str(parameters[4]) + '/' + "plot.pdf")

#EXECUTE export_simulations_csv before running this script!


import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json

simulation_type = [ f.path for f in os.scandir('./') if f.is_dir() ]
print(simulation_type)
for simulation in simulation_type:
    parameters_configuration = [ f.path for f in os.scandir (simulation + '/') if f.is_dir() ]
    for parameter_config in parameters_configuration:
        parameters = parameter_config.replace(simulation + '/', '')
        parameters = parameters.split('-')
        path = simulation + '/' + str(parameters[0]) +  '-' + str(parameters[1]) + '-' + str(parameters[2]) + '-' + str(parameters[3]) + '-' + str(parameters[4])
        print(path)
        df = pd.read_csv('./meassurements.csv')
        df = df.loc[(df.meassurement_type == "fix_position") & (df.min_delta_ftm == int(parameters[0])) & (df.burst_period == int(parameters[1])) & (df.burst_exponent == int(parameters[2])) & (df.burst_duration == int(parameters[3])) & (df.ftm_per_burst == int(parameters[4]))]
        if len(df.index) != 0:
            boxplot = df.boxplot(by ='real_distance', column =['meassured_distance'], grid = True)
            boxplot.set_title(simulation  + ' ' + parameters[0] + '-'  + parameters[1] + '-' + parameters[2] + '-'  + parameters[3] + '-'  + parameters[4])
            plt.savefig('./' + path + '/' + "boxplot.pdf")

            plt.clf()
            df = df.loc[df.real_distance == 20]
            histogram = df['error']
            
            histogram.plot(kind="hist", edgecolor='black', color='purple', bins= 30, title=simulation + ' ' + parameters[0] + '-'  + parameters[1] + '-' + parameters[2] + '-'  + parameters[3] + '-'  + parameters[4])
            plt.savefig('./' + path + '/' + "histogram.pdf")
    
    
# df = df.groupby('real_distance')
# df.mean('meassured_distance')
# # print(df.to_string())
# line = df.plot('real_distance', 'meassured_distance')
# plt.savefig('./' + str(parameters[0]) +  '-' + str(parameters[1]) + '-' + str(parameters[2]) + '-' + str(parameters[3]) + '-' + str(parameters[4]) + '/' + "plot.pdf")

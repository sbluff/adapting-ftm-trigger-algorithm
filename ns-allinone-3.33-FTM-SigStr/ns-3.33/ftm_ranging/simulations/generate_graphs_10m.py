#EXECUTE export_simulations_csv before running this script!


import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json
from matplotlib.ticker import FormatStrFormatter

#used for generating graphs
sampled_distance = 20

simulation_type = [ f.path for f in os.scandir('./') if f.is_dir() ]
for simulation in simulation_type:
    parameters_configuration = [ f.path for f in os.scandir (simulation + '/') if f.is_dir() ]
    for parameter_config in parameters_configuration:
        parameters = parameter_config.replace(simulation + '/', '')
        parameters = parameters.split('-')
        id = str(parameters[0]) +  '-' + str(parameters[1]) + '-' + str(parameters[2]) + '-' + str(parameters[3]) + '-' + str(parameters[4])
        path = simulation + '/' + id
        print(path)
        df = pd.read_csv('./meassurements.csv')
        df = df.loc[(df.meassurement_type == simulation.replace('./', '')) & (df.min_delta_ftm == int(parameters[0])) & (df.burst_period == int(parameters[1])) & (df.burst_exponent == int(parameters[2])) & (df.burst_duration == int(parameters[3])) & (df.ftm_per_burst == int(parameters[4]))]
        if len(df.index) != 0:
            boxplot = df.boxplot(by ='real_distance', column =['meassured_distance'], grid = True)
            boxplot.set_title(simulation  + ' ' + id)
            plt.savefig('./' + path + '/' + "boxplot.pdf")
            plt.clf()
            
            #get the sampled distance data !!
            df = df.loc[df.real_distance == sampled_distance]
            
            #histogram
            histogram = df['error']         
            histogram.plot(kind="hist", alpha=0.7, edgecolor='black', color='purple', bins= 30, title=simulation + ' ' + id)
            plt.title("Histogram (" + str(sampled_distance) + "m) "+  simulation  + ' ' + id)
            plt.savefig('./' + path + '/' + "histogram.pdf")
            plt.clf()
            
            #density
            df.error.plot.density(color='green')
            plt.title("Error density (" + str(sampled_distance) + "m) "+  simulation  + ' ' + id)
            plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d m'))
            plt.savefig('./' + path + '/' + "density.pdf")
            plt.close()
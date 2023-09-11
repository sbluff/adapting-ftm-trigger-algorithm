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
    df = pd.read_csv('./meassurements.csv')
    df = df.loc[(df.meassurement_type == simulation.replace('./', '')) & (df.real_distance == 20)]
    print(df.size)
    df['error'].hist(range=[0,5], edgecolor='black', grid=True, legend=True, by=df['ftm_per_burst'], bins=30)
    plt.xlabel('Error')
    plt.ylabel("Frequency");
    plt.savefig('./' + simulation +'/ftm_per_burst-histograms-' + str(20) + "m.pdf")
    plt.clf()
    
    df['error'].hist(range=[0,5], edgecolor='black', grid=True, legend=True, bins=30, by=df['burst_exponent'])
    plt.xlabel('Error(m)')
    plt.ylabel("Frequency(#)");
    plt.savefig('./' + simulation +'/burst_exponent-histograms-' + str(20) + "m.pdf")
    
    plt.close()
    
    
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
            df = df.loc[df.real_distance == 20]
        
            #histogram
            histogram = df['error']         
            histogram.plot(kind="hist", xlim=(0,5), alpha=0.7, edgecolor='black', color='purple', bins= 25, title=simulation + ' ' + id, grid=True)
            plt.title("Histogram (" + str(20) + "m) "+  simulation  + ' ' + id)
            

            plt.savefig('./' + path + '/histogram-' + str(20) + "m.pdf")
            plt.clf()
            
            #density
            df.error.plot.density(color='green', xlim=(0,5), grid=True)
            plt.title("Error density (" + str(20) + "m) "+  simulation  + ' ' + id)
            plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d m'))
            
            plt.savefig('./' + path + '/density-' + str(20) + "m.pdf")
            plt.close()
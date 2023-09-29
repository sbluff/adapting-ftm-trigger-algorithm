#EXECUTE export_simulations_csv before running this script!


import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json
import matplotlib
from matplotlib.ticker import FormatStrFormatter
#used for generating graphs
sampled_distance = 5

matplotlib.style.use('ggplot')

#¢reates histograms comparing ftm_per_burst & burst_size, also creates overlapping histograms
#simulation_type defines the type of meassurement
def createComparisonGraphs(simulation_type, df):
    hist = df
    ftm_per_burst_values = df['ftm_per_burst'].unique()
    path = './' + simulation_type
    if not os.path.isdir(path):
        os.makedirs(path)
        
    for value in ftm_per_burst_values:
        hist = df.loc[(df.ftm_per_burst == value)]
        hist['error'].hist(range=[0,4], edgecolor='black', grid=True, label=value, bins=20,alpha=0.5)      
    plt.xlabel('Error')
    plt.ylabel("Frequency")
    plt.legend()
    plt.savefig(path + '/ftm_per_burst-overlap-histograms-' + str(sampled_distance) + "m.pdf")
    plt.clf()
    
    df['error'].hist(range=[0,4], edgecolor='black', grid=True, legend=True, bins=30, by=df['ftm_per_burst'])
    plt.xlabel('Error(m)')
    plt.ylabel("Frequency(#)");
    plt.savefig(path + '/ftm_per_burst-histograms-' + str(sampled_distance) + "m.pdf")
    
    plt.clf()
    
    
    #BURST EXPONENT
    df['error'].hist(range=[0,4], edgecolor='black', grid=True, legend=True, bins=30, by=df['burst_exponent'])
    plt.xlabel('Error(m)')
    plt.ylabel("Frequency(#)");
    plt.savefig(path + '/burst_exponent-histograms-' + str(sampled_distance) + "m.pdf")
    
    plt.close()
    
    hist = df
    burst_exponent_values = df['burst_exponent'].unique()
    for value in burst_exponent_values:
        hist = df.loc[(df.burst_exponent == value)]
        hist['error'].hist(range=[0,4], edgecolor='black', grid=True, label=value, bins=20, alpha=0.5)
    plt.xlabel('Error')
    plt.ylabel("Frequency")
    plt.legend()
    plt.savefig(path + '/burst_exponent-overlap-histograms-' + str(sampled_distance) + "m.pdf")
    plt.clf()            

#¢reates and histogram, a boxplot and a density graph for each one of the parameters configuration in every simulation type
def createSpecificGraphs(simulation, df):     
    parameters_configuration = [ f.path for f in os.scandir (simulation + '/') if f.is_dir() ]
    for parameter_config in parameters_configuration:
        parameters = parameter_config.replace(simulation + '/', '')
        parameters = parameters.split('-')
        id = str(parameters[0]) +  '-' + str(parameters[1]) + '-' + str(parameters[2]) + '-' + str(parameters[3]) + '-' + str(parameters[4])
        path = simulation + '/' + id + '/graphs/'
        print(path)        
        if not os.path.isdir(path):
            os.makedirs(path)
            
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
            histogram.plot(kind="hist", xlim=(0,4), alpha=0.7, edgecolor='black', color='purple', bins= 25, title=simulation + ' ' + id, grid=True)
            plt.title("Histogram (" + str(sampled_distance) + "m) "+  simulation  + ' ' + id)
            

            plt.savefig('./' + path + '/histogram-' + str(sampled_distance) + "m.pdf")
            plt.clf()
            
            #density
            df.error.plot.density(color='green', xlim=(0,4), grid=True)
            plt.title("Error density (" + str(sampled_distance) + "m) "+  simulation  + ' ' + id)
            plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d m'))
            
            plt.savefig('./' + path + '/density-' + str(sampled_distance) + "m.pdf")
            plt.close()

simulation_type = [ f.path for f in os.scandir('./') if f.is_dir() ]
for simulation in simulation_type:
    df = pd.read_csv('./meassurements.csv')
    df = df.loc[(df.meassurement_type == simulation.replace('./', '')) & (df.real_distance == sampled_distance)]
    print(df.size)
    
    createComparisonGraphs(simulation, df)
    createSpecificGraphs(simulation, df)

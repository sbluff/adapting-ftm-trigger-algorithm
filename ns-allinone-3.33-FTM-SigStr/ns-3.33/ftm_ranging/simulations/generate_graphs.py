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
sampled_distance = 10

matplotlib.style.use('ggplot')

def createStdDeviationGraph(simulation, df):
    path = './' + simulation + '/parameter_study'
    stduy_parameters = ['ftm_per_burst', 'burst_exponent']
    for parameter in stduy_parameters:  
        parameter_values = df[parameter].unique()
        parameter_values.sort()
        data = [] #holds [parameter, std deviation]
        if parameter == 'ftm_per_burst':
            for value in parameter_values:
                hist = df.loc[(df.ftm_per_burst == value)]
                data.append([value, hist['error'].std()])
                plt.xlabel('FTM frames per burst')
                
        
        elif parameter == 'burst_exponent':         
            for value in parameter_values:
                hist = df.loc[(df.burst_exponent == value)]
                data.append([value, hist['error'].std()])
                plt.xlabel('Burst Exponent')
                
        std_df = pd.DataFrame(data, columns=[parameter, 'std_deviation'])  
        std_df['std_deviation'].plot(grid=True)
        plt.xticks(std_df.index, std_df[parameter].values)
        plt.ylabel('Standard Deviation')
        
        plt.savefig(path + "/std_deviation_" + parameter + ".pdf")
        plt.clf()

#¢reates histograms comparing ftm_per_burst & burst_size, also creates overlapping histograms
#simulation_type defines the type of meassurement
def createComparisonGraphs(simulation, df):
    hist = df
    ftm_per_burst_values = df['ftm_per_burst'].unique()
    path = './' + simulation + '/parameter_study'
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
    
    df['error'].hist(range=[-5,5], edgecolor='black', grid=True, legend=True, bins=30, by=df['ftm_per_burst'])
    plt.xlabel('Error(m)')
    plt.ylabel("Frequency(#)")
    plt.savefig(path + '/ftm_per_burst-histograms-' + str(sampled_distance) + "m.pdf")
    
    plt.clf()
    
    # hist = df
    # df.plot(x='channel_usage', y='error', by=df['ftm_per_burst'])
    # plt.savefig(path + '/channel_time-error-' + str(sampled_distance) + "m.pdf")
    
    # plt.clf()


    #BURST EXPONENT    
    df['error'].hist(range=[-5,5], edgecolor='black', grid=True, legend=True, bins=30, by=df['burst_exponent'])
    plt.xlabel('Error(m)')
    plt.ylabel("Frequency(#)")
    plt.savefig(path + '/burst_exponent-histograms-' + str(sampled_distance) + "m.pdf")
    
    plt.close()
    
    hist = df
    burst_exponent_values = df['burst_exponent'].unique()
    for value in burst_exponent_values:
        hist = df.loc[(df.burst_exponent == value)]
        hist['error'].hist(range=[-5,5], edgecolor='black', grid=True, label=value, bins=20, alpha=0.5)
    plt.xlabel('Error')
    plt.ylabel("Frequency")
    plt.legend()
    plt.savefig(path + '/burst_exponent-overlap-histograms-' + str(sampled_distance) + "m.pdf")
    plt.clf()  

    
    bp = sns.boxplot(data = df, x = 'session_time', y='error',linewidth=0.2)
    bp.set(xticklabels=[])
    plt.grid(linewidth=0.2, alpha=0.25, linestyle='--')
    plt.savefig(path + '/boxplot-error-time-' + str(sampled_distance) +'-m.pdf')   
    plt.clf()  
    
    # hist = df
    # df.plot(x='channel_usage', y='error', by=df['burst_exponent'])
    # plt.savefig(path + '/channel_time-error-' + str(sampled_distance) + "m.pdf")
    
    # plt.clf()

#¢reates and histogram, a boxplot and a density graph for each one of the parameters configuration in every simulation type
def createSpecificGraphs(simulation, df):     
    parameters_configuration = [ f.path for f in os.scandir (simulation + '/') if f.is_dir() ]
    for parameter_config in parameters_configuration:
        print(parameter_config)
        if "parameter_study" not in parameter_config:
            parameters = parameter_config.replace(simulation + '/', '')
            parameters = parameters.split('-')
            id = str(parameters[0]) +  '-' + str(parameters[1]) + '-' + str(parameters[2]) + '-' + str(parameters[3]) + '-' + str(parameters[4])
            path = simulation + '/' + id + '/graphs/'
            if not os.path.isdir(path):
                os.makedirs(path)
                
            df = pd.read_csv('./data/data.csv')
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

#studies the different distributions of the error for different meassurements_type
def createParamStudyGraphs(df):
    path = './data/parameter_study/'
    sim_types = ['fix_position', 'circle_mean', 'circle_velocity', 'gauss_markov']
    
    parameters = ['burst_exponent', 'ftm_per_burst']
    for parameter in parameters:
        values = df[parameter].unique()
        fig, axes = plt.subplots(2,2, figsize = (20, 12)) # syntax is plt.subplots(nrows, ncols, figsize=(width, height))
        ax = axes.ravel()

        counter = 0
        for sim_type in sim_types: 
            for value in values:
                if parameter == 'ftm_per_burst':
                    hist = df.loc[(df.ftm_per_burst == value) &  (df.meassurement_type == sim_type)]
                    print(hist.size)
                    hist['error'].hist(range=[-1,5], edgecolor='black', ax = ax[counter], grid=True, label=value, bins=80, alpha=0.5)  
                elif parameter == 'burst_exponent':
                    hist = df.loc[(df.burst_exponent == value) &  (df.meassurement_type == sim_type)]
                    print(hist.size)
                    hist['error'].hist(range=[-1,5], edgecolor='black', ax = ax[counter], grid=True, label=value, bins=80, alpha=0.5)  
            ax[counter].legend()
            ax[counter].set_xlim(-1, 5)
            ax[counter].set_title(parameter + ' for ' + sim_type, fontsize = 15)
            ax[counter].tick_params(axis='both', which='minor', labelsize=14)
            ax[counter].tick_params(axis='both', which='minor', labelsize=14)
            counter = counter + 1
        plt.xlabel('Error(m)')
        plt.ylabel("Frequency(#)")    
        plt.savefig(path + parameter + ".pdf")
        plt.clf()

def parameterValueGraphs(df):
    path = './data/parameter_study/'
    sampled_distance = 10

    parameters = ['burst_exponent', 'ftm_per_burst']
    for parameter in parameters:
        fig, axes = plt.subplots(4, figsize = (20, 12)) # syntax is plt.subplots(nrows, ncols, figsize=(width, height))
        ax = axes.ravel()
        values = df[parameter].unique()
        values.sort()
        counter = 0
        for value in values:
            simulation_types = df['meassurement_type'].unique()
            for simulation_type in simulation_types:
                if parameter == 'ftm_per_burst':
                    hist = df.loc[(df.ftm_per_burst == value) & (df.meassurement_type == simulation_type)]
                    hist['error'].hist(range=[-1,5], edgecolor='black', grid=True, ax = ax[counter], label=simulation_type, bins=80, alpha=0.5)

                elif parameter == 'burst_exponent':
                    hist = df.loc[(df.burst_exponent == value) & (df.meassurement_type == simulation_type)]
                    hist['error'].hist(range=[-1,5], edgecolor='black', grid=True, ax = ax[counter], label=simulation_type, bins=80, alpha=0.5)
                
                ax[counter].legend()
                ax[counter].set_xlim(-1, 4)
                ax[counter].set_title(parameter + "-" + str(value), fontsize = 15)
                ax[counter].tick_params(axis='both', which='minor', labelsize=14)
                ax[counter].tick_params(axis='both', which='minor', labelsize=14)    
                

            plt.title(parameter + " = " + str(value))
            plt.xlabel('Error(m)')
            plt.ylabel("Frequency(#)")
            #plt.savefig(path + parameter + "-" + str(value) + ".pdf")    
            counter = counter + 1
        plt.xlabel('Error(m)')
        plt.ylabel("Frequency(#)")    
        plt.savefig(path + parameter + "-values.pdf")
        plt.clf()

def violinPlots(df):
    graphs = ['error', 'channel_time', 'channel_usage']
    for graph in graphs:
        path = './data/parameter_study/'
        sim_types = ['fix_position', 'circle_mean', 'circle_velocity', 'gauss_markov']
        for type in sim_types:        
            pdf_name = path + type + "-" + graph + "-violin-plot.pdf"
            _data = df.loc[(df.meassurement_type == type)]
                
            sns.violinplot(data = _data, x = 'burst_exponent', y = graph, hue = 'ftm_per_burst')               
                
            plt.xlabel('burst_exponent')
            plt.ylabel(graph)    
            plt.savefig(pdf_name)
            # plt.show()
            plt.clf()         

def channelEfficiencyGraphs(df):
    path = './data/parameter_study/'
    sim_types = ['fix_position', 'circle_mean', 'circle_velocity', 'gauss_markov']
    
    parameters = ['burst_exponent', 'ftm_per_burst']
    for parameter in parameters:
        values = df[parameter].unique()
        fig, axes = plt.subplots(2,2, figsize = (20, 12)) # syntax is plt.subplots(nrows, ncols, figsize=(width, height))
        ax = axes.ravel()

        counter = 0
        for sim_type in sim_types: 
            for value in values:
                if parameter == 'ftm_per_burst':
                    hist = df.loc[(df.ftm_per_burst == value) &  (df.meassurement_type == sim_type)]
                    print(hist.size)
                    hist['efficiency'].hist(range=[0, 200], edgecolor='black', ax = ax[counter], grid=True, label=value, bins=80, alpha=0.5)  
                elif parameter == 'burst_exponent':
                    hist = df.loc[(df.burst_exponent == value) &  (df.meassurement_type == sim_type)]
                    print(hist.size)
                    hist['efficiency'].hist(range=[0, 200], edgecolor='black', ax = ax[counter], grid=True, label=value, bins=80, alpha=0.5)  
            ax[counter].legend()
            ax[counter].set_title(parameter + ' for ' + sim_type, fontsize = 15)
            ax[counter].tick_params(axis='both', which='minor', labelsize=14)
            ax[counter].tick_params(axis='both', which='minor', labelsize=14)
            counter = counter + 1
        plt.xlabel('Efficiency meassurement( 1/(m*s) )')
        plt.ylabel("Frequency(#)")    
        plt.savefig(path + parameter + "_efficiency.pdf")
        plt.clf()
  
df = pd.read_csv('./data/data.csv')
createParamStudyGraphs(df)
parameterValueGraphs(df)
channelEfficiencyGraphs(df)
violinPlots(df)
# simulation_type = [ f.path for f in os.scandir('./') if f.is_dir() ]
# for simulation in simulation_type:
#     if "data" not in simulation:
#         print(simulation)
#         df = df.loc[(df.meassurement_type == simulation.replace('./', '')) & (df.real_distance == sampled_distance)]
        
#         createComparisonGraphs(simulation, df)
#         createSpecificGraphs(simulation, df)
#         createStdDeviationGraph(simulation, df)
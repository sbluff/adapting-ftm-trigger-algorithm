import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json
import matplotlib
from matplotlib.ticker import FormatStrFormatter

#studies the different distributions of the error for different values of each parameter
def errorHistograms(df):
    path = './parameter/'
    sim_types = ['fix_position', 'circle_mean', 'circle_velocity', 'brownian']
    
    parameters = ['burst_exponent', 'ftm_per_burst', 'burst_period', 'burst_duration']
    for parameter in parameters:
        print(parameter)
        values = df[parameter].unique()
        values.sort()
        fig, axes = plt.subplots(2,2, figsize = (20, 12)) # syntax is plt.subplots(nrows, ncols, figsize=(width, height))
        ax = axes.ravel()

        counter = 0
        for sim_type in sim_types: 
            for value in values:
                if parameter == 'ftm_per_burst':
                    hist = df.loc[(df.ftm_per_burst == value) &  (df.simulation_type == sim_type)]
                    hist['error'].hist(range=[-10,10], density="True", edgecolor='black', ax = ax[counter], grid=True, label="FPB "+str(value), bins=80, alpha=0.5)  
                elif parameter == 'burst_exponent':
                    hist = df.loc[(df.burst_exponent == value) &  (df.simulation_type == sim_type)]
                    hist['error'].hist(range=[-10,10], density="True", edgecolor='black', ax = ax[counter], grid=True, label="BE "+str(value), bins=80, alpha=0.5)
                elif parameter == 'burst_duration':
                    hist = df.loc[(df.burst_duration == value) &  (df.simulation_type == sim_type)]
                    hist['error'].hist(range=[-10,10], density="True", edgecolor='black', ax = ax[counter], grid=True, label="BD "+str(value), bins=80, alpha=0.5)  
                elif parameter == 'burst_period':
                    hist = df.loc[(df.burst_period == value) &  (df.simulation_type == sim_type)]
                    hist['error'].hist(range=[-10,10], density="True", edgecolor='black', ax = ax[counter], grid=True, label="BP "+str(value), bins=80, alpha=0.5)            
            ax[counter].legend()
            ax[counter].set_xlim(-10, 10)
            ax[counter].set_title('Error for ' + sim_type, fontsize = 23)
            ax[counter].tick_params(axis='both', which='minor', labelsize=25)
            ax[counter].tick_params(axis='both', which='minor', labelsize=25)
            ax[counter].set(xlabel="Error(m)", ylabel="Frequency(#)")
            
            counter = counter + 1
        
        if not os.path.isdir(path + parameter):
            os.makedirs(path + parameter)
            
        plt.savefig(path + parameter + "/error_histogram.pdf")
        print(path + parameter + "/error_histogram.pdf")
        plt.clf()

#studies the different distributions of the channel_efficiency for different values of each parameter
def channelEfficiencyHistograms(df):
    path = './parameter/'
    sim_types = ['fix_position', 'circle_mean', 'circle_velocity', 'brownian']
    
    parameters = ['burst_exponent', 'ftm_per_burst', 'burst_duration', 'burst_period']
    for parameter in parameters:
        values = df[parameter].unique()
        values.sort()
        fig, axes = plt.subplots(2,2, figsize = (20, 12)) # syntax is plt.subplots(nrows, ncols, figsize=(width, height))
        ax = axes.ravel()

        counter = 0
        for sim_type in sim_types: 
            for value in values:
                if parameter == 'ftm_per_burst':
                    hist = df.loc[(df.ftm_per_burst == value) &  (df.simulation_type == sim_type)]
                    hist['efficiency'].hist(range=[0, 200], edgecolor='black', ax = ax[counter], density=True, grid=True, label="FPB "+str(value), bins=80, alpha=0.5)  
                elif parameter == 'burst_exponent':
                    hist = df.loc[(df.burst_exponent == value) &  (df.simulation_type == sim_type)]
                    hist['efficiency'].hist(range=[0, 200], edgecolor='black', ax = ax[counter], density=True, grid=True, label="BE "+str(value), bins=80, alpha=0.5)
                elif parameter == 'burst_duration':
                    hist = df.loc[(df.burst_duration == value) &  (df.simulation_type == sim_type)]
                    hist['efficiency'].hist(range=[-10,2000], edgecolor='black', ax = ax[counter], density=True, grid=True, label="BD "+str(value), bins=80, alpha=0.5)  
                elif parameter == 'burst_period':
                    hist = df.loc[(df.burst_period == value) &  (df.simulation_type == sim_type)]
                    hist['efficiency'].hist(range=[-10,2000], edgecolor='black', ax = ax[counter], density=True, grid=True, label="BP "+str(value), bins=80, alpha=0.5)                  
            ax[counter].legend()
            ax[counter].set_title('Channel efficiency for ' + sim_type, fontsize = 15)
            ax[counter].tick_params(axis='both', which='minor', labelsize=14)
            ax[counter].tick_params(axis='both', which='minor', labelsize=14)
            ax[counter].set(xlabel="Measurement efficiency( 1/(m*s) )", ylabel="Frequency(#)")
            counter = counter + 1
        
        if not os.path.isdir(path + parameter):
            os.makedirs(path + parameter)
            
        plt.savefig(path + parameter + '/' + "channel_efficiency.pdf")
        print(path + parameter + '/' + "channel_efficiency.pdf")
        plt.clf()           

circle_mean_data = pd.read_csv('../data/data-circle_mean.csv')    
circle_mean_data.insert(1, "simulation_type", ['circle_mean'] * len(circle_mean_data))

circle_velocity_data = pd.read_csv('../data/data-circle_velocity.csv')
circle_velocity_data.insert(1, "simulation_type", ['circle_velocity'] * len(circle_velocity_data))
    
fix_position_data = pd.read_csv('../data/data-fix_position.csv')    
fix_position_data.insert(1, "simulation_type", ['fix_position'] * len(fix_position_data))

brownian_data = pd.read_csv('../data/data-brownian.csv')   
brownian_data.insert(1, "simulation_type", ['brownian'] * len(brownian_data))

all_data = pd.concat([circle_mean_data, circle_velocity_data, fix_position_data, brownian_data]) #merge all data in a data frame


errorHistograms(all_data)
channelEfficiencyHistograms(all_data)

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

stduy_parameters = ['ftm_per_burst', 'burst_exponent']
for parameter in stduy_parameters:      
    simulation_type = [ f.path for f in os.scandir('./') if f.is_dir() ]
    for simulation in simulation_type:
        print(simulation)
        df = pd.read_csv('./meassurements.csv')
        df = df.loc[(df.meassurement_type == simulation.replace('./', '')) & (df.real_distance == sampled_distance)]
        
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
        print(std_df)
        std_df['std_deviation'].plot(grid=True, ylim=[0, 1])
        plt.xticks(std_df.index, std_df[parameter].values)
        plt.ylabel('Standard Deviation')
        
        plt.savefig('./' + simulation + '/' + "std_deviation_" + parameter + ".pdf")
        plt.clf()

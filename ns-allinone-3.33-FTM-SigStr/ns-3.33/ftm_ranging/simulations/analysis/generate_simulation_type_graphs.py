import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json
import matplotlib
from matplotlib.ticker import FormatStrFormatter
import copy
import itertools


def generateDataStructure(iterable_params, df):
    data = {}
    for param in iterable_params:
        data[param] = df[param].unique()
    
    keys, values = zip(*data.items())    
    permutations_dicts = [dict(zip(keys, v)) for v in itertools.product(*values)]
    
    return permutations_dicts    

#¢reates violin plots for the specified data fields
def velocityViolinPlots(df, simulation_type):
    
    path = './simulation_type/' + simulation_type + '/'     
    parameters = ['ftm_per_burst', 'burst_duration', 'burst_period', 'burst_exponent']
    result_fields = ['error', 'channel_time', 'channel_usage', 'session_time']
    conditions = ['velocity']
    
    for parameter in parameters:
        iterable_parameters = copy.deepcopy(parameters)
        iterable_parameters.remove(parameter)
        all_combinations = generateDataStructure(iterable_parameters, df)  
        for field in result_fields:
            file_path = path + parameter + '-' + field + '/'
            
            if not os.path.isdir(file_path):
                os.makedirs(file_path)
            
            for combination in all_combinations:
                # file_path = path + dumps(combination) + '.pdf'
                pdf_name = file_path + str(combination).replace(" ", "")+".pdf" 
                hist = df
                # print(combination)
                for x in combination:
                    hist = hist[hist[x] == combination[x]]
                    # print(hist.size)
                
                if hist.size != 0:
                    sns.set(style="whitegrid")    
                    sns.violinplot(data = hist, x = parameter, y = field, hue = 'velocity')               
                        
                    plt.xlabel(parameter)
                    plt.ylabel(field)    
                    plt.savefig(pdf_name)
                    print(pdf_name)
                    # plt.show()
                    plt.clf() 
                        
        # for key, value in combinations.items():
        #     print(key, "->", value)
        # print('------')    

# creates violin plots comparing parameters and data fields separating it by velocity
def staticViolinPlots(df, simulation_type):
    path = './simulation_type/' + simulation_type + '/'     
    parameters = ['ftm_per_burst', 'burst_duration', 'burst_period', 'burst_exponent']
    result_fields = ['error', 'channel_time', 'channel_usage', 'session_time']
    conditions = ['velocity']
    
    for parameter in parameters:
        iterable_parameters = copy.deepcopy(parameters)
        iterable_parameters.remove(parameter)
        all_combinations = generateDataStructure(iterable_parameters, df)  
        for field in result_fields:
            file_path = path + parameter + '-' + field + '/'
            
            if not os.path.isdir(file_path):
                os.makedirs(file_path)
            
            for combination in all_combinations:
                # file_path = path + dumps(combination) + '.pdf'
                pdf_name = file_path + str(combination).replace(" ", "")+".pdf" 
                hist = df
                # print(combination)
                for x in combination:
                    hist = hist[hist[x] == combination[x]]
                    # print(hist.size)
                
                if hist.size != 0:
                    sns.set(style="whitegrid")    
                    sns.violinplot(data = hist, x = parameter, y = field, hue = 'velocity')               
                        
                    plt.xlabel(parameter)
                    plt.ylabel(field)    
                    plt.savefig(pdf_name)
                    print(pdf_name)
                    # plt.show()
                    plt.clf()


circle_mean_data = pd.read_csv('../data/data-circle_mean.csv')    
circle_velocity_data = pd.read_csv('../data/data-circle_velocity.csv')    
fix_position_data = pd.read_csv('../data/data-fix_position.csv')    
brownian_data = pd.read_csv('../data/data-brownian.csv')   
all_data = pd.concat([circle_mean_data, circle_velocity_data, fix_position_data, brownian_data]) #merge all data in a data frame

velocityViolinPlots(brownian_data, 'brownian')
velocityViolinPlots(circle_velocity_data, 'circle_velocity')
staticViolinPlots(fix_position_data, 'fix_position')
staticViolinPlots(circle_mean_data, 'circle_mean')
print("Done...")

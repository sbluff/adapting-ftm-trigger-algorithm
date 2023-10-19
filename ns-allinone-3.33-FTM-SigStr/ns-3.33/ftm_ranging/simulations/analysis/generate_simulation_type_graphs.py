import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json
import matplotlib
from matplotlib.ticker import FormatStrFormatter

#¢reates violin plots for the specified data fields
def violinPlots(df):
    params = ['error', 'channel_time', 'channel_usage']
    for param in params:
        sim_types = ['fix_position', 'circle_mean', 'circle_velocity', 'brownian']
        for type in sim_types:        
            path = './simulation_type/' + type + '/'
            pdf_name = path + param + "_violin_plot.pdf"
            _data = df.loc[(df.simulation_type == type)]
                
            sns.violinplot(data = _data, x = 'burst_exponent', y = param, hue = 'ftm_per_burst')               
            plt.xlabel('burst_exponent')
            plt.ylabel(param)    
            plt.savefig(pdf_name)
            print(pdf_name)
            plt.clf()         

#creates violin plots comparing parameters and data fields separating it by velocity
def velocityViolinComparison(df, simulation_type):
    params = ['error', 'channel_time', 'channel_usage']
    fields = ['ftm_per_burst', 'burst_exponent']
    df['velocity'].unique()
    for param in params:
        for field in fields:
            path = './simulation_type/' + simulation_type + '/velocities/'
            pdf_name = path + param + "-" + field + "_violin_plot.pdf"
                
            sns.violinplot(data = df, x = field, y = param, hue = 'velocity')               
                
            plt.xlabel(field)
            plt.ylabel(param)    
            plt.savefig(pdf_name)
            print(pdf_name)
            # plt.show()
            plt.clf()         


circle_mean_data = pd.read_csv('data-circle_mean.csv')    
circle_velocity_data = pd.read_csv('data-circle_velocity.csv')    
fix_position_data = pd.read_csv('data-fix_position.csv')    
brownian_data = pd.read_csv('data-brownian.csv')   
all_data = pd.concat([circle_mean_data, circle_velocity_data, fix_position_data, brownian_data]) #merge all data in a data frame

violinPlots(all_data)
velocityViolinComparison(brownian_data, 'brownian')
velocityViolinComparison(circle_velocity_data, 'circle_velocity')

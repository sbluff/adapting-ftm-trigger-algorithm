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
    values = df['simulation_type'].unique()
    for value in values:
        if value == "static_algorithm":
            hist = df.loc[(df.burst_exponent == 3) & (df.simulation_type == value)] 
            hist 
        else:
            hist = df.loc[df.simulation_type == value]
        hist['error'].hist(range=[-10,10], edgecolor='black', density="True", label=value, grid=True, bins=80, alpha=0.5)  
    plt.legend(loc="upper left")
    plt.savefig("./algorithm/error.pdf")
    
def trajectoryPlot(df):
    g = sns.relplot(data=df, x="x_position", y="y_position", col="simulation_type")
    plt.savefig("./algorithm/trajectory.pdf")
    
algorithm_data = pd.read_csv('../data/data-algorithm.csv')   
errorHistograms(algorithm_data)   
trajectoryPlot(algorithm_data)     
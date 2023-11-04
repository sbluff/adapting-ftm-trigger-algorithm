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
        hist = df.loc[df.simulation_type == value]
        hist['error'].hist(range=[-10,10], density="True", edgecolor='black', label=value, grid=True, bins=80, alpha=0.5)  
    plt.legend(loc="upper left")
    plt.savefig("./algorithm/error.pdf")
    
algorithm_data = pd.read_csv('../data/data-algorithm.csv')   
errorHistograms(algorithm_data)        
#EXECUTE export_simulations_csv before running this script!


import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json


parameters = [15, 10, 1, 10, 2]
df = pd.read_csv('../meassurements.csv')
df = df.loc[(df.meassurement_type == "fix_position") & (df.real_distance % 10 == 0) & (df.min_delta_ftm == parameters[0]) & (df.burst_period == parameters[1]) & (df.burst_exponent == parameters[2]) & (df.burst_duration == parameters[3])& (df.ftm_per_burst == parameters[4])]
boxplot = df.boxplot(by ='real_distance', column =['meassured_distance'], grid = False)
plt.savefig('./' + str(parameters[0]) +  '-' + str(parameters[1]) + '-' + str(parameters[2]) + '-' + str(parameters[3]) + '-' + str(parameters[4]) + '/' + "boxplot.pdf")
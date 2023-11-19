import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json
import matplotlib
from matplotlib.ticker import FormatStrFormatter


#studies the different distributions of the error for different values of each parameter
def ErrorHistograms(df):
    df = df.loc[df.version != 0]
    versions = df['version'].unique()
    print(versions)

    for version in versions:
        if version != 1:
            hist = df.loc[df.version == version]
            hist['error'].hist(range=[-10,10], edgecolor='black', density="True", grid=True, label='v'+str(version), bins=80, alpha=0.5)  
    plt.legend(loc="upper left")
    plt.savefig("./algorithm/smooth-versions-error.pdf")
    
def RangePlot(df):
    df = df.loc[df.version == 0].head(100)
    df.set_index('ts', inplace=True)
    df['real_distance'].plot( marker='o', c="purple", markerfacecolor='yellow', markersize=1.5, label="real_distance")
    df['meassured_distance'].plot( marker='o', c="blue", markerfacecolor='red', markersize=1.5, label="measured_distance", drawstyle='steps')
    plt.xlabel('Session Time(s)')
    plt.ylabel('Nodes Distance(m)')
    plt.title('Nodes Ranging Distance')
    plt.legend(loc="upper left")
    plt.savefig("./algorithm/nodes-ranging-distance-v0.pdf")
    
def ErrorAnalysis(df):
    versions = df['version'].unique()
    count = 0
    data = []
    for version in versions:
        error = 0
        channel_time = 0
        session_time = 0
        hist = df.loc[df.version == version]
        for ind in hist.index:
            session_time += hist['session_time'][ind]
            channel_time += hist['channel_time'][ind]
            if count != 0:  
                error += (hist['ts'][ind] - hist['ts'][ind-1]) * (abs(hist['meassured_distance'][ind-1] - hist['real_distance'][ind-1]) + 0.5 * (hist['real_distance'][ind-1] - hist['real_distance'][ind])) 
            count += 1
        data.append([version, error, channel_time, session_time, count, error/count, channel_time/error, session_time/count])    
        count = 0    
        print(data)
    error_csv = pd.DataFrame(data, columns=['version', 'error', 'channel_time', 'session_time', 'measurements', 'measurement_error', 'measurement_channel_time', 'measurement_session_time'])
    error_csv.to_csv('./algorithm/error.csv')    
    
algorithm_data = pd.read_csv('../data/data-algorithm.csv')   
ErrorHistograms(algorithm_data)   
RangePlot(algorithm_data)  
ErrorAnalysis(algorithm_data)   
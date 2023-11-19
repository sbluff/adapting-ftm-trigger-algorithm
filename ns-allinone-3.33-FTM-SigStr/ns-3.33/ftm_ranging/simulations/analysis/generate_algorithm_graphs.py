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
    plt.clf()
  
def ErrorKde(df):  
    versions = df['version'].unique()
    pause_times = df['pause'].unique()
    print(pause_times)

    for pause in pause_times:
        for version in versions:
            # if version != 1:
            # hist = df.loc[df.version == version]
            # hist['error'].kde(range=[-10,10], edgecolor='black', density="True", grid=True, label='v'+str(version), bins=80, alpha=0.5)
            sns.kdeplot(df.loc[(df['version']==version) & (df['pause']==pause), 'error'], label='v'+str(version))  
        plt.legend(loc="upper left")
        plt.title("KDEs for pause of " + str(pause) + "s")
        plt.savefig("./algorithm/kde-"+str(pause)+"s.pdf")
        plt.clf()
  
def RangePlot(df):
    versions = df['version'].unique()
    pause_times = df['pause'].unique()
    for version in versions:
        print(version)
        for pause in pause_times:
            hist = df
            hist = hist.loc[(hist.version == version) & (hist.pause == pause)].head(100)
            hist.set_index('ts', inplace=True)
            hist['real_distance'].plot( marker='o', c="purple", markerfacecolor='yellow', markersize=1.5, label="real_distance")
            hist['meassured_distance'].plot( marker='o', c="blue", markerfacecolor='red', markersize=1.5, label="measured_distance", drawstyle='steps')
            plt.xlabel('Session Time(s)')
            plt.ylabel('Nodes Distance(m)')
            plt.title('Nodes Ranging Distance')
            plt.legend(loc="upper left")
            plt.savefig("./algorithm/nodes-ranging-distance-v"+str(version)+"-pause-"+str(pause)+".pdf")
            plt.clf()
    
def ErrorAnalysis(df):
    versions = df['version'].unique()
    pause_times = df['pause'].unique()
    data = []
    for version in versions:
        for pause in pause_times:
            count = 0
            error = 0
            channel_time = 0
            session_time = 0
            hist = df.loc[(df.version == version) & (df.pause == pause)]
            for ind in hist.index:
                session_time += hist['session_time'][ind]
                channel_time += hist['channel_time'][ind]
                if count != 0:  
                    error += (hist['ts'][ind] - hist['ts'][ind-1]) * (abs(hist['meassured_distance'][ind-1] - hist['real_distance'][ind-1]) + 0.5 * (hist['real_distance'][ind-1] - hist['real_distance'][ind])) 
                count += 1
            data.append([version, pause, error, channel_time, session_time, count, error/count, channel_time/error, session_time/count])    
        error_csv = pd.DataFrame(data, columns=['version', 'pause', 'error', 'channel_time', 'session_time', 'measurements', 'measurement_error', 'measurement_channel_time', 'measurement_session_time'])
        error_csv.set_index(['version', 'pause'], inplace=True)    
        error_csv.to_csv('./algorithm/error.csv')    
    
algorithm_data = pd.read_csv('../data/data-algorithm.csv')   
# ErrorHistograms(algorithm_data)  
ErrorKde(algorithm_data) 
RangePlot(algorithm_data)  
ErrorAnalysis(algorithm_data)   
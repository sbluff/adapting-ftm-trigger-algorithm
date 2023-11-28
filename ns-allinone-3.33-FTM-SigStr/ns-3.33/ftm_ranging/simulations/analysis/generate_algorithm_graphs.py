import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json
import matplotlib
from matplotlib.ticker import FormatStrFormatter
from scipy.integrate import quad

t0 = 0
t1 = 0
r0 = 0
r1 = 0
m = 0


#real distance between two timestamps
def f1(x):
    return x 

def f2(x):
    return 1
    
#measured distance between two timestamps
def g(x):
    return 1


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
            hist = hist.loc[(hist.version == version) & (hist.pause == pause)].head(50)
            hist.set_index('ts', inplace=True)
            hist['real_distance'].plot( marker='o', c="purple", markerfacecolor='yellow', markersize=1.5, label="real_distance")
            hist['meassured_distance'].plot( marker='o', c="blue", markerfacecolor='red', markersize=1.5, label="measured_distance", drawstyle='steps-post')
            plt.xlabel('Session Time(s)')
            plt.ylabel('Nodes Distance(m)')
            plt.title('Nodes Ranging Distance')
            plt.legend(loc="upper left")
            plt.savefig("./algorithm/nodes-ranging-distance-v"+str(version)+"-pause-"+str(pause)+".pdf")
            plt.clf()
    
# def ErrorAnalysis(df):
#     ErrorAreaHistogram(df)
#     versions = df['version'].unique()
#     pause_times = df['pause'].unique()
#     data = []
#     for version in versions:
#         for pause in pause_times:
#             count = 0
#             error = 0
#             channel_time = 0
#             session_time = 0
#             hist = df.loc[(df.version == version) & (df.pause == pause)]
#             for ind in hist.index:
#                 session_time += hist['session_time'][ind]
#                 channel_time += hist['channel_time'][ind]
#                 if count != 0:  
#                     t0 = float(hist['ts'][ind-1])
#                     t1 = float(hist['ts'][ind])
#                     r0 = hist['real_distance'][ind-1]
#                     r1 = hist['real_distance'][ind]
#                     m = hist['meassured_distance'][ind-1] 
#                     error += quad(f1, t0, t1)[0] * ((r1-r0)/(t1-t0)) + quad(f2, t0, t1)[0] * (t1*r0 - t0*r1)/(t1-t0) - quad(g, t0, t1)[0] * m
#                 count += 1
#             data.append([version, pause, error, channel_time, session_time, count, error/count, channel_time/error, session_time/count])    
#         error_csv = pd.DataFrame(data, columns=['version', 'pause', 'error', 'channel_time', 'session_time', 'measurements', 'measurement_error', 'measurement_channel_time', 'measurement_session_time'])
#         error_csv.set_index(['version', 'pause'], inplace=True)    
#         error_csv.to_csv('./algorithm/error.csv')

def ErrorAreaHistogram(df):
    versions = df['version'].unique()
    pause_times = df['pause'].unique()
    data = []
    for version in versions:
        for pause in pause_times:
            error = []
            channel_time = []
            count = 0
            session_time = 0
            hist = df.loc[(df.version == version) & (df.pause == pause)]
            
            for ind in hist.index:
                session_time += hist['session_time'][ind]
                if count != 0:
                    t0 = float(hist['ts'][ind-1])
                    t1 = float(hist['ts'][ind])
                    r0 = hist['real_distance'][ind-1]
                    r1 = hist['real_distance'][ind]
                    m = hist['meassured_distance'][ind-1] 
                    channel_time.append(hist['channel_time'][ind])
                    error.append(quad(f1, t0, t1)[0] * ((r1-r0)/(t1-t0)) + quad(f2, t0, t1)[0] * (t1*r0 - t0*r1)/(t1-t0) - quad(g, t0, t1)[0] * m)
                    
                count += 1   
                
            error_area = pd.DataFrame({'error_area': error, 'channel_time': channel_time})
                
            data.append([version, pause, sum(error), sum(channel_time), session_time, count, (sum(error)/len(error)), error_area['error_area'].std(), (sum(channel_time)/len(channel_time)), session_time/count, error_area['channel_time'].std()])       
            error_csv = pd.DataFrame(data, columns=['version', 'pause', 'error', 'channel_time', 'session_time', 'measurements', 'measurement_error', 'std_deviation_error', 'measurement_channel_time', 'measurement_session_time', 'std_deviation_channel_time'])
            error_csv.set_index(['version', 'pause'], inplace=True)    
            error_csv.to_csv('./algorithm/error.csv')
            
            
            error_area['error_area'].hist(density="True", edgecolor='black', grid=True, bins=80, alpha=0.5)
            plt.title("Area of error measurements for version " + str(version) + " and pause " + str(int(pause)) + "s")
            plt.savefig("./algorithm/error_area_hist_v" + str(version) + "-p" + str(int(pause)) + ".pdf")
            plt.clf()  
            
            error_area['channel_time'].hist(density="True", edgecolor='black', grid=True, bins=80, alpha=0.5)
            plt.title("Channel time for version " + str(version) + " and pause " + str(int(pause)) + "s")
            plt.savefig("./algorithm/channel_time_hist_v" + str(version) + "-p" + str(int(pause)) + ".pdf")
            plt.clf()  
            
            std = error_area['error_area'].std()
            std_error = []
            for entry in error:
                if abs(entry) < std:
                    std_error.append(entry)
            
            error_area = pd.DataFrame({'std_error_area': std_error})
            plt.title("75% percentile measurements for area of error version " + str(version) + " and pause " + str(int(pause)) + "s")
            error_area['std_error_area'].hist(density="True", edgecolor='black', grid=True, bins=80, alpha=0.5)
            plt.savefig("./algorithm/std_error_area_hist_v" + str(version) + "-p" + str(int(pause)) + ".pdf")
            plt.clf()
                    
            print(std)
            
            
                
matplotlib.style.use('ggplot')
algorithm_data = pd.read_csv('../data/data-algorithm.csv')   
# ErrorHistograms(algorithm_data)  
# ErrorKde(algorithm_data) 
# RangePlot(algorithm_data)  
ErrorAreaHistogram(algorithm_data)   
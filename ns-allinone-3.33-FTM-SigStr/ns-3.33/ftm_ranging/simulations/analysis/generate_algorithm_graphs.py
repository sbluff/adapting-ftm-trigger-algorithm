import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
import csv
import json
import matplotlib
import pylab as pl
from matplotlib.ticker import FormatStrFormatter
from scipy.integrate import quad
from matplotlib.lines import Line2D
from scipy import stats

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
  
def Kde(df):  
    versions = df['version'].unique()
    versions.sort()
    axis_info = {
        "metrics": ['error_area', 'channel_usage', 'channel_time'],
        "labels": ['Error (m²)', 'Channel Usage (%)', 'Channel Time (s)'],
        "x_ranges": [[-50,50], [-0.050, 0.125], [-0.005,0.015]],
        # "y_ranges": [[0, 0.5], [0, 30], [0,2000]]
    }
    axis_count = 0
    for metric in axis_info["metrics"]:
        plt.title(metric, {
            'fontsize': 16,
            'fontweight' : 16,
            'verticalalignment': 'center',
            'horizontalalignment': 'center'
        })
        fig, axes = plt.subplots(len(versions), figsize = (20, 12)) # syntax is plt.subplots(nrows, ncols, figsize=(width, height))
        ax = axes.ravel()
        count = 0
        for version in versions:
            hist = df.loc[(df.version == version)]

            ax[count].tick_params(axis='both', labelsize=15)
            ax[count].set_xlabel(axis_info["labels"][axis_count], fontdict={'fontsize':24})
            ax[count].set_xlim(axis_info["x_ranges"][axis_count])
            # ax[count].set_ylim(axis_info["y_ranges"][axis_count])
            sns.kdeplot(data=hist, x = metric, ax=ax[count], hue="pause", fill=True, common_norm=False, alpha=.5, linewidth=0.5, palette="crest") 
            count += 1
        plt.savefig("./algorithm/kde-" + metric + ".pdf")
        plt.clf()
        axis_count += 1
  
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

def ErrorAreaHistogram(df):
    versions = df['version'].unique()
    pause_times = df['pause'].unique()
    data = []
    for version in versions:
        print(version)
        for pause in pause_times:
            print(pause)
            error = []
            channel_time = []
            channel_usage = []
            count = 0
            session_time = 0
            hist = df.loc[(df.version == version) & (df.pause == pause)]
            
            if len(hist) > 0:
                for ind in hist.index:
                    session_time += hist['session_time'][ind]
                    if count != 0:
                        t0 = float(hist['ts'][ind-1])
                        t1 = float(hist['ts'][ind])
                        r0 = hist['real_distance'][ind-1]
                        r1 = hist['real_distance'][ind]
                        m = hist['meassured_distance'][ind-1] 
                        channel_time.append(hist['channel_time'][ind])
                        channel_usage.append(hist['channel_usage'][ind])
                        error.append(quad(f1, t0, t1)[0] * ((r1-r0)/(t1-t0)) + quad(f2, t0, t1)[0] * (t1*r0 - t0*r1)/(t1-t0) - quad(g, t0, t1)[0] * m)
                        
                    count += 1   
                    
                stat_data = pd.DataFrame({'error_area': error, 'channel_time': channel_time, 'channel_usage': channel_usage})
                    
                data.append([version, pause, sum(stat_data['error_area']), sum(channel_time), sum(channel_usage), session_time, count, (sum(stat_data['error_area'])/len(stat_data['error_area'])), error_area['error_area'].std(), (sum(channel_time)/len(channel_time)), sum(channel_usage)/len(channel_usage),session_time/count, error_area['channel_time'].std()])       
                error_csv = pd.DataFrame(data, columns=['version', 'pause', 'error', 'channel_time', 'channel_usage', 'session_time', 'measurements', 'measurement_error', 'std_deviation_error', 'measurement_channel_time', 'measurement_channel_usage', 'measurement_session_time', 'std_deviation_channel_time'])
                error_csv.set_index(['version', 'pause'], inplace=True)    
                error_csv.to_csv('./algorithm/error.csv')
                
                
                stat_data['error_area'].hist(density="True", edgecolor='black', grid=True, bins=80, alpha=0.5)
                plt.title("Area of error measurements for version " + str(version) + " and pause " + str(int(pause)) + "s")
                plt.savefig("./algorithm/error_area_hist_v" + str(version) + "-p" + str(int(pause)) + ".pdf")
                plt.clf()  
                
                stat_data['channel_time'].hist(density="True", edgecolor='black', grid=True, bins=80, alpha=0.5)
                plt.title("Channel time for version " + str(version) + " and pause " + str(int(pause)) + "s")
                plt.savefig("./algorithm/channel_time_hist_v" + str(version) + "-p" + str(int(pause)) + ".pdf")
                plt.clf()  
                
                sns.kdeplot(df.loc[(df['version']==version), 'channel_usage'], label='v'+str(version))           
                plt.title("Channel usage for version " + str(version))
                plt.savefig("./algorithm/channel_usage_kde_v" + str(version) + ".pdf")
                plt.clf()  
                
                std = stat_data['error_area'].std()
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
     
def SpyderPlot():
    BG_WHITE = "#fbf9f4"
    BLUE = "#2a475e"
    GREY70 = "#b3b3b3"
    GREY_LIGHT = "#f2efe8"
    COLORS = ["#000000", "#57cae3", "#3884ec", "#cc0000", "#FBAE46"]
    
    HANGLES = np.linspace(0, 2 * np.pi)
    
    H0 = np.zeros(len(HANGLES))
    H1 = np.ones(len(HANGLES)) * 0.5
    H2 = np.ones(len(HANGLES))
    
    data = pd.read_csv('./algorithm/error.csv')
    # data.set_index('version', inplace=True)
    labels=np.array(['measurement_session_time', 'measurement_channel_usage', 'measurement_channel_time', 'measurement_error']) 
    N = len(labels)
    
    versions = data['version'].unique()
    pauses = data['pause'].unique()
    # print(versions)

    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    
    counter = 0
    for version in versions:
        print(version)
        # for pause in pauses:
        values=data.loc[(data.version == version),labels]
        if len(values) != 0:
            # values["measurement_error"] = values["measurement_error"].abs()
            values = [values["measurement_session_time"].mean(), values["measurement_channel_usage"].mean()*100, values["measurement_channel_time"].mean()*10000, values["measurement_error"].mean()]
            print(values)
            # close the radar plots
            angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
            values = np.concatenate((values, [values[0]]))
            angles = np.concatenate((angles, [angles[0]]))
            
            ax.spines["start"].set_color("none")
            ax.spines["polar"].set_color("none")    
            
            ax.plot(angles, values, marker="o", c=COLORS[counter],linewidth=1, label=str(version))
                
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, size=10)   
        counter += 1    
    plt.title("Version metric analysis")
    ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels)
    ax.grid(True)
    plt.legend(labels, loc="best", bbox_to_anchor=(0.5, 0.0, -0.54, 1.15))
    
    handles = [
        Line2D(
            [], [], 
            c=color, 
            lw=3, 
            marker="o", 
            markersize=2, 
            label="v"+str(version)
        )
        for version, color in zip(versions, COLORS)
    ]   

    legend = ax.legend(
        handles=handles,
        loc=(1, 0),       # bottom-right
        labelspacing=1.5, # add space between labels
        frameon=False     # don't put a frame
    )
    
    plt.title("Version stats")
    plt.savefig("./algorithm/spyder_versions.pdf")
    plt.clf()  
   

def WriteReport(df):
    versions = df['version'].unique()
    pause_times = df['pause'].unique()
    data = []
    csv_data_version = []
    for version in versions:
        error_area = []
        error = []
        channel_time = []
        channel_usage = []
        session_time = 0
        hist = df.loc[(df.version == version)]
        if len(hist) > 0:
            count = 0
            prev_index = hist.index[0]
            for ind in hist.index:
                # print(ind)
                if count != 0:
                    t0 = float(hist['ts'][prev_index])
                    t1 = float(hist['ts'][ind])
                    r0 = hist['real_distance'][prev_index]
                    r1 = hist['real_distance'][ind]
                    m = hist['meassured_distance'][prev_index] 
                    error_area.append(quad(f1, t0, t1)[0] * ((r1-r0)/(t1-t0)) + quad(f2, t0, t1)[0] * (t1*r0 - t0*r1)/(t1-t0) - quad(g, t0, t1)[0] * m)
                    channel_time.append(hist['channel_time'][ind])
                    channel_usage.append(hist['channel_usage'][ind])
                    error.append(hist['real_distance'][ind] - hist['meassured_distance'][ind])
                    session_time += hist['session_time'][ind]
                prev_index = ind    
                    
                count += 1
                    
                
            stat_data = pd.DataFrame({
                'error': error,
                'error_area': error_area,
                'channel_time': channel_time,
                'channel_usage': channel_usage}
            )
            
            csv_data = {
                'version': version,
                'error': sum(stat_data['error']),
                'error_area': sum(stat_data['error_area']),
                'channel_time': sum(channel_time),
                'channel_usage': sum(channel_usage),
                'session_time': session_time,
                'measurements': len(hist),
                'measurement_error': sum(stat_data['error'])/len(stat_data['error']),
                'measurement_error_area': sum(stat_data['error_area'])/len(stat_data['error_area']),
                'std_deviation_error': stat_data['error_area'].std(),
                'measurement_channel_time': sum(channel_time)/len(channel_time),
                'std_deviation_channel_time': stat_data['channel_time'].std(),
                'measurement_channel_usage': sum(channel_usage)/len(channel_usage),
                'measurement_session_time': session_time/len(hist),
            }
            
            csv_data_version.append(csv_data)

    with open ('./algorithm/error.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(csv_data_version[0].keys())
        for version in csv_data_version:
            writer.writerow(version.values())
            
            # f = open('./algorithm/error.csv', w)
            # print(data['data'].shape)
            # report = pd.DataFrame(data=data['data'], columns=data['fields'])
            # report.set_index('version', inplace=True)    
            # report.to_csv('./algorithm/error.csv')
                
    
           
matplotlib.style.use('ggplot')
algorithm_data = pd.read_csv('../data/data-algorithm.csv')


WriteReport(algorithm_data)
# SpyderPlot()   
# ErrorHistograms(algorithm_data)  
# Kde(algorithm_data) 
# RangePlot(algorithm_data)  
# ErrorAreaHistogram(algorithm_data)   
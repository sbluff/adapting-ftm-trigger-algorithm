import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
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

class Radar(object):
    def __init__(self, fig, titles, labels, rect=None):
        if rect is None:
            rect = [0.05, 0.05, 0.95, 0.95]

        self.n = len(titles)
        self.angles = np.arange(90, 90+360, 360.0/self.n)
        self.axes = [fig.add_axes(rect, projection="polar", label="axes%d" % i) 
                         for i in range(self.n)]

        self.ax = self.axes[0]
        self.ax.set_thetagrids(self.angles, labels=titles, fontsize=14)

        for ax in self.axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)

        for ax, angle, label in zip(self.axes, self.angles, labels):
            ax.set_rgrids(range(1, 6), angle=angle, labels=label)
            ax.spines["polar"].set_visible(False)
            ax.set_ylim(0, 5)

    def plot(self, values, *args, **kw):
        angle = np.deg2rad(np.r_[self.angles, self.angles[0]])
        values = np.r_[values, values[0]]
        self.ax.plot(angle, values, *args, **kw)



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
    
    for version in versions:
        hist = df.loc[(df.version == version)]
        # hist['error_area_quantile'] = hist['error_area'].quantile(q=0.95)
        print(hist['error_area'].quantile(q=0.95))
        plt.title("Error / Channel Usage / Efficiency for version " + str(version), {
            'fontsize': 16,
            'fontweight' : 16,
            'verticalalignment': 'center',
            'horizontalalignment': 'center'
        })
        fig, axes = plt.subplots(3, figsize = (20, 12)) # syntax is plt.subplots(nrows, ncols, figsize=(width, height))
        ax = axes.ravel()

        ax[0].tick_params(axis='both', labelsize=14)
        ax[0].set(xlabel="Error (m²)")
        sns.kdeplot(data=hist.loc[df.error_area < hist['error_area'].quantile(q=0.95)], x = 'error_area', ax=ax[0], hue="pause", fill=True, common_norm=False, alpha=.5, linewidth=0, palette="crest") 
        
        
        ax[1].tick_params(axis='both', which='minor', labelsize=14)
        ax[1].set(xlabel="Channel Usage (%)")
        sns.kdeplot(data=hist, x = 'channel_usage', ax=ax[1], hue="pause", fill=True, common_norm=False, alpha=.5, linewidth=0, palette="crest") 
        
        
        ax[2].tick_params(axis='both', which='minor', labelsize=14)
        ax[2].set(xlabel="Channel Time (s)")
        sns.kdeplot(data=hist, x = 'channel_time', ax=ax[2], hue="pause", fill=True, common_norm=False, alpha=.5, linewidth=0, palette="crest") 
             
        plt.savefig("./algorithm/kde-v"+str(version)+"s.pdf")
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
                    
                error_area = pd.DataFrame({'error_area': error, 'channel_time': channel_time, 'channel_usage': channel_usage})
                    
                data.append([version, pause, sum(error), sum(channel_time), sum(channel_usage), session_time, count, (sum(error)/len(error)), error_area['error_area'].std(), (sum(channel_time)/len(channel_time)), sum(channel_usage)/len(channel_usage),session_time/count, error_area['channel_time'].std()])       
                error_csv = pd.DataFrame(data, columns=['version', 'pause', 'error', 'channel_time', 'channel_usage', 'session_time', 'measurements', 'measurement_error', 'std_deviation_error', 'measurement_channel_time', 'measurement_channel_usage', 'measurement_session_time', 'std_deviation_channel_time'])
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
                
                sns.kdeplot(df.loc[(df['version']==version) & (df['pause']==pause), 'channel_usage'], label='v'+str(version))           
                plt.title("Channel usage for version " + str(version) + " and pause " + str(int(pause)) + "s")
                plt.savefig("./algorithm/channel_usage_kde_v" + str(version) + "-p" + str(int(pause)) + ".pdf")
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
            values = [values["measurement_session_time"].mean(), values["measurement_channel_usage"].mean(), values["measurement_channel_time"].mean(), values["measurement_error"].mean()]
            print(values)
            # close the radar plots
            angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
            values = np.concatenate((values, [values[0]]))
            angles = np.concatenate((angles, [angles[0]]))
            
            ax.spines["start"].set_color("none")
            ax.spines["polar"].set_color("none")    
            
            ax.plot(angles, values, "o-", c=COLORS[counter],linewidth=2, label=str(version))
                
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
            markersize=8, 
            label=version
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
    plt.show()
    
           
matplotlib.style.use('ggplot')
algorithm_data = pd.read_csv('../data/data-algorithm.csv')


# SpyderPlot()   
# ErrorHistograms(algorithm_data)  
ErrorKde(algorithm_data) 
# RangePlot(algorithm_data)  
# ErrorAreaHistogram(algorithm_data)   
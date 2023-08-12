import numpy as np
import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json

error_models = ["wireless"]

def file_is_empty(filename):
    with open(filename)as fin:
        for line in fin:
            line = line[:line.find('#')]  # remove '#' comments
            line = line.strip() #rmv leading/trailing white space
            if len(line) != 0:
                return False
    return True

params = dict(min_delta_ftm=0, burst_duration=0, burst_exponent=0, burst_period=0, ftm_per_burst=0)
f = open('./simulations/simulation_parameters.json')
data = json.load(f)
params['error_models'] = data['error_models']
params['burst_duration'] = data['burst_duration']
params['burst_period'] = data['burst_period']
params['burst_exponent'] = data['burst_exponent']
params['min_delta_ftm'] = data['min_delta_ftm']
params['ftm_per_burst'] = data['ftm_per_burst']

for curr_error_model in error_models:
    files = sorted(glob.glob('simulations/' + str(params['min_delta_ftm']) + '-' + str(params['burst_duration']) + '-' + str(params['burst_exponent']) + '-'  + str(params['burst_period']) + '-' + str(params['ftm_per_burst']) + "/*m"))
    print(files)
    files = files[25:75+1:5]
    data = np.zeros((len(files) * 17820, 4))
    i = 0
    for f in files:
        curr_distance = int(f.split('/').pop().rstrip(f.split('/').pop()[-1]))
        if not file_is_empty(f):
            curr_measurement = np.loadtxt(f)
            for m in curr_measurement:
                data[i,0] = m[0] #RTT
                data[i,1] = m[1] #sig_str
                data[i,2] = curr_distance #real distance
                data[i,3] = m[0] / 2 / 1000 * 0.3 #convert RTT to distance in meters
                i += 1
   
    df = pd.DataFrame(data, columns=["RTT", "SigStr", "RealDist", "MeasuredDist"])
    df = df.loc[(df!=0).any(axis=1)]
    fig = plt.figure(figsize=(2.5,2.5*12/8))
    plt.rcParams['font.size'] = '7'
    sns.boxplot(data=df, x='RealDist', y='MeasuredDist', fliersize=0.5, linewidth=0.2)
    sns.lineplot(x=np.arange(0,len(files)), y=np.arange(25,75+1,5), linewidth=0.2, alpha=0.75, label="ground truth")
    plt.xlabel("Real distance [m]")
    plt.ylabel("Measured distance [m]")
    tick_labels = np.arange(0,len(files))
    for i in range(0, len(tick_labels)):
        tick_labels[i] = 25 + tick_labels[i] * 5 

    plt.xticks(ticks=np.arange(0,len(files)), labels=tick_labels, ha='center', fontsize=5)
    
    plt.ylim(20,80)
    y_tick_labels = []
    for i in np.arange(20,80):
        if i%5 == 0:
            y_tick_labels.append(str(i))
        else:
            y_tick_labels.append("")

    plt.yticks(ticks=np.arange(20,80), labels=y_tick_labels, fontsize=5)
    plt.grid(linewidth=0.2, alpha=0.25, linestyle='--')
    plt.legend()
    plt.tight_layout() 
    dir = "simulations/" + str(params['min_delta_ftm']) + '-' + str(params['burst_duration']) + '-' + str(params['burst_exponent']) + '-'  + str(params['burst_period']) + '-' + str(params['ftm_per_burst']) + '/'
    if (not os.path.isdir(dir)):
        os.mkdir(dir)
    plt.savefig(dir + curr_error_model + "_5m" + ".pdf")
    # break

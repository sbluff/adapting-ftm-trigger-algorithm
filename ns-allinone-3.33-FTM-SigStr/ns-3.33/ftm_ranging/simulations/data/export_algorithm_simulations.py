#the aim of this script is to export all the simulation data to the csv file meassurements.csv
# WARNING! The content of the file will be overwritten and only the current data will be stored in the file.

import os
import csv
import glob
import numpy as np
from separate_data import separate_csv
from scipy.integrate import quad
from matplotlib.lines import Line2D

#real distance between two timestamps
def f1(x):
    return x 

def f2(x):
    return 1
    
#measured distance between two timestamps
def g(x):
    return 1


def file_is_empty(filename):
    with open(filename)as fin:
        for line in fin:
            line = line[:line.find('#')]  # remove '#' comments
            line = line.strip() #rmv leading/trailing white space
            if len(line) != 0:
                return False
    return True

files = ['./adaptive-algorithm/adaptive-algorithm']

with open('./data-algorithm.csv', 'w+', newline='') as csvfile:
    fieldnames = ['real_distance','meassured_distance','min_delta_ftm','burst_period','burst_exponent','burst_duration','ftm_per_burst', 'error', 'session_time', 'channel_time', 'channel_usage', 'efficiency', 'velocity', 'x_position', 'y_position', 'version', 'ts', 'pause', 'speed']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    count = 0
    for file in files:
        if not file_is_empty(file):
            curr_measurement = np.loadtxt(file)
            ts = 0
            
            t0 = float(previous_measurement['ts'])
            t1 = float(m['ts'])
            r0 = previous_measurement['real_distance']
            r1 = m['real_distance']
            m = previous_measurement['meassured_distance']

            previous_measurement = []
            for m in curr_measurement:
                error_area = 0
                if previous_measurement != []:
                    t0 = float(previous_measurement['ts'])
                    t1 = float(m['ts'])
                    r0 = previous_measurement['real_distance']
                    r1 = m['real_distance']
                    m = previous_measurement['meassured_distance']
                    error_area = quad(f1, t0, t1)[0] * ((r1-r0)/(t1-t0)) + quad(f2, t0, t1)[0] * (t1*r0 - t0*r1)/(t1-t0) - quad(g, t0, t1)[0] * m
                value = int(m[6]) / 2 / (10000 * 0.3)
                channel_usage = abs(float(m[9]/m[8])*100)
                writer.writerow({
                    'real_distance': m[5],
                    'meassured_distance': value,
                    'min_delta_ftm': m[0],
                    'burst_period': m[1],
                    'burst_exponent': m[2],
                    'burst_duration': m[3],
                    'ftm_per_burst':m[4],
                    'error': value-m[5],
                    'error_area': error_area,
                    'session_time': abs(m[8]), 
                    'channel_time': abs(m[9]),
                    'channel_usage': channel_usage,
                    'efficiency':1/(float(channel_usage * abs(value-m[5]))) if channel_usage * abs(value-m[5]) != 0 else 0,
                    'velocity': m[10],
                    'x_position': m[11],
                    'y_position': m[12],
                    'version': m[14] if "static-algorithm" not in file else 0,
                    'ts': ts,
                    'pause': m[15],
                    'speed': m[16],
                })
                ts += abs(m[8])
                previous_measurement = m
        count += 1       

print("Data exported correctly!")
            
        
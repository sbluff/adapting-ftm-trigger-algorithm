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
    fieldnames = ['real_distance','meassured_distance','error', 'error_area','min_delta_ftm','burst_period','burst_exponent','burst_duration','ftm_per_burst','session_time', 'channel_time', 'channel_usage', 'efficiency', 'velocity', 'x_position', 'y_position', 'version', 'ts', 'pause', 'speed']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    count = 0
    for file in files:
        if not file_is_empty(file):
            curr_measurement = np.loadtxt(file)
            ts = 0
            previous_measurement = curr_measurement[0]
            for measurement in curr_measurement:       
                error_area = 0
                t0 = ts
                t1 = ts + abs(measurement[8])
                r0 = previous_measurement[5]
                r1 = measurement[5]
                m = int(previous_measurement[6]) / 2 / (10000 * 0.3)
                error_area = quad(f1, t0, t1)[0] * ((r1-r0)/(t1-t0)) + quad(f2, t0, t1)[0] * (t1*r0 - t0*r1)/(t1-t0) - quad(g, t0, t1)[0] * m
                value = int(measurement[6]) / 2 / (10000 * 0.3)
                channel_usage = abs(float(measurement[9]/measurement[8])*100)
                writer.writerow({
                    'real_distance': measurement[5],
                    'meassured_distance': value,
                    'error': value-measurement[5],
                    'error_area': error_area,
                    'min_delta_ftm': measurement[0],
                    'burst_period': measurement[1],
                    'burst_exponent': measurement[2],
                    'burst_duration': measurement[3],
                    'ftm_per_burst':measurement[4],
                    'session_time': abs(measurement[8]), 
                    'channel_time': abs(measurement[9]),
                    'channel_usage': channel_usage,
                    'efficiency':1/(float(channel_usage * abs(error_area))) if channel_usage * abs(error_area) != 0 else 0,
                    'velocity': measurement[10],
                    'x_position': measurement[11],
                    'y_position': measurement[12],
                    'version': measurement[14],
                    'ts': ts,
                    'pause': measurement[15],
                    'speed': measurement[16],
                })
                # if measurement[14] == 0.1:
                #     print("t0: " + str(t0))
                #     print("t1: " + str(t1))
                #     print("r0: " + str(r0))
                #     print("r1: " + str(r1))
                #     print("m: " + str(m))
                #     print("measurement[0]" + measurement)
                #     print(error_area)
                ts = t1
                previous_measurement = measurement
        count += 1       

print("Data exported correctly!")
            
        
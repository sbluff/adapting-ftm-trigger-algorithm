#the aim of this script is to export all the simulation data to the csv file meassurements.csv
# WARNING! The content of the file will be overwritten and only the current data will be stored in the file.

import os
import csv
import glob
import numpy as np
from separate_data import separate_csv

def file_is_empty(filename):
    with open(filename)as fin:
        for line in fin:
            line = line[:line.find('#')]  # remove '#' comments
            line = line.strip() #rmv leading/trailing white space
            if len(line) != 0:
                return False
    return True

files = ['./data/adaptive-algorithm-test/adaptive-algorithm', './data/adaptive-algorithm-test/static-algorithm']
simulation_types = ['adaptive-algorithm', 'static_algorithm']

with open('./data/data-algorithm.csv', 'w+', newline='') as csvfile:
    fieldnames = ['real_distance','meassured_distance','simulation_type','min_delta_ftm','burst_period','burst_exponent','burst_duration','ftm_per_burst', 'error', 'session_time', 'channel_time', 'channel_usage', 'efficiency', 'velocity']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    count = 0
    for file in files:
        if not file_is_empty(file):
            curr_measurement = np.loadtxt(file)
            for m in curr_measurement:
                value = int(m[6]) / 2 / (10000 * 0.3)
                channel_usage = abs(float(m[8]/m[9])*100)
                writer.writerow({
                    'real_distance': m[5],
                    'meassured_distance': value,
                    'simulation_type': simulation_types[count],
                    'min_delta_ftm': m[0],
                    'burst_period': m[1],
                    'burst_exponent': m[2],
                    'burst_duration': m[3],
                    'ftm_per_burst':m[4],
                    'error': value-m[5],
                    'session_time': abs(m[8]), 
                    'channel_time': abs(m[9]),
                    'channel_usage': channel_usage,
                    'efficiency':1/(float(channel_usage * abs(value-m[5]))) if value-m[5] else 0,
                    'velocity': m[10]
                })
        count += 1       

print("Data exported correctly!")
            
        
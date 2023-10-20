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

with open('./data/data.csv', 'w+', newline='') as csvfile:
    fieldnames = ['real_distance','meassured_distance','simulation_type','min_delta_ftm','burst_period','burst_exponent','burst_duration','ftm_per_burst', 'error', 'session_time', 'channel_time', 'channel_usage', 'efficiency', 'velocity']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    subfolders = [ f.path for f in os.scandir('./data/') if f.is_dir() ]
    for subfolder in subfolders:
        meassurment_type = subfolder.replace('./data/', '')
        parameters_configuration = [ f.path for f in os.scandir(subfolder) if f.is_dir() ]
        for parameter_config in parameters_configuration:
            parameters = parameter_config.replace(subfolder + '/', '')
            parameters = parameters.split('-')
            files = sorted(glob.glob(parameter_config + "/*m"))
            for file in files:
                print(file)
                if not file_is_empty(file):
                    curr_measurement = np.loadtxt(file)
                    for m in curr_measurement:
                        value = int(m[1]) / 2 / (10000 * 0.3)
                        channel_usage = abs(float(m[4]/m[3])*100)
                        writer.writerow({
                            'real_distance': m[0],
                            'meassured_distance': value,
                            'simulation_type': meassurment_type,
                            'min_delta_ftm': parameters[0],'burst_period': parameters[1],
                            'burst_exponent': parameters[2],'burst_duration': parameters[3],
                            'ftm_per_burst':parameters[4],
                            'error': value-m[0],
                            'session_time': abs(m[3]), 
                            'channel_time': abs(m[4]),
                            'channel_usage': channel_usage,
                            'efficiency':1/(float(channel_usage * abs(value-m[0]))) if value-m[0] else 0,
                            'velocity': m[5]
                        })

print("Data exported correctly!")
            
        
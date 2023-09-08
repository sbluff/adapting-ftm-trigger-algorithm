#the aim of this script is to export all the simulation data to the csv file meassurements.csv
# WARNING! The content of the file will be overwritten and only the current data will be stored in the file.

import os
import csv
import glob
import numpy as np

def file_is_empty(filename):
    with open(filename)as fin:
        for line in fin:
            line = line[:line.find('#')]  # remove '#' comments
            line = line.strip() #rmv leading/trailing white space
            if len(line) != 0:
                return False
    return True

with open('./meassurements.csv', 'w', newline='') as csvfile:
    fieldnames = ['real_distance','meassured_distance','meassurement_type','min_delta_ftm','burst_period','burst_exponent','burst_duration','ftm_per_burst', 'error']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    subfolders = [ f.path for f in os.scandir('./') if f.is_dir() ]
    for subfolder in subfolders:
        meassurment_type = subfolder.replace('./', '')
        parameters_configuration = [ f.path for f in os.scandir(subfolder) if f.is_dir() ]
        for parameter_config in parameters_configuration:
            parameters = parameter_config.replace(subfolder + '/', '')
            parameters = parameters.split('-')
            files = sorted(glob.glob(parameter_config + "/*m"))
            for file in files:
                print(file)
                curr_distance = int(file.split('/').pop().rstrip(file.split('/').pop()[-1]))
                if not file_is_empty(file):
                    curr_measurement = np.loadtxt(file)
                    for m in curr_measurement:
                        value = int(m[0]) / 2 / (10000 * 0.3)
                        writer.writerow({'real_distance': curr_distance, 'meassured_distance': value, 'meassurement_type': meassurment_type, 'min_delta_ftm': parameters[0],'burst_period': parameters[1],'burst_exponent': parameters[2],'burst_duration': parameters[3],'ftm_per_burst':parameters[4], 'error': value-curr_distance})

print("Data exported correctly!")
            
        
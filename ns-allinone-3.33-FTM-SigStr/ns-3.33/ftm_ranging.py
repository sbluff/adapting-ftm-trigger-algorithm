from pathlib import Path
import subprocess
import time
import numpy as np
import json
import os

f = open('./ftm_ranging/simulations/simulation_parameters.json')
data = json.load(f)
simulation_type = data['simulation_type']
error_models = ['wireless']
burst_duration = data['burst_duration']
burst_period = data['burst_period']
burst_exponent = data['burst_exponent']
min_delta_ftm = data['min_delta_ftm']
ftm_per_burst = data['ftm_per_burst']
results_path = "./ftm_ranging/simulations/" + simulation_type + '/' + str(min_delta_ftm) + '-' + str(burst_duration) + '-' + str(burst_exponent) + '-'  + str(burst_period) + '-' + str(ftm_per_burst) + '/'

def performTests():
    error_model_index = 0
    for curr_error_model in error_models:
        for curr_dist in range(1, 101):
            print(curr_error_model, curr_dist, "m")
            output = results_path
            #¢reate folder if it doesnt exist
            try: 
                os.mkdir(output) 
            except OSError as error: 
                print(error)
            
            #compose file name      
            if curr_dist < 10:
                output += "0" + str(curr_dist)
            else:
                output += str(curr_dist)
            output += "m"
            print(output)

            # create empty output file for ns-3 to append if it doesnt exist
            filePath = Path(output)
            filePath.touch(exist_ok= True)
            curr_file= open(filePath,"w+")            
            curr_file.close()

            if curr_dist % 5 != 0:
                continue
            
            waf_command = ["--run=ftm-ranging-" + simulation_type,
                    "--distance=" + str(curr_dist),
                    "--error=1",
                    "--filename=" + output,
                    "--min_delta_ftm=" + str(min_delta_ftm),
                    "--burst_duration=" + str(burst_duration),
                    "--burst_exponent=" + str(burst_exponent),
                    "--burst_period=" + str(burst_period),
                    "--ftm_per_burst=" + str(ftm_per_burst),
                    ]
            print(waf_command)
            waf_string = ' '.join(waf_command)
            subprocess.run(["./waf", waf_string])
        error_model_index += 1

def main():
    performTests()
    os.system('sudo mv *.pcap ' + results_path)
    os.system('python3 ./ftm_ranging/visualize_5m_steps.py')
    os.system('python3 ./ftm_ranging/visualize_10m_steps.py')

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    time_elapsed = round(end_time - start_time, 3)
    print("DONE")
    print("Time elapsed: " + str(time_elapsed) + 's')


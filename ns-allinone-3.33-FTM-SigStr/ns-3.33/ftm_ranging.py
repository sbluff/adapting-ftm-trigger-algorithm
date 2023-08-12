from pathlib import Path
import subprocess
import time
import numpy as np
import json

f = open('./ftm_ranging/simulations/simulation_parameters.json')
data = json.load(f)
error_models = data['error_models']
burst_duration = data['burst_duration']
burst_period = data['burst_period']
burst_exponent = data['burst_exponent']
min_delta_ftm = data['min_delta_ftm']
ftm_per_burst = data['ftm_per_burst']
results_path = "ftm_ranging/simulations/" + str(min_delta_ftm) + '-' + str(burst_duration) + '-' + str(burst_exponent) + '-'  + str(burst_period) + '-' + str(ftm_per_burst) + '/'

def performTests():
    error_model_index = 0
    for curr_error_model in error_models:
        for curr_dist in range(1, 101):
            print(curr_error_model, curr_dist, "m")
            output = './' + results_path
            if curr_dist < 10:
                output += "0" + str(curr_dist)
            else:
                output += str(curr_dist)
            output += "m"
            print(output)

            # create empty output file for ns-3 to append
            filePath = Path(output)
            filePath.touch(exist_ok= True)
            curr_file= open(filePath,"w+")
            
            # curr_file = open(output, "w+")
            curr_file.close()

            if curr_dist % 5 != 0:
                continue
            
            waf_command = ["--run=ftm-ranging",
                    "--distance=" + str(curr_dist),
                    "--error=" + str(error_model_index),
                    "--filename=" + output,
                    "--min_delta_ftm=" + str(min_delta_ftm),
                    "--burst_duration=" + str(burst_duration),
                    "--burst_exponent=" + str(burst_exponent),
                    "--burst_period=" + str(burst_period),
                    "--ftm_per_burst=" + str(ftm_per_burst),
                    ]
            waf_string = ' '.join(waf_command)
            subprocess.run(["./waf", waf_string])
        error_model_index += 1

def main():
    performTests()

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    time_elapsed = round(end_time - start_time, 3)
    print("DONE")
    print("Time elapsed: " + str(time_elapsed) + 's')


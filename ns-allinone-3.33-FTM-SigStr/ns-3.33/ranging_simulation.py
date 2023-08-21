import json
import os

os.setuid(0)

min_delta_ftm = [16,15,15,15,15]
burst_duration = [10,10,10,10,10]
burst_exponent = [3,3,3,3,3]
burst_period = [12,12,12,12,12]
ftm_per_burst = [2,3,4,5,6]

with open('ftm_ranging/simulations/simulation_parameters.json', 'r+') as f:
    data = json.load(f)
    iterate = True
    for i in range (1,5):
        for item in data:
            if item == 'min_delta_ftm':
                iterate = True
                data[item] = min_delta_ftm[i]
            elif item == 'burst_duration':
                iterate = True
                data[item] = burst_duration[i]
            elif item == 'burst_exponent':
                iterate = True
                data[item] = burst_exponent[i]
            elif item == 'burst_period':
                iterate = True
                data[item] = burst_period[i]
            elif item == 'ftm_per_burst':
                iterate = True
                data[item] = ftm_per_burst[i]
            elif item == 'error_models':
                iterate = False    
            print(data)    
                
            if iterate:    
                f.seek(0)        # <--- should reset file position to the beginning.
                json.dump(data, f, indent=2)
                f.truncate()     # remove remaining part
                
                os.system('python3 ./ftm_ranging.py')
                os.system('python3 ./ftm_ranging/visualize_5m_steps.py')
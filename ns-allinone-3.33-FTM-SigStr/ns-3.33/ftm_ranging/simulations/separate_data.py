import pandas as pd
import os


def separate_csv():
    simulation_types = ['fix_position', 'circle_mean', 'circle_velocity', 'brownian']
    df = pd.read_csv('data/data.csv')
    print(df.size)
    for simulation in simulation_types:
        aux = df.loc[(df.simulation_type == simulation)]
        print(aux.size)
        aux.to_csv('data/data-' + simulation + '.csv')
        
    # os.remove("data/data.csv")  
    

separate_csv()      
    

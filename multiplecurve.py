# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 14:40:00 2020

@author: 03Jamakate17
"""
import singlecurve as sc
import numpy as np
import pandas as pd

data_start = 60
data_end  = 200             # replace it with robouster design of -40 seconds after experiment enc

def split_big_data(Data, begasung_column = 5, dataset_number = 0):
    data_to_be_splitted = Data.iloc[:,(dataset_number +7)]             #8th Column has data this is importatn
    temperature_data_column = Data.iloc[:,6 ]
    begasung_index_start, begasung_index_end = get_start_end_index(Data)
 
    splitted_data = pd.DataFrame()
    
    i= 1
    for experiment_start_index, experiment_end_index in  zip(begasung_index_start, begasung_index_end):
       
        experiment_number = "Experiment Nr. "+ str(i)
        start_ = experiment_start_index-data_start
        end_ = experiment_end_index + data_end
        data_temporary= (data_to_be_splitted.iloc[start_: end_]).reset_index(drop = True)   
        splitted_data[str(experiment_number)] = data_temporary
        i= i+1
    
    temperature_value =[]
    for experiment_start_index in begasung_index_start:
        corresponding_temperature_at_experiment_start = temperature_data_column[experiment_start_index]
        temperature_value.append(corresponding_temperature_at_experiment_start)
    
    splitted_data.columns = temperature_value  
    
    return splitted_data
    


def get_start_end_index(Data, begasung_column = 5):
    begasung_data = Data.iloc[:,begasung_column]              #here is begasung beginn data
    begasung_data_diff = begasung_data.diff()                # diff of data
    begasung_data_diff =  begasung_data_diff.fillna(0)
    begasung_index_null = (begasung_data_diff.nonzero())            # all non o diffs 
    begasung_index = begasung_index_null[0]                      #0 becasue  diff. non zero returns tuple
    #begasung_index= np.delete(begasung_index_null , 0)
    #begasung_number = len(begasung_index)/2              # through 2 because each begasung registerd twice
    
    begasung_index_start = begasung_index[::2]
    begasung_index_end  = begasung_index [1::2]    
    
    return begasung_index_start, begasung_index_end

  
def get_curve_parameters_from_big_data(splitted_data, timestamp = False, for_plotting = True):
    curve_parameter_list = []
    temperature = splitted_data.columns
    for i in range(len(splitted_data.columns)):
    
        data_= splitted_data.iloc[:,i]
        if(timestamp == True and for_plotting == True ):
            curve_parameter = sc.parameter_calculator(data_, timestamp = True, for_plotting = True)
        
        elif(timestamp == True and for_plotting == False ):
            curve_parameter = sc.parameter_calculator(data_, timestamp = True, for_plotting = False)
        
        elif(timestamp == False and for_plotting == False):
            curve_parameter = sc.parameter_calculator(data_, timestamp = False , for_plotting = False)
        elif(timestamp == False and for_plotting == True):
            curve_parameter = sc.parameter_calculator(data_, timestamp = False , for_plotting = True)
        
        curve_parameter_list.append(curve_parameter)
    
    curve_parameter_df = pd.DataFrame(curve_parameter_list, columns = ['I Stable', 'I 90', 'I 10', 'T 90', 'F 90', 'Baseline'])
    curve_parameter_df.insert(0, column = 'Temperature', value = temperature)

    return curve_parameter_df
        
        
   
""" k garnu parxa ta 
    first ma duita option rakheko xa, kina ki tesma ta begasung end ko data hunxa naii vanesi
    tyo kina use nagarni, ta, tyo use garera garda kheri dherai ramro hunxa
    tespaxi button haru, kun kun thichda, kun kun function haru hunxa vanera pani hunxa
    tespaxi index number haru milauni
    tespaxi scaling haru milauni
    ani sabai vaye paxi balla tyo save ko kura garni,natra tyo kura arthahin xa
    

"""
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 14:39:41 2020

@author: 03Jamakate17
"""

import pandas as pd
import numpy as np

import multiplecurve as mc
good_data_limit = 7
medium_data_limit = 20
look_back_index_for_i_stable = 30
look_ahead_index_for_i_stable = 5



def derrivative_calculator(Data):
    return Data.diff()

def movingmedian_calculator(Data, position):
    return Data.rolling(position,center =True).median() #what happens to nan values here

def movingmean_calculator(Data, position):
    return Data.rolling(position).median() #what happens to nan values here 

def standard_deviation_calculator(Data):
    return np.std(Data)

def remove_nan_from_numpy(Data):
    return Data[np.logical_not(np.isnan(Data))]

def find_sign_change_in_numpy(Data):
    return np.where(np.diff(np.sign(Data)) != 0 )[0] +1 

def check_quality_of_data(Data):
    '''
    The idea is to change how much the index of minimum and maximum differential
    deviates when smoothing is changed. If the data is very noisy, this deviation 
    will be much higher than when the data is less noisy. 
    '''
    min_diff_for_std_position = []  #forward declared array to store std deviation for different smoothing value
    max_diff_for_std_position = []
    for i in range (1, 40):
        data_for_std_derivative = movingmedian_calculator(Data, i ) #check std de
        derivative_std_data = derrivative_calculator(data_for_std_derivative)
        min_diff_for_std_position.append(derivative_std_data.idxmin())
        max_diff_for_std_position.append(derivative_std_data.idxmax())
    
    deviation_min_diff = standard_deviation_calculator(min_diff_for_std_position)
    deviation_max_diff =  standard_deviation_calculator(max_diff_for_std_position)
    
    if((deviation_max_diff < good_data_limit) and (deviation_min_diff < good_data_limit)):
        data_good_enough= 'good'  # data quality is good
    elif ((deviation_max_diff < medium_data_limit) and (deviation_min_diff <medium_data_limit)):
        data_good_enough= 'medium'    #medium data quality
    elif ((deviation_max_diff > medium_data_limit) or (deviation_min_diff > medium_data_limit)):
        data_good_enough= 'bad' #bad data qulaity 
            
        
 
    
    return deviation_max_diff, deviation_min_diff, data_good_enough

def determine_position_of_min_max_derrivative(Data):
     derivate_of_data_to_check_rising_or_falling = derrivative_calculator(Data)
     position_of_min =  derivate_of_data_to_check_rising_or_falling.idxmin()
     position_of_max =  derivate_of_data_to_check_rising_or_falling.idxmax()
     return position_of_min, position_of_max

def determine_curve_rising_or_falling(Data):
   
    position_of_min_, position_of_max_ =  determine_position_of_min_max_derrivative(Data)
  
    if(position_of_max_ < position_of_min_):  #curve is rising, when position of max is bigger than min
         rising = True
    else:
         rising = False
    return rising 
    
def baseline_calculator(Data):
    position_of_min_, position_of_max_ = determine_position_of_min_max_derrivative(Data)
    curve_rising= determine_curve_rising_or_falling(Data)
    if(curve_rising== True):
        baseline_data = Data.iloc[:position_of_max_].array
    else:
        baseline_data = Data.iloc[:position_of_min_].array
    splitted_baseline_data = np.array_split(baseline_data, 3)  
    std_of_splitted_baseline_seg_0 = np.std(remove_nan_from_numpy(splitted_baseline_data[0]))
    std_of_splitted_baseline_seg_1 = np.std(remove_nan_from_numpy(splitted_baseline_data[1]))
    std_of_splitted_baseline_seg_2 = np.std(remove_nan_from_numpy(splitted_baseline_data[2]))
    std_of_splitted_baseline_data = np.array([std_of_splitted_baseline_seg_0,
                                              std_of_splitted_baseline_seg_1,
                                              std_of_splitted_baseline_seg_2])
    
                                      
    
    
    position_min_std = np.argmin(std_of_splitted_baseline_data)
    return np.mean(remove_nan_from_numpy(splitted_baseline_data[position_min_std]))
    #todo smoothing greater than 20 does not work for experiment 5



def parameter_calculator(Data, timestamp , for_plotting ):    #maximum and minimum derivates are only used to determine if the curve is ring and falling and istable. That is legitimate
    baseline = baseline_calculator(Data)
    if (timestamp == False):
        curve_rising = determine_curve_rising_or_falling(Data) #for time stamped data, things should be changed in curve drawing and not here
        position_of_min, position_of_max = determine_position_of_min_max_derrivative(Data)
        
        if(curve_rising == True):
            i_stable= (Data[(position_of_min - look_back_index_for_i_stable):position_of_min]).median() 
          
                          
                               
          
        else:
            i_stable = (Data[(position_of_max - look_back_index_for_i_stable):(position_of_max-look_ahead_index_for_i_stable)]).median()
            
    if(timestamp != False):
            i_stable = (Data[len(Data)-mc.data_end - mc.data_start :len(Data)-mc.data_end]).median()      #look 30 seconds back before experiment ends
        
   
    i90 = 0.9*(i_stable - baseline ) +baseline
    i10 = 0.1*(i_stable - baseline ) +baseline
        
    pre_data_for_t90 = remove_nan_from_numpy((Data - i90).to_numpy())
    pre_data_for_f90 = remove_nan_from_numpy((Data -i10).to_numpy())
    sign_change_index_t90 = find_sign_change_in_numpy(pre_data_for_t90)
    sign_change_index_f90 = find_sign_change_in_numpy(pre_data_for_f90)

    
    if(for_plotting == False):
        
        if(timestamp == True):
            t90 = sign_change_index_t90[0] - mc.data_start
            f90 = sign_change_index_f90[-1] - (len(Data)-mc.data_end)
        
        elif(timestamp == False):
            position_of_min, position_of_max = determine_position_of_min_max_derrivative(Data)
            curve_rising = determine_curve_rising_or_falling(Data) #for time stamped data, things should be changed in curve drawing and not here
            if(curve_rising == True):
                t90 = sign_change_index_t90[0] - position_of_max
                f90 = sign_change_index_f90[-1] - position_of_min
            elif(curve_rising ==  False):
                t90 = sign_change_index_t90[0] - position_of_min
                f90 = sign_change_index_f90[-1] - position_of_max
     #   i90 = i90 -baseline
      #  i10 = i10 -baseline 
               
    if(for_plotting == True):
        t90 = sign_change_index_t90[0]
        f90 = sign_change_index_f90[-1] 
            
                


   
        
    
    
    return i_stable, i90, i10 , t90, f90 , baseline

    
    #yo mug laii funktioneren ma lyaunu paryo
    #tespaxi multiple curve laii halnu paryo
    #tespaxi excel export garnu paryo
    #kina milena ta kura patta laugnu parxa ani tha hunxa balla

    
    
    
        
    
    
    
    
    
    
    
    
    
        
        
        
    
    


        
         
         
            
        
        

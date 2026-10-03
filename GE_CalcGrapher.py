# This code generates the relevant graphs for ground effect testing
# it also calculates the step responses and give the entire time response characteristics
# This file can only be called by the Report Generator file

# The pipeline is as follows:
# SITL Mission Plan
# Run SITL
# If report is asked
# Create the JSON file with the relevant information of the created Flight Plan
#   Run the report generator
#       Basic test information is printed
#       Write up is printed
#   If graphs and step info is requested
#       This program first plots the required plots for characterization
#       Next using the JSON file, it figures out which Waypoints are the step response points
#       When the log has detected these points, it will automatically begin the step response characterization
#       Finally displays these results for every test where a test response was ordered

# Since this file will mainly be called from the Report Generator, this will be only for Ground Effect test
# For future versions where different graphs are needed, this file can be branched and the same logic can be used

# Imports
import pandas as pd
import matplotlib as mpl
import json

# Extract JSON info - again
with open('test_information.json', 'r') as f:
    test_information = json.load(f)

# Process the data by first loading it into variables which we can use
# The get command ensures if there is no value, it will just skip it or put NaN
pass_flog_path = test_information.get('Flight_log_path',False)
pass_airframe_name = test_information.get('Airframe_Name',"Rascal - Default")
pass_cruise_speed = test_information.get('Airframe_Cruise_Speed',0)
pass_leg_no = test_information.get('Number_of_legs',0)
pass_run_alt = test_information.get('Run_Altitude',0)
pass_run_dist = test_information.get('Run_Distance',0)
pass_run_step_duration = test_information.get('Run_Step_Duration',0)
pass_run_step_percent = test_information.get('Run_Step_Percent',0)
pass_test_type = test_information.get('Test_Type',"DEFAULT")
pass_flog_number = test_information.get('Flight_Log_Number',"0000000.BIN")
pass_flog_number = pass_flog_number.removesuffix(".BIN")


##########################
# Function definition area
##########################

def cen_moving_avg(noisy_array,window_size):
    # Centered moving average algorithm
   # This is distance from center to other end - actual window is (this*2)+1
    clean_array = []
    true_size = (window_size*2)+1
    for i in range(window_size, len(noisy_array)-window_size):
        numerator = 0
        for j in range(-window_size, window_size+1):
            numerator += noisy_array[i+j]
        clean_array.append(numerator/true_size)
    return clean_array

#####################
# Main code area
#####################


# Plotting the data
# This code is mainly developed for using with GroundEffect_FlightPlan.py
# But I think this can be branched later on for a different report generator
# This is a test to check if branch change has actually worked - I'm going to leave this comment here anyway
# Import section for other uses
from datetime import datetime
import subprocess
import os
import json

# Fancy ass title
title = r"""
     _____ _ _       _     _     _____         _     ____                       _    
    |  ___| (_) __ _| |__ | |_  |_   _|__  ___| |_  |  _ \ ___ _ __   ___  _ __| |_  
    | |_  | | |/ _` | '_ \| __|   | |/ _ \/ __| __| | |_) / _ \ '_ \ / _ \| '__| __| 
    |  _| | | | (_| | | | | |_    | |  __/\__ \ |_  |  _ <  __/ |_) | (_) | |  | |_  
    |_|   |_|_|\__, |_| |_|\__|   |_|\___||___/\__| |_| \_\___| .__/ \___/|_|   \__| 
               |___/                                          |_|                    
"""
format_total_row_len = 140
# For centering the title
for line in title.splitlines():
    print(line.center(format_total_row_len))
print("="*format_total_row_len)

# Just loading all the test information
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
pass_flog_number = test_information.get('Flight_Log_Number',"00000000.BIN")

if isinstance(pass_flog_number, int):
    pass_flog_number = f"{pass_flog_number:08d}.BIN"

pass_flog_number = pass_flog_number.removesuffix(".BIN")
current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# To start making the table like format that can be copied and pasted into Google Docs
if pass_test_type == "GE":
    report_title = "Ground Effect Test Flight"
elif pass_test_type == "NO":
    report_title = "Normal Test Flight"
else:
    report_title = "Fuck all test flight"  # <-- remove later lmao
print(report_title.center(format_total_row_len))

# The introduction table with the basic information
format_margin = 2
format_first_col = int((format_total_row_len-2*format_margin)/2)
print(f"{'|'}{'-'*format_first_col}{'|'}{'-'*format_first_col}{'|'}")
print(f"|{'Aircraft Name':^{format_first_col}}|{pass_airframe_name:^{format_first_col}}|")
print(f"|{'Flight Log Path':^{format_first_col}}|{pass_flog_path:^{format_first_col}}|")
print(f"|{'Flight Date and Time':^{format_first_col}}|{current_datetime:^{format_first_col}}|")
print(f"|{'Cruise Speed':^{format_first_col}}|{pass_cruise_speed:^{format_first_col}}|")
print(f"{'|'}{'-'*format_first_col}{'|'}{'-'*format_first_col}{'|'}")

# Making the Test Matrix
print(f"{'|'}{'Test Matrix':^{format_total_row_len}}{'|'}")

# For formatting the table
format_table_col = int(format_total_row_len / 5)
print(f"{'|'}{'Run No':^{format_table_col}}{'|'}{'Altitude':^{format_table_col}}{'|'}{'Distance':^{format_table_col}}{'|'}"
      f"{'Step Duration':^{format_table_col}}{'|'}{'Step Percent':^{format_table_col}}{'|'}")
pos_message = ""
neg_message = ""
for i in range(pass_leg_no):
    pos_step,neg_step = pass_run_step_percent[i]
    if pos_step > 0:
        pos_message = "+"
    if neg_step > 0:
        neg_message = "-"
    print(f"{'|'}{f'Test - {i+1}':{pass_leg_no[i]}'}"
          f"{'|'}{pass_run_alt[i]:^{format_table_col}}"
          f"{'|'}{pass_run_dist[i]:^{format_table_col}}"
          f"{'|'}{pass_run_step_duration[i]:^{format_table_col}}"
          f"{'|'}{f'{pos_message}{pos_step},{neg_message}{neg_step}':^{format_table_col}}")
    pos_message = ""
    neg_message = ""
print("-"*format_total_row_len)
# Write-up
print("\n\nTesting procedure")
print("~"*len("Testing procedure"))
print("The plane has taken off from the Waterfly Warehouse, with a heading of 0 degree")
print("After which it performs a left turn once it has obtained the desired cruising altitude")
print("This altitude is also the reference for the plane to reach once a test run or leg is completed")
print("The plane performs one more left turn and begins to approach the testing leg")
print("The first waypoint before going to the required testing altitude is a Loiter-to-Alt command")
print("The plane performs a circle maneuver to descend or ascend in altitude based on the altitude required")
print("Once the test altitude has been achieved, it performs one final circle to change the heading into the test path")
print("The test has officially commenced from this point onwards \n")
if any(pass_run_step_percent):
    print("As a step disturbance was ordered, the duration and percent change are calculated and correspondingly")
    print("waypoints are placed in the flight path. The waypoints ensure a step change in altitude only")
    print("They do not however, apply the disturbance to the low level controllers \n")
    print("NOTE: This is a known issue and we are only testing the TECS controller - a Lua script can be used to change this later")
print("Intermediate waypoints are defined which can cause small bumps in the flight path ")
print(f"The test runs are executed a total of {pass_leg_no} times as ordered by the user")
print("Each time the plane completes a test run, it takes a left turn and prepares itself by climbing to the relief altitude")
print("Buffer waypoints are also added at the end of each test run to ensure it can safely climb to said altitude")
print("It then performs a series of left turns and prepares for the next leg \n")
print("Each time, the racetrack style path gets slightly deviated if asked by the user")
print("This is useful to visualize the flight tests later in a viewer as all tests will be at different locations")
print("Once the ordered tests are completed, as this is an SITL simulation, the plane is ordered to land")
print("The plane attempts to go home and land, and once landed, it changes to Manual mode and indicating it has crashed")
print("The user at this point kills the SITL simulation and this report is generated\n")

# A section to call the bin2csv.py and start the conversion into CSV and plotting the required graphs
print("Would you like to convert the flight log into a CSV file and start calculations? (Y/N)")
check_calc = input().upper()
if check_calc == "Y":
    print("\n Converting into CSV....")
    # !!WARNING!! - THIS EXPECTS THE BIN2CSV CODE TO BE IN THE SAME LOCATION AS THIS FILE
    # MAKE IT EXPLICIT IN THE FUTURE IF YOU CANNOT HAVE IT IN THE SAME LOCATION
    subprocess.run(["python3", "/home/kiryuzerodev/Waterfly Python Code/bin2csv_custom.py",pass_flog_path])
    print("Starting process of calculations and plotting...")
    # !!WARNING!! - THE PATH HAS BEEN HARDCODED FOR NOW WHICH MEANS THIS WORKS ONLY FOR MY SYSTEM
    # YOU MUST CHANGE IT TO WHERE THE CSV FILES ARE BEING STORED OR ELSE THIS WON'T WORK
    flog_csv_path = "/home/kiryuzerodev/Waterfly Python Code/flight_csv/"
    flog_csv_path += pass_flog_number
    subprocess.run(["python3", "/home/kiryuzerodev/Waterfly Python Code/clean_the_CSVs.py",flog_csv_path])

    # Finally automatically pass the cleaned file to calcgrapher to complete the pipeline
    cleaned_path = os.path.join(flog_csv_path, "Cleaned")

    subprocess.run(["python3", "/home/kiryuzerodev/Waterfly Python Code/GE_CalcGrapher.py",cleaned_path])
else:
    print(f"\n Thank you for using this script! Flight log can be found at: \n{pass_flog_path}")
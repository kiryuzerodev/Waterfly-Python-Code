# This code is mainly developed for using with GroundEffect_FlightPlan.py
# But I think this can be branched later on for a different report generator
# This is a test to check if branch change has actually worked - I'm going to leave this comment here anyway
# Import section for other uses
from datetime import datetime

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
import json
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
    print(f"{'|'}{f'Test - {pass_leg_no[i]}':^{format_table_col}}"
          f"{'|'}{pass_run_alt[i]:^{format_table_col}}"
          f"{'|'}{pass_run_dist[i]:^{format_table_col}}"
          f"{'|'}{pass_run_step_duration[i]:^{format_table_col}}"
          f"{'|'}{f'{pos_message}{pos_step},{neg_message}{neg_step}':^{format_table_col}}")
    pos_message = ""
    neg_message = ""

# Write-up
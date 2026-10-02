# This code is mainly developed for using with GroundEffect_FlightPlan.py
# But I think this can be branched later on for a different report generator
# This is a test to check if branch change has actually worked - I'm going to leave this comment here anyway
# Import section for other uses
from datetime import datetime

# Fancy ass title
print(r"""
     _____ _ _       _     _     _____         _     ____                       _    
    |  ___| (_) __ _| |__ | |_  |_   _|__  ___| |_  |  _ \ ___ _ __   ___  _ __| |_  
    | |_  | | |/ _` | '_ \| __|   | |/ _ \/ __| __| | |_) / _ \ '_ \ / _ \| '__| __| 
    |  _| | | | (_| | | | | |_    | |  __/\__ \ |_  |  _ <  __/ |_) | (_) | |  | |_  
    |_|   |_|_|\__, |_| |_|\__|   |_|\___||___/\__| |_| \_\___| .__/ \___/|_|   \__| 
               |___/                                          |_|                    
""")
print("="*82)

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

current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# To start making the table like format that can be copied and pasted into Google Docs
print("\n"*2)
print(f" "*25, "Ground Effect Test Flight ")
print("\n"*2)

# The Table from here on out
format_margin = 2
format_total_row_len = 82
format_first_col = int((format_total_row_len-2*format_margin)/2)
print(f"{'|'}{'-'*format_first_col}{'|'}{'-'*format_first_col}{'|'}")
print(f"|{'Aircraft Name':^{format_first_col}}|{pass_airframe_name:^{format_first_col}}|")
print(f"|{'Flight Log Path':^{format_first_col}}|{pass_flog_path:^{format_first_col}}|")
print(f"|{'Flight Date and Time':^{format_first_col}}|{current_datetime:^{format_first_col}}|")
print(f"|{'Cruise Speed':^{format_first_col}}|{pass_cruise_speed:^{format_first_col}}|")
print(f"{'|'}{'-'*format_first_col}{'|'}{'-'*format_first_col}{'|'}")
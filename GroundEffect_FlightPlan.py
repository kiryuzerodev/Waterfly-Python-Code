#This Python script will create the waypoints for a low ground effect flight, for a given altitude.
#You must calculate the h/b or h/c ratio manually.
#It also takes 4 inputs, 2+ve and 2-ve percentages which denote the step change in altitude to be executed. A value of zero skips the step change

from pymavlink import mavutil
import math
import time
import os
###############################################################################################################
# FUNCTION DEFINITION SPACE
###############################################################################################################
def print_positive_step():
    print("Enter the % Increase in Altitude")
def print_negative_step():
    print("Enter the % Decrease in Altitude")
def print_step_duration():
    print("Enter Step Duration")

def wp_dist2latlng(curr_lat,curr_long,curr_head,next_dist,next_head):
    r = 6371000.0 # Radius of Earth in meters (m)
    lat1 = math.radians(curr_lat)
    lon1 = math.radians(curr_long)
    bear = math.radians(curr_head)

    ang_dist = next_dist/r

    lat2 = math.asin(math.sin(lat1)*math.cos(ang_dist) + math.cos(lat1)*math.sin(ang_dist)*math.cos(bear))
    lon2 = lon1 + math.atan2(math.sin(bear) * math.sin(ang_dist) * math.cos(lat1),
                          math.cos(ang_dist) - math.sin(lat1) * math.sin(lat2))
    # Normalize longitude to [-180, 180]
    lon2 = (lon2+3*math.pi)%(2*math.pi)-math.pi

    return math.degrees(lat2), math.degrees(lon2)


###############################################################################################################
# MAIN CODE SPACE
###############################################################################################################




# ###################################### INPUT INTERFACE ########################################
print("--------------------------------------------------")
print("AUTOMATIC GROUND EFFECT TEST FLIGHT PLANNER - Version 1")
print("Developed by - Harshith Mahesh")
print("Automatically runs JSBSim + ArduPlane SITL")
print("P.S. It is configured for my system only for now")
print("P.P.S I am not a great programmer :(")
print("")
print("All test flights are from Waterfly Warehouse")
print("")
print("All disturbances are started after 5s of test run commencing")
print("---------------------------------------------------")

print("Enter the required number of test runs")
test_runs = int(input())
if test_runs <= 0:
    print("Please enter a positive integer")
    exit()
else:
    test_alt = []
    test_distance = []
    test_step_duration = []
    test_step_percent = [[0.0, 0.0] for _ in range(test_runs)]
    # We are keeping 1st Col as +ve increments and 2nd as -ve increments
    print("Please enter the required details of the test runs")
    print("--------------------------------------------------")
    for i in range(test_runs):
        print(f"Details of Test {i+1}")
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Required Altitude (m)- WARNING: below 1m may cause noisy RangeFinder readings")
        print("*** You must calculate h/b or h/c on your own! ***")
        test_alt.append(float(input()))
        print("Step Disturbance during test?")
        print("1. Positive Step")
        print("2. Negative Step")
        print("3. Both Step - after returning to steady")
        print("4. None")
        step_case = int(input())
        match step_case:
            case 1:
                print_step_duration()
                test_step_duration.append(abs(float(input())))
                print_positive_step()
                test_step_percent[i][0] = abs(float(input()))
                print("Accepted!")
            case 2:
                print_step_duration()
                test_step_duration.append(abs(float(input())))
                print_negative_step()
                test_step_percent[i][1] = abs(float(input()))
                print("Accepted!")
            case 3:
                print_positive_step()
                test_step_percent[i][0] = abs(float(input()))
                print_negative_step()
                test_step_percent[i][1] = abs(float(input()))
                print_step_duration()
                print("***** Both will have the same time! *****")
                test_step_duration.append(abs(float(input())))
                print("Accepted!")
            case 4:
                print("Accepted!")
            case _:
                print("Invalid - Exiting cause idk how to go back")
        print("Enter the total distance of this test run (m)")
        test_distance.append(abs(float(input())))
print("Required Airframe Name - case sensitive! - If it doesn't work, try again lol")
test_airframe_name = str(input())
print("Enter the side deviation (m) between every test run")
print("+ve means EAST or RIGHT")
print("-ve means WEST or LEFT")
print("I fixed latitude bro...")
test_deviation = float(input())
print("Enter LOITER-TO-ALT (m) before and after every test run")
test_loiter_to_alt = abs(float(input()))

##################### MAV LINK COMMANDS ##############################

mav = mavutil.mavlink
wp_dist = 150 # Distance between waypoints
wp_alt = test_loiter_to_alt+25 # Unused waypoint altitudes - eg: takeoff alt


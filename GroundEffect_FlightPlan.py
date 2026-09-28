#This Python script will create the waypoints for a low ground effect flight, for a given altitude.
#You must calculate the h/b or h/c ratio manually.
#It also takes 4 inputs, 2+ve and 2-ve percentages which denote the step change in altitude to be executed. A value of zero skips the step change

###############################################################################################################
# FUNCTION DEFINITION SPACE
###############################################################################################################
def print_positive_step():
    print("Enter the % Increase in Altitude")
def print_negative_step():
    print("Enter the % Decrease in Altitude")

###############################################################################################################
# MAIN CODE SPACE
###############################################################################################################
from pymavlink import mavutil

print("--------------------------------------------------")
print("AUTOMATIC GROUND EFFECT TEST FLIGHT PLANNER - Version 1")
print("Developed by - Harshith Mahesh")
print("Automatically runs JSBSim + ArduPlane SITL")
print("P.S. It is configured for my system only for now")
print("P.P.S I am not a great programmer :(")
print("---------------------------------------------------")

print("Enter the required number of test runs")
test_runs = int(input())
if test_runs <= 0:
    print("Please enter a positive integer")
    exit()
else:
    test_alt = []
    test_step_percent = [[0.0, 0.0] for _ in range(test_runs)]
    # We are keeping 1st Col as +ve increments and 2nd as -ve increments
    print("Please enter the required details of the test runs")
    print("--------------------------------------------------")
    for i in range(test_runs):
        print(f"Details of Test {i+1}")
        print("~~~~~~~~~~~~~~~~~~~~")
        print("Required Altitude (m)- WARNING: below 1m may cause noisy RangeFinder readings")
        print("*** You must calculate h/b or h/c on your own! ***")
        test_alt.append(float(input()))
        print("Step Disturbance during test?")
        print("1. Positive Step")
        print("2. Negative Step")
        print("3. Both Step")
        print("4. None")
        step_case = int(input())
        match step_case:
            case 1:
                print_positive_step()
                test_step_percent[i][0] = abs(float(input()))
                print("Accepted")
            case 2:
                print_negative_step()
                test_step_percent[i][1] = abs(float(input()))
                print("Accepted")
            case 3:
                print_positive_step()
                test_step_percent[i][0] = abs(float(input()))
                print_negative_step()
                test_step_percent[i][1] = abs(float(input()))
                print("Accepted")
            case 4:
                print("Accepted")
            case _:
                print("Invalid - Exiting cause idk how to go back")
        print("Enter the total distance of this test run (m)")
        test_distance =abs(float(input()))
print("Required Airframe Name - case sensitive! - If it doesn't work, try again lol")




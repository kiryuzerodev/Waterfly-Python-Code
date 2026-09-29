#This Python script will create the waypoints for a low ground effect flight, for a given altitude.
#You must calculate the h/b or h/c ratio manually.
#It also takes 4 inputs, 2+ve and 2-ve percentages which denote the step change in altitude to be executed. A value of zero skips the step change
from turtle import distance

from pymavlink import mavutil, mavwp
import math
import time
import os
# Predefinition - for scope related issues
mav = mavutil.mavlink
wp = mavwp.MAVWPLoader()

###############################################################################################################
# FUNCTION DEFINITION SPACE
###############################################################################################################
def print_positive_step():
    print("Enter the % Increase in Altitude")
def print_negative_step():
    print("Enter the % Decrease in Altitude")
def print_step_duration():
    print("Enter Step Duration")

def wp_dist2latlng(curr_lat,curr_long,curr_head,next_dist):
    r = 6371000.0 # Radius of Earth in meters (m)
    lat1 = math.radians(curr_lat)
    lon1 = math.radians(curr_long)
    bear = math.radians(curr_head)

    ang_dist = next_dist/r

    lat2 = math.asin(math.sin(lat1)*math.cos(ang_dist) + math.cos(lat1)*math.sin(ang_dist)*math.cos(bear))
    lon2 = lon1 + math.atan2(math.sin(bear) * math.sin(ang_dist) * math.cos(lat1),
                          math.cos(ang_dist) - math.sin(lat1) * math.sin(lat2))
    # Normalize longitude to -180, 180
    lon2 = (lon2+3*math.pi)%(2*math.pi)-math.pi

    return math.degrees(lat2), math.degrees(lon2)

def turn_left(hdg):  return (hdg - 90.0) % 360.0
def reverse(hdg):    return (hdg + 180.0) % 360.0

def point(along, right):
    """along = metres down the runway heading from home, right = metres to its right (east if hdg=0)"""
    lat_calc, lng_calc = wp_dist2latlng(home_lat, home_lng, takeoff_heading, along)
    return wp_dist2latlng(lat_calc, lng_calc, (takeoff_heading + 90.0) % 360.0, right)

def add_waypoint(mav_command, lat_calc, lng_calc, alt_calc, p1=0, p2=0, p3=0, p4=0, frame=mav.MAV_FRAME_GLOBAL_RELATIVE_ALT):
    global sequence
    # MAVLink_mission_item_message(target_system, target_component, seq, frame, command, current, autocontinue, p1,p2,p3,p4, x, y, z)
    wp.add(mav.MAVLink_mission_item_message(m.target_system, m.target_component, sequence, frame, mav_command,
                                            0, 1, p1, p2, p3, p4, lat_calc, lng_calc, alt_calc))
    sequence = sequence+1
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


wp_dist = 150 # Distance between waypoints
wp_alt = test_loiter_to_alt+25 # Unused waypoint altitudes - eg: takeoff alt
home_lat = 12.886097191929261
home_lng = 79.8657674964945
home_alt = 0.0  # Waterfly Warehouse points
wp_radius = 50.0
wp_takeoff_alt = test_loiter_to_alt +20.0
takeoff_dist = 100.0  # Defaulted for a small craft
turn_heading = 270.0 # Make a turn of this many degrees after every way point
takeoff_heading = 0.0
loiter_radius = 50.0

# Connecting and setting up the communication with SITL on port 5762. 127.0.01 is address. tcp is protocol
m = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
m.wait_heartbeat()
print(f"Heartbeat from system {m.target_system} and component {m.target_component}")

# Check the vehicle is actually at the warehouse (home is set by SITL at boot, not by the mission)
gpi = m.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=10)
if gpi is None or abs(gpi.lat / 1e7 - home_lat) > 0.01 or abs(gpi.lon / 1e7 - home_lng) > 0.01:
  print("WARNING: vehicle is not at the warehouse. Start SITL with:")
  print(f"  fly {test_airframe_name} --custom-location={home_lat},{home_lng},{home_alt},{takeoff_heading:.0f}")

# Get the set cruise speed so we can calc the distance
m.param_fetch_one('AIRSPEED_CRUISE')
pv = m.recv_match(type='PARAM_VALUE', blocking=True, timeout=5)
cruise_speed = pv.param_value if pv and pv.param_id.strip('\x00') == 'AIRSPEED_CRUISE' else 12.0
print(f"Cruise airspeed used for step timing: {cruise_speed:.1f} m/s")
m.param_set_send('WP_RADIUS', wp_radius)

# Start building the mission plan
sequence = 0

# Initializing the mission
add_waypoint(mav.MAV_CMD_NAV_WAYPOINT,home_lat,home_lng,home_alt,frame=mav.MAV_FRAME_GLOBAL)
add_waypoint(mav.MAV_CMD_NAV_TAKEOFF,0,0,wp_takeoff_alt,p1=12)

# The main stuff
lat,lng = point(takeoff_dist,0.0)
add_waypoint(lat,lng,wp_alt)
# To the west side
west_track = -wp_dist
east_track = -wp_dist - test_deviation

# The Racetrack type flight plan
index_step = 0
temp_message = ""
along_cursor = takeoff_dist
for i in range(test_runs):
    alt = test_alt[i]
    dist = test_distance[i]
    up_step, down_step = test_step_percent[i] # extracts the entire row and gives it's columns to the members - **Python**
    has_step = (up_step > 0) or (down_step > 0) # Check if a step disturbance was ordered by the user
    time_step = test_step_duration[index_step] if has_step else 0.0 # Looks like [2 0 1 2] based on times and no disturbance passes
    # meaning test_step_duration is not the same as test_runs index
    if has_step:
        index_step = index_step + 1

        # Printing some shit
        print(f"Step Disturbance for Test Run {i+1} has been received!")
        print("Details are as follows:")
        temp_message = "Positive Step" if test_step_percent[0][i] > 0 else ""
        temp_step = up_step if up_step > 0 else down_step
        if test_step_percent[0][i] > 0 and test_step_percent[1][i]:
            print("Both side step")
        print(f"{temp_message}: {temp_step}")
        temp_message = "Negative Step" if test_step_percent[1][i] > 0 else ""
        temp_step = down_step if down_step > 0 else up_step
        print(f"{temp_message}: {temp_step}")
        print("~~~Zero means no step~~~")

        # To check direction - if it is -ve then it gets multiplied to change which way we are pointing
        track = west_track if i % 2 == 0 else east_track
        direction = -1 if i % 2 == 0 else +1
        settle_dist = 7.5*cruise_speed  # Settle for 7.5s before performing a step disturbance
        step_dist = time_step*cruise_speed # Distance of the step
        needed_dist = settle_dist + ((step_dist+settle_dist) if up_step > 0 else 0) + ((step_dist+settle_dist) if down_step > 0 else 0)
        if needed_dist > dist:
            print(
                f"WARNING Test {i + 1}: distance {dist:.0f} m too short for the steps ({needed_dist:.0f} m needed) - extending")
            dist = needed_dist + settle_dist*2

        # LOITER-TO-ALT and start the process
        start = along_cursor
        lat,lng = point(start,track)
        add_waypoint(mav.MAV_CMD_NAV_LOITER_TO_ALT, lat,lng,alt,p2 = loiter_radius, p4=1)

        # The main run
        pos = start + (direction*dist)
        if up_step > 0:
            # We are putting one waypoint on top in the path and then after the distance, it is set back
            lat,lng = point(pos,track)
            pos = pos + (direction*step_dist)
            add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, lat, lng, alt*(1+up_step / 100.0))
            lat, lng = point(pos, track)
            add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, lat, lng, alt)
            pos = pos +(direction*settle_dist)
        if down_step > 0:
            lat, lng = point(pos, track)
            pos = pos + (direction * step_dist)
            add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, lat, lng, alt * (1 + down_step / 100.0))
            lat, lng = point(pos, track)
            add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, lat, lng, alt)
            pos = pos + (direction * settle_dist)
        end = start + (direction*dist)
        lat,lng = point(end,track)
        add_waypoint(mav.MAV_CMD_NAV_LOITER_TO_ALT, lat, lng, test_loiter_to_alt, p2=loiter_radius, p4=1)

        # NEW: Add a buffer at the end in case there are some overshoots still present
        buffer_along = end + (direction* wp_dist)
        lat, lng = point(buffer_along, track)
        add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, lat, lng, wp_alt)

        # Direction change
        if i < test_runs - 1:
            other_track = east_track if track == west_track else west_track
            lat, lng = point(buffer_along, other_track);
            add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, lat, lng, wp_alt)
            along_cursor = buffer_along
lat, lng = point(takeoff_dist + 2 * wp_dist, 0.0)
add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, lat, lng, wp_alt)
add_waypoint(mav.MAV_CMD_NAV_LAND, home_lat, home_lng, 0)

## Ending the Mission
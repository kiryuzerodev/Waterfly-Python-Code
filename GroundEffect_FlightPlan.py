#This Python script will create the waypoints for a low ground effect flight, for a given altitude.
#You must calculate the h/b or h/c ratio manually.
#It also takes 4 inputs, 2+ve and 2-ve percentages which denote the step change in altitude to be executed. A value of zero skips the step change
# this is a test comment!

from pymavlink import mavutil, mavwp
import math
import os
import json
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

def turn_left(hdg):
    return (hdg - 90.0) % 360.0


def add_waypoint(mav_command, lat_calc, lng_calc, alt_calc, p1=0, p2=0, p3=0, p4=0, frame=mav.MAV_FRAME_GLOBAL_RELATIVE_ALT):
    global sequence
    # MAVLink_mission_item_message(target_system, target_component, seq, frame, command, current, autocontinue, p1,p2,p3,p4, x, y, z)
    wp.add(mav.MAVLink_mission_item_message(m.target_system, m.target_component, sequence, frame, mav_command,
                                            0, 1, p1, p2, p3, p4, lat_calc, lng_calc, alt_calc))
    sequence = sequence+1

class LatLongHead:
    # A class to hold the latitude, longitude, heading, altitude and distance for different aspects
    lat = 0
    lng = 0
    hdg = 0
    alt = 0
    distance = 0
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
print("All disturbances are started after 30s of test run commencing")
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

print("Enter LOITER-TO-ALT height ABOVE each test altitude (m) - min 15, 20 recommended")
loiter_above = max(15.0, abs(float(input())))
test_loiter_to_alt = max(test_alt) + loiter_above      # only used for wp_buffer_alt now
##################### MAV LINK COMMANDS ##############################


wp_dist = 150 # Distance between waypoints
wp_buffer_alt = test_loiter_to_alt # We will be flying to this altitude to prepare for the nexy test
home_lat = 12.886097191929261
home_lng = 79.8657674964945
home_alt = 0.0  # Waterfly Warehouse points
wp_radius = 5.0
takeoff_dist = 200.0  # Defaulted for a small craft
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
curr = LatLongHead()
curr.lat = home_lat
curr.lng = home_lng
curr.hdg = 0
curr.alt = home_alt

# Initializing the mission
curr.alt = home_alt + 30 # The height we want it to ascend to
add_waypoint(mav.MAV_CMD_NAV_WAYPOINT,curr.lat,curr.lng,curr.alt,frame=mav.MAV_FRAME_GLOBAL)
add_waypoint(mav.MAV_CMD_NAV_TAKEOFF,0,0,curr.alt,p1=12)

# The main stuff
# We are going some meters ahead from the takeoff point and then telling it to fly this altitude
curr.lat, curr.lng = wp_dist2latlng(curr.lat, curr.lng, curr.hdg, takeoff_dist)
add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, wp_buffer_alt)
# To turn left after reaching the waypoint
curr.hdg = turn_left(curr.hdg)
curr.lat, curr.lng = wp_dist2latlng(curr.lat, curr.lng, curr.hdg, wp_dist)
curr.alt = test_loiter_to_alt
add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, wp_buffer_alt)
curr.hdg = turn_left(curr.hdg)

# test start ..X... X <- here now
#                   |
#                   |
# H ----------------X
# The Racetrack type flight plan


index_step = 0
temp_message = ""
test = LatLongHead()
deviateFlag = False  # A flag that becomes true after an even test so that the track deviates slightly
                     # prevents multiple tests happening over the same region
for i in range(test_runs):

    test.alt = test_alt[i]
    test.distance = test_distance[i]
    up_step, down_step = test_step_percent[i] # extracts the entire row and gives it's columns to the members - **Python**
    has_step = (up_step > 0) or (down_step > 0) # Check if a step disturbance was ordered by the user
    time_step = test_step_duration[index_step] if has_step else 0.0 # Looks like [2 0 1 2] based on times and no disturbance passes
    # meaning test_step_duration is not the same as test_runs index
    if has_step:
        index_step = index_step + 1

        # Printing some shit
        print(f"Step Disturbance for Test Run {i+1} has been received!")
        print("Details are as follows:")
        temp_message = "Positive Step" if up_step > 0 else ""
        temp_step = up_step if up_step > 0 else down_step
        if up_step > 0 and down_step > 0:
            print("Both side step")
        print(f"{temp_message}: {temp_step}")
        temp_message = "Negative Step" if down_step > 0 else ""
        temp_step = down_step if down_step > 0 else up_step
        print(f"{temp_message}: {temp_step}")
        print("~~~Zero means no step~~~")

    # To check direction - if it is -ve then it gets multiplied to change which way we are pointing
    deviateFlag = True if i%2 == 0 else False  # Use
    settle_dist = 30*cruise_speed  # Settle for 30s before performing a step disturbance
    step_dist = time_step*cruise_speed # Distance of the step
    needed_dist = settle_dist + ((step_dist+settle_dist) if up_step > 0 else 0) + ((step_dist+settle_dist) if down_step > 0 else 0)
    if needed_dist > test.distance + settle_dist*2:
        print(
            f"WARNING Test {i+1}: distance {test.distance:.0f} m too short for the steps ({needed_dist:.0f} m needed) - extending")
        test.distance = needed_dist + settle_dist*2 + 10 # the 10 is there just in case to avoid tailstrikes
    curr.alt = test.alt + loiter_above

    # LOITER-TO-ALT and start the process to first settle the aircraft
    curr.alt = test_loiter_to_alt
    curr.lat, curr.lng = wp_dist2latlng(curr.lat,curr.lng,curr.hdg,settle_dist/2)
    add_waypoint(mav.MAV_CMD_NAV_LOITER_TO_ALT, curr.lat,curr.lng,curr.alt,p1=1 ,p2 = loiter_radius, p4=1)
    # By now we should be at the start of the test
    # First way point at same testing altitude to ensure it flies straight there and is settled
    curr.alt = test.alt
    curr.lat, curr.lng = wp_dist2latlng(curr.lat, curr.lng, curr.hdg, 400)
    add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, curr.alt)

    # This is to ensure a proper stepped descent into every test run
    curr.lat, curr.lng = wp_dist2latlng(curr.lat, curr.lng, curr.hdg, settle_dist)
    add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, curr.alt)

    # The test run. We will check if there is a step and execute the following
    # Note: Step profiles look like
    #         X____<____
    #        /          \
    # X__<__/            \X__<___
    # or the other side for a negative dip

    if up_step > 0:
        # It will be settled at the correct altitude now. Time for the step disturbance
        curr.alt = test.alt*(1+up_step/100)
        curr.distance = step_dist
        curr.lat,curr.lng = wp_dist2latlng(curr.lat,curr.lng,curr.hdg,curr.distance)
        add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, curr.alt)
        test.distance = test.distance - curr.distance

        # Now for the waypoint that will bring it back to the same altitude but a little faster
        curr.alt = test.alt
        curr.distance = settle_dist/2
        curr.lat, curr.lng = wp_dist2latlng(curr.lat, curr.lng, curr.hdg, curr.distance)
        add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, curr.alt)
        test.distance = test.distance - curr.distance
    if down_step > 0:
        # It will be settled at the correct altitude now. Time for the step disturbance
        curr.alt = test.alt * (1 - down_step / 100)
        curr.distance = step_dist
        curr.lat, curr.lng = wp_dist2latlng(curr.lat, curr.lng, curr.hdg, curr.distance)
        add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, curr.alt)
        test.distance = test.distance - curr.distance

        # Now for the waypoint that will bring it back to the same altitude but a little faster
        curr.alt = test.alt
        curr.distance = settle_dist/2
        curr.lat, curr.lng = wp_dist2latlng(curr.lat, curr.lng, curr.hdg, curr.distance)
        add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, curr.alt)
        test.distance = test.distance - curr.distance

    # Here is where the test run has completed - mark the final waypoint!
    curr.distance = max(test.distance,10)
    curr.alt = test.alt
    curr.lat, curr.lng = wp_dist2latlng(curr.lat, curr.lng, curr.hdg, curr.distance)
    add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, curr.alt)

    # NEW: Add a buffer at the end in case there are some overshoots still present
    curr.distance = settle_dist*1.3  # this is for a buffer distance
    curr.alt = wp_buffer_alt
    curr.lat, curr.lng = wp_dist2latlng(curr.lat, curr.lng, curr.hdg, curr.distance)
    add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, curr.alt)


    # Removed the Loiter-to-alt again cause we dont need it. One loiter to alt for the next test is enough
    curr.hdg = turn_left(curr.hdg)

    # Check if the next run has to be offset or not - if true then do it else dont
    if deviateFlag:
        curr.distance = wp_dist + test_deviation
    else:
        curr.distance = wp_dist

    # Add the waypoint
    curr.alt = wp_buffer_alt
    curr.lat, curr.lng = wp_dist2latlng(curr.lat, curr.lng, curr.hdg, curr.distance)
    add_waypoint(mav.MAV_CMD_NAV_WAYPOINT, curr.lat, curr.lng, curr.alt)
    curr.hdg = turn_left(curr.hdg)

# To land instantly after test is done (We dont care about RTL - waste of time and battery in SITL)
add_waypoint(mav.MAV_CMD_NAV_LAND, home_lat, home_lng, 0)

## Run the Mission and then End it once landed  - AI GENERATED
m.waypoint_clear_all_send()
m.waypoint_count_send(wp.count())
for _ in range(wp.count()):
    req = m.recv_match(type=['MISSION_REQUEST', 'MISSION_REQUEST_INT'], blocking=True, timeout=10)
    m.mav.send(wp.wp(req.seq))
m.recv_match(type='MISSION_ACK', blocking=True, timeout=10)

m.arducopter_arm()
m.motors_armed_wait()
m.set_mode('AUTO')
print("The test is now running! Go for a stroll")

while m.motors_armed():
    m.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
print("Your plane has landed successfullay")

log_dir = os.path.expanduser("~/ardupilot/ArduPlane/logs")
log_num = int(open(f"{log_dir}/LASTLOG.TXT").read().strip())
log_path = f"{log_dir}/{log_num}"
os.system("pkill -f arduplane; pkill -f mavproxy; pkill -f JSBSim")
print(f"Log file: {log_dir}/{log_num:08d}.BIN")

Ans = input("Would you like to open the Flight Test report generator interface? (y/n): ")
if Ans == "y":
    print("Transferring the data of the test flight")
    # Defining a dictionary with the ordered test data so that we can parse it later and display it in the report
    test_type = "GE"
    test_information = {
        "Test_type": test_type,
        "Flight_log_path": log_path,
        "Airframe_Name": test_airframe_name,
        "Airframe_Cruise_Speed": cruise_speed,
        "Number_of_legs": test_runs,
        "Run_Altitude": test_alt,
        "Run_Distance": test_distance,
        "Run_Step_Duration": test_step_duration,
        "Run_Step_Percent": test_step_percent, # <--- this will be used to check if we got a +,-,0,Both step cases
    }

    # Since a dictionary is an object in Python, we can now send it using the dump() function of JSON
    with open('test_information.json', 'w') as f:
        json.dump(test_information, f)

    # Now call the report generation file using the following line:
    os.system("python3 GE_ReportGenerator.py")
    # Rest will be continued into the report generation file
else:
    print("The flight log is available at the above location!")
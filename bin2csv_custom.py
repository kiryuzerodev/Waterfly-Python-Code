#Import the needed header file for reading MAVLink
from pymavlink import mavutil

# Where the log is
flight_log_path = "/home/kiryuzerodev/Downloads/Waterfly Test Flights/18 Aug Flight Test at 13_49hrs.bin"

# Using the function in the header or object, using MAVLink connection to open
# the flight log as an object
flight_log = mavutil.mavlink_connection(flight_log_path)


# Using recv_match() will allow us to read messages from the .bin file which
# has become an object. So this is to read a message
# we will keep reading until we get the IMU text. Then from there we can extract
# the time data
# This code also first creates the "Master Time Axis", you will be needing this
# as loop rates will vary and a tolerance needs to be established

Master_Time_Axis = []
last_time = 0 # works as TimeUS is positive and in micro seconds
while True:
    # Receive new message
    msg = flight_log.recv_match()

    # Applicable if we are the end of the .bin file
    if msg is None:
        break

    # Else do this
    # Check if the data is of the IMU
    if msg.get_type() == "IMU":
        # append the time if the time stamp is not already there
        # also check if time is going backwards :|
        if last_time > msg.TimeUS:
            print("data fucked! :D")
            exit(1)
        if last_time != msg.TimeUS:
             Master_Time_Axis.append(msg.TimeUS)
             last_time = msg.TimeUS
             # Loop back to get next data point
# shows number of data points
print(len(Master_Time_Axis))

# Convert into seconds from micro seconds and also make sure the entire
# time axis is increasing
Time_Axis = [0]
for i in range(1,len(Master_Time_Axis)):
    val = (Master_Time_Axis[i]-Master_Time_Axis[0])/1_000_000
    Time_Axis.append(val)
print(Time_Axis[:10])








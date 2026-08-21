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


# Convert into seconds from micro seconds and also make sure the entire
# time axis is increasing
Time_Axis = [0]
for i in range(1,len(Master_Time_Axis)):
    val = (Master_Time_Axis[i]-Master_Time_Axis[0])/1_000_000
    Time_Axis.append(val)


#
# Now we will attempt to read the sensor data - Attitude first
# reload the flight log as we went to the end of the file
flight_log = mavutil.mavlink_connection(flight_log_path)

# Iterate until we start getting the Attitude Data
# ATT contains - Time, DesRoll, Roll, DesPitch, Pitch, DesYaw, Yaw
# and the Active EKF

Attitude_Data = []
while True:
    msg = flight_log.recv_match()
# Logic remains the same as when we read the data for the IMU
    if msg is None:
        break
    if msg.get_type() == "ATT":
        Attitude_Data.append([msg.TimeUS,
                              msg.DesRoll,
                              msg.DesPitch,
                              msg.DesYaw,
                              msg.Roll,
                              msg.Pitch,
                              msg.Yaw])


# Now we will start matching the time stamps and adding them
# with our closest matching IMU timestamps

Attitude_Timed = []
tol = 10_000# Tolerance for how close the data must be, if
#it is less than this we can add it with the time stamp
# NOTE: We will be first checking which is the closest and add
# the data there
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function for adding NaN easily
def nan_row(matime, number_of_values):
    row = [matime]

    for k in range(number_of_values):
        row.append(float("NaN"))

    return row
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
i = 0 # controls Master Time
j = 0 # Data time

# Double pointer tech to keep moving the master time and
# attitude time, and when there is no more master time,
# we just put everything as NaN.
# When there is no close value, we put NaN. This can be
# detected by the fact that if the data point time increases
# and master time is still way back, it means there is no
# matching timestamp and we will proceed to the next one
while i < len(Master_Time_Axis):
    mtime = Master_Time_Axis[i]

    if j < len(Attitude_Data):
        # Attitude_Data[j][0] corresponds to attitude time stamp
        if abs(mtime - Attitude_Data[j][0]) < tol:
            Attitude_Timed.append([
                mtime,
                Attitude_Data[j][1],
                Attitude_Data[j][2],
                Attitude_Data[j][3],
                Attitude_Data[j][4],
                Attitude_Data[j][5],
                Attitude_Data[j][6]
            ])
            i = i + 1
            j = j + 1
        elif mtime > Attitude_Data[j][0]:
            j = j + 1
        else:
            # No measurement for this master time
            Attitude_Timed.append(nan_row(mtime, 6))
            i += 1
    else:
        Attitude_Timed.append(nan_row(mtime, 6))
        i += 1


############# REPEAT FOR REMAINING DATA SETS ###############
# Copied from AI as it is just a repetition of what we did with
# the double pointer technique
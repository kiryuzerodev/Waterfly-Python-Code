#Import the needed header file for reading MAVLink
from pymavlink import mavutil
import csv
import os


# Where the log is
flight_log_path = "/home/kiryuzerodev/Downloads/Waterfly Test Flights/18 Aug Flight Test at 13_49hrs.bin"

# Create the output directory
output_dir = "flight_csv"

os.makedirs(output_dir, exist_ok=True)

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
def time_match(master_time, data, tol, number_of_values):
    timed_data = []

    i = 0
    j = 0

    while i < len(master_time):

        mtime = master_time[i]

        if j >= len(data):
            timed_data.append(nan_row(mtime, number_of_values))
            i += 1
            continue

        data_time = data[j][0]

        if abs(mtime - data_time) < tol:

            timed_data.append([mtime] + data[j][1:])

            i += 1
            j += 1

        elif mtime > data_time:

            j += 1

        else:

            timed_data.append(nan_row(mtime, number_of_values))
            i += 1

    return timed_data
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

#Replaced with a function
Attitude_Timed = time_match(
    Master_Time_Axis,
    Attitude_Data,
    tol,
    6
)

print("ATT timed:", len(Attitude_Timed))


############# REPEAT FOR REMAINING DATA SETS ###############
# Copied from AI as it is just a repetition of what we did with
# the double pointer technique

# For IMU
IMU_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "IMU":
        IMU_Data.append([
            msg.TimeUS,
            msg.I,
            msg.GyrX,
            msg.GyrY,
            msg.GyrZ,
            msg.AccX,
            msg.AccY,
            msg.AccZ
        ])
# For BAROMETER
BARO_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "BARO":
        BARO_Data.append([
            msg.TimeUS,
            msg.I,
            msg.Alt,
            msg.AltAMSL,
            msg.Press,
            msg.Temp,
            msg.CRt,
            msg.SMS,
            msg.Offset,
            msg.GndTemp,
            msg.H,
            msg.CPress
        ])

# For MAGNETOMETER
MAG_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "MAG":
        MAG_Data.append([
            msg.TimeUS,
            msg.I,
            msg.MagX,
            msg.MagY,
            msg.MagZ,
            msg.OfsX,
            msg.OfsY,
            msg.OfsZ,
            msg.MOX,
            msg.MOY,
            msg.MOZ,
            msg.Health
        ])

# For VIBRATION
VIBE_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "VIBE":
        VIBE_Data.append([
            msg.TimeUS,
            msg.IMU,
            msg.VibeX,
            msg.VibeY,
            msg.VibeZ,
            msg.Clip
        ])
# For GPS
GPS_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "GPS":
        GPS_Data.append([
            msg.TimeUS,
            msg.Status,
            msg.NSats,
            msg.HDop,
            msg.Lat,
            msg.Lng,
            msg.Alt,
            msg.Spd,
            msg.GCrs,
            msg.VZ,
            msg.Yaw
        ])
# For RC INPUTS

RCIN_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "RCIN":
        RCIN_Data.append([
            msg.TimeUS,
            msg.C1,
            msg.C2,
            msg.C3,
            msg.C4,
            msg.C5,
            msg.C6,
            msg.C7,
            msg.C8,
            msg.C9,
            msg.C10,
            msg.C11,
            msg.C12,
            msg.C13,
            msg.C14
        ])

# For SERVO OUTPUTS
RCOU_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "RCOU":
        RCOU_Data.append([
            msg.TimeUS,
            msg.C1,
            msg.C2,
            msg.C3,
            msg.C4,
            msg.C5,
            msg.C6,
            msg.C7,
            msg.C8,
            msg.C9,
            msg.C10,
            msg.C11,
            msg.C12,
            msg.C13,
            msg.C14
        ])

GPS_Timed = time_match(
    Master_Time_Axis,
    GPS_Data,
    tol,
    10
)

RCIN_Timed = time_match(
    Master_Time_Axis,
    RCIN_Data,
    tol,
    14
)

RCOU_Timed = time_match(
    Master_Time_Axis,
    RCOU_Data,
    tol,
    14
)

VIBE_Timed = time_match(
    Master_Time_Axis,
    VIBE_Data,
    tol,
    5
)

MAG_Timed = time_match(
    Master_Time_Axis,
    MAG_Data,
    tol,
    11
)

BARO_Timed = time_match(
    Master_Time_Axis,
    BARO_Data,
    tol,
    11
)

with open(os.path.join(output_dir, "attitude.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",
        "DesRoll",
        "DesPitch",
        "DesYaw",
        "Roll",
        "Pitch",
        "Yaw"
    ])

    for i in range(len(Attitude_Timed)):

        row = Attitude_Timed[i].copy()

        row[0] = Time_Axis[i]

        writer.writerow(row)

with open(os.path.join(output_dir, "gps.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",
        "Status",
        "NSats",
        "HDop",
        "Lat",
        "Lng",
        "Alt",
        "Spd",
        "GCrs",
        "VZ",
        "Yaw"
    ])

    for i in range(len(GPS_Timed)):

        row = GPS_Timed[i].copy()

        row[0] = Time_Axis[i]

        writer.writerow(row)

with open(os.path.join(output_dir, "controls.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",
        "RCIN_C1", "RCIN_C2", "RCIN_C3", "RCIN_C4",
        "RCIN_C5", "RCIN_C6", "RCIN_C7", "RCIN_C8",
        "RCIN_C9", "RCIN_C10", "RCIN_C11", "RCIN_C12",
        "RCIN_C13", "RCIN_C14",
        "RCOU_C1", "RCOU_C2", "RCOU_C3", "RCOU_C4",
        "RCOU_C5", "RCOU_C6", "RCOU_C7", "RCOU_C8",
        "RCOU_C9", "RCOU_C10", "RCOU_C11", "RCOU_C12",
        "RCOU_C13", "RCOU_C14"
    ])

    for i in range(len(Master_Time_Axis)):

        row = [Time_Axis[i]]

        row.extend(RCIN_Timed[i][1:])
        row.extend(RCOU_Timed[i][1:])

        writer.writerow(row)

with open(os.path.join(output_dir, "sensors.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",

        "VIBE_IMU",
        "VibeX",
        "VibeY",
        "VibeZ",
        "Clip",

        "MAG_I",
        "MagX",
        "MagY",
        "MagZ",
        "OfsX",
        "OfsY",
        "OfsZ",
        "MOX",
        "MOY",
        "MOZ",
        "MAG_Health",

        "BARO_I",
        "BaroAlt",
        "AltAMSL",
        "Press",
        "Temp",
        "CRt",
        "SMS",
        "Offset",
        "GndTemp",
        "H",
        "CPress"
    ])

    for i in range(len(Master_Time_Axis)):

        row = [Time_Axis[i]]

        row.extend(VIBE_Timed[i][1:])
        row.extend(MAG_Timed[i][1:])
        row.extend(BARO_Timed[i][1:])

        writer.writerow(row)

print("CSV files written to:", output_dir)

print("ATT:", len(Attitude_Timed))
print("GPS:", len(GPS_Timed))
print("RCIN:", len(RCIN_Timed))
print("RCOU:", len(RCOU_Timed))
print("VIBE:", len(VIBE_Timed))
print("MAG:", len(MAG_Timed))
print("BARO:", len(BARO_Timed))
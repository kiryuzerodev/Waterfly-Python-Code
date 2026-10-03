#Import the needed header file for reading MAVLink
from pymavlink import mavutil
import csv
import os
import sys


# Where the log is
if len(sys.argv) < 2:
    print("Usage: python bin2csv_custom.py <flight_log.bin>")
    exit(1)

flight_log_path = sys.argv[1]
file_name = os.path.splitext(os.path.basename(flight_log_path))[0]

# Create the output directory
output_dir = os.path.join("/home/kiryuzerodev/Waterfly Python Code/flight_csv", file_name)

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
# matching timestamp, and we will proceed to the next one

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
            getattr(msg, "H", float("NaN")),
            getattr(msg, "CPress", float("NaN")),
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

# For CONTROL TUNING CTUN
CTUN_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "CTUN":
        CTUN_Data.append([
            msg.TimeUS,
            msg.NavPitch,
            msg.Pitch,
            msg.ThO
        ])

# For PITCH PID
PIDP_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "PIDP":
        PIDP_Data.append([
            msg.TimeUS,
            msg.Tar,
            msg.Act,
            msg.Flags
        ])

# For AIRSPEED
ARSP_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "ARSP":
        ARSP_Data.append([
            msg.TimeUS,
            getattr(msg, "Airspeed", float("NaN"))
        ])

# For RANGEFINDER
RFND_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "RFND":
        RFND_Data.append([
            msg.TimeUS,
            getattr(msg, "Dist", float("NaN"))
        ])

# For FLIGHT MODE
MODE_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "MODE":
        MODE_Data.append([
            msg.TimeUS,
            msg.Mode,
            msg.ModeNum
        ])

# For EKF XKF1
XKF1_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "XKF1":
        XKF1_Data.append([
            msg.TimeUS,
            msg.C,
            msg.Roll,
            msg.Pitch,
            msg.Yaw,
            msg.VN,
            msg.VE,
            msg.VD,
            msg.dPD,
            msg.PN,
            msg.PE,
            msg.PD,
            msg.GX,
            msg.GY,
            msg.GZ,
            msg.OH
        ])

# For EKF XKF2
XKF2_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "XKF2":
        XKF2_Data.append([
            msg.TimeUS,
            msg.C,
            msg.AX,
            msg.AY,
            msg.AZ,
            msg.VWN,
            msg.VWE,
            msg.MN,
            msg.ME,
            msg.MD,
            msg.MX,
            msg.MY,
            msg.MZ,
            msg.IDX,
            msg.IDY,
            msg.IS
        ])

# For EKF XKF3
XKF3_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "XKF3":
        XKF3_Data.append([
            msg.TimeUS,
            msg.C,
            msg.IVN,
            msg.IVE,
            msg.IVD,
            msg.IPN,
            msg.IPE,
            msg.IPD,
            msg.IMX,
            msg.IMY,
            msg.IMZ,
            msg.IYAW,
            msg.IVT,
            msg.RErr,
            msg.ErSc
        ])

# For Navigation NTUN
NTUN_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "NTUN":
        NTUN_Data.append([
            msg.TimeUS,
            msg.Dist,
            msg.TBrg,
            msg.NavBrg,
            msg.AltE,
            msg.XT,
            msg.XTi,
            msg.AsE,
            msg.TLat,
            msg.TLng,
            msg.TAW,
            msg.TAT,
            msg.TAsp
        ])

# For Navigation TECS
TECS_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "TECS":
        TECS_Data.append([
            msg.TimeUS,
            msg.h,
            msg.dh,
            msg.hin,
            msg.hdem,
            msg.dhdem,
            msg.spdem,
            msg.sp,
            msg.dsp,
            msg.th,
            msg.ph,
            msg.pmin,
            msg.pmax,
            msg.dspdem,
            getattr(msg, "iph", float("NaN")),
            getattr(msg, "ith", float("NaN")),
            getattr(msg, "f", float("NaN"))
        ])

# For Power BAT
BAT_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "BAT":
        BAT_Data.append([
            msg.TimeUS,
            getattr(msg, "Instance", float("NaN")),
            msg.Volt,
            msg.Curr,
            msg.CurrTot,
            msg.EnrgTot,
            msg.Temp,
            msg.Res
        ])

# For MISSION COMMANDS
CMD_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "CMD":
        CMD_Data.append([
            msg.TimeUS,
            msg.CTot,
            msg.CNum,
            msg.CId,
            msg.Prm1,
            msg.Prm2,
            msg.Prm3,
            msg.Prm4,
            msg.Lat,
            msg.Lng,
            msg.Alt,
            msg.Frame
        ])
# For LOG MESSAGES
MSG_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "MSG":
        MSG_Data.append([
            msg.TimeUS,
            getattr(msg, "ID", float("NaN")),
            getattr(msg, "Seq", float("NaN")),
            getattr(msg, "Message", "")
        ])

# For GEO FENCE
FNCE_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "FNCE":
        FNCE_Data.append([
            msg.TimeUS,
            msg.Tot,
            msg.Seq,
            msg.Type,
            msg.Lat,
            msg.Lng,
            msg.Count,
            msg.Radius
        ])
# For IMU
IMU_Data = []

flight_log = mavutil.mavlink_connection(flight_log_path)

while True:
    msg = flight_log.recv_match()

    if msg is None:
        break

    if msg.get_type() == "IMU":
        if msg.I == 0:
            IMU_Data.append([
                msg.TimeUS,
                msg.GyrX,
                msg.GyrY,
                msg.GyrZ,
                msg.AccX,
                msg.AccY,
                msg.AccZ
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

XKF1_Timed = time_match(
    Master_Time_Axis,
    XKF1_Data,
    tol,
    15
)

XKF2_Timed = time_match(
    Master_Time_Axis,
    XKF2_Data,
    tol,
    15
)

XKF3_Timed = time_match(
    Master_Time_Axis,
    XKF3_Data,
    tol,
    14
)

NTUN_Timed = time_match(
    Master_Time_Axis,
    NTUN_Data,
    tol,
    12
)

TECS_Timed = time_match(
    Master_Time_Axis,
    TECS_Data,
    tol,
    16
)

CTUN_Timed = time_match(
    Master_Time_Axis,
    CTUN_Data,
    tol,
    3
)

PIDP_Timed = time_match(
    Master_Time_Axis,
    PIDP_Data,
    tol,
    3
)

ARSP_Timed = time_match(
    Master_Time_Axis,
    ARSP_Data,
    tol,
    1
)

RFND_Timed = time_match(
    Master_Time_Axis,
    RFND_Data,
    tol,
    1
)

BAT_Timed = time_match(
    Master_Time_Axis,
    BAT_Data,
    tol,
    7
)

MODE_Timed = time_match(
    Master_Time_Axis,
    MODE_Data,
    tol,
    2
)

IMU_Timed = time_match(
    Master_Time_Axis,
    IMU_Data,
    tol,
    6
)

with open(os.path.join(output_dir, f"Attitude_{file_name}.csv"), "w", newline="") as file:

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

with open(os.path.join(output_dir, f"GPS_{file_name}.csv"), "w", newline="") as file:

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

with open(os.path.join(output_dir, f"Controls_{file_name}.csv"), "w", newline="") as file:

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
        "RCOU_C13", "RCOU_C14",
        "Mode",
        "ModeNum"
    ])

    for i in range(len(Master_Time_Axis)):

        row = [Time_Axis[i]]

        row.extend(RCIN_Timed[i][1:])
        row.extend(RCOU_Timed[i][1:])
        row.extend(MODE_Timed[i][1:])

        writer.writerow(row)

with open(os.path.join(output_dir, f"Sensors_{file_name}.csv"), "w", newline="") as file:

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

# Write PIDP data
with open(os.path.join(output_dir, f"PIDP_{file_name}.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",
        "PIDP_Tar",
        "PIDP_Act",
        "PIDP_Flags"
    ])

    for i in range(len(Master_Time_Axis)):

        row = [Time_Axis[i]]

        row.extend(PIDP_Timed[i][1:])

        writer.writerow(row)

# Write airspeed and rangefinder data
with open(os.path.join(output_dir, f"AirData_{file_name}.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",
        "ARSP_Airspeed",
        "RFND_Dist"
    ])

    for i in range(len(Master_Time_Axis)):

        row = [Time_Axis[i]]

        row.extend(ARSP_Timed[i][1:])
        row.extend(RFND_Timed[i][1:])

        writer.writerow(row)



with open(os.path.join(output_dir, f"EKF_{file_name}.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",

        "XKF1_C",
        "XKF1_Roll",
        "XKF1_Pitch",
        "XKF1_Yaw",
        "XKF1_VN",
        "XKF1_VE",
        "XKF1_VD",
        "XKF1_dPD",
        "XKF1_PN",
        "XKF1_PE",
        "XKF1_PD",
        "XKF1_GX",
        "XKF1_GY",
        "XKF1_GZ",
        "XKF1_OH",

        "XKF2_C",
        "XKF2_AX",
        "XKF2_AY",
        "XKF2_AZ",
        "XKF2_VWN",
        "XKF2_VWE",
        "XKF2_MN",
        "XKF2_ME",
        "XKF2_MD",
        "XKF2_MX",
        "XKF2_MY",
        "XKF2_MZ",
        "XKF2_IDX",
        "XKF2_IDY",
        "XKF2_IS",

        "XKF3_C",
        "XKF3_IVN",
        "XKF3_IVE",
        "XKF3_IVD",
        "XKF3_IPN",
        "XKF3_IPE",
        "XKF3_IPD",
        "XKF3_IMX",
        "XKF3_IMY",
        "XKF3_IMZ",
        "XKF3_IYAW",
        "XKF3_IVT",
        "XKF3_RErr",
        "XKF3_ErSc"
    ])

    for i in range(len(Master_Time_Axis)):

        row = [Time_Axis[i]]

        row.extend(XKF1_Timed[i][1:])
        row.extend(XKF2_Timed[i][1:])
        row.extend(XKF3_Timed[i][1:])

        writer.writerow(row)

with open(os.path.join(output_dir, f"Navigation_{file_name}.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",

        "NTUN_Dist",
        "NTUN_TBrg",
        "NTUN_NavBrg",
        "NTUN_AltE",
        "NTUN_XT",
        "NTUN_XTi",
        "NTUN_AsE",
        "NTUN_TLat",
        "NTUN_TLng",
        "NTUN_TAW",
        "NTUN_TAT",
        "NTUN_TAsp",

        "TECS_h",
        "TECS_dh",
        "TECS_hin",
        "TECS_hdem",
        "TECS_dhdem",
        "TECS_spdem",
        "TECS_sp",
        "TECS_dsp",
        "TECS_th",
        "TECS_ph",
        "TECS_pmin",
        "TECS_pmax",
        "TECS_dspdem",
        "TECS_iph",
        "TECS_ith",
        "TECS_f",

        "CTUN_NavPitch",
        "CTUN_Pitch",
        "CTUN_ThO"
    ])

    for i in range(len(Master_Time_Axis)):

        row = [Time_Axis[i]]

        row.extend(NTUN_Timed[i][1:])
        row.extend(TECS_Timed[i][1:])

        row.extend(CTUN_Timed[i][1:])

        writer.writerow(row)

with open(os.path.join(output_dir, f"Power_{file_name}.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",
        "BAT_Instance",
        "BAT_Volt",
        "BAT_Curr",
        "BAT_CurrTot",
        "BAT_EnrgTot",
        "BAT_Temp",
        "BAT_Res"
    ])

    for i in range(len(Master_Time_Axis)):

        row = [Time_Axis[i]]

        row.extend(BAT_Timed[i][1:])

        writer.writerow(row)


# For IMU related
with open(os.path.join(output_dir, f"IMU_{file_name}.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",
        "GyrX",
        "GyrY",
        "GyrZ",
        "AccX",
        "AccY",
        "AccZ"
    ])

    for i in range(len(Master_Time_Axis)):

        row = IMU_Timed[i].copy()

        row[0] = Time_Axis[i]

        writer.writerow(row)


# Write mission commands only if they exist
if len(CMD_Data) > 0:

    with open(os.path.join(output_dir, f"Mission_{file_name}.csv"), "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Time",
            "TotalCommands",
            "CommandNumber",
            "CommandID",
            "Prm1",
            "Prm2",
            "Prm3",
            "Prm4",
            "Latitude",
            "Longitude",
            "Altitude",
            "Frame"
        ])

        for row in CMD_Data:

            writer.writerow([
                (row[0] - Master_Time_Axis[0]) / 1_000_000,
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[11]
            ])

    print("Mission:", len(CMD_Data))

else:

    print("Mission: not found - skipped")

# Write log messages only if they exist
if len(MSG_Data) > 0:

    with open(
        os.path.join(output_dir, f"Messages_{file_name}.csv"),
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Time",
            "ID",
            "Seq",
            "Message"
        ])

        for row in MSG_Data:

            writer.writerow([
                (row[0] - Master_Time_Axis[0]) / 1_000_000,
                row[1],
                row[2],
                row[3]
            ])

    print("Messages:", len(MSG_Data))

else:

    print("Messages: not found - skipped")

# Write geofence only if it exists
if len(FNCE_Data) > 0:

    with open(os.path.join(output_dir, f"GeoFence_{file_name}.csv"), "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Time",
            "TotalPoints",
            "Sequence",
            "Type",
            "Latitude",
            "Longitude",
            "Count",
            "Radius"
        ])

        for row in FNCE_Data:

            writer.writerow([
                (row[0] - Master_Time_Axis[0]) / 1_000_000,
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7]
            ])

    print("GeoFence:", len(FNCE_Data))

else:

    print("GeoFence: not found - skipped")

#diagonostics
print("CSV files written to:", output_dir)

print("ATT:", len(Attitude_Timed))
print("GPS:", len(GPS_Timed))
print("RCIN:", len(RCIN_Timed))
print("RCOU:", len(RCOU_Timed))
print("MODE:", len(MODE_Data))
print("MODE timed:", len(MODE_Timed))
print("VIBE:", len(VIBE_Timed))
print("MAG:", len(MAG_Timed))
print("BARO:", len(BARO_Timed))
print("XKF1:", len(XKF1_Timed))
print("XKF2:", len(XKF2_Timed))
print("XKF3:", len(XKF3_Timed))
print("NTUN:", len(NTUN_Timed))
print("TECS:", len(TECS_Timed))
print("CTUN:", len(CTUN_Timed))
print("PIDP:", len(PIDP_Timed))
print("ARSP:", len(ARSP_Timed))
print("RFND:", len(RFND_Timed))
print("BAT:", len(BAT_Timed))
print("IMU:", len(IMU_Data))
print("IMU timed:", len(IMU_Timed))

with open(os.path.join(output_dir, f"FlightData_{file_name}.csv"), "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Time",

        "DesRoll",
        "DesPitch",
        "DesYaw",
        "Roll",
        "Pitch",
        "Yaw",

        "GPS_Status",
        "GPS_NSats",
        "GPS_HDop",
        "GPS_Lat",
        "GPS_Lng",
        "GPS_Alt",
        "GPS_Spd",
        "GPS_GCrs",
        "GPS_VZ",
        "GPS_Yaw",

        "RCIN_C1",
        "RCIN_C2",
        "RCIN_C3",
        "RCIN_C4",
        "RCIN_C5",
        "RCIN_C6",
        "RCIN_C7",
        "RCIN_C8",
        "RCIN_C9",
        "RCIN_C10",
        "RCIN_C11",
        "RCIN_C12",
        "RCIN_C13",
        "RCIN_C14",

        "RCOU_C1",
        "RCOU_C2",
        "RCOU_C3",
        "RCOU_C4",
        "RCOU_C5",
        "RCOU_C6",
        "RCOU_C7",
        "RCOU_C8",
        "RCOU_C9",
        "RCOU_C10",
        "RCOU_C11",
        "RCOU_C12",
        "RCOU_C13",
        "RCOU_C14",

        "Mode",
        "ModeNum",

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
        "CPress",

        "XKF1_C",
        "XKF1_Roll",
        "XKF1_Pitch",
        "XKF1_Yaw",
        "XKF1_VN",
        "XKF1_VE",
        "XKF1_VD",
        "XKF1_dPD",
        "XKF1_PN",
        "XKF1_PE",
        "XKF1_PD",
        "XKF1_GX",
        "XKF1_GY",
        "XKF1_GZ",
        "XKF1_OH",

        "XKF2_C",
        "XKF2_AX",
        "XKF2_AY",
        "XKF2_AZ",
        "XKF2_VWN",
        "XKF2_VWE",
        "XKF2_MN",
        "XKF2_ME",
        "XKF2_MD",
        "XKF2_MX",
        "XKF2_MY",
        "XKF2_MZ",
        "XKF2_IDX",
        "XKF2_IDY",
        "XKF2_IS",

        "XKF3_C",
        "XKF3_IVN",
        "XKF3_IVE",
        "XKF3_IVD",
        "XKF3_IPN",
        "XKF3_IPE",
        "XKF3_IPD",
        "XKF3_IMX",
        "XKF3_IMY",
        "XKF3_IMZ",
        "XKF3_IYAW",
        "XKF3_IVT",
        "XKF3_RErr",
        "XKF3_ErSc",

        "NTUN_Dist",
        "NTUN_TBrg",
        "NTUN_NavBrg",
        "NTUN_AltE",
        "NTUN_XT",
        "NTUN_XTi",
        "NTUN_AsE",
        "NTUN_TLat",
        "NTUN_TLng",
        "NTUN_TAW",
        "NTUN_TAT",
        "NTUN_TAsp",

        "TECS_h",
        "TECS_dh",
        "TECS_hin",
        "TECS_hdem",
        "TECS_dhdem",
        "TECS_spdem",
        "TECS_sp",
        "TECS_dsp",
        "TECS_th",
        "TECS_ph",
        "TECS_pmin",
        "TECS_pmax",
        "TECS_dspdem",

        "BAT_Instance",
        "BAT_Volt",
        "BAT_Curr",
        "BAT_CurrTot",
        "BAT_EnrgTot",
        "BAT_Temp",
        "BAT_Res"
    ])

    for i in range(len(Master_Time_Axis)):

        row = [Time_Axis[i]]

        row.extend(Attitude_Timed[i][1:])

        row.extend(GPS_Timed[i][1:])

        row.extend(RCIN_Timed[i][1:])

        row.extend(RCOU_Timed[i][1:])

        row.extend(MODE_Timed[i][1:])

        row.extend(VIBE_Timed[i][1:])

        row.extend(MAG_Timed[i][1:])

        row.extend(BARO_Timed[i][1:])

        row.extend(XKF1_Timed[i][1:])

        row.extend(XKF2_Timed[i][1:])

        row.extend(XKF3_Timed[i][1:])

        row.extend(NTUN_Timed[i][1:])

        row.extend(TECS_Timed[i][1:])

        row.extend(BAT_Timed[i][1:])

        writer.writerow(row)

print("CSVs ready! Go to Waterfly Python Code/flight_csv and look for the flight log name you want")
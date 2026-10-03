import pandas as pd
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

flight_folder = "/home/kiryuzerodev/Waterfly Python Code/flight_csv/00000039/Cleaned"

def cen_moving_avg(noisy_array, window_size):
    clean_array = []
    true_size = (window_size * 2) + 1
    for i in range(window_size, len(noisy_array) - window_size):
        numerator = 0
        for j in range(-window_size, window_size + 1):
            numerator += noisy_array[i + j]
        clean_array.append(numerator / true_size)
    return clean_array


#~~~~~~~~~~~~ Function for Plotting Graphs ~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_this_shit(x_axis_data,y_axis_data,label_name):
    color_options = ['red','blue','green','yellow','magenta','cyan',
                    'black','orange','purple','pink','brown','gray',
                    'lime','navy','teal','olive','maroon','gold',
                    'indigo','violet','coral','salmon','turquoise',
                    'crimson','darkgreen','darkblue','darkred','darkorange']
    random_color = random.choice(color_options)
    plt.plot(x_axis_data,y_axis_data,linewidth=2.5,color=random_color,label= label_name)
#####################
# Main code area
#####################


Sensors_file = [
    file for file in os.listdir(flight_folder)
    if file.startswith("Sensors_") and file.endswith(".csv")
][0]

# #~~~~~~~~~~~~~~~~ AIRSPEED SECTION ~~~~~~~~~~~~~~~~~~
# # Extracting
# AirData_file = [file for file in os.listdir(flight_folder) if file.startswith("AirData_") and file.endswith(".csv")][0]
# AirData = pd.read_csv(os.path.join(flight_folder, AirData_file))
# airspeed = AirData["ARSP_Airspeed"]
#
# # Plotting
# plt.figure()
# smoothing = 3
# plot_this_shit(AirData["Time"],airspeed,"Raw Airspeed")
# airspeed_avg = cen_moving_avg(airspeed,smoothing)
# plot_this_shit(AirData["Time"][smoothing:-smoothing],airspeed_avg,"Cleaned Airspeed")
#
# # Formatting
# plt.title("Airspeed vs Time")
# plt.xlabel("Time (s)")
# plt.ylabel("Airspeed (m/s)")
# plt.grid(True)
# plt.show()
#
# #~~~~~~~~~~~~~~~~ RANGEFINDER SECTION ~~~~~~~~~~~~~~~~~~
# # Extracting
# AirData_file = [file for file in os.listdir(flight_folder) if file.startswith("AirData_") and file.endswith(".csv")][0]
# AirData = pd.read_csv(os.path.join(flight_folder, AirData_file))
# rngfndr = AirData["RFND_Dist"]
#
# # Plotting
# plt.figure()
# smoothing = 5
# plot_this_shit(AirData["Time"],rngfndr,"Raw RangeFinder Data")
# rngfndr_avg = cen_moving_avg(rngfndr,smoothing)
# plot_this_shit(AirData["Time"][smoothing:-smoothing],rngfndr_avg,"Cleaned RangeFinder Data")
#
# # Formatting
# plt.title("RangeFinder Data vs Time")
# plt.xlabel("Time (s)")
# plt.ylabel("RangeFinder (m)")
# plt.grid(True)
# plt.show()

#~~~~~~~~~~~~~~~~ ALTITUDE SECTION ~~~~~~~~~~~~~~~~~~
# Extracting
Sensors_file = [file for file in os.listdir(flight_folder) if file.startswith("Sensors_") and file.endswith(".csv")][0]
Sensors = pd.read_csv(os.path.join(flight_folder, Sensors_file))

baro_alt = Sensors["BaroAlt"]
time = Sensors["Time"]

plt.figure()

smoothing = 3

plot_this_shit(time, baro_alt, "Raw Barometric Altitude")

baro_alt_avg = cen_moving_avg(baro_alt, smoothing)

plot_this_shit(
    time[smoothing:-smoothing],
    baro_alt_avg,
    "Cleaned Barometric Altitude"
)

plt.title("Barometric Altitude vs Time")
plt.xlabel("Time (s)")
plt.ylabel("Barometric Altitude (m)")
plt.grid(True)
plt.legend()

plt.savefig("/home/kiryuzerodev/Waterfly Python Code/Altitude_Test_00000039.png", dpi=150)

print("Graph saved.")
print("Opening graph...")

plt.show()
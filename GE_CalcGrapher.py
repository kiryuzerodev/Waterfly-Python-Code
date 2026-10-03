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

def plot_this_shit(x_axis_data, y_axis_data, label_name):
    plt.plot(x_axis_data, y_axis_data, linewidth=2.5, label=label_name)

print("GRAPHING AND CALCULATION INTERFACE STARTED")
print("Altitude section running...")

Sensors_file = [
    file for file in os.listdir(flight_folder)
    if file.startswith("Sensors_") and file.endswith(".csv")
][0]

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
## This code cleans the CSV files that were generated previously
# It removes NaN spaces by interpolating numerical data onto
# the IMU master time axis and forward-filling discrete data.
# It also keeps the CSV headings unchanged for later analysis.

import os
import sys
import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Check input
# ---------------------------------------------------------

if len(sys.argv) < 2:
    print("Usage:")
    print("python clean_the_CSVs.py <flight_folder>")
    exit(1)

flight_folder = sys.argv[1]

if not os.path.isdir(flight_folder):
    print("Error: folder not found")
    exit(1)


# ---------------------------------------------------------
# Find IMU file
# ---------------------------------------------------------

imu_files = [
    f for f in os.listdir(flight_folder)
    if f.startswith("IMU_") and f.endswith(".csv")
]

if len(imu_files) == 0:
    print("Error: IMU CSV not found")
    exit(1)

if len(imu_files) > 1:
    print("Error: multiple IMU CSV files found")
    print(imu_files)
    exit(1)

imu_file = imu_files[0]

imu_path = os.path.join(
    flight_folder,
    imu_file
)

print("Reference IMU:", imu_file)


# ---------------------------------------------------------
# Read IMU
# ---------------------------------------------------------

imu_data = pd.read_csv(
    imu_path
)

if "Time" not in imu_data.columns:
    print("Error: IMU file does not contain 'Time' column")
    exit(1)

master_time = imu_data["Time"].to_numpy(
    dtype=float
)

print("Master time points:", len(master_time))
print("Start time:", master_time[0])
print("End time:", master_time[-1])


# ---------------------------------------------------------
# Create output folder
# ---------------------------------------------------------

output_folder = os.path.join(
    flight_folder,
    "Cleaned"
)

os.makedirs(
    output_folder,
    exist_ok=True
)


# ---------------------------------------------------------
# Columns that should NOT be linearly interpolated
# ---------------------------------------------------------
#
# These fields represent discrete states, IDs, commands,
# or counters rather than continuously varying signals.
#
# All other numerical fields will be linearly interpolated.
#
# RCIN and RCOU are intentionally NOT included here because
# they are numerical signals that can be interpolated.
# ---------------------------------------------------------

discrete_columns = {
    "Mode",
    "ModeNum",

    "TotalCommands",
    "CommandNumber",
    "CommandID",
    "Frame",

    "TotalPoints",
    "Sequence",
    "Type",
    "Count",
}


# ---------------------------------------------------------
# Numerical interpolation function
# ---------------------------------------------------------

def interpolate_column(
    source_time,
    values,
    master_time
):

    values = np.asarray(
        values,
        dtype=float
    )

    # Only use samples where both the time and value
    # are valid.

    valid = (
        np.isfinite(values)
        & np.isfinite(source_time)
    )

    # Need at least two valid samples for interpolation.

    if np.sum(valid) < 2:

        return np.full(
            len(master_time),
            np.nan
        )

    x = source_time[valid]
    y = values[valid]

    # Make sure timestamps are sorted.

    order = np.argsort(x)

    x = x[order]
    y = y[order]

    # Remove duplicate timestamps.

    x_unique, unique_indices = np.unique(
        x,
        return_index=True
    )

    y_unique = y[unique_indices]

    if len(x_unique) < 2:

        return np.full(
            len(master_time),
            np.nan
        )

    # Linear interpolation onto the IMU master
    # time axis.

    result = np.interp(
        master_time,
        x_unique,
        y_unique
    )

    # Do NOT extrapolate before the first valid
    # source-data sample.

    result[
        master_time < x_unique[0]
    ] = np.nan

    # Do NOT extrapolate after the last valid
    # source-data sample.

    result[
        master_time > x_unique[-1]
    ] = np.nan

    return result


# ---------------------------------------------------------
# Forward-fill discrete data
# ---------------------------------------------------------

def interpolate_discrete(
    source_time,
    values,
    master_time
):

    values = np.asarray(
        values,
        dtype=object
    )

    valid = (
        pd.notna(values)
        & np.isfinite(source_time)
    )

    # No valid samples.

    if np.sum(valid) == 0:

        return np.full(
            len(master_time),
            np.nan,
            dtype=object
        )

    x = source_time[valid]
    y = values[valid]

    # Make sure timestamps are sorted.
    order = np.argsort(x)

    x = x[order]
    y = y[order]

    result = np.full(
        len(master_time),
        np.nan,
        dtype=object
    )

    current_value = np.nan

    j = 0

    # Forward-fill the latest known discrete value
    # onto the master time axis.
    for i, t in enumerate(master_time):

        while j < len(x) and x[j] <= t:
            current_value = y[j]
            j += 1

        result[i] = current_value

    # Do NOT extrapolate before the first valid
    # discrete sample.

    first_valid_time = x[0]

    result[
        master_time < first_valid_time
    ] = np.nan

    return result


# ---------------------------------------------------------
# Process every CSV
# ---------------------------------------------------------

csv_files = [
    f for f in os.listdir(flight_folder)
    if f.endswith(".csv")
]

for csv_file in csv_files:

    # -----------------------------------------------------
    # IMU is the reference and does not need processing.
    # -----------------------------------------------------

    if csv_file == imu_file:

        output_path = os.path.join(
            output_folder,
            csv_file
        )

        imu_data.to_csv(
            output_path,
            index=False
        )

        print("IMU: copied unchanged")
        continue

    # -----------------------------------------------------
    # Read CSV
    # -----------------------------------------------------

    input_path = os.path.join(
        flight_folder,
        csv_file
    )

    print()
    print("Processing:", csv_file)

    try:

        data = pd.read_csv(
            input_path
        )

    except Exception as e:
        print("  Error reading file:", e)
        continue

    # -----------------------------------------------------
    # Check Time column
    # -----------------------------------------------------

    if "Time" not in data.columns:
        print("  Skipped: no Time column")
        continue

    source_time = pd.to_numeric(
        data["Time"],
        errors="coerce"
    ).to_numpy(
        dtype=float
    )

    # -----------------------------------------------------
    # Create cleaned dataframe
    # -----------------------------------------------------

    cleaned = pd.DataFrame()

    # All files use the IMU master time axis.

    cleaned["Time"] = master_time

    # -----------------------------------------------------
    # Process every column
    # -----------------------------------------------------

    for column in data.columns:

        if column == "Time":
            continue

        values = data[column]
        # -------------------------------------------------
        # Discrete data
        # -------------------------------------------------
        if column in discrete_columns:

            cleaned[column] = interpolate_discrete(
                source_time,
                values,
                master_time
            )
        # -------------------------------------------------
        # Numerical data
        # -------------------------------------------------
        else:

            numeric_values = pd.to_numeric(
                values,
                errors="coerce"
            ).to_numpy(
                dtype=float
            )

            cleaned[column] = interpolate_column(
                source_time,
                numeric_values,
                master_time
            )

    # -----------------------------------------------------
    # Save cleaned CSV
    # -----------------------------------------------------

    output_path = os.path.join(
        output_folder,
        csv_file
    )

    cleaned.to_csv(
        output_path,
        index=False
    )

    print("  Input rows :", len(data))
    print("  Output rows:", len(cleaned))


# ---------------------------------------------------------
# Done
# ---------------------------------------------------------

print()
print("======================================")
print("Cleaning complete")
print("Output folder:")
print(output_folder)
print("======================================")
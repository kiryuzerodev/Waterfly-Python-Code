# This code generates the relevant graphs for ground effect testing
# it also calculates the step responses and give the entire time response characteristics
# This file can only be called by the Report Generator file

# The pipeline is as follows:
# SITL Mission Plan
# Run SITL
# If report is asked
# Create the JSON file with the relevant information of the created Flight Plan
#   Run the report generator
#       Basic test information is printed
#       Write up is printed
#   If graphs and step info is requested
#       This program first plots the required plots for characterization
#       Next using the JSON file, it figures out which Waypoints are the step response points
#       When the log has detected these points, it will automatically begin the step response characterization
#       Finally displays these results for every test where a test response was ordered

# Since this file will mainly be called from the Report Generator, this will be only for Ground Effect test
# For future versions where different graphs are needed, this file can be branched and the same logic can be used

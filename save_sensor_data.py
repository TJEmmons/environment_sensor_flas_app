import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import random
from datetime import datetime
import time
import os

# Dataframe to store sensor data
df = pd.DataFrame()

# Function to read data from environmental sensor 
def read_enviro_sensor():
    # Read data from sensor
    gas_reading = gas.read_all()
    ox = gas_reading.oxidising
    nh3 = gas_reading.nh3
    red = gas_reading.reducing

    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    cpu_temp = get_cpu_temperature()


    sensor_dict = {
        'time':[current_time], 
        'oxidising_ohms':[ox],
        'nh3_ohms':[nh3],
        'reducing_ohms':[red],
        'temperature_bme280':[temperature],
        'pressure_bme280':[pressure],
        'humidity_bme280':[humidity],
        'temperature_cpu':[cpu_temp]
                    }

    # Create DataFrame
    df_timestep = pd.DataFrame(sensor_dict)

    global df
    df = df.append(df_timestep, ignore_index=True)
    return df

# construct the path to the csv folder
csv_folder = os.path.join(os.getcwd(), 'archived_data')

# Function to save dataframe to a CSV file
def save_to_csv():
    global df
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    if len(df) > 0:
        half_index = int(len(df) / 2)
        new_half_df = df.iloc[half_index:]
        file_name = f"data_{timestamp}.csv"
        new_half_df.to_csv(os.path.join(csv_folder, file_name), index=False)
        df.drop(df.index[:half_index], inplace=True)

# construct the path to the plots folder
plots_folder = os.path.join(os.getcwd(), 'static')
# Create the plots folder if it doesn't exist
if not os.path.exists(plots_folder):
    os.makedirs(plots_folder)

# Counter variable to keep track of the number of iterations
counter = 0


while True:
    # Get data
    read_enviro_sensor()

    # Create a figure with multiple subplots
    fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(10, 10))
    plt.suptitle("Time Series Plots")
    axes = axes.ravel()

    columns = ['oxidising_ohms', 'nh3_ohms', 'reducing_ohms', 'temperature_bme280', 'pressure_bme280', 'humidity_bme280', 'temperature_cpu']
    x_axis = 'time'
    for i, col in enumerate(columns):
        axes[i].plot(df[x_axis], df[col])
        axes[i].set_xlabel(x_axis)
        axes[i].set_ylabel(col)
    # construct the path to the plot image
    plot_path = os.path.join(plots_folder, 'plot.png')
    plt.savefig(plot_path)
    print("Figure saved!")
    # Save dataframe to a CSV file every 10 iterations
    if counter % 10 == 0:
        save_to_csv()
    counter += 1
    time.sleep(1)

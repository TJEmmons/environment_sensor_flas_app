import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import random
from datetime import datetime
import time
import os
import time
from enviroplus import gas
import logging
from bme280 import BME280
import pandas as pd 
import os 

import ST7735
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium as UserFont
import logging

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


working_directory=os.getcwd() #use as default
save_rate = 100000
initialization_wait = 30

# Dataframe to store sensor data
df = pd.DataFrame()
counter = 0

# construct the path to the csv folder
csv_folder = os.path.join(working_directory, 'archived_data')

###Set up BME Sensor
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

### Set up LCD 
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""Initialize text""")

# Create LCD class instance.
disp = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display.
disp.begin()

# Width and height to calculate text position.
WIDTH = disp.width
HEIGHT = disp.height

# New canvas to draw on.
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

def update_display(message: str = "", font_size: int = 25) -> None:
    """
    Update the text displayed on the LCD screen with the given message and font size.
    
    Parameters:
        message (str): The message to be displayed on the screen
        font_size (int): The font size of the message
        
    Returns:
        None
    """
    # Text settings.
    font = ImageFont.truetype(UserFont, font_size)
    text_colour = (255, 255, 255)
    back_colour = (0, 170, 170)

    size_x, size_y = draw.textsize(message, font)

    # Calculate text position
    x = (WIDTH - size_x) / 2
    y = (HEIGHT / 2) - (size_y / 2)

    # Draw background rectangle and write text.
    draw.rectangle((0, 0, 160, 80), back_colour)
    draw.text((x, y), message, font=font, fill=text_colour)
    disp.display(img)


def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp



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

#Initialize the sensors
#The first 20-30 seconds of a few sesors are grossly off of baseline

read_enviro_sensor()
df = pd.DataFrame()
time.sleep(initialization_wait)


try:
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
        if counter % save_rate == 0:
            save_to_csv()
        counter += 1
        print(df.tail(1))
        update_display(message=f"cpu_temp = {df['temperature_cpu'].round(2)} degC")
        time.sleep(1)
except MemoryError:
    update_display(message="Memory Error")
except KeyboardInterrupt:
    update_display(message="Bye!")
except IOError:
    update_display(message="IOError")
except OSError:
    update_display(message="OSError")
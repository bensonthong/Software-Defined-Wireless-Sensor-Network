##################################################################
###                                                            ###
###             TEMPERATURE SENSORS GATHERING DATA             ###
###                                                            ###
###             BY: DEREK MATA & JEFFERY SPAULDING             ###
###                PROFESSOR OMAR SDP & ECE 5590               ###
###                        SPRING 2022                         ###
###                                                            ###
##################################################################

# Library for csv functions
import csv

# General OS interaction libraries
import os
import time
import datetime

# Libraries for sensor data retrieval 
import board
import busio
import adafruit_dht
import adafruit_ina260

# Custom made libraries
import sensor


##################################################
#                                                #
#                PROGRAM CONSTANTS               #
#                                                #
##################################################
# csv file name and path
pi_id = os.popen("cat pi.id").readline()
file_name = f"pi-{pi_id[0]}-temp-data.csv"
file_path = os.path.abspath( os.path.join(os.path.dirname(__file__), file_name) )

# csv row data
col_headers = ["Timestamp (UTC)", "Temperature (F)", "Humidity (%% air-water mix compared to dew point)", "Current (mA)", "Voltage (V)", "Power (mW)"]
col_data = list()



##################################################
#                                                #
#                  DATA GATHERING                #
#                                                #
##################################################
# Get the temperature data from the sensor on RPi
def get_temp_sensor_data(temp_sense_obj: sensor.temperature_sensor):
    temp_f = temp_sense_obj.get_temp()
    humidity = temp_sense_obj.get_humidity()
    return (temp_f, humidity)

###############################

# Get current (mA), voltage (V), power(mW) from sensor on RPi
def get_power_sensor_data(power_sense_obj: sensor.power_sensor):
    current, voltage, power = power_sense_obj.get_cvp()
    return (current, voltage, power)

###############################

# Get the timestamp, temperature, and humidity for that row
def get_row_data(temp_sense_obj: sensor.temperature_sensor, power_sense_obj: sensor.power_sensor):
    temp_f, humidity = get_temp_sensor_data(temp_sense_obj)
    current, voltage, power = get_power_sensor_data(power_sense_obj)
    timestamp_obj = datetime.datetime.utcnow()
    timestamp = timestamp_obj.strftime("%m-%d-%Y %H:%M:%S")
    data_list = [timestamp, str(round(temp_f, 2)), str(round(humidity, 2)), str(round(current, 2)), str(round(voltage, 2)), str(round(power, 2))]
    print("\t", end="")
    print(data_list)
    col_data.append(data_list)
    return


##################################################
#                                                #
#                   COMPILE CSV                  #
#                                                #
##################################################
# Create the csv file with permissions of -rw-rw-rw
def make_csv(add_header=False):
    os.umask(0)
    with open(file_path, "w+") as csv_file:
        if(add_header):
            csv_wr_obj = csv.writer(csv_file)
            csv_wr_obj.writerow(col_headers)
        csv_file.close()
    return

###############################

# Write data to the csv file and remove old data after
def write_to_csv(header=False):
    global col_data
    with open(file_path, "a", newline="") as csv_file:
        csv_wr_obj = csv.writer(csv_file)
        if(header):
            csv_wr_obj.writerow(col_headers)
        else:
            csv_wr_obj.writerows(col_data)
            col_data.clear()
    return
    


##################################################
#                                                #
#                  MAIN FUNCTION                 #
#                                                #
##################################################
def main():        
    # Create Temperature Sensor object
    temp_sense_obj = sensor.temperature_sensor()    
    
    # Create power sensor object
    power_sense_obj = sensor.power_sensor()
    
    # Check if previous run had .csv file, if not make it
    if not os.path.exists(file_path):
        make_csv(add_header=True)
    
    # Gather data points every second until user presses CTRL+C or end with exception, then write everything to csv file
    try:
        print("Now gathering data from temperature sensor [timestamp (UTC), temp (F), humidity (%), current (mA), voltage (V), power (mW)]:")
        while True:
            get_row_data(temp_sense_obj, power_sense_obj)
            time.sleep(1)
    except KeyboardInterrupt as k:
        print("Stopping data collection...")
    except Exception as e:
        print(f"Error during data collection!!!  -->  {e}")
    finally:
        print("Now writing data to .csv file:")
        write_to_csv()
    
    # END
    print("\n\n********************************************************************")
    print("*                                                                  *")
    print("*                        Program complete!!                        *")
    print("*                                                                  *")
    print("********************************************************************")
    
    
#########################################################       


if __name__ == "__main__":
    main()

'''
Python 3.10.1 and Python 3.12.3

Written by Sadie Duncan at IVSG during 2024 Aug.
Supervised by Professor Sean Brennan

Purpose: The purpose of this script is to utilize the Polars and Pandas library to more
         efficiently handle the mapping van data. Polars or Pandas (mainly Polars)
         data frames will be created either from bag files or CSV files. Once the data
         frame is created, it can be altered to add or remove columns. From the data frame,
         one can create CSV files.

         TLDR:
            1. Read a bag file or CSV file and create a Pandas data frame
            2. Convert the Pandas data frame into a Polars data frame for faster handling
            3. Alter the Polars data frame if needed (remove or add columns, etc.)
            4. Write data frame to a CSV file

        Possible Uses:
            1. bag -> df    (DONE)
            2. csv -> df    (DONE)
            ----------------------
            3. df  -> csv   (DONE)

Usage:  python(3) parse_and_insert.py
    - Use with get_topics.py and raw_data_db_launch.sql
    - Need to know before using:
        - from_bag, from_csv, to_csv: 0 if no and 1 if yes
        - topic_lst: ['/GPS_SparkFun_Front_GGA', '/GPS_SparkFun_Front_VTG', 
                      '/GPS_SparkFun_RearLeft_GGA', '/GPS_SparkFun_RearLeft_GST', '/GPS_SparkFun_RearLeft_VTG',
                      '/GPS_SparkFun_RearRight_GGA', '/GPS_SparkFun_RearRight_GST', '/GPS_SparkFun_RearRight_VTG',
                      '/parseEncoder', '/parseTrigger']
        - if you're reading from from CSV files, you need to know a bag file name and id

Packages to Install:
    (May need to use: python -m pip install <package-name> --break-system-packages)

    pip install bagpy
        - Installing bagpy will install rosbag, pandas, numpy, and more

    pip install polars OR pip install polars-lts-cpu
        - Installing the normal version of polars may cause some error.
          In that case, install polars-lts-cpu

To-Do:
    1. Integrate camera parsing functions
    2. Integrate velodyne parsing functions
'''
from io import StringIO 
from pathlib import Path
import os
import sys
import shutil
import string
import csv
import time
import datetime
import warnings
import pdb

import rosbag
import pandas as pd
import polars as pl
import numpy as np
import hashlib

# Keep track of the differences between the ROS topics and database table topics
from get_topics import get_topics  
from parseCamera import parseCamera                         

# Using Pandas yielded an error -> ignore this error
warnings.simplefilter("ignore", category = FutureWarning)

bag_id = 1
base_station_id = 0
base_stations = []

'''
    ===================================== Class DFBuilder =========================================
    #	Purpose: Create a class DFBuilder to build and alter data frames from bag files or CSV files.
    #
    #    Methods:
    #       1. def __init__(self, file_name, topic, keys)
    #           Initialize the file name, topic, and list of keys that you will be using to
    #           create/alter the data frame.
    #
    #       2. def bag_to_df(self)
    #           Transform a bag file into a Polars data frame. Go through certain topics and each message
    #           in that topic to get the data that will be added to the data frame.
    #
    #        3. def csv_to_df(self)
    #           Transform a CSV file into a Pandas and then Polars data frame. Only add certain columns
    #           from the CSV file to the data frame to match with the SQL table.
    # 
    #       4. def update_df(self, df, table_name, mapping_dict, db_col_lst, bag_files_id)
    #           Edit a data frame to have the same columns, same column data types, and same column names
    #           as the corresponding database table. Information such as bag_files_id and ros_publish_time are
    #           added here.
    #
    # 	Author: Sadie Duncan
    # 	Date:   08/08/2024
    ===============================================================================================
'''
class DFBuilder:
    def __init__(self, file_name, topic, keys):
        self.file_name = file_name
        self.topic = topic
        self.keys = keys
    
    '''
    Transform a bag file into a Polars data frame. Go through certain topics and each message in that topic to get the data that will be added to the data frame.
    '''
    def bag_to_df(self):
        try:
            bag_file = self.file_name
            topic = self.topic
            keys = self.keys
            
            bag = rosbag.Bag(bag_file)
            data = []   # Append rows of data here, then transform this list into a Polars data frame

            # Go through each message for a specific topic, to get a new row of data
            for topic, msg, t in bag.read_messages(topics = [topic]):
                row = {}
                # Go through each key as secs, nsecs, and rosbagTimestamp need to be handled differently
                for key in keys:
                    if (key == 'rosbagTimestamp'):
                        value = msg.header.stamp
                    elif (key == 'secs'):
                        value = msg.header.stamp.secs
                    elif (key == 'nsecs'):
                        value = msg.header.stamp.nsecs
                    else:
                        value = getattr(msg, key, None)

                    # From each key, you'll get a corresponding value (as seen above). Add this as a new entry to the row dictionary.
                    row[key] = value

                data.append(row)

            # If any data was found, then make a data frame out of this data frame. Otherwise, create an empty data frame.
            if (len(data) > 0):
                df = pl.DataFrame(data)

            else:
                df = pl.DataFrame()

        except Exception as e:
            print(f"Error: {e}")
            df = pl.DataFrame()
        
        return df   # Return the data frame

    '''
    Transform a CSV file into a Pandas and then Polars data frame. Only add certain columns from the CSV file to the data frame to match with the SQL table.
    '''
    def csv_to_df(self):
        try:
            csv_file = self.file_name
            keys = self.keys

            # Using Pandas to create a data frame from certain columns from the CSV file
            df_pandas = pd.read_csv(csv_file, sep = ',', usecols = keys)
            # print(df_pandas.columns.tolist())   # For simple debugging uses, check if data was added to the data frame

            # Drop any emtpy rows
            df_pandas = df_pandas.dropna(how = 'all')

            # Convert to Polars to continue handling
            df = pl.from_pandas(df_pandas)

        except Exception as e:
            print(f"Error: {e}")
            df = pl.DataFrame()

        return df

    '''
    Edit a data frame to have the same columns, same column data types, and same column names as the corresponding database table. Information such as bag_files_id
    and ros_publish_time are added now.
    '''
    def update_df(self, df, table_name, mapping_dict, db_col_lst, bag_files_id):
        try:
            # Create a new column for the bag_file_id, which should be the same as bags are read one at a time
            bag_file_column = pl.Series('bag_files_id', [bag_files_id] * df.height, dtype =  pl.Int32)
            df = df.with_columns(bag_file_column)
            print("\tNew column for bag_files_id added.")

            # Add a column for ros_publish_time: ros_time = secs + nsecs * 10^-9
            exp = 10**(-9)
            ros_time_column = ((pl.col('secs') + (pl.col('nsecs') * exp)).cast(pl.Float32).alias('ros_publish_time'))
            df = df.with_columns(ros_time_column)
            print("\tNew column for ros_publish_time added.")

            if (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga' or
                table_name == 'gps_spark_fun_rear_left_gst' or table_name == 'gps_spark_fun_rear_right_gst' or table_name == 'gps_spark_fun_front_gst'):
                # Add a column for gpstime: gpstime = gpssecs + gpsnsecs * 10^-9
                gpstime_column = ((pl.col('GPSSecs') + (pl.col('GPSMicroSecs') * exp)).cast(pl.Float32).alias('gpstime'))
                df = df.with_columns(gpstime_column)
                print("\tNew column for gpstime added.")

                # GGA sensor has a column for base station - access the database for this to get the id of the base station
                if (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga'):
                    global base_station_id
                    global base_stations
                    
                    base_station_id_lst = []
                    
                    # Make a list out of all of the values in the 'BaseStationID' column
                    base_station_column = df.select(pl.col('BaseStationID'))
                    base_station_lst = base_station_column.to_series().str.strip_chars('"').to_list()

                    for base_station in base_station_lst:
                        if base_station not in base_stations:
                            base_stations.append(base_station)
                            base_station_id += 1
                        base_station_id_lst.append(base_station_id)
                    
                    # Add a column to the database of the list of base station ids
                    base_station_id_column = pl.Series('base_station_messages_id', base_station_id_lst)
                    df = df.with_columns(base_station_id_column)

                    # Drop the original 'BaseStationID' column from the data frame
                    df = df.drop('BaseStationID')

                    # Update the mapping_dict by replacing 'BaseStationID' with 'base_station_messages_id', keeping the original value
                    #   1. Find the key in the mapping_dict corresponding to 'BaseStationID', use this key to get the corresponding value
                    #   2. Delete the old key and add the new key with the same value
                    base_station_key = list(mapping_dict.keys())[-1]
                    base_station_value = mapping_dict[base_station_key]

                    del mapping_dict[base_station_key]
                    mapping_dict.update({'base_station_messages_id' : base_station_value})

                    print("\tNew column for base_station_ids added.")

            '''
            # Simple Debugging: Check How Data Frame Has Changed
            print("Updated Columns")
            print(df.columns)
            #print(df.head(2))
            print(db_col_lst)
            ''
            print(len(df.columns))
            print(len(db_col_lst))
            '''

            # Ensure uniformity between the data frame columns and the db table columns. Change the names and reorder to match the db table
            if (len(db_col_lst) == len(df.columns)):
                # Since the values in the mapping_dict are a list, create a new dictionary made of the same key but with the value being 1
                # of the items from the original value list

                # Rename the columns
                name_map = {original_name : new_name[0] for original_name, new_name in mapping_dict.items()}
                df = df.rename(name_map)

                # Ensure that columns have the same data types
                type_map = {new_name[0] : new_type for new_name, (new_name, new_type) in mapping_dict.items()}
                for name, type in type_map.items():
                    if name in df.columns:
                        df = df.with_columns([pl.col(name).cast(type)])

                # Reorder the columns to match with the db table layout
                new_column_order = db_col_lst
                df = df.select(new_column_order)
                # print(list(df.columns))   # Simple debugging, check whether columns match
                
            else:
                raise Exception("Error, the number of data frame columns is not the same as the number of database table columns.")

            return df

        except Exception as e:
            print(f"Error creating data frame: {e}")



'''
    ========================================= Functions ===========================================
    #	Purpose: To simplify the main() function, created many smaller methods to create data frames
    #            based off the location of where the data should be read from.
    # 
    #   Methods:
    #       1. def get_bag_file_topics(bag_file, topic_lst)
    #           Read a bag file to find out all of the topics and subtopics in that bag file.
    #           Helpful for either debugging or for later uses when more tables will be added to
    #           the database.
    #
    #       2. def bag_csv_to_df(files, bag_name, bag_id, topic_lst, from_bag, from_csv, to_csv)
    #           Both bag file and csv require the same logic/have the same needs to create data frames and
    #           then both need to be altered, hence why the two are combined.
    #
    #           To handle any differences, such as the fact that the bag file topics are based off of the 
    #           topic list while the CSV topics will come from the given CSV files - create a dictionary
    #           matching each CSV file name to the corresponding topic.      
    # 
    #           Looping through each topic, determine topics and other important information.
    #           Then build the proper data frame. Alter the data frame to add in new columns,
    #           reorder the columns, and change the column names.
    #           
    #           If writing to a CSV file, call those functions here.
    #           Time how long it takes to do all of this.
    # 
    #       3. def write_csv(folder, topic, df)
    #           Write a CSV file for a given topic with a corresponding data frame. Create a new
    #           folder to store each of these CSV files for the same bag file if it doesn't
    #           already exist.
    #
    # 	Author: Sadie Duncan
    # 	Date:   08/07/2024
    ===============================================================================================
'''
'''
Read a bag file to find out all of the topics and subtopics in that bag file.
'''
def get_bag_file_topics(bag_file, topic_lst):
    # Make both a dictionary to store topics and subtopics and a list to store topics
    topic_key_dict = {}
    all_topics_lst = []

    bag = rosbag.Bag(bag_file)
    for topic, msg, t in bag.read_messages():
        if topic not in all_topics_lst:
            all_topics_lst.append(topic)                         # Adding to the topics list

        if topic in all_topics_lst:
            if msg.__slots__ not in topic_key_dict.items():
                topic_key_dict.update({topic : msg.__slots__})   # Adding topics : subtopics to the dictionary

    # Printing these lists and dictionaries
    print(f"\nListing all topics from {bag_file}: \n{all_topics_lst}")

    print(f"\nListing all topics and keys from {bag_file}:")
    for topic, keys in topic_key_dict.items():
        print(f"{topic}: {keys}")

    return topic_key_dict   # Return the dictionary in case there is any useful information


def parse_camera_bags(cam_files):
    for file in cam_files:
        bag = rosbag.Bag(file)
        bag_name = bag.filename

        folder = bag_name.rstrip('.bag')
        try:
            os.makedirs(folder)
        except:
            print(f"This folder already exists: {folder}")
            pass

        topic_lst = []
        for topic, msg, t in bag.read_messages():
            if topic not in topic_lst:
                topic_lst.append(topic)                         # Adding to the topics list
        
        print(f"\nFor {file}, the following {len(topic_lst)} will be parsed: {topic_lst}")

        pc = parseCamera(folder, bag)
        for topic in topic_lst:
            cam_topic = topic
            output_file_name = f"{folder}/{cam_topic.replace('/', '_slash_')}.txt"   # Determining the file name
            pc.parseCamera(topic, output_file_name)
            print(f"{topic} has been parsed.")


'''
Both bag file and csv have the same needs to create data frames and then both need to be altered, use the same function for both.

To handle any differences, such as the fact that the bag file topics are based off of the topic list while the CSV topics
will come from the given CSV files - create a dictionary matching each CSV file name to the corresponding topic.      

Looping through each topic, determine topics and other important information. Then build the proper data frame. Alter the
data frame to add in new columns, reorder the columns, and change the column names.

If writing to a CSV file, call those functions here.
'''
def bag_csv_to_df(files, bag_name, bag_id, topic_lst, from_bag, from_csv, to_csv):
    topic_file_dict = {}

    # Create a dictionary where the key is the topic and the value is the bag file
    # Not really needed, but a dictionary is needed for CSV, so this is made just in case
    if (from_bag == 1):
        for topic in topic_lst:
            bag_file_name = files
            topic_file_dict.update({topic : bag_file_name})
    
    # Create a dictionary where the value is the CSV file name and the CSV file name is edited to create a topic key
    elif (from_csv == 1):
        for file_name in files:
            path = Path(file_name)
            topic = path.stem
            topic = topic.replace('_slash_', '/')   # Basically turning '/' into '_slash_'
            topic_file_dict.update({topic : file_name})
    
    else:
        raise Exception("Error: Something wrong with selected files.")
    
    df_count = 0   # Keep track of the number of data frames created

    # Go through each topic one at a time (or each CSV file)
    for topic, file in topic_file_dict.items():
        topic_start_time = time.time()

        # Declare and initialize a few variables
        table_name = ''
        mapping_dict = {}
        db_col_lst = []
                    
        print("------------------------------------------------------------------------------------------------------------------")
        print(f"\nNow parsing '{topic}':")

        # Determine relevant information based off of the topic
        table_name, mapping_dict, db_col_lst = get_topics(topic)
        key_lst = list(mapping_dict.keys())

        polars = DFBuilder(file_name = file, topic = topic, keys = key_lst)   # Create an instance of the DFBuilder class

        # Create the proper data frame
        if (from_bag == 1):
            df = polars.bag_to_df()
            print("\nOriginal data frame created.\n")
        
        else:
            df = polars.csv_to_df()
            print("\nOriginal data frame created.\n")
        

        # Update the data frame to add new columns, reorder the columns, and change the column names.
        new_df = polars.update_df(df, table_name, mapping_dict, db_col_lst, bag_id)

        print(f"\nTotal size of updated '{topic}' data frame: {new_df.shape}")
        print(f"Displaying the first 3 rows of updated '{topic}' data frame: ")
        print(new_df.head(3))
        
        if (to_csv == 1): 
            folder = bag_name[:-4]
            write_csv(folder, topic, new_df)

        topic_end_time = time.time()
        topic_total_time = topic_end_time - topic_start_time
        print(f"\nTime to read/write '{topic} ': {topic_total_time} seconds")
        print("------------------------------------------------------------------------------------------------------------------")

        df_count += 1   # Increase the count of the number of data frames created by 1
    
    print(f"Total number of data frames created: {df_count}")

'''
Write a CSV file for a given topic with a corresponding data frame. Create a new folder to store each of these CSV files for the same
bag file if it doesn't already exist.
'''
def write_csv(folder, topic, df):
    os.makedirs(folder, exist_ok = True)   # Make a new folder if one doesn't already exists

    # For handling LiDAR sensors - DO THIS LATER
    if topic == '/sick_lms500/scan' or topic == '/velodyne_points' or topic == '/velodyne_packets':
                # filename = f"{folder}/{topic.replace('/', '_slash_')}.txt"
                filename = 'pass'    
    else:
        filename = f"{folder}/{topic.replace('/', '_slash_')}.csv"   # Determining the file name
    
    if not os.path.exists(filename):     # Make sure the same file hasn't been written already
        print(f"\nWriting a csv file for '{topic}'")
        if filename != 'pass':
            if df.is_empty():            # If the data frame is empty, there must be an error
                print(f"\nThe {filename} data frame is empty. csv file was not written.")
            else:
                pd_df = df.to_pandas()   # Convert the data frame to Pandas to be easier to write
                pd_df.to_csv(filename, index = False, header = True)   # Write the CSV file
                print(f"\n'{filename}' has been successfully written with {df.shape[0]} rows and {df.shape[1]} columns.")



'''
    ========================================== Main() =============================================
    #   Process:
    #       1. Start timing the runtime.
    #       2. Determine plans: whether the data frame is coming from a bag file or a CSV file and 
    #          if the data frame is being written to a CSV file (from_bag, from_csv, to_csv).
    #       3. Check system arguments, whether the correct amount of arguments were given, and what files
    #          ('.csv' or '.bag') to read from the directory folder.
    #       4. If you're reading a camera parsing bag
    #       5. If you're reading from CSV files, you need to know either the corresponding bag file name AND id.
    # 
    #       6. If you are reading from a bag file, handle each bag file one at a time, find the
    #          bag file id from its name, and use bag_csv_to_df
    #               a. If you are writing to a CSV file, write the CSV files.
    #       7. If reading from CSV files, recall the corresponding bag file name and id, then use bag_csv_to_df
    #               a. If you are writing to a CSV file, write the CSV files.
    #       8. Calculate the total runtime.
    #
    # 	Author: Sadie Duncan
    # 	Date:   08/07/2024
    ===============================================================================================
'''
def main():
    start_time = time.time()   # Start timing the runtime

    # Determine plans: whether the df is coming from a bag file, or a CSV file and if the df is being written to a CSV file 
    cam_flag = 1
    from_bag = 0
    from_csv = 0
    to_csv = 0

    # Declare and initialize multiple variables
    bag_files = []
    csv_files = []

    # Most important topics currently: encoder, trigger, and GPS SparkFun sensors
    # Still to incorporate: velodyne and sick LiDAR
    topic_lst = ['/sick_lms_5xx/scan', 
                 '/GPS_SparkFun_Front_GGA', '/GPS_SparkFun_Front_VTG', 
                 '/GPS_SparkFun_RearLeft_GGA', '/GPS_SparkFun_RearLeft_GST', '/GPS_SparkFun_RearLeft_VTG',
                 '/GPS_SparkFun_RearRight_GGA', '/GPS_SparkFun_RearRight_GST', '/GPS_SparkFun_RearRight_VTG',
                 '/parseEncoder', '/parseTrigger']

    # Check system arguments
    if (len(sys.argv) > 2):
        # Too many arguments given, stop the program
        print(f"Invalid number of arguments - should either be 2 ('parse_and_insert.py' and '<>.bag'/'<>.csv') or just 1 ('parse_and_insert.py').")
        sys.exit(1)

    elif (len(sys.argv) == 2):
        # Gave both the Python script and either a CSV file or bag file to test
        # Determine the filename and what type of file ('.bag' or '.csv')
        file = [sys.argv[1]]
        file_type = file[0][-4:]

        # Check that you were not given the wrong type of file (ie. '.txt')
        if file[0] in os.listdir("."):
            if (file_type == ".bag"):
                bag_files = [file]   # Using this file as the bag file to read
            elif (file_type == ".csv"):
                csv_files = [file]   # Using this file as the CSV file to read
            else:
                # If else, you gave the wrong type of file, exit the program
                print(f"Not a valid file type: {sys.argv}")
                sys.exit(1)
        else:
            print(f"File does not exist: {sys.argv}")
            sys.exit(1)

        print(f"Reading 1 file: {file[0]}")
        
    elif (len(sys.argv) == 1):
        # Check the directory to see what '.bag' or '.csv' files there are to read - store these in a list
        if (from_bag == 1 or cam_flag == 1):
            # Check for files ending in '.bag' - adding these to a bag file list
            bag_files = [f for f in os.listdir(".") if f[-4:] == ".bag" and len(f) != 4]
            print(f"Reading {len(bag_files)} bag files in the current directory:")
            for f in bag_files:
                print(f"\t{f}")
        
        elif (from_csv == 1):
            # Check for files ending in '.csv' - adding these to a CSV file list
            csv_files = [f for f in os.listdir(".") if f[-4:] == ".csv"]
            print(f"Reading {len(csv_files)} CSV files in the current directory:")
            for f in csv_files:
                print(f"\t{f}")
        
        else:
            print(f"Planning to read from the database.")

    else:
        # Rare, shouldn't come across this. Stops the program.
        print(f"Bad arguments(s): {sys.argv}")
        sys.exit(1)

    # Get the full list of topics and subtopics
    '''
    for bag_file in bag_files:
        topic_key_dict = get_bag_file_topics(bag_file, topic_lst)
    all_topics_lst = list(topic_key_dict.keys())
    # '''

    print()
    global bag_id
    cam_files = []
    temp_lst = []

    for bag_file in bag_files:
        if (len(bag_file) > 37):
            cam_files.append(bag_file)
            print(f"{bag_file} would have a bag ID of: {bag_id}" )
            bag_id += 1
        else:
            temp_lst.append(bag_file)   
    bag_files = temp_lst
    
    if (cam_flag == 1):
        parse_camera_bags(cam_files)

    '''
    /velodyne_packets: ['header', 'packets']
    /sick_lms_5xx/scan: ['header', 'angle_min', 'angle_max', 'angle_increment', 'time_increment', 'scan_time', 'range_min', 'range_max', 'ranges', 'intensities']  
    '''

    if (from_bag == 1):
        # If you are reading from a bag file, handle each bag file one at a time, find the bag file id from its name
        for bag_file in bag_files:
            bag_name = bag_file
            print(f"\nNow reading '{bag_name}' (id = {bag_id}). The following {len(topic_lst)} topics will be parsed: \n{topic_lst}:")
            bag_csv_to_df(bag_file, bag_name, bag_id, topic_lst, from_bag, from_csv, to_csv)              # Create a data frame
            '''if (bag_file == 'mapping_van_2024-06-24-02-18-35_0.bag'):   # For testing
                print(f"\nNow reading '{bag_name}' (id = {bag_id}). The following {len(topic_lst)} topics will be parsed: \n{topic_lst}:")
                # bag_csv_to_df(bag_file, bag_name, bag_id, topic_lst, from_bag, from_csv, to_csv)      # Create a data frame'''
            bag_id += 1

    elif (from_csv == 1):
        bag_file_name2 = "mapping_van_2024-06-20-15-25-21_0.bag"
        bag_file_name = "mapping_van_2024-06-24-02-18-35_0.bag"   # For testing
        bag_file_id = 1

        # If reading from CSV files, recall the corresponding bag file name and id, then use bag_csv_to_df
        print(f"\nFor {bag_file_name} (id = {bag_file_id}):")
        bag_csv_to_df(csv_files, bag_file_name, bag_file_id, topic_lst, from_bag, from_csv, to_csv)   # Create a data frame

    else:
        print("\nError: Not given any instructions to execute.")

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal Runtime: {total_time} seconds")   # Calculate the total runtime

if __name__ == "__main__":
    main()

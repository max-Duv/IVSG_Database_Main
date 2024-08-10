'''
Python 3.10.1 and Python 3.12.3

Written by Sadie Duncan at IVSG during 2024 Aug.
Supervised by Professor Sean Brennan

Purpose: The purpose of this script is to utilize the Polars and Pandas library to more efficiently handle the mapping van data.
         Polars or Pandas (mainly Polars) dataframes will be created either from bag files, CSV files, or the database itself. 
         Once the data frame is created, it can be altered to add or remove columns. From the data frame, one can insert the data frame
         into the database or create CSV files.

         TLDR:
            1. Read a bag file, CSV file, or from the database and create a Pandas dataframe
            2. Convert the Pandas dataframe into a Polars dataframe for faster handling
            3. Alter the Polars dataframe if needed (remove or add columns, etc.)
            4. Write dataframe to the database or to a CSV file

        Possible Uses:
            1. bag -> df    (DONE)
            2. csv -> df    (DONE)
            3. db  -> df    (DONE)
            ----------------------
            4. df  -> db    (DONE)
            5. df  -> csv   (DONE)

Usage:
    In the psql server:
        Template:   \i <path_to_script>/<sql_script>.sql;
        Example:    \i  /home/brennan/Documents/SQLdatabase/raw_data_db_launch.sql; 
    
    In the folder with the SQL script:
        Template:   sudo -u <user> psql -d <db-name> -a -f <sql_script>.sql
        Example:    sudo -u postgres psql -d testdb -a -f raw_data_db_launch.sql

Note:
    1. At this point, the only point of the base_station_messages table is to hold the different base station 
       names: (LTI, Test Track, Reber1, and Reber2).
    2. Due to the foreign key relationships, when testing, it's best to delete the entire database and start over
       than delete each table individually.
'''

'''


To Do:
    1. Integrate camera parsing functions
    2. Integrate velodyne parsing functions

Packages to Install:
    pip install polars OR pip install polars-lts-cpu ()

6:40
'''

from io import StringIO 
from pathlib import Path
import os
import sys
import csv
import time
import datetime
import warnings
import pdb

import psycopg2
import rosbag
import pandas as pd
import polars as pl
import numpy as np

from updated_list_of_columns import determine_columns       # Keep records of different column names (for CSV and db) here to simplify script

warnings.simplefilter("ignore", category = FutureWarning)   # Using panadas yielded an error -> ignore this error

##########################################################################################################################################
'''
Creating a class for the database
'''
##########################################################################################################################################
class Database:
    def __init__(self, username, password, server, port, db_name):
        try:
            # Template: "postgresql://username:password@server:port/db_name"
            # self.postgres_url = f"postgresql://{username}:{password}@{server}:{port}/{db_name}"

            self.conn = psycopg2.connect(database = db_name,
                                        user = username,
                                        password = password,
                                        host = server,
                                        port = port)
            
            self.cursor = self.conn.cursor()
            print("PostgreSQL Connection is open.")
            
        except psycopg2.Error as e:
            print(f"Unable to connect to the database: {e}")
    
    def insert_and_return(self, table_name, col_lst, val_lst):
        try:
            cursor = self.cursor
            conn = self.conn

            cols = ','.join(col_lst)
            vals = ','.join(['%s'] * len(val_lst))

            insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({vals}) RETURNING id;"
            cursor.execute(insert_query, val_lst)
            print(f"\tNew row(s) inserted into {table_name}")

            inserted_id = cursor.fetchone()[0]
            return inserted_id

        except psycopg2.Error as e:
            print(f"Unable to insert into the database: {e}")
            conn.rollback()

    def select(self, table_name, param, col, val):
        try:
            cursor = self.cursor
            conn = self.conn

            select_query = f"SELECT {param} FROM {table_name} WHERE {col} = '{val}';"
            cursor.execute(select_query)

            result = cursor.fetchone()

            if (result is None):
                col_lst = [col]
                val_lst = [val]
                return_id = self.insert_and_return(table_name, col_lst, val_lst)
            
            else:
                return_id = result[0]
            
            return return_id

        except psycopg2.Error as e:
            print(f"Unable to connect to the database: {e}")
            conn.rollback()

    def select_multiple(self, table_name, col, val):
        try:
            cursor = self.cursor
            conn = self.conn

            select_query = f"SELECT * FROM {table_name} WHERE {col} = {val};"
            cursor.execute(select_query)

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            pd_df = pd.DataFrame(rows, columns = columns)
            df = pl.from_pandas(pd_df)


        except psycopg2.Error as e:
            df = pl.DataFrame()
            print(f"Unable to connect to the database: {e}")
            conn.rollback()

        return df

    def df_to_db(self, table_name, df, db_col_lst):
        try:
            cursor = self.cursor
            conn = self.conn

            # Convert the dataframe into a pandas dataframe and then into a CSV string to work with copy_expert
            pd_df = df.to_pandas()
            csv_buffer = StringIO()
            pd_df.to_csv(csv_buffer, index = False, header = True, sep = ",")
            csv_buffer.seek(0)   # Rewind the buffer to the beginning for reading
            # print(csv_buffer.read())

            # Build the query
            query_fillin = f"{table_name} ({', '.join(db_col_lst)})"
            query = f"COPY {query_fillin} FROM STDIN WITH CSV HEADER NULL AS 'NULL'"

            # Use copy_expert to transport data into the database
            cursor.copy_expert(sql = query, file = csv_buffer)
            print(f"The data frame has successfully been inserted into {table_name}.")

        except psycopg2.Error as e:
            print(f"Unable to write the data frame into the database: {e}")
            conn.rollback()

    def delete(self, table_name, id):
        try:
            cursor = self.cursor
            conn = self.conn

            delete_query = f"DELETE FROM {table_name} WHERE id = {id};"
            cursor.execute(delete_query)

        except psycopg2.Error as e:
            print(f"Unable to delete from the database: {e}")
            conn.rollback()
    
    def disconnect(self):
        cursor = self.cursor
        conn = self.conn

        cursor.close()
        conn.commit()
        conn.close()
        print("PostgreSQL connection is closed.")

##########################################################################################################################################
'''
Creating a class for the data frame builder
'''
##########################################################################################################################################
class DFBuilder:
    def __init__(self, file_name, topic, keys):
        self.file_name = file_name
        self.topic = topic
        self.keys = keys
    
    def bag_to_df(self):
        try:
            bag_file = self.file_name
            topic = self.topic
            keys = self.keys

            bag = rosbag.Bag(bag_file)
            data = []

            for _, msg, _ in bag.read_messages(topics = [topic]):
                row = {}
                for key in keys:
                    if (key == 'rosbagTimestamp'):
                        value = msg.header.stamp
                    elif (key == 'secs'):
                        value = msg.header.stamp.secs
                    elif (key == 'nsecs'):
                        value = msg.header.stamp.nsecs
                    else:
                        value = getattr(msg, key, None)

                    row[key] = value

                data.append(row)

            if data:
                df = pl.DataFrame(data)

            else:
                df = pl.DataFrame()

        except Exception as e:
            print(f"Error: {e}")
            df = pl.DataFrame()

        return df

    def csv_to_df(self):
        try:
            csv_file = self.file_name
            keys = self.keys

            # Using pandas to read certain columns from the CSV file
            df_pandas = pd.read_csv(csv_file, sep = ',', usecols = keys)
            # print(df_pandas.columns.tolist())

            # Drop emtpy rows
            df_pandas = df_pandas.dropna(how = 'all')

            # Convert to polars to ontinue handling data frames
            df = pl.DataFrame(df_pandas)

            print("Successfully read the CSV file.")

        except Exception as e:
            print(f"Error: {e}")
            df = pl.DataFrame()

        return df

    def update_df(self, df, is_sensor, table_name, mapping_dict, db_col_lst, bag_files_id, db):
        try:
            if (is_sensor == 1):
                bag_file_column = pl.Series('bag_files_id', [bag_files_id] * df.height, dtype =  pl.Int32)
                df = df.with_columns(bag_file_column)
                print("\tNew column for bag_files added.")

                # ros_time = secs + nsecs * 10^-9
                # gpstime = gpssecs + gpsnsecs * 10^-9
                exp = 10**(-9)
                ros_time_column = ((pl.col('secs') + (pl.col('nsecs') * exp)).cast(pl.Float32).alias('ros_publish_time'))
                df = df.with_columns(ros_time_column)
                print("\tNew column for ros_publish_time added.")

                if (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga' or
                    table_name == 'gps_spark_fun_rear_left_gst' or table_name == 'gps_spark_fun_rear_right_gst' or table_name == 'gps_spark_fun_front_gst'):
                    gpstime_column = ((pl.col('GPSSecs') + (pl.col('GPSMicroSecs') * exp)).cast(pl.Float32).alias('gpstime'))
                    df = df.with_columns(gpstime_column)
                    print("\tNew column for gpstime added.")

                    # GGA sensor has a column for base station - access the db database for this, return the id of the base station
                    if (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga'):
                        base_station_id_lst = []
                        
                        base_station_column = df.select(pl.col('BaseStationID'))
                        base_station_lst = base_station_column.to_series().str.strip_chars('"').to_list()

                        for base_station in base_station_lst:
                            base_station_id = db.select('base_station_messages', 'id', 'base_station_name', base_station)
                            base_station_id_lst.append(base_station_id)
                        
                        base_station_id_column = pl.Series('base_station_messages_id', base_station_id_lst)
                        df = df.with_columns(base_station_id_column)

                        df = df.drop('BaseStationID')

                        base_station_key = list(mapping_dict.keys())[-1]
                        base_station_value = mapping_dict[base_station_key]

                        del mapping_dict[base_station_key]
                        mapping_dict.update({'base_station_messages_id' : base_station_value})

                        print("\tNew column for base_station_ids added.")

            '''
            # Check How Data Frame Has Changed
            print("Updated Columns")
            print(df.columns)
            #print(df.head(2))
            print(db_col_lst)
            ''
            print(len(df.columns))
            print(len(db_col_lst))
            '''

            # Ensure uniformity between the dataframe columns and the db table columns. Changing the names and reordering to match db setup
            if (len(db_col_lst) == len(df.columns)):
                # Ensure datatypes are the same, otherwise you won't be able to insert
                name_map = {original_name : new_name[0] for original_name, new_name in mapping_dict.items()}
                df = df.rename(name_map)
                # df = df.rename({col: col.lower() for col in df.columns})

                type_map = {new_name[0] : new_type for new_name, (new_name, new_type) in mapping_dict.items()}
                
                for name, type in type_map.items():
                    if name in df.columns:
                        df = df.with_columns([pl.col(name).cast(type)])

                new_column_order = db_col_lst
                df = df.select(new_column_order)
                # print(list(df.columns))
            
            else:
                raise Exception("Error, the number of data frame columns is not the same as the number of database table columns.")

            return df

        except Exception as e:
            print(f"Error creating data frame: {e}")

##########################################################################################################################################
'''
Functions
'''
##########################################################################################################################################
def get_bag_file_topics(bag_file, topic_lst):
    topic_key_dict = {}
    all_topics_lst = []

    bag = rosbag.Bag(bag_file)
    for topic, msg, t in bag.read_messages():
        if topic not in all_topics_lst:
            all_topics_lst.append(topic)

        if topic in all_topics_lst:
            if msg.__slots__ not in topic_key_dict.items():
                topic_key_dict.update({topic : msg.__slots__})

    print(f"Listing all topics from {bag_file}: \n{all_topics_lst}")

    print(f"\nListing all topics and keys from {bag_file}:")
    for topic, keys in topic_key_dict.items():
        print(f"{topic}: {keys}")

    return topic_key_dict

def db_to_df(to_csv, db, bag_name, bag_id, topic_lst):
    df_count = 0

    for topic in topic_lst:
        topic_start_time = time.time()
                    
        print("------------------------------------------------------------------------------------------------------------------")
        print(f"\nStarting on '{topic}':")

        is_sensor, table_name, mapping_dict, db_col_lst = determine_columns(topic)
        col = "bag_files_id"
        val = bag_id
        df = db.select_multiple(table_name, col, val)

        print(f"\nTotal size of '{table_name}' for the bag file with id = {bag_id}: {df.shape}")
        print(f"Displaying the first 3 rows of '{table_name}:")
        print(df.head(3))
        
        if (to_csv == 1):                   
            folder = bag_name[:-4]
            write_csv(folder, topic, df)

        topic_end_time = time.time()
        topic_total_time = topic_end_time - topic_start_time
        print(f"\nTime to create a dataframe for '{topic} ': {topic_total_time} seconds")
        print("------------------------------------------------------------------------------------------------------------------")

        df_count += 1
    
    print(f"Total number of data frames created: {df_count}")

def bag_csv_to_df(db, files, bag_name, bag_id, topic_lst, from_bag, from_csv, to_csv, to_db):
    topic_file_dict = {}

    if (from_bag == 1):
        for topic in topic_lst:
            bag_file_name = files
            topic_file_dict.update({topic : bag_file_name})
    
    elif (from_csv == 1):
        for file_name in files:
            path = Path(file_name)
            topic = path.stem
            topic = topic.replace('_slash_', '/')
            topic_file_dict.update({topic : file_name})
    
    else:
        raise Exception("Error: Something wrong with selected files.")
    
    df_count = 0

    for topic, file in topic_file_dict.items():
        topic_start_time = time.time()

        is_sensor = 0
        table_name = ''
        mapping_dict = {}
        db_col_lst = []
                    
        print("------------------------------------------------------------------------------------------------------------------")
        print(f"\nStarting on '{topic}':")

        is_sensor, table_name, mapping_dict, db_col_lst = determine_columns(topic)
        key_lst = list(mapping_dict.keys())

        polars = DFBuilder(file_name = file, topic = topic, keys = key_lst)

        if (from_bag == 1):
            df = polars.bag_to_df()
            print("\nOriginal dataframe created.\n")
        
        else:
            df = polars.csv_to_df()
            print("Original dataframe created")

        new_df = polars.update_df(df = df, is_sensor = is_sensor, table_name = table_name,
                                  mapping_dict = mapping_dict, db_col_lst = db_col_lst,
                                  bag_files_id = bag_id, db = db)

        print(f"\nTotal size of updated '{topic}' dataframe: {new_df.shape}")
        print(f"Displaying the first 3 rows of updated '{topic}' dataframe: ")
        print(new_df.head(3))

        if (to_db == 1):
            db.df_to_db(table_name, new_df, db_col_lst)
        
        if (to_csv == 1): 
            folder = bag_name[:-4]
            write_csv(folder, topic, df)

        topic_end_time = time.time()
        topic_total_time = topic_end_time - topic_start_time
        print(f"\nTime to read/write '{topic} ': {topic_total_time} seconds")
        print("------------------------------------------------------------------------------------------------------------------")

        df_count += 1
    
    print(f"Total number of dataframes created: {df_count}")

def write_csv(folder, topic, df):
    os.makedirs(folder, exist_ok = True)
    if topic == '/sick_lms500/scan' or topic == '/velodyne_points' or topic == '/velodyne_packets':
                # filename = f"{folder}/{topic.replace('/', '_slash_')}.txt"
                filename = 'pass'    
    else:
        filename = f"{folder}/{topic.replace('/', '_slash_')}.csv"
    
    if not os.path.exists(filename):
        print(f"\nWriting a csv file for '{topic}'")
        if filename != 'pass':
            if df.is_empty():
                print(f"\nThe {filename} dataframe is empty. csv file was not written.")
            else:
                pd_df = df.to_pandas()
                pd_df.to_csv(filename, index = False, header = True)
                print(f"\n'{filename}.csv' has been successfully written with {df.shape[0]} rows and {df.shape[1]} columns.")

def main():
    start_time = time.time()

    from_db = 0
    from_bag = 1
    from_csv = 0
    to_csv = 1
    to_db = 1

    bag_files = []
    csv_files = []

    topic_lst = ['/GPS_SparkFun_Front_GGA', '/GPS_SparkFun_Front_VTG', 
                 '/GPS_SparkFun_RearLeft_GGA', '/GPS_SparkFun_RearLeft_GST', '/GPS_SparkFun_RearLeft_VTG',
                 '/GPS_SparkFun_RearRight_GGA', '/GPS_SparkFun_RearRight_GST', '/GPS_SparkFun_RearRight_VTG',
                 '/parseEncoder', '/parseTrigger']
        
    '''
    topic_key_dict = get_bag_file_topics(bag_file, topic_lst)
    all_topics_lst = list(topic_key_dict.keys())
    '''

    if (len(sys.argv) > 2):
        print(f"Invalid number of arguments - should either be 2 ('parse_and_insert.py' and '<>.bag'/'<>.csv') or just 1 ('parse_and_insert.py').")
        sys.exit(1)

    elif (len(sys.argv) == 2):
        file = [sys.argv[1]]
        file_type = file[0][-4:]

        if file[0] in os.listdir("."):
            if (file_type == ".bag"):
                bag_files = [file]
            elif (file_type == ".csv"):
                csv_files = [file]
            else:
                print(f"Not a valid file type: {sys.argv}")
                sys.exit(1)
        else:
            print(f"File does not exist: {sys.argv}")
            sys.exit(1)

        print(f"Reading 1 file: {file[0]}")
        
    elif (len(sys.argv) == 1):
        if (from_bag == 1):
            bag_files = [f for f in os.listdir(".") if f[-4:] == ".bag" and len(f) != 4]
            num_of_bags = len(bag_files)
            print(f"Reading {num_of_bags} bagfiles in the current directory:")
            for f in bag_files:
                print(f)
        
        elif (from_csv == 1):
            csv_files = [f for f in os.listdir(".") if f[-4:] == ".csv"]
            num_of_files = len(csv_files)
            print(f"Reading {num_of_files} csv files in the current directory:")
            for f in csv_files:
                print(f)
        
        else:
            print(f"Planning to read from the database.")

    else:
        print(f"Bad arguments(s): {sys.argv}")
        sys.exit(1)

    # Database connection parameters
    username = "postgres"
    password = "pass"
    server   = "127.0.0.1"
    port     = "5432"
    db_name  = "testdb"

    # Connect to the database
    if db_name is not None:
        db = Database(username, password, server, port, db_name)

    table = "bag_files"

    '''
    bag_file_id = 1
    param = "bag_file_name"
    col = "id"
    val = bag_file_id
    bag_file_name = db.select(table, param, col, val)
    '''

    # bag_file_name = "mapping_van_2024-06-24-02-18-35_0.bag"
    bag_file_name = "mapping_van_2024-06-20-15-25-21_0.bag"
    param = "id"
    col = "bag_file_name"
    val = bag_file_name
    bag_file_id = db.select(table, param, col, val)
    
    if (from_db == 1):
        print(f"Now reading '{bag_file_name}', which has an ID of {bag_file_id}:")
        db_to_df(to_csv, db, bag_file_name, bag_file_id, topic_lst)

    elif ((from_bag == 1) or (from_csv == 1)):
        if (from_bag == 1):
            for bag_file in bag_files:
                bag_name = bag_file
                bag_id = db.select('bag_files', 'id', 'bag_file_name', bag_file)
                # print(f"Now reading '{bag_file}', which has an ID of {bag_id}:")
                # bag_csv_to_df(db, bag_file, from_bag, from_csv, topic_lst, to_csv, to_db)
                if (bag_file == 'mapping_van_2024-06-20-15-25-21_0.bag'):
                    print(f"Now reading '{bag_name}', which has an ID of {bag_id}:")
                    bag_csv_to_df(db, bag_file, bag_name, bag_id, topic_lst, from_bag, from_csv, to_csv, to_db)

        else:
            print(f"For {bag_file_name}, which has an ID of {bag_file_id}:")
            bag_csv_to_df(db, csv_files, bag_file_name, bag_file_id, topic_lst, from_bag, from_csv, to_csv, to_db)

    else:
        print("\nError: Not given any instructions to execute.")

    db.disconnect()
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal Runtime: {total_time} seconds")

if __name__ == "__main__":  
    main()
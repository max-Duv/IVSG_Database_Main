'''
The purpose of this script is to efficiently bulk insert to the Postgres database from a CSV file using copy_expert.

Note: to install polars...
    pip install connectorx
    pip install polars
        OR pip install polars-lts-cpu ()

    (May need to use: python3 -m pip install <package-name> --break-system-packages)

Note: STILL NEEDS MORE TESTING

To-Do:
    - Fix select function
    - Continue testing with multiple CSV files (of different sensor types)
    - Insert into base_station_messages and bag_files table -> select from -> use those returned variables
    
    - Add in columns for ros_time and gps_time
    - Turn rosbagTimestamp into actual timestamp

    - Test not using sqlalchemy part
    - Test simplfing path to csv
'''

import psycopg2
import connectorx as cx
import polars as pl
import pandas as pd
import numpy as np
import csv
import time
import traceback
import warnings
import pdb

from io import StringIO                # For writting the csv buffer
from sqlalchemy import create_engine   # Will need to use both sqlalchemy and psycopg2 (might try to get rid of this step later)



warnings.simplefilter("ignore", category = FutureWarning)   # Using panadas yielded an error -> ignore this error


'''
Creating a class for the database
'''
class Database:
    # Connect to the postgres database
    def __init__(self, username, password, server, port, db_name):
        try:
            # Creating an engine through sqlalchmey, these same parameters will be used for polars
            # Template: "postgresql://username:password@server:port/db_name"
            #self.postgres_url = "postgresql://" + username + ":" + password + "@" + server + ":" + port + "/" + db_name
            #self.engine = create_engine(self.postgres_url)

            #Connecting and setting up a cursor through psycopg2
            self.conn = psycopg2.connect(database = db_name, 
                                        user = username,
                                        password = password,
                                        host = server,
                                        port = port)
            self.cursor = self.conn.cursor()

            print("PostgreSQL connection is open.")

        except psycopg2.Error as e:
            self.printErrors(error = e, message = "Unable to connect to the database.")

    # Simple insert function that returns the id of the newly inserted value
    def insert_and_return(self, table_name, col_lst, val_lst):
        try:
            cols = ','.join(col_lst)
            vals = ','.join(['%s'] * len(val_lst))

            insert_query = f'INSERT INTO {table_name} ({cols}) VALUES ({vals}) RETURNING id;'
            self.cursor.execute(insert_query, val_lst)

            inserted_id = self.cursor.fetchone()[0]
            return inserted_id

        except psycopg2.Error as e:
            self.printErrors(error = e, message = "Unable to insert to the database.")

    # Simple select function
    def select_from_db(self, table_name, col_lst, val_lst):
        try:
            cols = ','.join(col_lst)
            val = val_lst[0]
            #vals = ','.join(['%s'] * len(val_lst))

            select_query = f'SELECT bag_file_name FROM {table_name} WHERE id = 1;'
            self.cursor.execute(select_query)

            val_id = self.cursor.fetchone()[0]

            if val_id:
                return val_id
            else:
                self.insert_and_return(table_name, col_lst, val_lst)

        except psycopg2.Error as e:
            self.printErrors(error = e, message = "Unable to select from the database.")

    #
    def get_id_lst(self, table_name, col_name, vals):
        val_lst = []

        try:
            for val in vals:
                val_id = self.select_from_db(table_name, col_name, val)
                val_lst.append(val_id)

        except psycopg2.Error as e:
            self.printErrors(error = e, message = "Unable to select from the database.")

        return val_lst


    # Create a dataframe in the Pandas or Polars library from the CSV file
    def create_df(self, table_name, file, is_sensor, csv_col_lst, sql_col_lst, bag_files_id, base_station_messages_id):
        try:
            # Using pandas to read certain columns from the csv file
            # df = pd.read_csv(file_path, sep = "\t", usecols = csv_col_lst)

            # Using polars instead of pandas
            df = pl.read_csv(file, columns = csv_col_lst, separator = "\t")

            print(1)
            
            if (is_sensor == 1):
                bag_file_column = pl.Series("bag_files_id", [bag_files_id] * df.height)
                df = df.with_column(bag_file_column)
                print(2)

                exp = 10^9
                ros_time_column = pl.Series((pl.col('secs') + pl.col('nsecs')) * exp).alias('ros_time')
                df = df.with_column(ros_time_column)

                if (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga' or
                    table_name == 'gps_spark_fun_rear_left_gst' or table_name == 'gps_spark_fun_rear_right_gst' or table_name == 'gps_spark_fun_front_gst'):
                    gpstime_column = pl.Series((pl.col('GPSSecs') + pl.col('GPSMicroSecs')) * exp).alias('gpstime')
                    df = df.with_column(gpstime_column)

                if (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga'):
                    last_column = df.columns[-1]
                    last_column_vals = df[pl.col(last_column)].to_pandas()[last_column].tolist()
                    base_station_id_lst = self.get_id_lst('base_station_messages', 'base_station_name', last_column_vals)

                    base_station_id_column = pl.Series('base_station_messages_id', base_station_id_lst)
                    df = df.with_column(base_station_id_column)
            '''
            ["bag_files_id", "base_station_messages_id",
                       "gpssecs", "gpsmicrosecs", "gpstime"
                       "latitude", "longitude", "altitude",
                       "geosep", "nav_mode", "num_of_sats",
                       "hdop", "age_of_diff", "lock_status",
                       "ros_seconds", "ros_nanoseconds", "ros_time", "ros_timestamp"]
            '''
            columns = df.columns
            print(columns)

            '''
            rosbag_timestamp_column = columns[1]
            secs_column = columns[2]
            nsecs_column = columns[3]
            remaining_columns = columns[4:]

            new_column_order = [bag_file_column] + remaining_columns + [secs_column] + [nsecs_column] + [rosbag_timestamp_column]
            df = df.select(new_column_order)
            '''
                
            '''
            # Insert a new column
            new_column = pl.Series("new_col", [1, 2, 3])  # Adjust the data as needed
            df = df.with_column(new_column)

            # Move an existing column
            column_to_move = "existing_col"
            columns = df.columns
            new_order = [column_to_move] + [col for col in columns if col != column_to_move]

            # Reorder columns in DataFrame
            df = df.select(new_order)
            '''

            # Ensure uniformity between the datafram columns and the db table columns
            ''''
            if (len(sql_col_lst) == len(df.columns)):
                df = df.rename(dict(zip(df.columns, sql_col_lst)))
                df = df.rename({col: col.lower() for col in df.columns})

            print(list(df.columns.values))

            # For each table, print the first two rows
            print(f"First contents of '{table_name}' CSV file: ")
            print(df.head(2))

            return df
            '''

        except:
            print("Error creating dataframe.")

    def csv_to_db(self, table_name, df, sql_col_lst):
        try:

            # Convert the dataframe into a CSV string to work with copy_expert
            csv_buffer = StringIO()
            df.write_csv(file = csv_buffer, has_header = False, sep = ',')
            csv_buffer.seek(0)   # Rewind the buffer to the beginning for reading
            # print(csv_buffer.read())

            # Build the query statement
            query_fillin = table_name + " (" + ", ".join(sql_col_lst) + ") "
            query = '''COPY {} FROM STDIN WITH CSV NULL AS 'NULL' '''.format(query_fillin)
 
            # Use copy_expert to transport data into the database
            self.cursor.copy_expert(sql = query, file = csv_buffer)

            print("CSV successfully inserted into database.")

        except Exception as e:
            self.printErrors(error = e, message = "Error inserting CSV into database.")

    # A function to disconnect from the postgres server
    def disconnect(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()
        print("PostgreSQL connection is closed.")

    # A function to print various errors
    def printErrors(self, error, message = None):
        if message is not None:
            print(message)

        print(error)
        print(error.pgcode)
        print(error.pgerror)
        print(traceback.format_exc())

'''
This function will take a table name and return whether or not the table involves a sensor,
the columns to take from the CSV file and the columns to insert for the Postgres database.
Currently only for the encoder, GPS SparkFun and 3D LiDAR tables. Columns may be changed as needed.
'''
def determine_columns(table_name):
    # Table: base_station_messages
    if (table_name == 'base_station_messages'):
        is_sensor = 0
        csv_col_lst = ["base_station_name", "base_station_message"]
        sql_col_lst = ["base_station_name", "base_station_message"]

    # Table: bag_files
    elif (table_name == 'bag_files'):
        is_sensor = 0
        csv_col_lst = ["bag_files_id"]
        sql_col_lst = ["bag_files_id"]

    # Table: encoder
    elif (table_name == 'encoder'):
        is_sensor = 1
        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs", "mode", "time"
                       "C1", "C2", "C3", "C4", "P1", "E1",
                       "err_wrong_element_length" "err_bad_element_structure",
                       "err_failed_time", "err_bad_uppercase_character",
                       "err_bad_lowercase_character", "err_bad_character"
                       ]
        sql_col_lst = ["bag_files_id", "encoder_mode", "time",
                       "c1", "c2", "c3", "c4", "p1", "e1",
                       "err_wrong_element_length" "err_bad_element_structure",
                       "err_failed_time", "err_bad_uppercase_character",
                       "err_bad_lowercase_character", "err_bad_character",
                       "ros_seconds", "ros_nanoseconds", "ros_time", "ros_timestamp"]

    # Table: gps_spark_fun_gga (left, right, or front)
    elif (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga'):
        is_sensor = 1
        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs",
                       "GPSSecs", "GPSMicroSecs",
                       "Latitude", "Longitude", "Altitude",
                       "GeoSep", "NavMode", "NumOfSats",
                       "HDOP", "AgeOfDiff", "LockStatus" 
                       
                       ]
        sql_col_lst = ["bag_files_id", "base_station_messages_id",
                       "gpssecs", "gpsmicrosecs", "gpstime"
                       "latitude", "longitude", "altitude",
                       "geosep", "nav_mode", "num_of_sats",
                       "hdop", "age_of_diff", "lock_status",
                       "ros_seconds", "ros_nanoseconds", "ros_time", "ros_timestamp"]

    # Table: gps_spark_fun_gst (left, right, or front)
    elif (table_name == 'gps_spark_fun_rear_left_gst' or table_name == 'gps_spark_fun_rear_right_gst' or table_name == 'gps_spark_fun_front_gst'):
        is_sensor = 1
        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs",
                       "GPSSecs", "GPSMicroSecs",
                       "StdMajor", "StdMinor", "StdOri",
                       "StdLat", "StdLon", "StdAlt", 
                       
                       ]
        sql_col_lst = ["bag_files_id", "gpssecs", "gpsmicrosecs", "gpstime"
                       "stdmajor", "stdminor", "stdori",
                       "stdlat", "stdlon", "stdalt",
                       "ros_seconds", "ros_nanoseconds", "ros_time", "ros_timestamp"]

    # Table: gps_spark_fun_vtg (left, right, or front)
    elif (table_name == 'gps_spark_fun_rear_left_vtg' or table_name == 'gps_spark_fun_rear_right_vtg' or table_name == 'gps_spark_fun_front_vtg'):
        is_sensor = 1
        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs",
                       "TrueTrack", "MagTrack", 
                       "SpdOverGrndKnots", "SpdOverGrndKmph"
                       ]
        sql_col_lst = ["bag_files_id", "true_track", "mag_track",
                       "spdovergrndknots", "spdovergrndkmph",
                       "ros_seconds", "ros_nanoseconds", "ros_time", "ros_timestamp"]

    # Table: velodyne_lidar and ouster_lidar
    elif (table_name == 'velodyne_lidar' or table_name == "ouster_lidar" ):
        is_sensor = 1
        csv_col_lst = ["bag_files_id", 
                       "ouster_lidar_hash_tag", "ouster_lidar_location",
                       "ouster_lidar_file_size", "ouster_lidar_file_time",
                       "ros_seconds", "ros_nanoseconds", "ros_timestamp"]
        sql_col_lst = ["bag_files_id", 
                       "ouster_lidar_hash_tag", "ouster_lidar_location",
                       "ouster_lidar_file_size", "ouster_lidar_file_time",
                       "ros_seconds", "ros_nanoseconds", "ros_time", "ros_timestamp"]

    # Table: trigger
    elif (table_name == 'trigger'):
        is_sensor = 1
        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs",
                       "mode", "mode_counts",
                       "adjone", "adjtwo", "adjthree",
                       "err_failed_mode_count", "err_failed_XI_format", "err_failed_checkInformation",
                       "err_trigger_unknown_error_occured", "err_bad_uppercase_character",
                       "err_bad_lowercase_character", "err_bad_three_adj_element",
                       "err_bad_first_element", "err_bad_character", "err_wrong_element_length",]
        sql_col_lst = ["bag_files_id", "trigger_mode", "trigger_mode_counts",
                       "adjone", "adjtwo", "adjthree",
                       "err_failed_mode_count", "err_failed_xi_format", "err_failed_check_information",
                       "err_trigger_unknown_error_occured", "err_bad_uppercase_character",
                       "err_bad_lowercase_character", "err_bad_three_adj_element",
                       "err_bad_first_element", "err_bad_character", "err_wrong_element_length",
                       "ros_seconds", "ros_nanoseconds", "ros_time", "ros_timestamp"]

    return is_sensor, csv_col_lst, sql_col_lst

'''
Main Function
'''
def main():
    start_time = time.time()

    # database connection parameters
    username = "postgres"
    password = "pass"
    server   = "127.0.0.1"
    port     = "5432"
    db_name  = "testdb"

    # Connect to the database
    if db_name is not None:
        db = Database(username, password, server, port, db_name)
    
    # INSERT and SELECT from the base_station_messages table:
    #base_station_val = "N/A"
    #db.insert_to_db("base_station_messages", "base_station_name", base_station_val)

    #base_station_val = "PSU_Pitts"
    #db.insert_to_db("base_station_messages", "base_station_name", base_station_val) 
    #base_station_messages_id = db.select_from_db("base_station_messages", "base_station_name", base_station_val)

    # INSERT and SELECT from the base_station_messages table:
    bag_file_table = "bag_files"
    bag_file_cols = ["bag_file_name"]
    bag_file_vals = ["mapping_van_2024-06-24-02-18-35_0"]
    #id1 = db.insert_and_return(bag_file_table, bag_file_cols, bag_file_vals) 

    #print(id1)

    id2 = db.select_from_db(bag_file_table, bag_file_cols, bag_file_vals)
    print (id2)


    #bag_files_id = db.select_from_db("bag_files", "bag_file_name", bag_file_val)

    csv_files = {
        'trigger' : '_slash_parseTrigger.csv'
    }

    '''
    'gps_spark_fun_rear_left_gga' : '_slash_GPS_SparkFun_RearLeft_GGA.csv'
    'gps_spark_fun_rear_left_gga' : '/home/sed5658/Documents/_slash_GPS_SparkFun_RearLeft_GGA.csv',
    'gps_spark_fun_rear_right_gst' : '/home/sed5658/Documents/_slash_GPS_SparkFun_RearRight_GST.csv',
    'gps_spark_fun_front_vtg' : '/home/sed5658/Documents/_slash__GPS_SparkFun_Front_VTG.csv'
    '''

    for table_name, file in csv_files.items():
        write_start_time = time.time()

        # Declare and initialize a few variables
        base_station_messages_id = 0
        is_sensor = 0
        csv_col_lst = []
        sql_col_lst =[]

        # From the table name, determine whether the csv file is for a sensor, and what columns are needed
        is_sensor, csv_col_lst, sql_col_lst = determine_columns(table_name)
        
        # Create the dataframe based off the csv and given column parameters. For the sql columns, add an additional bag_files_id column. Then, write to the database
        # Note: Keeping the df.to_sql rather than just using pd_csv_to_database since there might be issues with the if_exists and index which the former addresses
        #df = db.create_df(table_name, file, is_sensor, csv_col_lst, sql_col_lst, bag_files_id, base_station_messages_id)
        #db.csv_to_db(table_name, df, sql_col_lst)
        #df.to_sql(table_name, db.engine, method = db.csv_to_db(table_name, df, sql_col_lst), if_exists = 'append', index = False)
  
        write_end_time = time.time()
        write_time = write_end_time - write_start_time
        print(f"Time to write {table_name}: {write_time}\n")  

    db.disconnect()

    end_time = time.time()
    total_time = end_time - start_time
    print("Total Time: ", total_time)

if __name__ == "__main__":
    main()

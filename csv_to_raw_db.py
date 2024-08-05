'''
The purpose of this script is to efficiently bulk insert to the Postgres database from a CSV file using copy_expert.

Note: to install polars...
    pip install connectorx
    pip install polars
        OR pip install polars-lts-cpu ()

    (May need to use: python3 -m pip install <package-name> --break-system-packages)

Note: STILL NEEDS MORE TESTING

To-Do:
    - Continue testing with multiple CSV files (of different sensor types)
    - Insert into base_station_messages and bag_files table -> select from -> use those returned variables
'''

import psycopg2
import connectorx as cx
import polars as pl
import pandas as pd
import csv
import time
import traceback
import warnings

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
            self.postgres_url = "postgresql://" + username + ":" + password + "@" + server + ":" + port + "/" + db_name
            self.engine = create_engine(self.postgres_url)

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

    # Create a dataframe in the Pandas or Polars library from the CSV file
    def create_df(self, table_name, file_path, is_sensor, csv_col_lst, sql_col_lst, bag_files_id, base_station_messages_id):
        try:
            # Using pandas to read certain columns from the csv file
            df = pd.read_csv(file_path, sep = "\t", usecols = csv_col_lst)
            df.insert(loc = 0, column = 'bag_file_id', value = bag_files_id) 

            if (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga'):
                df.insert(loc = 1, column = 'base_station_messages_id', value = base_station_messages_id)
            
            # Using polars instead of pandas
            #df = pl.read_csv(file, columns = col_list, separator = "\t")  

            # For sensors, the csv files start with the time columns, but in the db tables, they are last. The following lines will move these lines
            if (is_sensor == 1):
                col_length = df.shape[1]

                col1 = df.pop("rosbagTimestamp")
                df.insert(col_length - 1, "rosbagTimestamp", col1)

                col2 = df.pop("secs")
                df.insert(col_length - 3, "secs", col2)

                col3 = df.pop("nsecs")
                df.insert(col_length - 2, "nsecs", col3)
                
            # Ensure uniformity between the datafram columns and the db table columns
            df.columns = sql_col_lst
            df.columns = df.columns.str.lower()

            #print(list(df.columns.values))

            # For each table, print the first two rows
            print(f"First contents of '{table_name}' CSV file: ")
            print(df.head(2))

            return df

        except:
            print("Error creating dataframe.")

    def pd_csv_to_database(self, table_name, df, sql_col_lst):
        try:

            # Convert the dataframe into a CSV string to work with copy_expert
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index = False, header = False, sep = ',')
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
                       "ros_seconds", "ros_nanoseconds", "ros_timestamp"]

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
                       "gpssecs", "gpsmicrosecs",
                       "latitude", "longitude", "altitude",
                       "geosep", "nav_mode", "num_of_sats",
                       "hdop", "age_of_diff", "lock_status",
                       "ros_seconds", "ros_nanoseconds", "ros_timestamp"]

    # Table: gps_spark_fun_gst (left, right, or front)
    elif (table_name == 'gps_spark_fun_rear_left_gst' or table_name == 'gps_spark_fun_rear_right_gst' or table_name == 'gps_spark_fun_front_gst'):
        is_sensor = 1
        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs",
                       "GPSSecs", "GPSMicroSecs",
                       "StdMajor", "StdMinor", "StdOri",
                       "StdLat", "StdLon", "StdAlt", 
                       
                       ]
        sql_col_lst = ["bag_files_id", "gpssecs", "gpsmicrosecs",
                       "stdmajor", "stdminor", "stdori",
                       "stdlat", "stdlon", "stdalt",
                       "ros_seconds", "ros_nanoseconds", "ros_timestamp"]

    # Table: gps_spark_fun_vtg (left, right, or front)
    elif (table_name == 'gps_spark_fun_rear_left_vtg' or table_name == 'gps_spark_fun_rear_right_vtg' or table_name == 'gps_spark_fun_front_vtg'):
        is_sensor = 1
        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs",
                       "TrueTrack", "MagTrack", 
                       "SpdOverGrndKnots", "SpdOverGrndKmph"
                       ]
        sql_col_lst = ["bag_files_id", "true_track", "mag_track",
                       "spdovergrndknots", "spdovergrndkmph",
                       "ros_seconds", "ros_nanoseconds", "ros_timestamp"]

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
                       "ros_seconds", "ros_nanoseconds", "ros_timestamp"]

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
                       "ros_seconds", "ros_nanoseconds", "ros_timestamp"]

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

    csv_files = {
        'trigger' : '/home/sed5658/Documents/_slash_parseTrigger.csv',
        'gps_spark_fun_rear_left_gga' : '/home/sed5658/Documents/_slash_GPS_SparkFun_RearLeft_GGA.csv',
        'gps_spark_fun_rear_right_gst' : '/home/sed5658/Documents/_slash_GPS_SparkFun_RearRight_GST.csv',
        'gps_spark_fun_front_vtg' : '/home/sed5658/Documents/_slash__GPS_SparkFun_Front_VTG.csv'
    }

    for table_name, file_path in csv_files.items():
        write_start_time = time.time()
        # Declare and initialize a few variables 
        base_station_messages_id = 1 
        bag_files_id = 1
        is_sensor = 0
        csv_col_lst = []
        sql_col_lst =[]

        # From the table name, determine whether the csv file is for a sensor, and what columns are needed
        is_sensor, csv_col_lst, sql_col_lst = determine_columns(table_name)
        
        # Create the dataframe based off the csv and given column parameters. For the sql columns, add an additional bag_files_id column. Then, write to the database
        # Note: Keeping the df.to_sql rather than just using pd_csv_to_database since there might be issues with the if_exists and index which the former addresses
        df = db.create_df(table_name, file_path, is_sensor, csv_col_lst, sql_col_lst, bag_files_id, base_station_messages_id)
        df.to_sql(table_name, db.engine, method = db.pd_csv_to_database(table_name, df, sql_col_lst), if_exists = 'append', index = False)

        # db.pd_csv_to_database(table_name, df, sql_col_lst)
  
        write_end_time = time.time()
        write_time = write_end_time - write_start_time
        print(f"Time to write {table_name}: {write_time}\n")  

    db.disconnect()

    end_time = time.time()
    total_time = end_time - start_time
    print("Total Time: ", total_time)

if __name__ == "__main__":
    main()

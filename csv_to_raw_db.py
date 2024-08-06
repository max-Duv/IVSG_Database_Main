'''
The purpose of this script is to efficiently bulk insert to the Postgres database from a CSV file using copy_expert and the Polars library.

Use with csv_to_sql_columns.py script.

Note: to install polars...
    pip install connectorx
    pip install polars
        OR pip install polars-lts-cpu ()

    (May need to use: python3 -m pip install <package-name> --break-system-packages)

Update:
    - Updated to mainly use Polars to properly edit the dataframe to inlcude new columns and match the layout of the corresponding database table.
    - The script works with at least the trigger CSV file. More testing is needed for the different sensor types, particularly with the GPS SparkFun.     

To-Do:
    1. (IN PROGRESS) Continue testing with multiple CSV files (of different sensor types)
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

from io import StringIO                            # For writting the csv buffer
from csv_to_sql_columns import determine_columns   # Keep records of different column names (for CSV and SQL) here to simplify script



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
            self.postgres_url = "postgresql://" + username + " :" + password + "@" + server + " :" + port + "/" + db_name
            #self.engine = self.postgres_url

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

            insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({vals}) RETURNING id;"
            self.cursor.execute(insert_query, val_lst)

            inserted_id = self.cursor.fetchone()[0]
            return inserted_id

        except psycopg2.Error as e:
            self.printErrors(error = e, message = "Unable to insert to the database.")

    # Simple select function
    def select_from_db(self, table_name, col, val):
        try:
            select_query = f"SELECT id FROM {table_name} WHERE {col} = '{val}';"
            self.cursor.execute(select_query)

            result = self.cursor.fetchone()

            if (result is None):
                col_lst = [col]
                val_lst = [val]
                return_id = self.insert_and_return(table_name, col_lst, val_lst)
            
            else:
                return_id = result[0]
            
            return return_id

        except psycopg2.Error as e:
            self.printErrors(error = e, message = "Unable to select from the database.")

    # Create a dataframe in the Pandas or Polars library from the CSV file. Edit the dataframe to align with the database table.
    def create_df(self, table_name, file, is_sensor, csv_col_dict, sql_col_lst, mapping_dict, bag_files_id):
        try:
            # Using pandas to read certain columns from the csv file
            # df = pd.read_csv(file_path, sep = "\t", usecols = csv_col_lst)

            # Using polars instead of pandas to read from the CSV file and create a dataframe
            csv_col_lst = list(csv_col_dict.keys())
            df = pl.read_csv(file, columns = csv_col_lst, separator = "\t")
            print("Used Polars to read the csv file.")
            
            # All sensors have a column for bag files and rostimes, add and fill those columns here
            if (is_sensor == 1):
                bag_file_column = pl.Series('bag_files_id', [bag_files_id] * df.height, dtype =  pl.Int32)
                df = df.with_columns(bag_file_column)
                print("New column for bag_files added")

                # ros_time = secs + nsecs * 10^-9
                # gpstime = gpssecs + gpsnsecs * 10^-9
                exp = 10**(-9)
                ros_time_column = ((pl.col('secs') + pl.col('nsecs') * exp).cast(pl.Float32).alias('ros_time'))
                df = df.with_columns(ros_time_column)
                print("New column for ros_time added")

                if (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga' or
                    table_name == 'gps_spark_fun_rear_left_gst' or table_name == 'gps_spark_fun_rear_right_gst' or table_name == 'gps_spark_fun_front_gst'):
                    gpstime_column = ((pl.col('GPSSecs') + pl.col('GPSMicroSecs') * exp).cast(pl.Float32).alias('gpstime'))
                    df = df.with_columns(gpstime_column)
                    print("New column for gpstime added")

                # GGA sensor has a column for base station - access the SQL database for this, return the id of the base station
                if (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga'):
                    base_station_id_lst = []
                    
                    last_column = df.columns[-1]
                    last_column_vals = df[pl.col(last_column)].to_pandas()[last_column].tolist()

                    for val in last_column_vals:
                        val_id = self.select_from_db('base_station_messages', 'base_station_name', val)
                        base_station_id_lst.append(val_id)

                    base_station_id_column = pl.Series('base_station_messages_id', base_station_id_lst)
                    df = df.with_columns(base_station_id_column)
                    print("New column for base_station_ids added")

            '''
            # Check How Data Frame Has Changed
            print("Old Columns")
            print(list(old_columns))

            print("Updated Columns")
            print(list(df.columns))
            print(df.head(2))
            '''
            
            # Ensure uniformity between the dataframe columns and the db table columns. Changing the names and reordering to match SQL setup
            if (len(sql_col_lst) != len(df.columns)):
                print("Error, the number of data frame columns is not the same as the number of database table columns.")
            
            else:
                # Ensure datatypes are the same, otherwise you won't be able to insert
                for key, value in csv_col_dict.items():
                    df = df.with_columns([pl.col(key).cast(value)])

                df = df.rename(mapping_dict)
                df = df.rename({col: col.lower() for col in df.columns})

                new_column_order = sql_col_lst
                df = df.select(new_column_order)
                #print(list(df.columns))
                    
                # For each table, print the first two rows
                print(f"First contents of '{table_name}' CSV file: ")
                print(df.head(2))
            
            return df

        except:
            print("Error creating data frame.")

    # This function will write the dataframe into the database using copy_expert
    def csv_to_db(self, table_name, df, sql_col_lst):
        try:
            # Convert the dataframe into a pandas dataframe and then into a CSV string to work with copy_expert
            pandas_df = df.to_pandas()
            csv_buffer = StringIO()
            pandas_df.to_csv(csv_buffer, index=False, header=True, sep=",")
            csv_buffer.seek(0)   # Rewind the buffer to the beginning for reading
            #print(csv_buffer.read())

            # Build the query
            query_fillin = f"{table_name} ({', '.join(sql_col_lst)})"
            query = f"COPY {query_fillin} FROM STDIN WITH CSV HEADER NULL AS 'NULL'"
 
            # Use copy_expert to transport data into the database
            self.cursor.copy_expert(sql = query, file = csv_buffer)
            print("CSV successfully inserted into database.")

        except:
            print("Error inserting CSV into database.")

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
    

    # Get the id of the bag file:
    bag_file_table = "bag_files"
    bag_file_cols = ["bag_file_name"]
    bag_file_vals = ["mapping_van_2024-06-24-02-18-35_0", "mapping_van_2024-06-24-02-33-05_0"]
    
    # new_bag_bile_id = db.insert_and_return(bag_file_table, bag_file_cols, bag_file_vals) 
    bag_files_id = db.select_from_db(bag_file_table, bag_file_cols[0], bag_file_vals[0])

    csv_files = {
        'trigger' : '/home/sed5658/Documents/_slash_parseTrigger.csv'
    }

    for table_name, file in csv_files.items():
        write_start_time = time.time()

        # Declare and initialize a few variables
        is_sensor = 0
        csv_col_dict = {}
        sql_col_lst = []
        mapping_dict = {}

        # From the table name, determine whether the csv file is for a sensor, and what columns are needed
        is_sensor, csv_col_dict, sql_col_lst, mapping_dict = determine_columns(table_name)

        '''
        # Check returned values from determine_columns function
        print(f"\n bag_files_id: {bag_files_id}")
        print(f"\n is_sensor: {is_sensor}")
        print(f"\n csv_col_lst: {csv_col_dict}")
        print(f"\n sql_col_lst: {sql_col_lst}")
        '''   
        
        # Create the dataframe based off the csv and given column parameters. For the sql columns, add an additional bag_files_id column. Then, write to the database
        df = db.create_df(table_name, file, is_sensor, csv_col_dict, sql_col_lst, mapping_dict, bag_files_id)
        db.csv_to_db(table_name, df, sql_col_lst)

        '''
        # Check created dataframe attributes:
        print("Shape of DataFrame:", df.shape)
        print("Column names:", df.columns)

        for column in df.columns:
            dtype = df[column].dtype
            print(f"Column '{column}' has type: {dtype}")
        '''

        write_end_time = time.time()
        write_time = write_end_time - write_start_time
        print(f"Time to write {table_name}: {write_time}\n")  

    db.disconnect()

    end_time = time.time()
    total_time = end_time - start_time
    print("Total Time: ", total_time)

if __name__ == "__main__" :
    main()

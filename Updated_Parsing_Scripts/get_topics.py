'''
Python 3.10.1 and Python 3.12.3

Written by Sadie Duncan at IVSG during 2024 Aug.
Supervised by Professor Sean Brennan

Purpose:
    This script keeps track of the differences between the ROS bag topics and its data types and the SQL database table columns
    and their data types. Currently, only contains information for the encoder, GPS SparkFun sensors, the 3D LiDAR sensors, and trigger.

Usage:
    Use with the parse_and_insert.py script. In the future, as this is only one function, it would be easy to integrate this into the
    parseUtilities.py script to simplify the number of scripts.

Method(s): get_topics(topic)
    Takes in a topic and will return the corresponding table (table_name), a mapping dictionary of the wanted ROS bag topics to the
    corresponding table column names and data types, and a list of the columns for the database table.

For adding in a future table:
    1. Update SQL script
        a. New CREATE TABLE
        b. New ADD FOREIGN KEY
    2. From the updated SQL script, set table_name to be the name of the newly added table
    3. Create a dictionary (mapping_dict)
        a. Keys are the topics you want from the ROS bag / the older CSV files
        b. Values are a list of the corresponding name in the database table and proper datatype. To ensure data can be written to
           the database, we will cast each value to be the same type as is in the database.
        c. Postgres - Polars Transformations:
                char/varchar/text = pl.Utf8
                int = pl.Int32
                bigint = pl.Int64
                real = pl.Float32
                float = pl.Float64
    4. Make a list of the columns in the database table that need 

Note: This script is applicable only for CSV files that were only written using the bag_to_csv_py3.py script, as the CSV columns match with
      with the ROS bag subtopics. If you were to use the parse_and_insert.py script to write a CSV file from a bag file, the columns would
      be altered before being written to the CSV file, thus the mapping dictionary would actually be incorrect. Changes to the parse_and_insert.py
      script should be made later to address this.

To-Do:
    1. Alter parse_and_insert.py script:
        a. Function for if the CSV file was written by the bag_to_csv_py3.py script
        b. Function for if the CSV file was written by the parse_and_insert.py script - likely no need to make any changes to columns
'''
import polars as pl

def get_topics(topic):
    table_name = ""
    mapping_dict = {}
    db_col_lst = []

    # Table: encoder
    if (topic == '/parseEncoder'):
        table_name = 'encoder'

        mapping_dict = {'rosbagTimestamp': ['ros_record_time', pl.Float32],
                        'secs': ['ros_seconds', pl.Int64],
                        'nsecs': ['ros_nanoseconds', pl.Int64],
                        'mode': ['encoder_mode', pl.Utf8],
                        'C1': ['c1', pl.Int64],
                        'C2': ['c2', pl.Int64],
                        'C3': ['c3', pl.Int64],
                        'C4': ['c4', pl.Int64],
                        'P1': ['p1', pl.Int64],
                        'E1': ['e1', pl.Int64],
                        'err_wrong_element_length': ['err_wrong_element_length', pl.Int32],
                        'err_bad_element_structure': ['err_bad_element_structure', pl.Int32],
                        'err_failed_time': ['err_failed_time', pl.Int32],
                        'err_bad_uppercase_character': ['err_bad_uppercase_character', pl.Int32],
                        'err_bad_lowercase_character': ['err_bad_lowercase_character', pl.Int32],
                        'err_bad_character': ['err_bad_character', pl.Int32]
        }
        
        db_col_lst = ["bag_files_id", "encoder_mode",
                      "c1", "c2", "c3", "c4", "p1", "e1",
                      "err_wrong_element_length", "err_bad_element_structure",
                      "err_failed_time", "err_bad_uppercase_character",
                      "err_bad_lowercase_character", "err_bad_character",
                      "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
        ]
        
    # Table: gps_spark_fun_gga (left, right, or front)
    elif (topic == '/GPS_SparkFun_RearLeft_GGA' or topic == '/GPS_SparkFun_RearRight_GGA' or topic == '/GPS_SparkFun_Front_GGA'):
        if (topic == '/GPS_SparkFun_RearLeft_GGA'):
            table_name = 'gps_spark_fun_rear_left_gga'
        elif (topic == '/GPS_SparkFun_RearRight_GGA'):
            table_name = 'gps_spark_fun_rear_right_gga'
        elif (topic == '/GPS_SparkFun_Front_GGA'):
            table_name = 'gps_spark_fun_front_gga'

        mapping_dict = {'rosbagTimestamp': ['ros_record_time', pl.Float32],
                        'secs': ['ros_seconds', pl.Int64],
                        'nsecs': ['ros_nanoseconds', pl.Int64],
                        'GPSSecs': ['gpssecs', pl.Float32],
                        'GPSMicroSecs': ['gpsmicrosecs', pl.Float32],
                        'Latitude': ['latitude', pl.Float32],
                        'Longitude': ['longitude', pl.Float32],
                        'Altitude': ['altitude', pl.Float32],
                        'GeoSep': ['geosep', pl.Float32],
                        'NavMode': ['nav_mode', pl.Int32],
                        'NumOfSats': ['num_of_sats', pl.Int32],
                        'HDOP': ['hdop', pl.Float64],
                        'AgeOfDiff': ['age_of_diff', pl.Float64],
                        'LockStatus': ['lock_status', pl.Int32],
                        'BaseStationID': ['base_station_messages_id', pl.Utf8]
        }
        
        db_col_lst = ["bag_files_id", "base_station_messages_id",
                      "gpssecs", "gpsmicrosecs", "gpstime",
                      "latitude", "longitude", "altitude",
                      "geosep", "nav_mode", "num_of_sats",
                      "hdop", "age_of_diff", "lock_status",
                      "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
        ]
        
    # Table: gps_spark_fun_gst (left, right, or front)
    elif (topic == '/GPS_SparkFun_RearLeft_GST' or topic == '/GPS_SparkFun_RearRight_GST' or topic == '/GPS_SparkFun_Front_GST'):
        if (topic == '/GPS_SparkFun_RearLeft_GST'):
            table_name = 'gps_spark_fun_rear_left_gst'
        elif (topic == '/GPS_SparkFun_RearRight_GST'):
            table_name = 'gps_spark_fun_rear_right_gst'
        elif (topic == '/GPS_SparkFun_Front_GST'):
            table_name = 'gps_spark_fun_front_gst'

        mapping_dict = {'rosbagTimestamp': ['ros_record_time', pl.Float32],
                        'secs': ['ros_seconds', pl.Int64],
                        'nsecs': ['ros_nanoseconds', pl.Int64],
                        'GPSSecs': ['gpssecs', pl.Float32],
                        'GPSMicroSecs': ['gpsmicrosecs', pl.Float32],
                        'StdMajor': ['stdmajor', pl.Float64],
                        'StdMinor': ['stdminor', pl.Float64],
                        'StdOri': ['stdori', pl.Float64],
                        'StdLat': ['stdlat', pl.Float64],
                        'StdLon': ['stdlon', pl.Float64],
                        'StdAlt': ['stdalt', pl.Float64]
        }

        db_col_lst = ["bag_files_id", "gpssecs", "gpsmicrosecs", "gpstime",
                      "stdmajor", "stdminor", "stdori",
                      "stdlat", "stdlon", "stdalt",
                      "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
        ]

    # Table: gps_spark_fun_vtg (left, right, or front)
    elif (topic == '/GPS_SparkFun_RearLeft_VTG' or topic == '/GPS_SparkFun_RearRight_VTG' or topic == '/GPS_SparkFun_Front_VTG'):
        if (topic == '/GPS_SparkFun_RearLeft_VTG'):
            table_name = 'gps_spark_fun_rear_left_vtg'
        elif (topic == '/GPS_SparkFun_RearRight_VTG'):
            table_name = 'gps_spark_fun_rear_right_vtg'
        elif (topic == '/GPS_SparkFun_Front_VTG'):
            table_name = 'gps_spark_fun_front_vtg'

        mapping_dict = {'rosbagTimestamp': ['ros_record_time', pl.Float32],
                        'secs': ['ros_seconds', pl.Int64],
                        'nsecs': ['ros_nanoseconds', pl.Int64],
                        'TrueTrack': ['true_track', pl.Float32],
                        'MagTrack': ['mag_track', pl.Float32],
                        'SpdOverGrndKnots': ['spdovergrndknots', pl.Float32],
                        'SpdOverGrndKmph': ['spdovergrndkmph', pl.Float32]
        }

        db_col_lst = ["bag_files_id", "true_track", "mag_track",
                      "spdovergrndknots", "spdovergrndkmph",
                      "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
        ]

    # Table: sick_lms_5xx
    elif (topic == '/sick_lms_5xx/scan'):
        table_name = 'sick_lms_5xx'

        mapping_dict = {'rosbagTimestamp': ['ros_record_time', pl.Float32],
                        'secs': ['ros_seconds', pl.Int64],
                        'nsecs': ['ros_nanoseconds', pl.Int64],
                        'angle_min' : ['angle_min', pl.Float32],
                        'angle_max' : ['angle_max', pl.Float32],
                        'angle_increment' : ['angle_increment', pl.Float32],
                        'time_increment' : ['time_increment', pl.Float32],
                        'scan_time' : ['scan_time', pl.Float32],
                        'range_min' : ['range_min', pl.Float32],
                        'range_max' : ['range_max', pl.Float32],
                        'ranges' : ['ranges', pl.Utf8],
                        'intensities' : ['intensities', pl.Utf8]
        }

        db_col_lst = ["bag_files_id", "scan_time", "time_increment",
                      "angle_min", "angle_max", "angle_increment",
                      "range_min", "range_max", "ranges", "intensities", 
                      "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
        ]
        
    # Table: velodyne_lidar and ouster_lidar
    elif (topic == '/velodyne_packets' or topic == '/ouster_packets'):
        if (topic == '/velodyne_packets'):
            table_name = 'velodyne_lidar'
        elif (topic == '/ouster_packets'):
            table_name = 'ouster_lidar'
        
        mapping_dict = {'rosbagTimestamp': ['ros_record_time', pl.Float32],
                        'secs': ['ros_seconds', pl.Int64],
                        'nsecs': ['ros_nanoseconds', pl.Int64],
                        'packets': ['packets', pl.Utf8]
        }
        
        db_col_lst = ["bag_files_id", 
                      "ouster_lidar_hash_tag", "ouster_lidar_location",
                      "ouster_lidar_file_size", "ouster_lidar_file_time",
                      "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
        ]
        
    # Table: trigger
    elif (topic == '/parseTrigger'):
        table_name = 'trigger'

        mapping_dict = {'rosbagTimestamp': ['ros_record_time', pl.Float32],
                        'secs': ['ros_seconds', pl.Int64],
                        'nsecs': ['ros_nanoseconds', pl.Int64],
                        'mode': ['trigger_mode', pl.Utf8],
                        'mode_counts': ['trigger_mode_counts', pl.Int32],
                        'adjone': ['adjone', pl.Int32],
                        'adjtwo': ['adjtwo', pl.Int32],
                        'adjthree': ['adjthree', pl.Int32],
                        'err_failed_mode_count': ['err_failed_mode_count', pl.Int32],
                        'err_failed_XI_format': ['err_failed_xi_format', pl.Int32],
                        'err_failed_checkInformation': ['err_failed_check_information', pl.Int32],
                        'err_trigger_unknown_error_occured': ['err_trigger_unknown_error_occured', pl.Int32],
                        'err_bad_uppercase_character': ['err_bad_uppercase_character', pl.Int32],
                        'err_bad_lowercase_character': ['err_bad_lowercase_character', pl.Int32],
                        'err_bad_three_adj_element': ['err_bad_three_adj_element', pl.Int32],
                        'err_bad_first_element': ['err_bad_first_element', pl.Int32],
                        'err_bad_character': ['err_bad_character', pl.Int32],
                        'err_wrong_element_length': ['err_wrong_element_length', pl.Int32]
        }

        db_col_lst = ["bag_files_id", "trigger_mode", "trigger_mode_counts",
                      "adjone", "adjtwo", "adjthree",
                      "err_failed_mode_count", "err_failed_xi_format", "err_failed_check_information",
                      "err_trigger_unknown_error_occured", "err_bad_uppercase_character",
                      "err_bad_lowercase_character", "err_bad_three_adj_element",
                      "err_bad_first_element", "err_bad_character", "err_wrong_element_length",
                      "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
        ]
        
        '''
        # Simple Debugging:
        print(f"table_name: {table_name}")
        print(f"mapping_dict: {mapping_dict}")
        print(f"df_col_dict: {df_col_dict}")
        print(f"db_col_lst: {db_col_lst}")
        '''

    return table_name, mapping_dict, db_col_lst

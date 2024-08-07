'''
This function will take a table name and return whether or not the table involves a sensor,
the columns to take from the CSV file and the columns to insert for the Postgres database.
Currently only for the encoder, GPS SparkFun and 3D LiDAR tables. Columns may be changed as needed.

For polars - postgres data types:
    char/varchar/text = pl.Utf8
    smallint = pl.Int16
    int = pl.Int32
    bigint = pl.Int64
    real = pl.Float32
    float = pl.Float64
'''
import polars as pl

def determine_columns(table_name):
    mapping_dict = {"rosbagTimestamp" : "ros_record_time",
                    "secs" : "ros_seconds", 
                    "nsecs" : "ros_nanoseconds"
                    }
    
    csv_col_dict = {"rosbagTimestamp" : pl.Float32,
                    "secs" : pl.Int64,
                    "nsecs" : pl.Int64
                    }

    # Table: base_station_messages
    if (table_name == 'base_station_messages'):
        is_sensor = 0

        csv_col_lst = ["base_station_name", "base_station_message"]

        csv_col_dict = {"base_station_name" : pl.Utf8,
                        "base_station_message" : pl.Utf8}

        sql_col_lst = ["base_station_name", "base_station_message"]

        mapping_dict = {"base_station_name" : "base_station_name",
                        "base_station_message" : "base_station_message"}

    # Table: bag_files
    elif (table_name == 'bag_files'):
        is_sensor = 0

        csv_col_lst = ["bag_files_id"]

        csv_col_dict = {"bag_files_id" : pl.Int32}

        sql_col_lst = ["bag_files_id"]

        mapping_dict = {"bag_files_id" : "bag_files_id"}


    # Table: encoder
    elif (table_name == 'encoder'):
        is_sensor = 1

        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs", "mode",
                       "C1", "C2", "C3", "C4", "P1", "E1",
                       "err_wrong_element_length", "err_bad_element_structure",
                       "err_failed_time", "err_bad_uppercase_character",
                       "err_bad_lowercase_character", "err_bad_character"]
        
        csv_col_dict.update({"mode" : pl.Utf8,
                             "C1" : pl.Int64,
                             "C2" : pl.Int64,
                             "C3" : pl.Int64,
                             "C4" : pl.Int64,
                             "P1" : pl.Int64,
                             "E1" : pl.Int64,
                             "err_wrong_element_length" : pl.Int32,
                             "err_bad_element_structure" : pl.Int32,
                             "err_failed_time" : pl.Int32,
                             "err_bad_uppercase_character" : pl.Int32,
                             "err_bad_lowercase_character" : pl.Int32,
                             "err_bad_character" : pl.Int32
                             })
        
        sql_col_lst = ["bag_files_id", "encoder_mode", "time",
                       "c1", "c2", "c3", "c4", "p1", "e1",
                       "err_wrong_element_length", "err_bad_element_structure",
                       "err_failed_time", "err_bad_uppercase_character",
                       "err_bad_lowercase_character", "err_bad_character",
                       "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"]
        
        mapping_dict.update({"mode" : "encoder_mode"})


    # Table: gps_spark_fun_gga (left, right, or front)
    elif (table_name == 'gps_spark_fun_rear_left_gga' or table_name == 'gps_spark_fun_rear_right_gga' or table_name == 'gps_spark_fun_front_gga'):
        is_sensor = 1

        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs",
                       "GPSSecs", "GPSMicroSecs",
                       "Latitude", "Longitude", "Altitude",
                       "GeoSep", "NavMode", "NumOfSats",
                       "HDOP", "AgeOfDiff", "LockStatus"
                       ]
        
        csv_col_dict.update({"GPSSecs" : pl.Float32,
                             "GPSMicroSecs" : pl.Float32,
                             "Latitude" : pl.Float32,
                             "Longitude" : pl.Float32,
                             "Altitude" : pl.Float32,
                             "GeoSep" : pl.Float32,
                             "NavMode" : pl.Int16,
                             "NumOfSats" : pl.Int32,
                             "HDOP" : pl.Float64,
                             "AgeOfDiff" : pl.Float64,
                             "LockStatus" : pl.Int32
                             })
        
        sql_col_lst = ["bag_files_id", "base_station_messages_id",
                       "gpssecs", "gpsmicrosecs", "gpstime"
                       "latitude", "longitude", "altitude",
                       "geosep", "nav_mode", "num_of_sats",
                       "hdop", "age_of_diff", "lock_status",
                       "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
                       ]
        
        mapping_dict.update({"NavMode" : "nav_mode",
                             "NumOfSats" : "num_of_sats",
                             "AgeOfDiff" : "age_of_diff",
                             "LockStatus" : "lock_status"
                             })

    # Table: gps_spark_fun_gst (left, right, or front)
    elif (table_name == 'gps_spark_fun_rear_left_gst' or table_name == 'gps_spark_fun_rear_right_gst' or table_name == 'gps_spark_fun_front_gst'):
        is_sensor = 1

        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs",
                       "GPSSecs", "GPSMicroSecs",
                       "StdMajor", "StdMinor", "StdOri",
                       "StdLat", "StdLon", "StdAlt"
                       ]
        
        csv_col_dict.update({"GPSSecs" : pl.Float32,
                             "GPSMicroSecs" : pl.Float32,
                             "StdMajor" : pl.Float64,
                             "StdMinor" : pl.Float64,
                             "StdOri" : pl.Float64,
                             "StdLat" : pl.Float64,
                             "StdLon" : pl.Float64,
                             "StdAlt" : pl.Float64
                             })
        
        sql_col_lst = ["bag_files_id", "gpssecs", "gpsmicrosecs", "gpstime",
                       "stdmajor", "stdminor", "stdori",
                       "stdlat", "stdlon", "stdalt",
                       "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
                       ]

    # Table: gps_spark_fun_vtg (left, right, or front)
    elif (table_name == 'gps_spark_fun_rear_left_vtg' or table_name == 'gps_spark_fun_rear_right_vtg' or table_name == 'gps_spark_fun_front_vtg'):
        is_sensor = 1

        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs",
                       "TrueTrack", "MagTrack", 
                       "SpdOverGrndKnots", "SpdOverGrndKmph"
                       ]
        
        csv_col_dict.update({"TrueTrack" : pl.Float32,
                             "MagTrack" : pl.Float32,
                             "SpdOverGrndKnots" : pl.Float32,
                             "SpdOverGrndKmph" : pl.Float32
                             })
        
        sql_col_lst = ["bag_files_id", "true_track", "mag_track",
                       "spdovergrndknots", "spdovergrndkmph",
                       "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
                       ]
        
        mapping_dict.update({"TrueTrack" : "true_track",
                             "MagTrack" : "mag_track"})

    # Table: velodyne_lidar and ouster_lidar
    elif (table_name == 'velodyne_lidar' or table_name == "ouster_lidar" ):
        is_sensor = 1

        csv_col_lst = ["bag_files_id", 
                       "ouster_lidar_hash_tag", "ouster_lidar_location",
                       "ouster_lidar_file_size", "ouster_lidar_file_time",
                       "ros_seconds", "ros_nanoseconds", "ros_record_time"
                       ]
        
        csv_col_dict = {"bag_files_id" : pl.Int32,
                        "ouster_lidar_hash_tag" : pl.Int32,
                        "ouster_lidar_location" : pl.Utf8,
                        "ouster_lidar_file_size" : pl.Int64,
                        "ouster_lidar_file_time" : pl.Float32,
                        "ros_seconds" : pl.Int64,
                        "ros_nanoseconds" : pl.Int64,
                        "ros_record_time" : pl.Float32
                        }
        
        sql_col_lst = ["bag_files_id", 
                       "ouster_lidar_hash_tag", "ouster_lidar_location",
                       "ouster_lidar_file_size", "ouster_lidar_file_time",
                       "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
                       ]
        
        mapping_dict = {"bag_files_id" : "bag_files_id",
                        "ouster_lidar_hash_tag" : "ouster_lidar_hash_tag",
                        "ouster_lidar_location" : "ouster_lidar_location",
                        "ouster_lidar_file_size" : "ouster_lidar_file_size",
                        "ouster_lidar_file_time" : "ouster_lidar_file_time",
                        "ros_seconds" : "ros_seconds",
                        "ros_nanoseconds" : "ros_nanoseconds",
                        "ros_record_time" : "ros_record_time"
                        }

    # Table: trigger
    elif (table_name == 'trigger'):
        is_sensor = 1

        csv_col_lst = ["rosbagTimestamp", "secs", "nsecs",
                       "mode", "mode_counts",
                       "adjone", "adjtwo", "adjthree",
                       "err_failed_mode_count", "err_failed_XI_format", "err_failed_checkInformation",
                       "err_trigger_unknown_error_occured", "err_bad_uppercase_character",
                       "err_bad_lowercase_character", "err_bad_three_adj_element",
                       "err_bad_first_element", "err_bad_character", "err_wrong_element_length"
                       ]
        
        csv_col_dict.update({"mode": pl.Utf8,
                             "mode_counts": pl.Int32,
                             "adjone" : pl.Int32,
                             "adjtwo" : pl.Int32,
                             "adjthree" : pl.Int32,
                             "err_failed_mode_count": pl.Int32,
                             "err_failed_XI_format" : pl.Int32,
                             "err_failed_checkInformation" : pl.Int32,
                             "err_trigger_unknown_error_occured" : pl.Int32,
                             "err_bad_uppercase_character" : pl.Int32,
                             "err_bad_lowercase_character" : pl.Int32,
                             "err_bad_three_adj_element" : pl.Int32,
                             "err_bad_first_element" : pl.Int32,
                             "err_bad_character" : pl.Int32,
                             "err_wrong_element_length" : pl.Int32
                             })
        
        sql_col_lst = ["bag_files_id", "trigger_mode", "trigger_mode_counts",
                       "adjone", "adjtwo", "adjthree",
                       "err_failed_mode_count", "err_failed_xi_format", "err_failed_check_information",
                       "err_trigger_unknown_error_occured", "err_bad_uppercase_character",
                       "err_bad_lowercase_character", "err_bad_three_adj_element",
                       "err_bad_first_element", "err_bad_character", "err_wrong_element_length",
                       "ros_seconds", "ros_nanoseconds", "ros_publish_time", "ros_record_time"
                       ]
        
        mapping_dict.update({"mode" : "trigger_mode", 
                             "mode_counts" : "trigger_mode_counts",
                             "err_failed_checkInformation" : "err_failed_check_information"
                             })

    return is_sensor, csv_col_dict, sql_col_lst, mapping_dict

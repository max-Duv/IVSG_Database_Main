/*
The SQL script create the beginning of the raw data database. To simplify things, start by setting up the most important
tables (encoder, GPS SparkFun sensors, 3D LiDAR (velodyne_lidar, ouster_lidar), and trigger). Other tables will be added later.

Note: Still considering whether or not to expand the GPS SparkFun tables back to 9 tables or keep them at 3.

Note: At this point, the only point of the base_station_messages table is to hold the different base station names (LTI, Test Track, Reber1, and Reber2)
*/

/*
DROP TABLE IF EXISTS base_station_messages;
DROP TABLE IF EXISTS bag_files;
DROP TABLE IF EXISTS encoder;
DROP TABLE IF EXISTS gps_spark_fun_rear_left_gga;
DROP TABLE IF EXISTS gps_spark_fun_rear_right_gga;
DROP TABLE IF EXISTS gps_spark_fun_front_gga;
DROP TABLE IF EXISTS gps_spark_fun_rear_left_gst;
DROP TABLE IF EXISTS gps_spark_fun_rear_right_gst;
DROP TABLE IF EXISTS gps_spark_fun_front_gst;
DROP TABLE IF EXISTS gps_spark_fun_rear_left_vtg;
DROP TABLE IF EXISTS gps_spark_fun_rear_right_vtg;
DROP TABLE IF EXISTS gps_spark_fun_front_vtg;
DROP TABLE IF EXISTS velodyne_lidar;
DROP TABLE IF EXISTS ouster_lidar;
DROP TABLE IF EXISTS trigger;
*/

CREATE EXTENSION postgis;
-- CREATE EXTENSION pointcloud;
-- CREATE EXTENSION pointcloud_postgis;

-- tables
-- Table: base_station_messages 
CREATE TABLE IF NOT EXISTS base_station_messages (
    id serial NOT NULL,
    base_station_name varchar(50) NOT NULL,
    base_station_message text NULL,
    base_station_message_timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT base_station_messages_pk PRIMARY KEY (id),
    CONSTRAINT base_station_name_unique UNIQUE (base_station_name)
);

-- Table: bag_files
CREATE TABLE IF NOT EXISTS bag_files (
    id serial NOT NULL,
    bag_file_name varchar(50) NOT NULL,
    CONSTRAINT bag_file_pk PRIMARY KEY (id),
    CONSTRAINT bag_file_unique UNIQUE (bag_file_name)
);

----------------------------------------------------------------------
-- Sensor Type: Encoder
----------------------------------------------------------------------
-- Table: encoder
CREATE TABLE IF NOT EXISTS encoder (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    encoder_mode varchar(50)NOT NULL,
    encoder_time real NOT NULL,
    c1 bigint NOT NULL,
    c2 bigint NOT NULL,
    c3 bigint NOT NULL,
    c4 bigint NOT NULL,
    p1 bigint NOT NULL,
    e1 bigint NOT NULL,
    err_wrong_element_length int NOT NULL,
    err_bad_element_structure int NOT NULL,
    err_failed_time int NOT NULL,
    err_bad_uppercase_character int NOT NULL,
    err_bad_lowercase_character int NOT NULL,
    err_bad_character int NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT encoder_pk PRIMARY KEY (id)
);

----------------------------------------------------------------------
-- Sensor Type: GPS
----------------------------------------------------------------------
-- Table: gps_spark_fun_rear_left_gga
CREATE TABLE IF NOT EXISTS gps_spark_fun_rear_left_gga (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    base_station_messages_id int NOT NULL,
    gpssecs real NOT NULL,
    gpsmicrosecs real NOT NULL,
    gpstime real NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    geosep real NOT NULL,
    nav_mode smallint NOT NULL,
    num_of_sats int NOT NULL,
    hdop float NOT NULL,
    age_of_diff float NOT NULL,
    lock_status int NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT gps_spark_fun_rear_left_gga_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_rear_right_gga
CREATE TABLE IF NOT EXISTS gps_spark_fun_rear_right_gga (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    base_station_messages_id int NOT NULL,
    gpssecs real NOT NULL,
    gpsmicrosecs real NOT NULL,
    gpstime real NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    geosep real NOT NULL,
    nav_mode smallint NOT NULL,
    num_of_sats int NOT NULL,
    hdop float NOT NULL,
    age_of_diff float NOT NULL,
    lock_status int NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT gps_spark_fun_rear_right_gga_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_front_gga
CREATE TABLE IF NOT EXISTS gps_spark_fun_front_gga (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    base_station_messages_id int NOT NULL,
    gpssecs real NOT NULL,
    gpsmicrosecs real NOT NULL,
    gpstime real NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    geosep real NOT NULL,
    nav_mode smallint NOT NULL,
    num_of_sats int NOT NULL,
    hdop float NOT NULL,
    age_of_diff float NOT NULL,
    lock_status int NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT gps_spark_fun_front_gga_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_rear_left_gst
CREATE TABLE IF NOT EXISTS gps_spark_fun_rear_left_gst (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    gpssecs real NOT NULL,
    gpsmicrosecs real NOT NULL,
    gpstime real NOT NULL,
    stdmajor float NOT NULL,
    stdminor float NOT NULL,
    stdori float NOT NULL,
    stdlat float NOT NULL,
    stdlon float NOT NULL,
    stdalt float NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT gps_spark_fun_rear_left_gst_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_rear_right_gst
CREATE TABLE IF NOT EXISTS gps_spark_fun_rear_right_gst (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    gpssecs real NOT NULL,
    gpsmicrosecs real NOT NULL,
    gpstime real NOT NULL,
    stdmajor float NOT NULL,
    stdminor float NOT NULL,
    stdori float NOT NULL,
    stdlat float NOT NULL,
    stdlon float NOT NULL,
    stdalt float NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT gps_spark_fun_rear_right_gst_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_front_gst
CREATE TABLE IF NOT EXISTS gps_spark_fun_front_gst (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    gpssecs real NOT NULL,
    gpsmicrosecs real NOT NULL,
    gpstime real NOT NULL,
    stdmajor float NOT NULL,
    stdminor float NOT NULL,
    stdori float NOT NULL,
    stdlat float NOT NULL,
    stdlon float NOT NULL,
    stdalt float NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT gps_spark_fun_front_gst_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_rear_left_vtg
CREATE TABLE IF NOT EXISTS gps_spark_fun_rear_left_vtg (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    true_track real NOT NULL,
    mag_track real NOT NULL,
    spdovergrndknots real NOT NULL,
    spdovergrndkmph real NOT NULL,
    ros_seconds bigint NULL,
    ros_nanoseconds bigint NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT gps_spark_fun_rear_left_vtg_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_rear_right_vtg
CREATE TABLE IF NOT EXISTS gps_spark_fun_rear_right_vtg (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    true_track real NOT NULL,
    mag_track real NOT NULL,
    spdovergrndknots real NOT NULL,
    spdovergrndkmph real NOT NULL,
    ros_seconds bigint NULL,
    ros_nanoseconds bigint NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT gps_spark_fun_rear_right_vtg_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_front_vtg
CREATE TABLE IF NOT EXISTS gps_spark_fun_front_vtg (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    true_track real NOT NULL,
    mag_track real NOT NULL,
    spdovergrndknots real NOT NULL,
    spdovergrndkmph real NOT NULL,
    ros_seconds bigint NULL,
    ros_nanoseconds bigint NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT gps_spark_fun_front_vtg_pk PRIMARY KEY (id)
);

----------------------------------------------------------------------
-- Sensor Type: LiDAR
----------------------------------------------------------------------
-- Table: velodyne_lidar (option 1)
CREATE TABLE IF NOT EXISTS velodyne_lidar (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    velodyne_lidar_hash_tag int NOT NULL,
    velodyne_lidar_location varchar (10) NOT NULL,
    velodyne_lidar_file_size bigint NOT NULL,
    velodyne_lidar_file_time real NOT NULL, -- Might not need
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT velodyne_lidar_pk PRIMARY KEY (id),
    CONSTRAINT velodyne_lidar_hash_tag_unique UNIQUE (velodyne_lidar_hash_tag)
);

/*
-- Table: velodyne_lidar (option 2)
CREATE TABLE IF NOT EXISTS velodyne_lidar (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    velodyne_lidar_sequence int NOT NULL,
    velodyne_lidar_file_name varchar (32) NOT NULL,
    velodyne_lidar_size bigint NOT NULL,
    velodyne_lidar_location varchar (10) NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    roll real NOT NULL,
    pitch real NOT NULL,
    yaw real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT velodyne_lidar_pk PRIMARY KEY (id),
    CONSTRAINT velodyne_lidar_file_name_unique UNIQUE (velodyne_lidar_file_name)
);
*/

-- Table: ouster_lidar (option 1)
CREATE TABLE IF NOT EXISTS ouster_lidar (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    ouster_lidar_hash_tag int NOT NULL,
    ouster_lidar_location varchar (10) NOT NULL,
    ouster_lidar_file_size bigint NOT NULL,
    ouster_lidar_file_time real NOT NULL, -- Might not need
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT ouster_lidar_pk PRIMARY KEY (id),
    CONSTRAINT ouster_lidar_hash_tag_unique UNIQUE (ouster_lidar_hash_tag)
);

/*
-- Table: ouster_lidar (option 2)
CREATE TABLE IF NOT EXISTS ouster_lidar (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    ouster_lidar_sequence int NOT NULL,
    ouster_lidar_file_name varchar (32) NOT NULL,
    ouster_lidar_size bigint NOT NULL,
    ouster_lidar_location varchar (10) NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    roll real NOT NULL,
    pitch real NOT NULL,
    yaw real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT ouster_lidar_pk PRIMARY KEY (id),
    CONSTRAINT ouster_lidar_file_name_unique UNIQUE (ouster_lidar_file_name)
);
*/

----------------------------------------------------------------------
-- Sensor Type: Trigger
----------------------------------------------------------------------
-- Table: trigger
CREATE TABLE IF NOT EXISTS trigger (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    trigger_mode varchar(50) NOT NULL,
    trigger_mode_counts int NOT NULL,
    adjone int NOT NULL,
    adjtwo int NOT NULL,
    adjthree int NOT NULL,
    err_failed_mode_count int NOT NULL,
    err_failed_xi_format int NOT NULL,
    err_failed_check_information int NOT NULL,
    err_trigger_unknown_error_occured int NOT NULL,
    err_bad_uppercase_character int NOT NULL,
    err_bad_lowercase_character int NOT NULL,
    err_bad_three_adj_element int NOT NULL,
    err_bad_first_element int NOT NULL,
    err_bad_character int NOT NULL,
    err_wrong_element_length int NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_publish_time real NOT NULL,
    ros_record_time real NOT NULL,
    CONSTRAINT trigger_pk PRIMARY KEY (id)
);

-- foreign keys
/*
FORMAT:
-- Reference: table_to_change_table_to_connect (table: table_to_change)
ALTER TABLE table_to_change ADD
    FOREIGN KEY (column_in_table_to_change)
    REFERENCES table_to_connect (column_in_table_to_connect)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;
*/

----------------------------------------------------------------------
-- Base Stations
----------------------------------------------------------------------
-- Reference: gps_spark_fun_rear_left_gga_base_station_messages (table: gps_spark_fun_rear_left_gga)
ALTER TABLE gps_spark_fun_rear_left_gga ADD
    FOREIGN KEY (base_station_messages_id)
    REFERENCES base_station_messages (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_rear_right_gga_base_station_messages (table: gps_spark_fun_rear_right_gga)
ALTER TABLE gps_spark_fun_rear_right_gga ADD
    FOREIGN KEY (base_station_messages_id)
    REFERENCES base_station_messages (id)
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_front_gga_base_station_messages (table: gps_spark_fun_front_gga)
ALTER TABLE gps_spark_fun_front_gga ADD
    FOREIGN KEY (base_station_messages_id)
    REFERENCES base_station_messages (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

----------------------------------------------------------------------
-- Bag Files
----------------------------------------------------------------------
-- Reference: encoder_bag_files (table: encoder)
ALTER TABLE encoder ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_rear_left_gga_bag_files (table: gps_spark_fun_rear_left_gga)
ALTER TABLE gps_spark_fun_rear_left_gga ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_rear_right_gga_bag_files (table: gps_spark_fun_rear_right_gga)
ALTER TABLE gps_spark_fun_rear_right_gga ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_front_gga_bag_files (table: gps_spark_fun_front_gga)
ALTER TABLE gps_spark_fun_front_gga ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_rear_left_gst_bag_files (table: gps_spark_fun_rear_left_gst)
ALTER TABLE gps_spark_fun_rear_left_gst ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_rear_right_gst_bag_files (table: gps_spark_fun_rear_right_gst)
ALTER TABLE gps_spark_fun_rear_right_gst ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_front_gst_bag_files (table: gps_spark_fun_front_gst)
ALTER TABLE gps_spark_fun_front_gst ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_rear_left_vtg_bag_files (table: gps_spark_fun_rear_left_vtg)
ALTER TABLE gps_spark_fun_rear_left_vtg ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_rear_right_vtg_bag_files (table: gps_spark_fun_rear_right_vtg)
ALTER TABLE gps_spark_fun_rear_right_vtg ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_front_vtg_bag_files (table: gps_spark_fun_front_vtg)
ALTER TABLE gps_spark_fun_front_vtg ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: velodyne_lidar_bag_files (table: velodyne_lidar)
ALTER TABLE velodyne_lidar ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: ouster_lidar_bag_files (table: ouster_lidar)
ALTER TABLE ouster_lidar ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: trigger_bag_files (table: trigger)
ALTER TABLE trigger ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

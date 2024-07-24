/*
DROP TABLE IF EXISTS base_station_messages;
DROP TABLE IF EXISTS bag_files;
DROP TABLE IF EXISTS camera;
DROP TABLE IF EXISTS encoder;
DROP TABLE IF EXISTS tire_radii;
DROP TABLE IF EXISTS nov_atel_gps
DROP TABLE IF EXISTS hemisphere_gps;
DROP TABLE IF EXISTS garmin_gps;
DROP TABLE IF EXISTS garmin_velocity;
DROP TABLE IF EXISTS gps_spark_fun_gga;
DROP TABLE IF EXISTS gps_spark_fun_gst;
DROP TABLE IF EXISTS gps_spark_fun_vtg;
DROP TABLE IF EXISTS adis_imu;
DROP TABLE IF EXISTS nov_atel_imu;
DROP TABLE IF EXISTS lidar2d;
DROP TABLE IF EXISTS lidar3d;
DROP TABLE IF EXISTS ntrip;
DROP TABLE IF EXISTS rosout;
DROP TABLE IF EXISTS trigger;
DROP TABLE IF EXISTS road_friction;
DROP TABLE IF EXISTS steering_angle;

base_station_messages
bag_files
camera
encoder
hemisphere_gps
garmin_gps
garmin_velocity
gps_spark_fun_gga
gps_spark_fun_gst
gps_spark_fun_vtg
adis_imu
nov_atel_imu
lidar2d
lidar3d
ntrip
rosout
trigger
road_friction
steering_angle
*/

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
    CONSTRAINT bag_file_pk PRIMARY KEY (id)
    CONSTRAINT bag_file_unique UNIQUE (bag_file_name)
);

----------------------------------------------------------------------
-- Sensor Type: Camera
----------------------------------------------------------------------
-- Table: camera (option 1)
CREATE TABLE IF NOT EXISTS camera (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    camera_hash_tag int NOT NULL,
    camera_location varchar (10) NOT NULL,
    image_size bigint NOT NULL,
    image_time real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT camera_pk PRIMARY KEY (id)
    CONSTRAINT camera_hash_tag_unique UNIQUE (camera_hash_tag)
);

/*
-- Table: camera (option 2)
CREATE TABLE IF NOT EXISTS camera (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    image_file_name varchar (32) NOT NULL,
    image_size bigint NOT NULL,
    camera_location varchar (10) NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    roll real NOT NULL,
    pitch real NOT NULL,
    yaw real NOT NULL,
    image_time real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT camera_pk PRIMARY KEY (id)
    CONSTRAINT image_file_name_unique UNIQUE (image_file_name)
);
*/

----------------------------------------------------------------------
-- Sensor Type: Code
----------------------------------------------------------------------
-- Table: <>
/*
CREATE TABLE IF NOT EXISTS <> (
    id serial NOT NULL,
    CONSTRAINT _pk PRIMARY KEY (id)
);
*/

----------------------------------------------------------------------
-- Sensor Type: Encoder
----------------------------------------------------------------------
-- Table: encoder
CREATE TABLE IF NOT EXISTS encoder (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    encoder_mode varchar(50)NOT NULL,
    C1 bigint NOT NULL,
    C2 bigint NOT NULL,
    C3 bigint NOT NULL,
    C4 bigint NOT NULL,
    P1 bigint NOT NULL,
    E1 bigint NOT NULL,
    err_wrong_element_length int NOT NULL,
    err_bad_element_structure int NOT NULL,
    err_failed_time int NOT NULL,
    err_bad_uppercase_character int NOT NULL,
    err_bad_lowercase_character int NOT NULL,
    err_bad_character int NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT encoder_pk PRIMARY KEY (id)
);

/*
Question 1: How does C1 compare to C2, C3 and C4 (I know it stands for count).
            Does the count order matter? If not, consider creating a separate table.
                - ex. the # of passengers in a trip can vary, the order doesnt matter
                    which is why a separate table was used

Question 2: Are the error messages either 0 or 1. Consider changeing to bool?
            Or, add constaint for each error message to only allow 0 or 1.
*/

-- Table: tire_radii
CREATE TABLE IF NOT EXISTS tire_radii (
    id serial NOT NULL,
    encoder_id int NOT NULL,
    front_left_wheel_radius int NOT NULL,
    front_right_wheel_radius int NOT NULL,
    rear_left_wheel_radius int NOT NULL,
    rear_right_wheel_radius int NOT NULL,
    CONSTRAINT tire_radii_pk PRIMARY KEY (id)
);
----------------------------------------------------------------------
-- Sensor Type: GPS
----------------------------------------------------------------------
-- Table: hemisphere_gps
CREATE TABLE IF NOT EXISTS hemisphere_gps (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    nav_mode smallint NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    roll real NOT NULL,
    pitch real NOT NULL,
    yaw real NOT NULL,
    east_velocity real NOT NULL,
    north_velocity real NOT NULL,
    up_velocity real NOT NULL,
    gps_week serial NOT NULL,
    gps_seconds real NOT NULL,
    std_dev_resid float NOT NULL,
    num_of_sats int NOT NULL,
    manual_mark int NOT NULL,
    age_of_diff int NOT NULL,
    extended_age_of_diff int NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT hemisphere_gps_pk PRIMARY KEY (id)
);

-- Table: nov_atel_gps
CREATE TABLE IF NOT EXISTS nov_atel_gps (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    nov_atel_gps_status varchar(255) NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    roll real NOT NULL,
    pitch real NOT NULL,
    yaw real NOT NULL,
    east_velocity real NOT NULL,
    north_velocity real NOT NULL,
    up_velocity real NOT NULL,
    gps_week serial NOT NULL,
    gps_seconds real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT nov_atel_gps PRIMARY KEY (id)
);

-- Table: garmin_gps
CREATE TABLE IF NOT EXISTS garmin_gps (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    garmin_status int NOT NULL,
    garmin_service int NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    roll real NOT NULL,
    pitch real NOT NULL,
    yaw real NOT NULL,
    position_covariance varchar(50) NOT NULL,
    position_covariance_type int NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT garmin_gps_pk PRIMARY KEY (id)
);

-- Table: garmin_velocity
CREATE TABLE IF NOT EXISTS garmin_velocity (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    roll real NOT NULL,
    pitch real NOT NULL,
    yaw real NOT NULL,
    east_velocity real NOT NULL,
    north_velocity real NOT NULL,
    up_velocity real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT garmin_velocity_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_gga
CREATE TABLE IF NOT EXISTS gps_spark_fun_gga (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    base_station_messages_id int NOT NULL,
    gps_gga_postion varchar (10) NOT NULL,
    gpssecs real NULL,
    gpsmicrosecs real NULL,
    gpstime real NULL,
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
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT gps_spark_fun_gga_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_gst
CREATE TABLE IF NOT EXISTS gps_spark_fun_gst (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    gps_gst_postion varchar (10) NOT NULL,
    gpssecs real NULL,
    gpsmicrosecs real NULL,
    gpstime real NULL,
    stdmajor float NOT NULL,
    stdminor float NOT NULL,
    stdori float NOT NULL,
    stdlat float NOT NULL,
    stdlon float NOT NULL,
    stdalt float NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT gps_spark_fun_gst_pk PRIMARY KEY (id)
);

-- Table: gps_spark_fun_vtg
CREATE TABLE IF NOT EXISTS gps_spark_fun_vtg (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    gps_vtg_postion varchar (10) NOT NULL,
    true_track real NOT NULL,
    mag_track real NOT NULL,
    spdovergrndknots real NOT NULL,
    spdovergrndkmph real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT gps_spark_fun_vtg_pk PRIMARY KEY (id)
);

----------------------------------------------------------------------
-- Sensor Type: IMU
----------------------------------------------------------------------
-- Table: adis_imu
CREATE TABLE IF NOT EXISTS adis_imu (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    adis_imu_status int NOT NULL,
    x_acceleration float NOT NULL,
    y_acceleration float NOT NULL,
    z_acceleration float NOT NULL,
    x_angular_velocity float NOT NULL,
    y_angular_velocity float NOT NULL,
    z_angular_velocity float NOT NULL,
    roll float NOT NULL,
    pitch float NOT NULL,
    yaw float NOT NULL,
    magnetic_x float NOT NULL,
    magnetic_y float NOT NULL,
    magnetic_z float NOT NULL,
    temperature float NOT NULL,
    pressure float NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT adis_imu_pk PRIMARY KEY (id)
);

-- Table: nov_atel_imu
CREATE TABLE IF NOT EXISTS nov_atel_imu (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    nov_atel_imu_status int NOT NULL,
    x_acceleration float NOT NULL,
    y_acceleration float NOT NULL,
    z_acceleration float NOT NULL,
    x_angular_velocity float NOT NULL,
    y_angular_velocity float NOT NULL,
    z_angular_velocity float NOT NULL,
    roll float NOT NULL,
    pitch float NOT NULL,
    yaw float NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    gps_week serial,
    gps_seconds real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT nov_atel_imu_pk PRIMARY KEY (id)
);

----------------------------------------------------------------------
-- Sensor Type: LiDAR
----------------------------------------------------------------------
-- Table: lidar2d
CREATE TABLE IF NOT EXISTS lidar2d (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    scan_time real NOT NULL,
    ranges real NOT NULL,
    intensities real NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    roll real NOT NULL,
    pitch real NOT NULL,
    yaw real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT lidar2d_pk PRIMARY KEY (id)
);

-- Table: lidar3d (option 1)
CREATE TABLE IF NOT EXISTS lidar3d (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    lidar3d_hash_tag int NOT NULL,
    lidar3d_location varchar (10) NOT NULL,
    lidar3d_file_size bigint NOT NULL,
    lidar3d_file_time real NOT NULL, -- Might not need
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT lidar3d_pk PRIMARY KEY (id)
    CONSTRAINT lidar3d_hash_tag_unique UNIQUE (lidar3d_hash_tag)
);

/*
-- Table: lidar3d (option 2)
CREATE TABLE IF NOT EXISTS camera (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    lidar3d_sequence int NOT NULL,
    lidar3d_file_name varchar (32) NOT NULL,
    lidar3d_size bigint NOT NULL,
    lidar3d_location varchar (10) NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    roll real NOT NULL,
    pitch real NOT NULL,
    yaw real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT lidar3d_pk PRIMARY KEY (id)
    CONSTRAINT lidar3d_file_name_unique UNIQUE (lidar3d_file_name)
);
*/

----------------------------------------------------------------------
-- Sensor Type: Sytem
----------------------------------------------------------------------
-- Table: 
CREATE TABLE IF NOT EXISTS ntrip (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    base_station_messages_id varchar (50) NOT NULL,
    rtcm int NULL,
    rtcm_type int NULL,
    ntrip_device varchar(100)[] NOT NULL,
    serial_ports varchar(100)[] NOT NULL,
    ntrip_status boolean NOT NULL,
    ntrip_connection boolean NOT NULL,
    serial_connection boolean[4] NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT ntrip_pk PRIMARY KEY (id),
    CONSTRAINT base_station_id_ck CHECK (base_station_id = 'PSU_TESTTRACK')
);

-- Table: rosout 
CREATE TABLE IF NOT EXISTS rosout (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    rosout_topics varchar(200)[] NOT NULL,
    CONSTRAINT rosout_pk PRIMARY KEY (id)
);

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
    err_failed_XI_format int NOT NULL,
    err_failed_checkInformation int NOT NULL,
    err_trigger_unknown_error_occured int NOT NULL,
    err_bad_uppercase_character int NOT NULL,
    err_bad_lowercase_character int NOT NULL,
    err_bad_three_adj_element int NOT NULL,
    err_bad_first_element int NOT NULL,
    err_bad_character int NOT NULL,
    err_wrong_element_length int NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT trigger_pk PRIMARY KEY (id)
);

----------------------------------------------------------------------
-- Sensor Type: Vehicle
----------------------------------------------------------------------
-- Table: road_friction
CREATE TABLE IF NOT EXISTS road_friction (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    friction_coefficient real NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT road_friction_pk PRIMARY KEY (id)
);

-- Table: steering_angle
CREATE TABLE IF NOT EXISTS steering_angle (
    id serial NOT NULL,
    bag_files_id int NOT NULL,
    left_counts float NOT NULL,
    right_counts float NOT NULL,
    left_counts_filtered float NOT NULL,
    right_counts_filtered float NOT NULL,
    left_angle float NOT NULL,
    right_angle float NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    ros_seconds bigint NOT NULL,
    ros_nanoseconds bigint NOT NULL,
    ros_time real NOT NULL,
    ros_timestamp timestamp NOT NULL,
    CONSTRAINT steering_angle_pk PRIMARY KEY (id)
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

-- Reference: tire_radii_encoder (table: tire_radii)
ALTER TABLE tire_radii ADD
    FOREIGN KEY (encoder_id)
    REFERENCES encoder (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE

----------------------------------------------------------------------
-- Base Stations
----------------------------------------------------------------------
-- Reference: gps_spark_fun_gga_base_station_messages (table: gps_spark_fun_gga)
ALTER TABLE gps_spark_fun_gga ADD
    FOREIGN KEY (base_station_messages_id)
    REFERENCES base_station_messages (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: ntrip_base_station_messages (table: ntrip)
ALTER TABLE ntrip ADD
    FOREIGN KEY (base_station_messages_id)
    REFERENCES base_station_messages (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

----------------------------------------------------------------------
-- Bag Files
----------------------------------------------------------------------
-- Reference: camera_bag_files (table: camera)
ALTER TABLE camera ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: encoder_bag_files (table: encoder)
ALTER TABLE encoder ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: hemisphere_gps_bag_files (table: hemisphere_gps)
ALTER TABLE hemisphere_gps ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: nov_atel_gps_bag_files (table: nov_atel_gps)
ALTER TABLE nov_atel_gps ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: garmin_gps_bag_files (table: garmin_gps)
ALTER TABLE garmin_gps ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: garmin_velocity_bag_files (table: garmin_velocity)
ALTER TABLE garmin_velocity ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_gga_bag_files (table: gps_spark_fun_gga)
ALTER TABLE gps_spark_fun_gga ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_gst_bag_files (table: gps_spark_fun_gst)
ALTER TABLE gps_spark_fun_gst ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_spark_fun_vtg_bag_files (table: gps_spark_fun_vtg)
ALTER TABLE gps_spark_fun_vtg ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: adis_imu_bag_files (table: adis_imu)
ALTER TABLE adis_imu ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: nov_atel_imu_bag_files (table: nov_atel_imu)
ALTER TABLE nov_atel_imu ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: lidar2d_bag_files (table: lidar2d)
ALTER TABLE lidar2d ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: lidar3d_bag_files (table: lidar3d)
ALTER TABLE lidar3d ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: ntrip_bag_files (table: ntrip)
ALTER TABLE ntrip ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: rosout_bag_files (table: rosout)
ALTER TABLE rosout ADD
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

-- Reference: road_friction_bag_files (table: road_friction)
ALTER TABLE road_friction ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: steering_angle_bag_files (table: steering_angle)
ALTER TABLE steering_angle ADD
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;
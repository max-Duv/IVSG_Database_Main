-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2024-07-09 19:16:30.922

/*
DROP TABLE IF EXISTS Vehicle;
DROP TABLE IF EXISTS base_stations;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS bag_files;
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS camera;
DROP TABLE IF EXISTS camera_parameters;
DROP TABLE IF EXISTS lidar2d;
DROP TABLE IF EXISTS lidar3d;
DROP TABLE IF EXISTS laser_parameters;
DROP TABLE IF EXISTS trigger;
DROP TABLE IF EXISTS encoder;
DROP TABLE IF EXISTS encoder_parameters;
DROP TABLE IF EXISTS transform;
DROP TABLE IF EXISTS steering_angle;
DROP TABLE IF EXISTS Road_friction;
DROP TABLE IF EXISTS imu;
DROP TABLE IF EXISTS adis16407_parameters;
DROP TABLE IF EXISTS Adis_IMU;
DROP TABLE IF EXISTS NovAtel_IMU;
DROP TABLE IF EXISTS ntrip;
DROP TABLE IF EXISTS gps;
DROP TABLE IF EXISTS garmin_gps;
DROP TABLE IF EXISTS garmin_velocity;
DROP TABLE IF EXISTS Hemisphere_gps;
DROP TABLE IF EXISTS NovAtel_gps;
DROP TABLE IF EXISTS GPS_SparkFun_LeftRear_GGA;
DROP TABLE IF EXISTS GPS_SparkFun_LeftRear_VTG;
DROP TABLE IF EXISTS GPS_SparkFun_LeftRear_GST;
DROP TABLE IF EXISTS GPS_SparkFun_Front_GGA;
DROP TABLE IF EXISTS GPS_SparkFun_Front_VTG;
DROP TABLE IF EXISTS GPS_SparkFun_Front_GST;
DROP TABLE IF EXISTS GPS_SparkFun_RightRear_GGA;
DROP TABLE IF EXISTS GPS_SparkFun_RightRear_VTG;
DROP TABLE IF EXISTS GPS_SparkFun_RightRear_GST;
DROP TABLE IF EXISTS rosout;
DROP TABLE IF EXISTS diagnostics;
DROP TABLE IF EXISTS spatial_ref_sys;
*/

CREATE EXTENSION postgis;
-- CREATE EXTENSION pointcloud;
-- CREATE EXTENSION pointcloud_postgis;

-- tables
-- Table: Adis_IMU
CREATE TABLE Adis_IMU (
    id serial  NOT NULL,
    imu_id int  NOT NULL,
    status int  NULL,
    x_acceleration FLOAT  NULL,
    y_acceleration FLOAT  NULL,
    z_acceleration FLOAT  NULL,
    x_angular_velocity FLOAT  NULL,
    y_angular_velocity FLOAT  NULL,
    z_angular_velocity FLOAT  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    roll FLOAT  NULL,
    pitch FLOAT  NULL,
    yaw FLOAT  NULL,
    magentic_x FLOAT  NULL,
    magnetic_y FLOAT  NULL,
    magnetic_z FLOAT  NULL,
    temperature FLOAT  NULL,
    pressure FLOAT  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT Adis_IMU_pk PRIMARY KEY (id)
);

CREATE INDEX Adis_imu_index on Adis_IMU (seconds ASC,nanoseconds ASC,imu_id ASC);

CREATE INDEX Adis_imu_geography_index on Adis_IMU (geography ASC);

-- Table: GPS_SparkFun_Front_GGA
CREATE TABLE GPS_SparkFun_Front_GGA (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    gpssecs real  NULL,
    gpsmicrosecs real  NULL,
    gpstime real  NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geosep real  NULL,
    navmode smallint  NULL,
    numOfSats int  NULL,
    hdop FLOAT  NULL,
    ageOfDiff FLOAT  NULL,
    lockstatus smallint  NULL,
    basestationid varchar(32)  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT GPS_SparkFun_Front_GGA_pk PRIMARY KEY (id)
);

-- Table: GPS_SparkFun_Front_GST
CREATE TABLE GPS_SparkFun_Front_GST (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    gpssecs real  NULL,
    gpsmicrosecs real  NULL,
    gpstime real  NULL,
    stdmajor FLOAT  NULL,
    stdminor FLOAT  NULL,
    stdori FLOAT  NULL,
    stdlat FLOAT  NULL,
    stdlon FLOAT  NULL,
    stdalt FLOAT  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT GPS_SparkFun_Front_GST_pk PRIMARY KEY (id)
);

-- Table: GPS_SparkFun_Front_VTG
CREATE TABLE GPS_SparkFun_Front_VTG (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    truetrack real  NULL,
    magtrack real  NULL,
    spdovergrndknots real  NULL,
    spdovergrndkmph real  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT GPS_SparkFun_Front_VTG_pk PRIMARY KEY (id)
);

-- Table: GPS_SparkFun_LeftRear_GGA
CREATE TABLE GPS_SparkFun_LeftRear_GGA (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    gpssecs real  NULL,
    gpsmicrosecs real  NULL,
    gpstime real  NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geosep real  NULL,
    navmode smallint  NULL,
    numOfSats int  NULL,
    hdop FLOAT  NULL,
    ageOfDiff FLOAT  NULL,
    lockstatus smallint  NULL,
    basestationid varchar(32)  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT GPS_SparkFun_LeftRear_GGA_pk PRIMARY KEY (id)
);

-- Table: GPS_SparkFun_LeftRear_GST
CREATE TABLE GPS_SparkFun_LeftRear_GST (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    gpssecs real  NULL,
    gpsmicrosecs real  NULL,
    gpstime real  NULL,
    stdmajor FLOAT  NULL,
    stdminor FLOAT  NULL,
    stdori FLOAT  NULL,
    stdlat FLOAT  NULL,
    stdlon FLOAT  NULL,
    stdalt FLOAT  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT GPS_SparkFun_LeftRear_GST_pk PRIMARY KEY (id)
);

-- Table: GPS_SparkFun_LeftRear_VTG
CREATE TABLE GPS_SparkFun_LeftRear_VTG (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    truetrack real  NULL,
    magtrack real  NULL,
    spdovergrndknots real  NULL,
    spdovergrndkmph real  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT GPS_SparkFun_LeftRear_VTG_pk PRIMARY KEY (id)
);

-- Table: GPS_SparkFun_RightRear_GGA
CREATE TABLE GPS_SparkFun_RightRear_GGA (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    gpssecs real  NULL,
    gpsmicrosecs real  NULL,
    gpstime real  NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geosep real  NULL,
    navmode smallint  NULL,
    numOfSats int  NULL,
    hdop FLOAT  NULL,
    ageOfDiff FLOAT  NULL,
    lockstatus smallint  NULL,
    basestationid varchar(32)  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT GPS_SparkFun_RightRear_GGA_pk PRIMARY KEY (id)
);

-- Table: GPS_SparkFun_RightRear_GST
CREATE TABLE GPS_SparkFun_RightRear_GST (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    gpssecs real  NULL,
    gpsmicrosecs real  NULL,
    gpstime real  NULL,
    stdmajor FLOAT  NULL,
    stdminor FLOAT  NULL,
    stdori FLOAT  NULL,
    stdlat FLOAT  NULL,
    stdlon FLOAT  NULL,
    stdalt FLOAT  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT GPS_SparkFun_RightRear_GST_pk PRIMARY KEY (id)
);

-- Table: GPS_SparkFun_RightRear_VTG
CREATE TABLE GPS_SparkFun_RightRear_VTG (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    truetrack real  NULL,
    magtrack real  NULL,
    spdovergrndknots real  NULL,
    spdovergrndkmph real  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT GPS_SparkFun_RightRear_VTG_pk PRIMARY KEY (id)
);

-- Table: Hemisphere_gps
CREATE TABLE Hemisphere_gps (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    NavMode smallint  NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    east_velocity real  NULL,
    north_velocity real  NULL,
    up_velocity real  NULL,
    StdDevResid FLOAT  NULL,
    roll real  NULL,
    pitch real  NULL,
    yaw real  NULL,
    gps_week serial,
    gps_seconds real  NULL,
    NumOfSats int  NULL,
    ManualMark int  NULL,
    AgeOfDiff int  NULL,
    ExtendedAgeOfDiff int  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT Hemisphere_gps_pk PRIMARY KEY (id)
);

CREATE INDEX HemisphereGPS_geography_index on Hemisphere_gps (geography ASC);

CREATE INDEX HemisphereGPS_index on Hemisphere_gps (seconds ASC,nanoseconds ASC);

-- Table: NovAtel_IMU
CREATE TABLE NovAtel_IMU (
    id serial  NOT NULL,
    imu_id int  NOT NULL,
    status int  NULL,
    x_acceleration real  NULL,
    y_acceleration real  NULL,
    z_acceleration real  NULL,
    x_angular_velocity real  NULL,
    y_angular_velocity real  NULL,
    z_angular_velocity real  NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    roll real  NULL,
    pitch real  NULL,
    yaw real  NULL,
    gps_week serial,
    gps_seconds real  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT NovAtel_IMU_pk PRIMARY KEY (id)
);

CREATE INDEX imu_index on NovAtel_IMU (id ASC,seconds ASC,nanoseconds ASC);

CREATE INDEX imu_geography_index on NovAtel_IMU (geography ASC);

-- Table: NovAtel_gps
CREATE TABLE NovAtel_gps (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    status varchar(255)  NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    east_velocity real  NULL,
    north_velocity real  NULL,
    up_velocity real  NULL,
    roll real  NULL,
    pitch real  NULL,
    yaw real  NULL,
    gps_week serial,
    gps_seconds real  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT NovAtel_gps_pk PRIMARY KEY (id)
);

CREATE INDEX gps_geography_index on NovAtel_gps (geography ASC);

CREATE INDEX gps_index on NovAtel_gps (seconds ASC,nanoseconds ASC);

-- Table: Road_friction
CREATE TABLE Road_friction (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    friction_coefficient real  NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT Road_friction_pk PRIMARY KEY (id)
);

CREATE INDEX Friction_geography_index on Road_friction (geography ASC);

CREATE INDEX Friction_index on Road_friction (seconds ASC,nanoseconds ASC);

-- Table: Vehicle
CREATE TABLE Vehicle (
    id serial  NOT NULL,
    name text  NULL,
    CONSTRAINT Vehicle_pk PRIMARY KEY (id)
);

-- Table: adis16407_parameters
CREATE TABLE adis16407_parameters (
    id serial  NOT NULL,
    imu_id int  NOT NULL,
    ACCEL_SCALE varchar(128)  NULL,
    GYRO_SCAEL FLOAT  NULL,
    MAG_SCALE FLOAT  NULL,
    BAR_SCALE FLOAT  NULL,
    TEMP_SCALE FLOAT  NULL,
    GRAVITY FLOAT  NULL,
    ACCEL_COV FLOAT  NULL,
    GYRO_COV FLOAT  NULL,
    MAG_COV FLOAT  NULL,
    BAR_COV FLOAT  NULL,
    date_added timestamp  NULL,
    CONSTRAINT adis16407_parameters_pk PRIMARY KEY (id)
);

CREATE UNIQUE INDEX adis16407_parameters_index on adis16407_parameters (imu_id ASC,ACCEL_SCALE ASC,GYRO_SCAEL ASC,MAG_SCALE ASC,BAR_SCALE ASC,TEMP_SCALE ASC,GRAVITY ASC,ACCEL_COV ASC,GYRO_COV ASC,MAG_COV ASC,BAR_COV ASC);

-- Table: bag_files
CREATE TABLE bag_files (
    id serial  NOT NULL,
    Vehicle_id int  NOT NULL,
    trips_id int  NOT NULL,
    file_path text  NULL,
    name text  NULL,
    datetime timestamp  NULL,
    datetime_end timestamp  NULL,
    parsed boolean  NULL,
    date_added timestamp  NULL,
    CONSTRAINT bag_files_pk PRIMARY KEY (id)
);

CREATE UNIQUE INDEX bag_files_index on bag_files (name ASC);

-- Table: base_stations
CREATE TABLE base_stations (
    id serial  NOT NULL,
    name text  NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitutde real  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    latitude_std real  NULL,
    longitude_std real  NULL,
    altitude_std real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT base_stations_pk PRIMARY KEY (id)
);

CREATE INDEX base_stations_geography_index on base_stations (geography ASC);

CREATE INDEX base_stations_index on base_stations (latitude ASC,longitude ASC,altitutde ASC);

-- Table: camera
CREATE TABLE camera (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    camera_hash_tag int  NULL,
    CONSTRAINT camera_pk PRIMARY KEY (id)
);

CREATE UNIQUE INDEX camera_index on camera (sensors_id ASC);

-- Table: camera_parameters
CREATE TABLE camera_parameters (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    focal_x real  NULL,
    focal_y real  NULL,
    center_x real  NULL,
    center_y real  NULL,
    skew real  NULL,
    image_width int  NULL,
    image_height int  NULL,
    distortion_k1 real  NULL,
    distortion_k2 real  NULL,
    distortion_k3 real  NULL,
    distortion_p1 real  NULL,
    distortion_p2 real  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT camera_parameters_pk PRIMARY KEY (id)
);

CREATE INDEX camera_parameters_index on camera_parameters (sensors_id ASC,bag_files_id ASC,focal_x ASC,focal_y ASC,center_x ASC,center_y ASC,skew ASC,image_width ASC,image_height ASC,distortion_k1 ASC,distortion_k2 ASC,distortion_k3 ASC,distortion_p1 ASC,distortion_p2 ASC);

-- Table: diagnostic
CREATE TABLE diagnostic (
    id serial  NOT NULL,
    status int  NULL,
    CONSTRAINT diagnostic_pk PRIMARY KEY (id)
);

-- Table: diagnostics
CREATE TABLE diagnostics (
    id serial  NOT NULL,
    camera_diagnostic text  NULL,
    velodyne_diagnostic text  NULL,
    sick_lms_5xx_diagnostic text  NULL,
    trigger_diagnostic text  NULL,
    encoder_diagnostic text  NULL,
    Adis_IMU_diagnostic text  NULL,
    NovAtel_IMU_diagnostic text  NULL,
    garmin_gps_diagnostic text  NULL,
    garmin_velocity_diagnostic text  NULL,
    Hemisphere_gps_diagnostic text  NULL,
    NovAtel_gps_diagnostic text  NULL,
    GPS_SparkFun_LeftRear_GGA_diagnostic text  NULL,
    GPS_SparkFun_LeftRear_GST_diagnostic text  NULL,
    GPS_SparkFun_LeftRear_VTG_diagnostic text  NULL,
    GPS_SparkFun_Front_GGA_diagnostic text  NULL,
    GPS_SparkFun_Front_GST_diagnostic text  NULL,
    GPS_SparkFun_Front_VTG_diagnostic text  NULL,
    GPS_SparkFun_RightRear_GGA_diagnostic text  NULL,
    GPS_SparkFun_RightRear_GST_diagnostic text  NULL,
    GPS_SparkFun_RightRear_VTG_diagnostic text  NULL,
    CONSTRAINT diagnostics_pk PRIMARY KEY (id)
);

-- Table: encoder
CREATE TABLE encoder (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    mode varchar(50)  NULL,
    C1 bigint  NULL,
    C2 bigint  NULL,
    C3 bigint  NULL,
    C4 bigint  NULL,
    P1 bigint  NULL,
    E1 bigint  NULL,
    err_wrong_element_length int  NULL,
    err_bad_element_structure int  NULL,
    err_failed_time int  NULL,
    err_bad_uppercase_character int  NULL,
    err_bad_lowercase_character int  NULL,
    err_bad_character int  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT encoder_pk PRIMARY KEY (id)
);

CREATE INDEX encoder_index on encoder (sensors_id ASC,seconds ASC,nanoseconds ASC);

CREATE INDEX encoder_geography_index on encoder (geography ASC);

-- Table: encoder_parameters
CREATE TABLE encoder_parameters (
    id serial  NOT NULL,
    sensors_id int  NOT NULL,
    counts_per_revolution int  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT encoder_parameters_pk PRIMARY KEY (id)
);

CREATE UNIQUE INDEX encoder_parameters_idx on encoder_parameters (sensors_id ASC,counts_per_revolution ASC);

-- Table: garmin_gps
CREATE TABLE garmin_gps (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    status int  NULL,
    service int  NULL,
    latitude FLOAT  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    roll real  NULL,
    pitch real  NULL,
    yaw real  NULL,
    position_covariance text  NULL,
    position_covariance_type int  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT garmin_gps_pk PRIMARY KEY (id)
);

CREATE INDEX GarminGps_geography_index on garmin_gps (geography ASC);

CREATE INDEX Garmingps_index on garmin_gps (seconds ASC,nanoseconds ASC);

-- Table: garmin_velocity
CREATE TABLE garmin_velocity (
    id serial  NOT NULL,
    gps_id int  NOT NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    roll real  NULL,
    pitch real  NULL,
    yaw real  NULL,
    east_velocity real  NULL,
    north_velocity real  NULL,
    up_velocity real  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT garmin_velocity_pk PRIMARY KEY (id)
);

CREATE INDEX GarminGpsVel_geography_index on garmin_velocity (geography ASC);

CREATE INDEX GarmingpsVel_index on garmin_velocity (seconds ASC,nanoseconds ASC);

-- Table: gps
CREATE TABLE gps (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    ntrip_id int  NOT NULL,
    GPS_SparkFun_List text  NULL,
    status int  NOT NULL,
    CONSTRAINT gps_pk PRIMARY KEY (id)
);

-- Table: imu
CREATE TABLE imu (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    CONSTRAINT imu_pk PRIMARY KEY (id)
);

-- Table: laser_parameters
CREATE TABLE laser_parameters (
    id serial  NOT NULL,
    sensors_id int  NOT NULL,
    angle_min real  NULL,
    angle_max real  NULL,
    angle_increment real  NULL,
    time_increment real  NULL,
    range_min real  NULL,
    range_max real  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT laser_parameters_pk PRIMARY KEY (id)
);

CREATE UNIQUE INDEX laser_parameters_index on laser_parameters (sensors_id,angle_min ,angle_max ,angle_increment ,time_increment ,range_min ,range_max);

-- Table: lidar2d
CREATE TABLE lidar2d (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    sick_lms_5xx_hashtag int  NULL,
    CONSTRAINT lidar2d_pk PRIMARY KEY (id)
);

CREATE UNIQUE INDEX lidar2d_index on lidar2d (sensors_id);

-- Table: lidar3d
CREATE TABLE lidar3d (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    velodyne_hashtag int  NULL,
    CONSTRAINT lidar3d_pk PRIMARY KEY (id)
);

CREATE UNIQUE INDEX lidar3d_index on lidar3d (sensors_id);

-- Table: ntrip
CREATE TABLE ntrip (
    id serial  NOT NULL,
    status int  NULL,
    CONSTRAINT ntrip_pk PRIMARY KEY (id)
);

-- Table: rosout
CREATE TABLE rosout (
    id serial  NOT NULL,
    rosout_message text  NOT NULL,
    CONSTRAINT rosout_pk PRIMARY KEY (id)
);

-- Table: sensors
CREATE TABLE sensors (
    id serial  NOT NULL,
    type int  NOT NULL,
    serial_number varchar(255)  NULL,
    company_name varchar(255)  NULL,
    product_name varchar(255)  NULL,
    date_added timestamp  NULL,
    CONSTRAINT sensors_pk PRIMARY KEY (id)
);

-- Table: steering_angle
CREATE TABLE steering_angle (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    left_counts FLOAT  NULL,
    right_counts FLOAT  NULL,
    left_counts_filtered FLOAT  NULL,
    rights_counts_filtered FLOAT  NULL,
    left_angle FLOAT  NULL,
    right_angle FLOAT  NULL,
    angle FLOAT  NULL,
    latitude FLOAT  NULL,
    longitude FLOAT  NULL,
    altitude FLOAT  NULL,
    geography GEOGRAPHY(point,4326)  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT steering_angle_pk PRIMARY KEY (id)
);

CREATE INDEX steering_angle_geography_index on steering_angle (geography ASC);

CREATE UNIQUE INDEX steering_angle_index on steering_angle (seconds ASC,nanoseconds ASC);

-- Table: transform
CREATE TABLE transform (
    id serial  NOT NULL,
    encoder_id int  NOT NULL,
    front_left_wheel_radius int  NULL,
    front_right_wheel_radius int  NULL,
    rear_left_wheel_radius int  NULL,
    rear_right_wheel_radius int  NULL,
    CONSTRAINT transform_pk PRIMARY KEY (id)
);

-- Table: trigger
CREATE TABLE trigger (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    mode varchar(50)  NULL,
    mode_counts int  NULL,
    adjone int  NULL,
    adjtwo int  NULL,
    adjthree int  NULL,
    err_failed_mode_count int  NULL,
    err_failed_XI_format int  NULL,
    err_failed_checkInformation int  NULL,
    err_trigger_unknown_error_occured int  NULL,
    err_bad_uppercase_character int  NULL,
    err_bad_lowercase_character int  NULL,
    err_bad_three_adj_element int  NULL,
    err_bad_first_element int  NULL,
    err_bad_character int  NULL,
    err_wrong_element_length int  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL,
    CONSTRAINT trigger_pk PRIMARY KEY (id)
);

CREATE INDEX trigger_index on trigger (sensors_id ASC,seconds ASC,nanoseconds ASC);

CREATE INDEX trigger_geography_index on trigger (geography ASC);

-- Table: trips
CREATE TABLE trips (
    id serial  NOT NULL,
    name text  NULL,
    date date  NULL,
    base_stations_id int  NOT NULL,
    description text  NULL,
    driver text  NULL,
    passengers text  NULL,
    notes text  NULL,
    date_added timestamp  NULL,
    CONSTRAINT trips_pk PRIMARY KEY (id)
);

-- foreign keys
-- Reference: Adis_IMU_imu (table: Adis_IMU)
ALTER TABLE Adis_IMU ADD CONSTRAINT Adis_IMU_imu
    FOREIGN KEY (imu_id)
    REFERENCES imu (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_Front_GGA_gps (table: GPS_SparkFun_Front_GGA)
ALTER TABLE GPS_SparkFun_Front_GGA ADD CONSTRAINT GPS_SparkFun_Front_GGA_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_Front_GST_gps (table: GPS_SparkFun_Front_GST)
ALTER TABLE GPS_SparkFun_Front_GST ADD CONSTRAINT GPS_SparkFun_Front_GST_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_Front_VTG_gps (table: GPS_SparkFun_Front_VTG)
ALTER TABLE GPS_SparkFun_Front_VTG ADD CONSTRAINT GPS_SparkFun_Front_VTG_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_GGA_bag_files (table: gps)
ALTER TABLE gps ADD CONSTRAINT GPS_SparkFun_GGA_bag_files
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_GGA_sensors (table: gps)
ALTER TABLE gps ADD CONSTRAINT GPS_SparkFun_GGA_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_LeftRear_GGA_gps (table: GPS_SparkFun_LeftRear_GGA)
ALTER TABLE GPS_SparkFun_LeftRear_GGA ADD CONSTRAINT GPS_SparkFun_LeftRear_GGA_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_LeftRear_GST_gps (table: GPS_SparkFun_LeftRear_GST)
ALTER TABLE GPS_SparkFun_LeftRear_GST ADD CONSTRAINT GPS_SparkFun_LeftRear_GST_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_LeftRear_VTG_gps (table: GPS_SparkFun_LeftRear_VTG)
ALTER TABLE GPS_SparkFun_LeftRear_VTG ADD CONSTRAINT GPS_SparkFun_LeftRear_VTG_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_RightRear_GGA_gps (table: GPS_SparkFun_RightRear_GGA)
ALTER TABLE GPS_SparkFun_RightRear_GGA ADD CONSTRAINT GPS_SparkFun_RightRear_GGA_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_RightRear_GST_gps (table: GPS_SparkFun_RightRear_GST)
ALTER TABLE GPS_SparkFun_RightRear_GST ADD CONSTRAINT GPS_SparkFun_RightRear_GST_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: GPS_SparkFun_RightRear_VTG_gps (table: GPS_SparkFun_RightRear_VTG)
ALTER TABLE GPS_SparkFun_RightRear_VTG ADD CONSTRAINT GPS_SparkFun_RightRear_VTG_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Hemisphere_gps_gps (table: Hemisphere_gps)
ALTER TABLE Hemisphere_gps ADD CONSTRAINT Hemisphere_gps_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: NovAtel_IMU_imu (table: NovAtel_IMU)
ALTER TABLE NovAtel_IMU ADD CONSTRAINT NovAtel_IMU_imu
    FOREIGN KEY (imu_id)
    REFERENCES imu (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: NovAtel_gps_gps (table: NovAtel_gps)
ALTER TABLE NovAtel_gps ADD CONSTRAINT NovAtel_gps_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: adis16407_parameters_imu (table: adis16407_parameters)
ALTER TABLE adis16407_parameters ADD CONSTRAINT adis16407_parameters_imu
    FOREIGN KEY (imu_id)
    REFERENCES imu (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: bag_files_Vehicle (table: bag_files)
ALTER TABLE bag_files ADD CONSTRAINT bag_files_Vehicle
    FOREIGN KEY (Vehicle_id)
    REFERENCES Vehicle (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: bag_files_trips (table: bag_files)
ALTER TABLE bag_files ADD CONSTRAINT bag_files_trips
    FOREIGN KEY (trips_id)
    REFERENCES trips (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: camera_bag_files (table: camera)
ALTER TABLE camera ADD CONSTRAINT camera_bag_files
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: camera_parameters_bag_files (table: camera_parameters)
ALTER TABLE camera_parameters ADD CONSTRAINT camera_parameters_bag_files
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: camera_parameters_sensors (table: camera_parameters)
ALTER TABLE camera_parameters ADD CONSTRAINT camera_parameters_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: camera_sensors (table: camera)
ALTER TABLE camera ADD CONSTRAINT camera_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: encoder_new_bag_files (table: encoder)
ALTER TABLE encoder ADD CONSTRAINT encoder_new_bag_files
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: encoder_new_sensors (table: encoder)
ALTER TABLE encoder ADD CONSTRAINT encoder_new_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: encoder_parameters_sensors (table: encoder_parameters)
ALTER TABLE encoder_parameters ADD CONSTRAINT encoder_parameters_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: garmin_gps_gps (table: garmin_gps)
ALTER TABLE garmin_gps ADD CONSTRAINT garmin_gps_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: garmin_velocity_gps (table: garmin_velocity)
ALTER TABLE garmin_velocity ADD CONSTRAINT garmin_velocity_gps
    FOREIGN KEY (gps_id)
    REFERENCES gps (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_ntrip (table: gps)
ALTER TABLE gps ADD CONSTRAINT gps_ntrip
    FOREIGN KEY (ntrip_id)
    REFERENCES ntrip (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: imu_bag_files (table: imu)
ALTER TABLE imu ADD CONSTRAINT imu_bag_files
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: imu_sensors (table: imu)
ALTER TABLE imu ADD CONSTRAINT imu_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: laser_parameters_sensors (table: laser_parameters)
ALTER TABLE laser_parameters ADD CONSTRAINT laser_parameters_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: lidar2d_bag_files (table: lidar2d)
ALTER TABLE lidar2d ADD CONSTRAINT lidar2d_bag_files
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: lidar2d_sensors (table: lidar2d)
ALTER TABLE lidar2d ADD CONSTRAINT lidar2d_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: lidar3d_bag_files (table: lidar3d)
ALTER TABLE lidar3d ADD CONSTRAINT lidar3d_bag_files
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: lidar3d_sensors (table: lidar3d)
ALTER TABLE lidar3d ADD CONSTRAINT lidar3d_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: road_friction_bag_files (table: Road_friction)
ALTER TABLE Road_friction ADD CONSTRAINT road_friction_bag_files
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: road_friction_sensors (table: Road_friction)
ALTER TABLE Road_friction ADD CONSTRAINT road_friction_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: steering_angle_bag_files (table: steering_angle)
ALTER TABLE steering_angle ADD CONSTRAINT steering_angle_bag_files
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: steering_angle_sensors (table: steering_angle)
ALTER TABLE steering_angle ADD CONSTRAINT steering_angle_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: transform_encoder (table: transform)
ALTER TABLE transform ADD CONSTRAINT transform_encoder
    FOREIGN KEY (encoder_id)
    REFERENCES encoder (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: trigger_bag_files (table: trigger)
ALTER TABLE trigger ADD CONSTRAINT trigger_bag_files
    FOREIGN KEY (bag_files_id)
    REFERENCES bag_files (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: trigger_sensors (table: trigger)
ALTER TABLE trigger ADD CONSTRAINT trigger_sensors
    FOREIGN KEY (sensors_id)
    REFERENCES sensors (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: trips_base_stations (table: trips)
ALTER TABLE trips ADD CONSTRAINT trips_base_stations
    FOREIGN KEY (base_stations_id)
    REFERENCES base_stations (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- End of file.


/*
ivsg_members
base_station_parameters
trip_name
trip_members
trip_base_stations
conditions
bag_files
pre_trip_details
post_trip_details
purchasing_parameters
installation_parameters
performance_setting_parameters
camera_parameters
code_parameters
encoder_parameters
gps_parameters
imu_parameters
lidar_parameters
trigger_parameters
system_parameters
vehicle_parameters
parameter_config
*/

/*
DROP TABLE IF EXISTS ivsg_members;
DROP TABLE IF EXISTS base_station_parameters;
DROP TABLE IF EXISTS trip_name;
DROP TABLE IF EXISTS trip_members;
DROP TABLE IF EXISTS trip_base_stations;
DROP TABLE IF EXISTS conditions;
DROP TABLE IF EXISTS bag_files;
DROP TABLE IF EXISTS pre_trip_details;
DROP TABLE IF EXISTS post_trip_details;
DROP TABLE IF EXISTS purchasing_parameters;
DROP TABLE IF EXISTS installation_parameters;
DROP TABLE IF EXISTS performance_setting_parameters;
DROP TABLE IF EXISTS camera_parameters;
DROP TABLE IF EXISTS code_parameters;
DROP TABLE IF EXISTS encoder_parameters;
DROP TABLE IF EXISTS gps_parameters;
DROP TABLE IF EXISTS imu_parameters;
DROP TABLE IF EXISTS lidar_parameters;
DROP TABLE IF EXISTS trigger_parameters;
DROP TABLE IF EXISTS system_parameters;
DROP TABLE IF EXISTS vehicle_parameters;
DROP TABLE IF EXISTS parameter_config;
*/

-- tables
-- Table: ivsg_members
CREATE TABLE IF NOT EXISTS ivsg_members(
    id serial NOT NULL,
    first_name varchar(50) NOT NULL,
    last_name varchar(50) NOT NULL,
    date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT ivsg_members_pk PRIMARY KEY (id),
    CONSTRAINT ivsg_member_name_unique UNIQUE (first_name, last_name)
); 

-- Table: base_station_parameters
CREATE TABLE IF NOT EXISTS base_station_parameters (
    id serial NOT NULL,
    base_station_name varchar(20) NOT NULL,
    latitude real NULL,
    longitude real NULL,
    altitude real NULL,
    latitude_std_dev real NULL,
    longitude_std_dev real NULL,
    altitude_std_dev real NULL,
    date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT base_station_parameters_pk PRIMARY KEY (id),
    CONSTRAINT base_station_name_unique UNIQUE (base_station_name)
);

-- Table: trip_name
CREATE TABLE IF NOT EXISTS trip_name (
    id serial NOT NULL,
    trip_name varchar(50),
    trip_date date NULL,
    date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT trip_name_pk PRIMARY KEY (id),
    CONSTRAINT trip_name_unique UNIQUE (trip_name)
);

-- Table: trip_members
CREATE TABLE IF NOT EXISTS trip_members (
    id serial NOT NULL,
    trip_id int NOT NULL,
    member_id int NOT NULL,
    drove boolean NOT NULL
    CONSTRAINT trip_members_pk PRIMARY KEY (id)
    CONSTRAINT trip_members_unique UNIQUE (trip_id, member_id, drove)
);

-- Table: trip_base_stations
CREATE TABLE IF NOT EXISTS trip_base_stations (
    id serial NOT NULL,
    trip_id int NOT NULL,
    base_station_id NOT NULL,
    was_pre_trip boolean NOT NULL,
    was_post_trip boolean NOT NULL,
    CONSTRAINT trip_base_stations_pk PRIMARY KEY (id)
    CONSTRAINT trip_base_stations_unique UNIQUE (trip_id, base_station_id) -- TEST THIS
);

-- Table: conditions
CREATE TABLE IF NOT EXISTS conditions (
    id serial NOT NULL,
    time_of_day varchar(10) NOT NULL,
    weather_condition varchar(10) NOT NULL,
    had_extreme_weather boolean NOT NULL,
    road_wet boolean NOT NULL,
    traffic_level varchar(15) NOT NULL,
    road_work_level varchar(15) NOT NULL,
    weather_notes varchar (50) NOT NULL,
    CONSTRAINT conditions_pk PRIMARY KEY (id)
    CONSTRAINT conditions_unique UNIQUE (time_of_day, weather_condition) -- TEST
    /*
    Planned acceptable time_of_day values:
        day, night, dusk, sunrise, sunset

    Planned acceptable weather values:
        rain, clouds, wind, snow, fog, storms 
    
    Planned acceptable traffic and roadwork level and  values:
        little, medium, lots, standstill 

    */
);

-- Table: bag_files
CREATE TABLE IF NOT EXISTS bag_files (
    id serial NOT NULL,
    bag_file_name varchar(50) NOT NULL,
    bag_file_size int NOT NULL,
    trip_id int NOT NULL,
    date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT bag_files_pk PRIMARY KEY (id),
    CONSTRAINT bag_file_trip_unique (bag_file_name, trip_id)
);

-- Table: pre_trip_details
CREATE TABLE IF NOT EXISTS pre_trip_details (
    id serial NOT NULL,
    trip_name_id int NOT NULL,
    trip_members_id int NOT NULL,
    parameter_config_id int NOT NULL,
    planned_base_stations_id int NOT NULL,
    pre_trip_starting_conditions_id int NOT NULL,
    pre_trip_notes text NULL,
    trip_date date NOT NULL,
    ate_added_to_db date NOT NULL DEFAULT GETDATE(),

    CONSTRAINT pre_trip_details_pk PRIMARY KEY (id)
);

-- Table: post_trip_details
CREATE TABLE IF NOT EXISTS post_trip_details (
    id serial NOT NULL,

    CONSTRAINT post_trip_details_pk PRIMARY KEY (id)
);

-- Table: purchasing_parameters
CREATE TABLE IF NOT EXISTS purchasing_parameters (
    id serial NOT NULL,

    CONSTRAINT purchasing_parameters_pk PRIMARY KEY (id)
);

-- Table: installation_parameters
CREATE TABLE IF NOT EXISTS installation_parameters (
    id serial NOT NULL,

    CONSTRAINT installation_parameters_pk PRIMARY KEY (id)
);

-- Table: performance_setting_parameters
CREATE TABLE IF NOT EXISTS performance_setting_parameters (
    id serial NOT NULL,

    CONSTRAINT performance_setting_parameters_pk PRIMARY KEY (id)
);

-- Table: camera_parameters
CREATE TABLE IF NOT EXISTS camera_parameters (
    id serial NOT NULL,

    CONSTRAINT camera_parameters_pk PRIMARY KEY (id)
);

-- Table: code_parameters
CREATE TABLE IF NOT EXISTS code_parameters (
    id serial NOT NULL,

    CONSTRAINT code_parameters_pk PRIMARY KEY (id)
);

-- Table: encoder_parameters
CREATE TABLE IF NOT EXISTS encoder_parameters (
    id serial NOT NULL,

    CONSTRAINT encoder_parameters_pk PRIMARY KEY (id)
);

-- Table: gps_parameters
CREATE TABLE IF NOT EXISTS gps_parameters (
    id serial NOT NULL,

    CONSTRAINT gps_parameters_pk PRIMARY KEY (id)
);

-- Table: imu_parameters
CREATE TABLE IF NOT EXISTS imu_parameters (
    id serial NOT NULL,

    CONSTRAINT imu_parameters_pk PRIMARY KEY (id)
);

-- Table: lidar_parameters
CREATE TABLE IF NOT EXISTS lidar_parameters (
    id serial NOT NULL,

    CONSTRAINT lidar_parameters_pk PRIMARY KEY (id)
);

-- Table: trigger_parameters
CREATE TABLE IF NOT EXISTS trigger_parameters (
    id serial NOT NULL,

    CONSTRAINT trigger_parameters_pk PRIMARY KEY (id)
);

-- Table: system_parameters
CREATE TABLE IF NOT EXISTS system_parameters (
    id serial NOT NULL,

    CONSTRAINT system_parameters_pk PRIMARY KEY (id)
);

-- Table: vehicle_parameters
CREATE TABLE IF NOT EXISTS vehicle_parameters (
    id serial NOT NULL,

    CONSTRAINT vehicle_parameters_pk PRIMARY KEY (id)
);

-- Table: parameter_config
CREATE TABLE IF NOT EXISTS parameter_config (
    id serial NOT NULL,

    CONSTRAINT parameter_config_pk PRIMARY KEY (id)
);

-- foreign keys
-- Reference: trip_members_trip_names(table: trip_members)
ALTER TABLE trip_members ADD CONSTRAINT 
    FOREIGN KEY (trip_id)
    REFERENCES trip_names (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: trip_members_ivsg_members (table: trip_members)
ALTER TABLE trip_members ADD CONSTRAINT 
    FOREIGN KEY (member_id)
    REFERENCES ivsg_members (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: trip_base_stations_base_station (table: trip_base_stations)
ALTER TABLE trip_base_stations ADD CONSTRAINT 
    FOREIGN KEY (base_station_id)
    REFERENCES base_station_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: trip_base_stations_trip_names (table: trip_base_stations)
ALTER TABLE trip_base_stations ADD CONSTRAINT 
    FOREIGN KEY (trip_id)
    REFERENCES trip_names (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;
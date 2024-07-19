/*
DROP TABLE IF EXISTS ivsg_members;
DROP TABLE IF EXISTS base_station_parameters;
DROP TABLE IF EXISTS trip_names;
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
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT ivsg_members_pk PRIMARY KEY (id),
    CONSTRAINT ivsg_member_name_unique UNIQUE (first_name, last_name)
); 

-- Table: base_station_parameters
CREATE TABLE IF NOT EXISTS base_station_parameters (
    id serial NOT NULL,
    base_station_name varchar(20) NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    altitude real NOT NULL,
    latitude_std_dev real NOT NULL,
    longitude_std_dev real NOT NULL,
    altitude_std_dev real NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT base_station_parameters_pk PRIMARY KEY (id),
    CONSTRAINT base_station_name_unique UNIQUE (base_station_name)
);

-- Table: trip_name
CREATE TABLE IF NOT EXISTS trip_names (
    id serial NOT NULL,
    trip_name varchar(50) NOT NULL,
    trip_date date NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT trip_names_pk PRIMARY KEY (id),
    CONSTRAINT trip_name_unique UNIQUE (trip_name)
);

-- Table: trip_members
CREATE TABLE IF NOT EXISTS trip_members (
    id serial NOT NULL,
    trip_id int NOT NULL,
    member_id int NOT NULL,
    drove boolean NOT NULL,
    CONSTRAINT trip_members_pk PRIMARY KEY (id),
    CONSTRAINT trip_members_unique UNIQUE (trip_id, member_id, drove)
);

-- Table: trip_base_stations
CREATE TABLE IF NOT EXISTS trip_base_stations (
    id serial NOT NULL,
    trip_id int NOT NULL,
    base_station_id int NOT NULL,
    was_pre_trip boolean NOT NULL,
    CONSTRAINT trip_base_stations_pk PRIMARY KEY (id),
    CONSTRAINT trip_base_stations_unique UNIQUE (trip_id, base_station_id, was_pre_trip)
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
    weather_notes varchar (50) NULL,
    CONSTRAINT conditions_pk PRIMARY KEY (id),
    CONSTRAINT conditions_unique UNIQUE (time_of_day, weather_condition)
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
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT bag_files_pk PRIMARY KEY (id),
    CONSTRAINT bag_file_name_trip_unique UNIQUE (bag_file_name, trip_id)
);

-- Table: pre_trip_details
CREATE TABLE IF NOT EXISTS pre_trip_details (
    id serial NOT NULL,
    trip_name_id int NOT NULL,
    trip_members_id int NOT NULL,
    parameter_config_id int NOT NULL,
    base_stations_planned_id int NOT NULL,
    pre_trip_starting_conditions_id int NOT NULL,
    pre_trip_notes text NULL,
    trip_date date NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT pre_trip_details_pk PRIMARY KEY (id),
    CONSTRAINT pre_trip_name_id_unique UNIQUE (trip_name_id)
);

-- Table: post_trip_details
CREATE TABLE IF NOT EXISTS post_trip_details (
    id serial NOT NULL,
    trip_name_id int NOT NULL,
    base_stations_visited_id int NOT NULL,
    trip_actual_conditions_id int NOT NULL,
    num_of_bag_files int NOT NULL,
    post_trip_notes text NULL,
    trip_start_time timestamp NOT NULL,
    trip_end_time timestamp NOT NULL,
    --trip_date date NOT NULL DEFAULT GETDATE(),
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT post_trip_details_pk PRIMARY KEY (id),
    CONSTRAINT post_trip_name_id_unique UNIQUE (trip_name_id)
);

-- Table: purchasing_parameters
CREATE TABLE IF NOT EXISTS purchasing_parameters (
    id serial NOT NULL,
    product_name varchar(50) NOT NULL,
    make varchar(50) NOT NULL,
    model varchar(50) NOT NULL,
    product_year int NOT NULL,
    vendor varchar(50) NOT NULL,
    purchase_date date NOT NULL,
    serial_number varchar(50) NOT NULL,
    penn_state_property_tag_number varchar(10) NULL,
    CONSTRAINT purchasing_parameters_pk PRIMARY KEY (id),
    CONSTRAINT serial_number_unique UNIQUE (serial_number),
    CONSTRAINT property_tag_number_unique UNIQUE (penn_state_property_tag_number)
);

-- Table: installation_parameters
CREATE TABLE IF NOT EXISTS installation_parameters (
    id serial NOT NULL,
    installation_date date NOT NULL,
    mapping_van_location varchar(50) NOT NULL,
    orientation varchar(50) NOT NULL,
    calibration varchar(50) NOT NULL,
    installation_notes text NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT installation_parameters_pk PRIMARY KEY (id)
);

-- Table: camera_parameters
CREATE TABLE IF NOT EXISTS camera_parameters (
    id serial NOT NULL,
    purchasing_parameters_id int NOT NULL,
    installation_parameters_id int NOT NULL,
    focal_x real NOT NULL,
    focal_y real NOT NULL,
    center_x real NOT NULL,
    center_y real NOT NULL,
    skew real NOT NULL,
    image_width int NOT NULL,
    image_height int NOT NULL,
    distortion_k1 real NOT NULL,
    distortion_k2 real NOT NULL,
    distortion_k3 real NOT NULL,
    distortion_p1 real NOT NULL,
    distortion_p2 real NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT camera_parameters_pk PRIMARY KEY (id),
    CONSTRAINT camera_parameters_unique UNIQUE (purchasing_parameters_id,
    installation_parameters_id, focal_x, focal_y, center_x, center_y, skew,
    image_width, image_height, distortion_k1, distortion_k2, distortion_k3,
    distortion_p1, distortion_p2)
);

-- Table: code_parameters
CREATE TABLE IF NOT EXISTS code_parameters (
    id serial NOT NULL,
    purchasing_parameters_id int NOT NULL,
    installation_parameters_id int NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT code_parameters_pk PRIMARY KEY (id),
    CONSTRAINT code_parameters_unique UNIQUE (purchasing_parameters_id, installation_parameters_id)
    -- ^ may change later
);

-- Table: encoder_parameters
CREATE TABLE IF NOT EXISTS encoder_parameters (
    id serial NOT NULL,
    purchasing_parameters_id int NOT NULL,
    installation_parameters_id int NOT NULL,
    counts_per_revolution int NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT encoder_parameters_pk PRIMARY KEY (id),
    CONSTRAINT encoder_parameters_unique UNIQUE (purchasing_parameters_id, installation_parameters_id, counts_per_revolution)
);

-- Table: gps_parameters
CREATE TABLE IF NOT EXISTS gps_parameters (
    id serial NOT NULL,
    purchasing_parameters_id int NOT NULL,
    installation_parameters_id int NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT gps_parameters_pk PRIMARY KEY (id),
    CONSTRAINT gps_parameters_unique UNIQUE (purchasing_parameters_id, installation_parameters_id)
    -- ^ may change later
);

-- Table: imu_parameters
CREATE TABLE IF NOT EXISTS imu_parameters (
    id serial NOT NULL,
    purchasing_parameters_id int NOT NULL,
    installation_parameters_id int NOT NULL,
    accel_scale varchar(128) NOT NULL,
    gyro_scale float NOT NULL,
    mag_scale float NOT NULL,
    bar_scale float NOT NULL,
    temp_scale float NOT NULL,
    gravity float NOT NULL,
    accel_cov float NOT NULL,
    gyro_cov float NOT NULL,
    mag_cov float NOT NULL,
    bar_cov float NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT imu_parameters_pk PRIMARY KEY (id),
    CONSTRAINT imu_parameters_unique UNIQUE (purchasing_parameters_id,
    installation_parameters_id, accel_scale, gyro_scale, mag_scale, bar_scale,
    temp_scale, gravity, accel_cov, gyro_cov, mag_cov, bar_cov)
);

-- Table: lidar_parameters
CREATE TABLE IF NOT EXISTS lidar_parameters (
    id serial NOT NULL,
    purchasing_parameters_id int NOT NULL,
    installation_parameters_id int NOT NULL,
    angle_min real NOT NULL,
    angle_max real NOT NULL,
    angle_increment real NOT NULL,
    time_increment real NOT NULL,
    range_min real NOT NULL,
    range_max real NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT lidar_parameters_pk PRIMARY KEY (id),
    CONSTRAINT lidar_parameters_unique UNIQUE (purchasing_parameters_id,
    installation_parameters_id, angle_min, angle_max, angle_increment,
    time_increment, range_min, range_max)
);

-- Table: trigger_parameters
CREATE TABLE IF NOT EXISTS trigger_parameters (
    id serial NOT NULL,
    purchasing_parameters_id int NOT NULL,
    installation_parameters_id int NOT NULL,
    trigger_frequency_1 int NOT NULL,
    trigger_frequency_2 int NOT NULL,
    trigger_frequency_3 int NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT trigger_parameters_pk PRIMARY KEY (id),
    CONSTRAINT trigger_parameters_unique UNIQUE (purchasing_parameters_id,
    installation_parameters_id, trigger_frequency_1, trigger_frequency_2, trigger_frequency_3)
);

-- Table: system_parameters
CREATE TABLE IF NOT EXISTS system_parameters (
    id serial NOT NULL,
    purchasing_parameters_id int NOT NULL,
    installation_parameters_id int NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT system_parameters_pk PRIMARY KEY (id),
    CONSTRAINT system_parameters_unique UNIQUE (purchasing_parameters_id, installation_parameters_id)
    -- ^ may change later
);

-- Table: vehicle_parameters
CREATE TABLE IF NOT EXISTS vehicle_parameters (
    id serial NOT NULL,
    purchasing_parameters_id int NOT NULL,
    installation_parameters_id int NOT NULL,
    make varchar(50) NOT NULL,
    model varchar(50) NOT NULL,
    vehicle_year int NOT NULL,
    service_iteration_id int NOT NULL,
    --date_added_to_db date NOT NULL DEFAULT GETDATE(),
    CONSTRAINT vehicle_parameters_pk PRIMARY KEY (id),
    CONSTRAINT service_iteration_id_unique UNIQUE (service_iteration_id),
    CONSTRAINT vehicle_parameters_unique UNIQUE (purchasing_parameters_id,
    installation_parameters_id, make, model, vehicle_year, service_iteration_id)
);

-- Table: parameter_config
CREATE TABLE IF NOT EXISTS parameter_config (
    id serial NOT NULL,
    camera_parameters_id int NOT NULL,
    code_parameters_id int NOT NULL,
    encoder_parameters_id int NOT NULL,
    gps_parameters_id int NOT NULL,
    imu_parameters_id int NOT NULL,
    lidar_parameters_id int NOT NULL,
    trigger_parameters_id int NOT NULL,
    system_parameters_id int NOT NULL,
    vehicle_parameters_id int NOT NULL,
    CONSTRAINT parameter_config_pk PRIMARY KEY (id),
    CONSTRAINT parameter_config_unique UNIQUE (camera_parameters_id,
    code_parameters_id, encoder_parameters_id, gps_parameters_id, imu_parameters_id,
    lidar_parameters_id, trigger_parameters_id, system_parameters_id, vehicle_parameters_id)
);



-- foreign keys
/*
trip_members table:
*/
-- Reference: trip_members_trip_names(table: trip_members)
ALTER TABLE trip_members ADD
    FOREIGN KEY (trip_id)
    REFERENCES trip_names (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: trip_members_ivsg_members (table: trip_members)
ALTER TABLE trip_members ADD
    FOREIGN KEY (member_id)
    REFERENCES ivsg_members (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
trip_base_stations table:
*/
-- Reference: trip_base_stations_base_station (table: trip_base_stations)
ALTER TABLE trip_base_stations ADD
    FOREIGN KEY (base_station_id)
    REFERENCES base_station_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: trip_base_stations_trip_names (table: trip_base_stations)
ALTER TABLE trip_base_stations ADD
    FOREIGN KEY (trip_id)
    REFERENCES trip_names (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
camera_parameters table:
*/
-- Reference: camera_parameters_purchasing_parameters (table: camera_parameters)
ALTER TABLE camera_parameters ADD
    FOREIGN KEY (purchasing_parameters_id)
    REFERENCES purchasing_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: camera_parameters_installation_parameters (table: camera_parameters)
ALTER TABLE camera_parameters ADD
    FOREIGN KEY (installation_parameters_id)
    REFERENCES installation_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
code_parameters table:
*/
-- Reference: code_parameters_purchasing_parameters (table: code_parameters)
ALTER TABLE _parameters ADD
    FOREIGN KEY (purchasing_parameters_id)
    REFERENCES purchasing_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: code_parameters_installation_parameters (table: code_parameters)
ALTER TABLE code_parameters ADD
    FOREIGN KEY (installation_parameters_id)
    REFERENCES installation_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
encoder_parameters table:
*/
-- Reference: encoder_parameters_purchasing_parameters (table: encoder_parameters)
ALTER TABLE encoder_parameters ADD
    FOREIGN KEY (purchasing_parameters_id)
    REFERENCES purchasing_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: encoder_parameters_installation_parameters (table: encoder_parameters)
ALTER TABLE encoder_parameters ADD
    FOREIGN KEY (installation_parameters_id)
    REFERENCES installation_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
gps_parameters table:
*/
-- Reference: gps_parameters_purchasing_parameters (table: gps_parameters)
ALTER TABLE gps_parameters ADD
    FOREIGN KEY (purchasing_parameters_id)
    REFERENCES purchasing_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: gps_parameters_installation_parameters (table: gps_parameters)
ALTER TABLE gps_parameters ADD
    FOREIGN KEY (installation_parameters_id)
    REFERENCES installation_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
imu_parameters table:
*/
-- Reference: imu_parameters_purchasing_parameters (table: imu_parameters)
ALTER TABLE imu_parameters ADD
    FOREIGN KEY (purchasing_parameters_id)
    REFERENCES purchasing_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: imu_parameters_installation_parameters (table: imu_parameters)
ALTER TABLE imu_parameters ADD
    FOREIGN KEY (installation_parameters_id)
    REFERENCES installation_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
lidar_parameters table:
*/
-- Reference: lidar_parameters_purchasing_parameters (table: lidar_parameters)
ALTER TABLE lidar_parameters ADD
    FOREIGN KEY (purchasing_parameters_id)
    REFERENCES purchasing_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: lidar_parameters_installation_parameters (table: lidar_parameters)
ALTER TABLE lidar_parameters ADD
    FOREIGN KEY (installation_parameters_id)
    REFERENCES installation_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
trigger_parameters table:
*/
-- Reference: trigger_parameters_purchasing_parameters (table: trigger_parameters)
ALTER TABLE trigger_parameters ADD
    FOREIGN KEY (purchasing_parameters_id)
    REFERENCES purchasing_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: trigger_parameters_installation_parameters (table: trigger_parameters)
ALTER TABLE trigger_parameters ADD
    FOREIGN KEY (installation_parameters_id)
    REFERENCES installation_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
system_parameters table:
*/
-- Reference: system_parameters_purchasing_parameters (table: system_parameters)
ALTER TABLE system_parameters ADD
    FOREIGN KEY (purchasing_parameters_id)
    REFERENCES purchasing_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: system_parameters_installation_parameters (table: system_parameters)
ALTER TABLE system_parameters ADD
    FOREIGN KEY (installation_parameters_id)
    REFERENCES installation_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
vehicle_parameters table:
*/
-- Reference: vehicle_parameters_purchasing_parameters (table: vehicle_parameters)
ALTER TABLE vehicle_parameters ADD
    FOREIGN KEY (purchasing_parameters_id)
    REFERENCES purchasing_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: vehicle_parameters_installation_parameters (table: vehicle_parameters)
ALTER TABLE vehicle_parameters ADD
    FOREIGN KEY (installation_parameters_id)
    REFERENCES installation_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
parameter_config table:
*/
-- Reference: parameter_config_camera_parameters (table: parameter_config)
ALTER TABLE parameter_config ADD
    FOREIGN KEY (camera_parameters_id)
    REFERENCES camera_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: parameter_config_code_parameters (table: parameter_config)
ALTER TABLE parameter_config ADD
    FOREIGN KEY (code_parameters_id)
    REFERENCES code_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: parameter_config_encoder_parameters (table: parameter_config)
ALTER TABLE parameter_config ADD
    FOREIGN KEY (encoder_parameters_id)
    REFERENCES encoder_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: parameter_config_gps_parameters (table: parameter_config)
ALTER TABLE parameter_config ADD
    FOREIGN KEY (gps_parameters_id)
    REFERENCES gps_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: parameter_config_imu_parameters (table: parameter_config)
ALTER TABLE parameter_config ADD
    FOREIGN KEY (imu_parameters_id)
    REFERENCES imu_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: parameter_config_lidar_parameters (table: parameter_config)
ALTER TABLE parameter_config ADD
    FOREIGN KEY (lidar_parameters_id)
    REFERENCES lidar_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: parameter_config_trigger_parameters (table: parameter_config)
ALTER TABLE parameter_config ADD
    FOREIGN KEY (trigger_parameters_id)
    REFERENCES trigger_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: parameter_config_system_parameters (table: parameter_config)
ALTER TABLE parameter_config ADD
    FOREIGN KEY (system_parameters_id)
    REFERENCES system_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: parameter_config_vehicle_parameters (table: parameter_config)
ALTER TABLE parameter_config ADD
    FOREIGN KEY (vehicle_parameters_id)
    REFERENCES vehicle_parameters (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
pre_trip_details table:
*/
-- Reference: pre_trip_details_trip_names (table: pre_trip_details)
ALTER TABLE pre_trip_details ADD
    FOREIGN KEY (trip_name_id)
    REFERENCES trip_names (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: pre_trip_details_trip_members (table: pre_trip_details)
ALTER TABLE pre_trip_details ADD
    FOREIGN KEY (trip_members_id)
    REFERENCES trip_members (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: pre_trip_details_parameter_config (table: pre_trip_details)
ALTER TABLE pre_trip_details ADD
    FOREIGN KEY (parameter_config_id)
    REFERENCES parameter_config (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: pre_trip_details_trip_base_stations (table: pre_trip_details)
ALTER TABLE pre_trip_details ADD
    FOREIGN KEY (base_stations_planned_id)
    REFERENCES trip_base_stations (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: pre_trip_details_conditions (table: pre_trip_details)
ALTER TABLE pre_trip_details ADD
    FOREIGN KEY (pre_trip_starting_conditions_id)
    REFERENCES conditions (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

/*
post_trip_details table:
*/
-- Reference: post_trip_details_trip_names (table: post_trip_details)
ALTER TABLE post_trip_details ADD
    FOREIGN KEY (trip_name_id)
    REFERENCES trip_names (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: post_trip_details_trip_base_stations (table: post_trip_details)
ALTER TABLE post_trip_details ADD
    FOREIGN KEY (base_stations_visited_id)
    REFERENCES trip_base_stations (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: post_trip_details_conditions (table: post_trip_details)
ALTER TABLE post_trip_details ADD
    FOREIGN KEY (trip_actual_conditions_id)
    REFERENCES conditions (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

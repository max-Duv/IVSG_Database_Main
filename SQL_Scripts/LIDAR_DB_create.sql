-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2024-07-09 19:38:55.525

/*
DROP TABLE IF EXISTS Vehicle;
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS base_stations;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS bag_files;
DROP TABLE IF EXISTS lidar2d;
DROP TABLE IF EXISTS lidar3d;
DROP TABLE IF EXISTS laser_parameters;
DROP TABLE IF EXISTS spatial_ref_sys;
*/

CREATE EXTENSION postgis;
-- CREATE EXTENSION pointcloud;
-- CREATE EXTENSION pointcloud_postgis;


-- tables
-- Table: Vehicle
CREATE TABLE Vehicle (
    id serial  NOT NULL,
    name text  NULL,
    CONSTRAINT Vehicle_pk PRIMARY KEY (id)
);

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
    scan_time real  NULL,
    ranges text  NULL,
    intensities text  NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geography GEOGRAPHY(POINT,4326)  NULL,
    roll real  NULL,
    pitch real  NULL,
    yaw real  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT lidar2d_pk PRIMARY KEY (id)
);

CREATE INDEX laser_geography_index on lidar2d  USING GIST (geography );

CREATE UNIQUE INDEX laser_index on lidar2d (sensors_id, seconds ,nanoseconds);

-- Table: lidar3d
CREATE TABLE lidar3d (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    velodyne_hashtag int  NOT NULL,
    seq int  NOT NULL,
    timestamp timestamp  NOT NULL,
    seconds bigint  NOT NULL,
    nanonseconds bigint  NOT NULL,
    time real  NOT NULL,
    file_name varchar(255)  NOT NULL,
    date_added timestamp  NOT NULL,
    CONSTRAINT lidar3d_pk PRIMARY KEY (id)
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

-- Reference: trips_base_stations (table: trips)
ALTER TABLE trips ADD CONSTRAINT trips_base_stations
    FOREIGN KEY (base_stations_id)
    REFERENCES base_stations (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- End of file.


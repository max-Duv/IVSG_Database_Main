-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2024-07-09 19:48:01.328

/*
DROP TABLE IF EXISTS Vehicle;
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS base_stations;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS bag_files;
DROP TABLE IF EXISTS camera;
DROP TABLE IF EXISTS camera_parameters;
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

-- Table: camera
CREATE TABLE camera (
    id serial  NOT NULL,
    bag_files_id int  NOT NULL,
    sensors_id int  NOT NULL,
    camera_hashtag int  NOT NULL,
    file_name varchar(32)  NULL,
    latitude real  NULL,
    longitude real  NULL,
    altitude real  NULL,
    geography GEOGRAPHY(point,4326)  NULL,
    roll real  NULL,
    pitch real  NULL,
    yaw real  NULL,
    seconds bigint  NULL,
    nanoseconds bigint  NULL,
    seconds_triggered bigint  NULL,
    nanoseconds_triggered bigint  NULL,
    time real  NULL,
    timestamp timestamp  NULL,
    date_added timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT camera_pk PRIMARY KEY (id)
);

CREATE INDEX camera_geography_index on camera (geography ASC);

CREATE UNIQUE INDEX camera_index on camera (sensors_id ASC,file_name ASC);

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

-- Reference: trips_base_stations (table: trips)
ALTER TABLE trips ADD CONSTRAINT trips_base_stations
    FOREIGN KEY (base_stations_id)
    REFERENCES base_stations (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- End of file.


CREATE EXTENSION postgis;
-- CREATE EXTENSION pointcloud;
-- CREATE EXTENSION pointcloud_postgis;


-- tables
-- Table: vehicle
CREATE TABLE vehicle (
    id serial  NOT NULL,
    name text  NULL,
    CONSTRAINT Vehicle_pk PRIMARY KEY (id)
);

-- Table: base_stations
CREATE TABLE base_stations (
    id int  NOT NULL,
    name varchar(20)  NOT NULL,
    latitude real  NOT NULL,
    longitude real  NOT NULL,
    altitutde real  NOT NULL,
    latitude_std real  NOT NULL,
    longitude_std real  NOT NULL,
    altitude_std real  NOT NULL,
    timestamp timestamp  NOT NULL,
    date_added timestamp  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT base_stations_pk PRIMARY KEY (id)
);

CREATE INDEX base_stations_index on base_stations (latitude ASC, longitude ASC, altitutde ASC);

-- Table: trips
CREATE TABLE trips (
    id serial  NOT NULL,
    name varchar(100)  NOT NULL,
    base_stations_id int  NOT NULL,
    date date  NOT NULL,
    description varchar(200)  NOT NULL,
    driver varchar(50)  NOT NULL,
    passengers varchar(50)  NOT NULL,
    notes text  NOT NULL,
    date_added timestamp  NOT NULL,
    CONSTRAINT trips_pk PRIMARY KEY (id)
);

-- Table: bag_files
CREATE TABLE bag_files (
    id serial  NOT NULL,
    Vehicle_id int  NOT NULL,
    trips_id int  NOT NULL,
    file_path varchar(100)  NOT NULL,
    name varchar(50)  NOT NULL,
    parsed boolean  NOT NULL,
    datetime timestamp  NOT NULL,
    datetime_end timestamp  NOT NULL,
    date_added timestamp  NOT NULL,
    CONSTRAINT bag_files_pk PRIMARY KEY (id)
);

CREATE UNIQUE INDEX bag_files_index on bag_files (name ASC);

-- Reference: bag_files_Vehicle (table: bag_files)
ALTER TABLE bag_files ADD CONSTRAINT bag_files_vehicle
    FOREIGN KEY (vehicle_id)
    REFERENCES vehicle (id)  
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

-- Reference: trips_base_stations (table: trips)
ALTER TABLE trips ADD CONSTRAINT trips_base_stations
    FOREIGN KEY (base_stations_id)
    REFERENCES base_stations (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;
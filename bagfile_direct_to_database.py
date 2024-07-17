'''
This code is the beginning of exploring pushing data directly from the mapping van to the database,
without needing a csv file.
    - Looking at the source code for the bagpy library, looking at the function to automatically write
      csv file and insteading changing the loop to write each row to the database (probably not efficient?)

Currently looking only at the parseTrigger data as it is much smaller - currently have 2 rows working.

If this were to be implemented for the entire database, each table would have to be looked over for variable and
nullability.

Question to answer: in the end will this be an efficient method? Benchmark and compare to other libraries (pandas and
polars - may have to look at the source code)
'''


import bagpy
from bagpy import bagreader
import pandas as pd
import seaborn as sea
import matplotlib.pyplot as plt
import numpy as np
import time
import traceback
import psycopg2

class Database:
    def __init__(self, db_name):
        try:
            self.conn = psycopg2.connect(database = db_name,
                                    user = 'postgres',
                                    password = 'pass',
                                    host = '127.0.0.1',
                                    port = '5432')
            print ("Database connected sucessfully.")

            self.cursor = self.conn.cursor()

        
        except psycopg2.Error as e:
            self.printErrors(error = e, message = "Unable to connect to the database.")
    
    def create_table(self):
        query = '''CREATE TABLE trigger (
                        id serial  NOT NULL,
                        bag_files_id int NULL,
                        sensors_id int NULL,
                        MODE_COUNTS int  NOT NULL,
                        ADJONE int  NOT NULL,
                        CONSTRAINT trigger_pk PRIMARY KEY (id)
                );'''
        
        self.cursor.execute(query)
        print("Table has been created new.")
        """
        query = '''CREATE TABLE trigger (
                        id serial  NOT NULL,
                        bag_files_id int NULL,
                        sensors_id int NULL,
                        MODE varchar(50)  NOT NULL,
                        MODE_COUNTS int  NOT NULL,
                        ADJONE int  NOT NULL,
                        ADJTWO int  NOT NULL,
                        adjthree int  NOT NULL,
                        err_failed_mode_count int  NOT NULL,
                        err_failed_XI_format int  NOT NULL,
                        err_failed_checkInformation int  NOT NULL,
                        err_trigger_unknown_error_occured int  NOT NULL,
                        err_bad_uppercase_character int  NOT NULL,
                        err_bad_lowercase_character int  NOT NULL,
                        err_bad_three_adj_element int  NOT NULL,
                        err_bad_first_element int  NOT NULL,
                        err_bad_character int  NOT NULL,
                        err_wrong_element_length int  NOT NULL,
                        seconds bigint  NOT NULL,
                        nanoseconds bigint  NOT NULL,
                        time real NULL,
                        timestamp timestamp  NULL,
                        date_added timestamp  NULL,
                        CONSTRAINT trigger_pk PRIMARY KEY (id)
                );'''
        """

    def delete_table(self):
        query = '''DROP TABLE IF EXISTS trigger'''
        self.cursor.execute(query)
        print("Table has been dropped.")

    def insert(self):
        #bag_file_name = 'test_parse.bag'           # Set bag file name
        bag_file_name = 'mapping_van_2024-06-20-15-25-21_0.bag'
        b = bagreader(bag_file_name)                # Set a variable 'b' to the bag file using bagreader library
        b.topic_table                              # Produce the table

        topic_lst = b.topic_table.Topics.unique()   # Create a list of the different topics
        
        tstart = None
        tend = None
        timelst = []

        count = 0

        try:
            #for topics in topic_lst:
            topics = topic_lst[14]
            for topics, msg, t, in b.reader.read_messages(topics=[topics], start_time = tstart, end_time = tend):
                count += 1
                timelst.append(t)

                self.cursor.execute("INSERT INTO trigger (mode_counts, adjone) VALUES({},{})".format(msg.mode_counts, msg.adjone))
                print("Inserted to database successfully!")
                
                """
                NEED TO CHANGE
                query_template = '''INSERT INTO trigger
                (SECONDS, NANOSECONDS, MODE, MODE_COUNTS,
                ADJONE, ADJTWO, ADJTHREE,
                ERR_FAILED_MODE_COUNT, ERR_FAILED_XI_FORMAT,
                ERR_FAILED_CHECKINFORMATION, ERR_TRIGGER_UNKNOWN_ERROR_OCCURED,
                ERR_BAD_UPPERCASE_CHARACTER, ERR_BAD_LOWERCASE_CHARACTER,
                ERR_BAD_THREE_ADJ_ELEMENT, ERR_BAD_FIRST_ELEMENT,
                ERR_BAD_CHARACTER, ERR_WRONG_ELEMENT_LENGTH
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        
                query_fillin = (str(db.unixTimeToTimeStamp(msg.header.stamp.secs)), 
                                str(msg.header.stamp.secs), str(msg.header.stamp.nsecs),
                                str(msg.mode), str(msg.mode_counts),
                                str(msg.adjone), str(msg.adjtwo), str(msg.adjthree),
                                str(msg.err_failed_mode_count), str(msg.err_failed_XI_format),
                                str(msg.err_failed_checkInformation), str(msg.err_trigger_unknown_error_occured),
                                str(msg.err_bad_uppercase_character), str(msg.err_bad_lowercase_character),
                                str(msg.err_bad_three_adj_element), str(msg.err_bad_first_element),
                                str(msg.err_bad_character), str(msg.err_wrong_element_length)
                                )
                """
        
        except:
            print("exception")
            self.conn.rollback()

        print(count)

        """
        query_template = '''INSERT INTO trigger
                (SECONDS, NANOSECONDS, MODE, MODE_COUNTS,
                ADJONE, ADJTWO, ADJTHREE,
                ERR_FAILED_MODE_COUNT, ERR_FAILED_XI_FORMAT,
                ERR_FAILED_CHECKINFORMATION, ERR_TRIGGER_UNKNOWN_ERROR_OCCURED,
                ERR_BAD_UPPERCASE_CHARACTER, ERR_BAD_LOWERCASE_CHARACTER,
                ERR_BAD_THREE_ADJ_ELEMENT, ERR_BAD_FIRST_ELEMENT, ERR_BAD_CHARACTER,
                ERR_WRONG_ELEMENT_LENGTH
                ) VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        
            query_fillin = ('Person', 'One', 'SR', '2.5')

            self.cursor.execute(query_template, query_fillin)
        """

    def bulk_insert(self):
        query = ''' '''
        self.cursor.execute(query)

    def disconnect(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()
        print("PostgreSQL connection is closed.")

    def printErrors(self, error, message = None):
        if message is not None:
            print(message)

        print(error)
        print(error.pgcode)
        print(error.pgerror)
        print(traceback.format_exc())

def main():
    start_time = time.time()

    reset_table = 0
    
    db_name = "testdb"
    if db_name is not None:
        db = Database(db_name = db_name)

    if (reset_table == 1):
        db.delete_table()


    '''Functions'''
    #db.create_table()
    #db.delete_table()
    db.insert()
    #db.bulk_insert()

    db.disconnect()

    end_time = time.time()
    total_time = end_time - start_time
    print("Total Time: ", total_time)

main()
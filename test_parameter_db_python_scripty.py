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
        query = '''CREATE TABLE IF NOT EXISTS table_1(
                    id serial NOT NULL,
        );'''

        self.cursor.execute(query)

    def delete_table(self):
        query = '''DROP TABLE IF EXISTS STUDENT'''
        self.cursor.execute(query)

    def insert(self):
        query_template = '''INSERT INTO <table-name>
            (FIRST_NAME, LAST_NAME, GRADE, GPA) VALUES
            (%s, %s, %s, %s)'''

        query_fillin1 = ('Person', 'One', 'SR', '2.5')

        #self.cursor.execute(query_template, query_fillin1)
        #self.cursor.execute(query_template, query_fillin2)
        #self.cursor.execute(query_template, query_fillin3)

    def insert_to_ivsg_members(self):
        query_template = '''INSERT INTO ivsg_members
            (first_name, last_name) VALUES
            (%s, %s)'''

        query_fillin1 = ('John', 'Doe')
        query_fillin2 = ('Jane', 'Doe')

        self.cursor.execute(query_template, query_fillin1)
        self.cursor.execute(query_template, query_fillin2)


    def insert_to_trip_names(self):
        query_template = '''INSERT INTO trip_names
            (trip_name) VALUES
            (%s)'''

        query_fillin1 = ('Trip 1')
        query_fillin2 = ('Trip 2')
        query_fillin3 = ('Trip 3')

        self.cursor.execute(query_template, query_fillin1)
        self.cursor.execute(query_template, query_fillin2)
        self.cursor.execute(query_template, query_fillin3)


    def insert_to_base_station_parameters(self):
        query_template = '''INSERT INTO base_station_parameters
            (base_station_name) VALUES
            (%s)'''

        query_fillin1 = ('LTI')
        query_fillin2 = ('Test Track')
        query_fillin3 = ('Reber')

        self.cursor.execute(query_template, query_fillin1)
        self.cursor.execute(query_template, query_fillin2)
        self.cursor.execute(query_template, query_fillin3)


    def insert_to_trip_members(self):
        query_template = '''INSERT INTO trip_members
            (tripid, member_id, drove) VALUES
            (%d, %d, %s)'''
        # Note: the above may not work

        query_fillin1 = (1, 2, 'true') #check how boolean should be entered

        self.cursor.execute(query_template, query_fillin1)
        #self.cursor.execute(query_template, query_fillin2)
        #self.cursor.execute(query_template, query_fillin3)


    def insert_to_trip_base_stations(self):
        query_template = '''INSERT INTO trip_base_stations
            (trip_id, base_station_id, was_pre_trip, was_post_trip) VALUES
            (%d, %d, %s, %s)'''

        query_fillin1 = (2, 2, 'true', 'false')
        #add constraint where was_pre_trip must != was_post_trip

        self.cursor.execute(query_template, query_fillin1)
        #self.cursor.execute(query_template, query_fillin2)
        #self.cursor.execute(query_template, query_fillin3)


    def bulk_insert(self):
        query = ''' '''
        self.cursor.execute(query)

    def delete(self):
        query = '''DELETE FROM STUDENT WHERE STUDENT_ID = 3'''
        self.cursor.execute(query)

    def update(self):
        query = ''' '''
        self.cursor.execute(query)

    def merge(self):
        query = ''' '''
        self.cursor.execute(query)

    def select(self):
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

    '''db name may vary'''
    db_name = "testdb"
    if db_name is not None:
        db = Database(db_name = db_name)

    '''Functions'''
    #db.create_table()
    #db.delete_table()
    #db.insert()
    #db.bulk_insert()
    #db.delete()
    #db.update()
    #db.merge()
    #db.select()

    '''USE'''
    db.insert_to_ivsg_members()
    db.insert_to_trip_names()
    db.insert_to_base_station_parameters()
    db.insert_to_trip_members()
    db.insert_to_trip_base_stations()

    db.disconnect()

    end_time = time.time()
    total_time = end_time - start_time
    print("Total Time: ", total_time)

main()
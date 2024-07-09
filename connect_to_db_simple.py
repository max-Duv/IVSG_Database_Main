import time
import traceback
import psycopg2

class Database:
    def __init__(self, db_name):
        try:
            '''
            Simplified:
                self.conn = psycopg2.connect(database = <updated_mapping_van_raw_db>,
                                                user = '<user>',
                                                password = '<password>',
                                                host = '127.0.0.1',
                                                port = '5432')
                self.cursor = self.conn.cursor()

                query = ''
                self.cursor.execute(query)


                self.cursor.close()
                self.conn.commit()
                self.conn.close()
            '''

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
        query = '''CREATE TABLE IF NOT EXISTS STUDENT(
            STUDENT_ID SERIAL PRIMARY KEY,
            FIRST_NAME CHAR(20) NOT NULL,
            LAST_NAME CHAR(20),
            GRADE CHAR(2),
            GPA FLOAT
        )'''

        self.cursor.execute(query)

    def delete_table(self):
        query = '''DROP TABLE IF EXISTS STUDENT'''
        self.cursor.execute(query)

    def insert(self):
        query_template = '''INSERT INTO STUDENT
            (FIRST_NAME, LAST_NAME, GRADE, GPA) VALUES
            (%s, %s, %s, %s)'''

        query_fillin1 = ('Person', 'One', 'SR', '2.5')
        query_fillin2 = ('Bruce', 'Wayne', 'FR', '4.0')
        query_fillin3 = ('Clark', 'Kent', 'JR', '3.7')

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

    reset_table = 1

    db_name = "testdb"
    if db_name is not None:
        db = Database(db_name = db_name)

    if (reset_table == 1):
        db.delete_table()


    '''Functions'''
    #db.create_table()
    #db.delete_table()
    #db.insert()
    #db.bulk_insert()
    #db.delete()
    #db.update()
    #db.merge()
    #db.select()

    db.disconnect()

    end_time = time.time()
    total_time = end_time - start_time
    print("Total Time: ", total_time)

main()

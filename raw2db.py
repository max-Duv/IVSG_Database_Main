#!/usr/bin/env python


#Where is the numpy import?
import csv
import psycopg2
import traceback

class Database:

    def __init__(self, db_name):
        try:
            self.conn = psycopg2.connect(database=db_name)
            connection = psycopg2.connect(user='dbadmin',
                                          password='<PASSWORD>',
                                          host='localhost',
                                          port='5432')
        except psycopg2.Error as e:
            self.print_errors(e, "Unable to connect to the database")

    def select(self, table, fields, where=None, orderby=None, limit=None):
        query = "SELECT " + ", ".join(fields) + " FROM " + table
        if where: query += " WHERE " + " AND ".join(where)
        if orderby: query += " ORDER BY " + orderby
        if limit: query += " LIMIT " + str(limit)
        return self.execute_query(query)

    def insert(self, table, fields, values, upsert=False, conflict_on=None):
        query = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))})"
        if upsert:
            conflict_target = f"({', '.join(conflict_on or ['id'])})"
            query += f" ON CONFLICT {conflict_target} DO UPDATE SET "
            query += ", ".join([f"{field}=EXCLUDED.{field}" for field in fields])
        query += " RETURNING id;"
        return self.execute_query(query, values)

    def insert_csvfile(self, table, file_name):
        with open(file_name, 'r') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            query = f"COPY {table} ({', '.join(fields)}) FROM STDIN WITH CSV HEADER"
            cur = self.conn.cursor()
            cur.copy_expert(sql=query, file=f)
            self.conn.commit()

    def update(self, table, update_set, where=None, returning=None):
        query = f"UPDATE {table} SET {', '.join(update_set)}"
        if where: query += " WHERE " + " AND ".join(where)
        if returning: query += " RETURNING " + ", ".join(returning)
        return self.execute_query(query)

    def delete(self, table, using=None, where=None):
        query = f"DELETE FROM {table}"
        if using: query += " USING " + using
        if where: query += " WHERE " + " AND ".join(where)
        return self.execute_query(query)

    def execute_query(self, query, values=None):
        try:
            cur = self.conn.cursor()
            cur.execute(query, values) if values else cur.execute(query)
            self.conn.commit()
            if query.strip().startswith("SELECT"):
                return cur.fetchall(), True
            return cur.fetchone(), True
        except psycopg2.Error as e:
            self.print_errors(e, "Error executing query")
            return None, False

    def print_errors(self, error, message=None):
        if message: print(message)
        print(error, error.pgcode, error.pgerror, traceback.format_exc())

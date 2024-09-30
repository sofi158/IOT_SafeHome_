# data_acq.py - Database management for SafeHome project

import sqlite3
import pandas as pd
from init import *
from icecream import ic
from datetime import datetime

def time_format():
    return f'{datetime.now()}  DB|> '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False)

# Create a database connection
def create_connection(db_file=db_name):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        ic('Connected to database: ' + db_file)
        return conn
    except sqlite3.Error as e:
        ic(e)
    return conn

# Create a new table in the database
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        ic(e)

# Initialize the database with necessary tables
def init_db(database):
    tables = [
        """ CREATE TABLE IF NOT EXISTS data (
            name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            value TEXT NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS iot_devices (
            sys_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            status TEXT,
            units TEXT,
            last_updated TEXT NOT NULL,
            update_interval INTEGER NOT NULL,
            placed TEXT,
            dev_type TEXT NOT NULL,
            enabled INTEGER,    
            state TEXT,
            mode TEXT,
            fan TEXT,
            temperature REAL,
            dev_pub_topic TEXT NOT NULL,
            dev_sub_topic TEXT NOT NULL,
            special TEXT
        );"""
    ]
    conn = create_connection(database)
    if conn is not None:
        for table in tables:
            create_table(conn, table)
        conn.close()
    else:
        ic("Error! Cannot create the database connection.")

# Insert data into a table
def add_IOT_data(name, updated, value):
    sql = ''' INSERT INTO data(name, timestamp, value)
              VALUES(?,?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [name, updated, value])
        conn.commit()
        conn.close()
    else:
        ic("Error! Cannot create the database connection.")

# Fetch data from a table
def read_IOT_data(table, name):
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + table + " WHERE name=?", (name,))
        rows = cur.fetchall()
        return rows
    else:
        ic("Error! Cannot create the database connection.")

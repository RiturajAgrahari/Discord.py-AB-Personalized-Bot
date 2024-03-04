import discord
import os
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Query:
    def __init__(self):
        self.database = os.getenv("MY_SQL_DATABASE")
        self.host = os.getenv("MY_SQL_HOST")
        self.user = os.getenv("MY_SQL_USER")
        self.password = os.getenv("MY_SQL_PASSWORD")

        mydb = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

        self.mydb = mydb
        self.mydb.close()

    def __str__(self):
        representation = 'queries...'
        return representation

    # Need to add multiple columns and conditions!
    async def select_query(self, column:str, table:str, condition_column:str=None, condition_value:str | int=None,
                           order_by_column:str=None, ascending:bool=True, limit:int=None, offset:int=0):
        sql = f"SELECT {column} FROM {table}"

        if condition_column is None or condition_value is None:
            pass
        else:
            if type(condition_value) is str:
                sql += f" WHERE {condition_column} = '{condition_value}'"
            else:
                sql += f" WHERE {condition_column} = {condition_value}"

        if order_by_column is None:
            pass
        else:
            sql += f" ORDER BY {order_by_column}"

        if not ascending:
            sql += " DESC"

        if limit:
            sql += f" LIMIT {offset}, {limit}"

        self.mydb.connect()
        mycursor = self.mydb.cursor()
        mycursor.execute(sql)
        output = mycursor.fetchall()
        self.mydb.close()
        return output


    async def add_test(self, title, description, image, post_type, send_time):
        clock_time = str(send_time[0]).split(':')
        custom_datetime = datetime(int(send_time[3]), int(send_time[2]), int(send_time[1]), int(clock_time[0]), int(clock_time[1]), 0)

        self.mydb.connect()
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO personalized_test (title, description, image, type, time) VALUES (%s, %s, %s, %s, %s)"
        val = [(title, description, image, post_type, custom_datetime)]
        mycursor.executemany(sql, val)
        self.mydb.commit()
        self.mydb.close()
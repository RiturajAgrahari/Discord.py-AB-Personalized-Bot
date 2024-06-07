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
            database=self.database,
            auth_plugin='mysql_native_password'
        )

        self.mydb = mydb
        self.mydb.close()

    def __str__(self):
        representation = 'queries...'
        return representation

    # Need to add multiple columns and conditions!
    async def select_query(self, column:str, table:str, condition_column:str=None, condition_value:str | int=None,
                           conditional_operation:str='=', order_by_column:str=None, ascending:bool=True, limit:int=None,
                           offset:int=0):
        sql = f"SELECT {column} FROM {table}"

        if condition_column is None or condition_value is None:
            pass
        else:
            if type(condition_value) is str:
                sql += f" WHERE {condition_column} {conditional_operation} '{condition_value}'"
            else:
                sql += f" WHERE {condition_column} {conditional_operation} {condition_value}"

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
        sql="INSERT INTO personalized_test_question (title, description, image, type, time) VALUES (%s, %s, %s, %s, %s)"
        val = [(title, description, image, post_type, custom_datetime)]
        mycursor.executemany(sql, val)
        self.mydb.commit()
        self.mydb.close()

    async def add_answer(self, interaction, question_id, answer):
        try:
            current_time_utc = datetime.utcnow().replace(second=0, microsecond=0)
        except Exception:
            current_time_utc = datetime.now(datetime.UTC).replace(second=0, microsecond=0)

        uid = await self.check_profile(interaction)

        self.mydb.connect()
        mycursor = self.mydb.cursor()
        sql="INSERT INTO personalized_test_answer (user_id, question_id, answers, time) VALUES (%s, %s, %s, %s)"
        val = [(int(uid), int(question_id), str(answer), str(current_time_utc))]
        mycursor.executemany(sql, val)
        self.mydb.commit()
        self.mydb.close()

    async def check_profile(self, interaction):
        self.mydb.connect()
        mycursor = self.mydb.cursor()
        sql = f'select uid from profile where discord_id = "{interaction.user.mention}"'
        mycursor.execute(sql)
        output = mycursor.fetchall()
        self.mydb.commit()
        self.mydb.close()

        if len(output) == 0:
            print(f'creating {interaction.user.name} profile...')
            return await self.creating_main_profile(interaction)
        else:
            return output[0][0]

    async def creating_main_profile(self, interaction):
        self.mydb.connect()
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO profile (name, discord_id) VALUES (%s, %s)"
        val = [(interaction.user.name, interaction.user.mention)]
        mycursor.executemany(sql, val)
        self.mydb.commit()
        self.mydb.close()
        uid = await self.check_profile(interaction)
        return uid

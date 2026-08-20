import psycopg2
from psycopg2.extensions import cursor
from dotenv import load_dotenv
import os
from typing import Annotated
from fastapi import Depends
from server.models.pydantic import FeedbackInput

load_dotenv()
POSTGRES_SQL_KEY = os.environ["POSTGRES_SQL_KEY"]

def connect():
    """ Connect to a local PostgresSQL database, yield the cursor object and perform cleaning

    Yields:
        cursor: object that allows us to perform SQL queries within the database
    """
    conn = psycopg2.connect(
        database="mydb",
        host="localhost",
        user="postgres",
        password=POSTGRES_SQL_KEY,
        port="5432" 
    )
    cur = conn.cursor()        # Open a cursor to execute commands

    try:
        yield cur
    finally:
        conn.commit()          # Make the changes in the db persistent
        cur.close()            # Close the cursor
        conn.close()           # Close the communication with the db

async def add_feedback(cursor : Annotated[cursor, Depends(connect)], input : FeedbackInput):
    """
        Add a new entry to the feedback table (and create the table if missing)

        Args:
            cursor (cursor) : cursor object needed to perform SQL queries
            input (FeedbackInput) : pydantic model containing the data to add to the table (feedback, type
            of interview, unique id and messages during the interview)
    """
    # Find the "feedback" table
    cursor.execute(""" SELECT EXISTS(
            SELECT * FROM information_schema.tables
            WHERE table_name='feedbackTable')
            """)

    # Create a new table if non existing
    if cursor.fetchone()[0] is None:
        cursor.execute("""CREATE TABLE feedbackTable(
                user_id SERIAL PRIMARY KEY,
                messages VARCHAR NOT NULL,
                feedback VARCHAR NOT NULL,
                interview_type INT NOT NULL);
                """)

    # Add a new row to the table
    cursor.execute(f"""INSERT INTO feedbackTable VALUES(
            {input.id},
            {input.messages},
            {input.feedback},
            {input.interview_type})""")


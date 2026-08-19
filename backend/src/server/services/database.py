import psycopg2
from psycopg2.extensions import cursor
from dotenv import load_dotenv
import os
from typing import Annotated
from fastapi import Depends
from server.models.pydantic import FeedbackInput

load_dotenv()
POSTGRE_SQL_KEY = os.environ["POSTGRE_SQL_KEY"]

def connect():
    conn = psycopg2.connect(
        database="mydb",
        host="localhost",
        user="postgres",
        password=POSTGRE_SQL_KEY,
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


# database.py
import mysql.connector

from config import DB_CONFIG

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the user_activity table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            user_id INT,
            activity_type VARCHAR(255),
            activity_data TEXT,
            timestamp VARCHAR(255)
        )
    """)

    # Create the job_postings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            job_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            title VARCHAR(255),
            required_skills TEXT,
            timestamp VARCHAR(255)
        )
    """)
    conn.commit()
    conn.close()
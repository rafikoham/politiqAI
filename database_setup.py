import psycopg2
from psycopg2 import sql

# Database connection parameters
DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_HOST = "localhost"
DB_PORT = "5432"

# SQL commands to create tables
CREATE_TABLES = [
    '''
    CREATE TABLE IF NOT EXISTS videos (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255),
        channel VARCHAR(255),
        upload_date DATE,
        duration INTEGER,
        url TEXT,
        participants TEXT[],  -- New column for participants

    );
    ''',
    '''
    CREATE TABLE IF NOT EXISTS transcriptions (
        id SERIAL PRIMARY KEY,
        video_id INTEGER REFERENCES videos(id),
        transcription TEXT
    );
    '''
]

def create_database():
    """Create database tables if they do not exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Create tables
        for command in CREATE_TABLES:
            cursor.execute(command)
            print("Table created successfully")

        # Close communication with the database
        cursor.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")

# Example usage
if __name__ == "__main__":
    create_database()

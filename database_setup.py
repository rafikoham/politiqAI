import json
import psycopg2

DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            channel VARCHAR(255),
            upload_date DATE,
            duration INTEGER,
            url TEXT,
            participants TEXT[]
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transcriptions (
            id SERIAL PRIMARY KEY,
            video_id INTEGER REFERENCES videos(id),
            transcription TEXT
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def insert_video_metadata(conn, video_metadata):
    try:
        with conn.cursor() as cursor:
            insert_query = '''
            INSERT INTO videos (title, channel, upload_date, duration, url, participants)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            '''
            cursor.execute(insert_query, (
                video_metadata['title'],
                video_metadata['uploader'],
                video_metadata['upload_date'],
                video_metadata['duration'],
                video_metadata['url'],
                video_metadata.get('participants', [])
            ))
            video_id = cursor.fetchone()[0]
            conn.commit()
            return video_id
    except Exception as e:
        print(f"Error inserting video metadata: {e}")
        conn.rollback()

def insert_transcription(conn, video_id, transcription_text):
    try:
        with conn.cursor() as cursor:
            insert_query = '''
            INSERT INTO transcriptions (video_id, transcription)
            VALUES (%s, %s);
            '''
            cursor.execute(insert_query, (video_id, transcription_text))
            conn.commit()
    except Exception as e:
        print(f"Error inserting transcription: {e}")
        conn.rollback()

def insert_metadata_from_json(json_file_path):
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            video_metadata = json.load(json_file)

        video_id = insert_video_metadata(conn, video_metadata)
        print(f"Inserted video with ID: {video_id}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
    json_file_path = 'path_to_metadata.json'
    insert_metadata_from_json(json_file_path)
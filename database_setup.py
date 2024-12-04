import json
import psycopg2
import os

from config import * 


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
            uploader VARCHAR(255),
            upload_date DATE,
            duration INTEGER,
            url TEXT,
            view_count INTEGER,
            like_count INTEGER, 
            comment_count INTEGER, 
            description TEXT
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

        with conn.cursor() as cursor:
            insert_query = '''
            INSERT INTO videos (title, uploader, upload_date, duration, url, view_count, like_count, comment_count, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (
                video_metadata['title'],
                video_metadata['uploader'],
                video_metadata['upload_date'],
                video_metadata['duration'],
                video_metadata['url'],
                video_metadata['view_count'],
                video_metadata['like_count'],
                video_metadata['comment_count'],
                video_metadata['description']
            ))
            conn.commit()
            print(f"Inserted video metadata from {json_file_path}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        conn.close()

def insert_all_metadata_from_directory(directory_path):
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    try:
        for filename in os.listdir(directory_path):
            if filename.endswith('.json'):
                json_file_path = os.path.join(directory_path, filename)
                with open(json_file_path, 'r', encoding='utf-8') as json_file:
                    video_metadata = json.load(json_file)

                with conn.cursor() as cursor:
                    insert_query = '''
                    INSERT INTO videos (title, uploader, upload_date, duration, url, view_count, like_count, comment_count, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    cursor.execute(insert_query, (
                        video_metadata['title'],
                        video_metadata['uploader'],
                        video_metadata['upload_date'],
                        video_metadata['duration'],
                        video_metadata['url'],
                        video_metadata['view_count'],
                        video_metadata['like_count'],
                        video_metadata['comment_count'],
                        video_metadata['description']
                    ))
                    conn.commit()
                    print(f"Inserted video metadata from {json_file_path}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    #create_database()
    directory_path = 'data/metadata'  
    insert_all_metadata_from_directory(directory_path)
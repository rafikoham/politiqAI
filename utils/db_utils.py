from sqlalchemy import create_engine, MetaData, Table, Column, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.connection_string = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
        self.engine = create_engine(self.connection_string)
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self._init_tables()

    def _init_tables(self):
        # Table for raw text data
        self.text_data = Table(
            'text_data', self.metadata,
            Column('id', String(50), primary_key=True),
            Column('source_file', String(255)),
            Column('content', Text),
            Column('processed_content', Text),
            Column('created_at', DateTime, default=datetime.utcnow),
            Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        )

        # Table for vector embeddings
        self.embeddings = Table(
            'embeddings', self.metadata,
            Column('id', String(50), primary_key=True),
            Column('text_id', String(50)),
            Column('vector_path', String(255)),
            Column('created_at', DateTime, default=datetime.utcnow)
        )

        # Create tables if they don't exist
        self.metadata.create_all(self.engine)

    def save_text_data(self, text_id, source_file, content, processed_content=None):
        session = self.Session()
        try:
            session.execute(
                self.text_data.insert().values(
                    id=text_id,
                    source_file=source_file,
                    content=content,
                    processed_content=processed_content
                )
            )
            session.commit()
        finally:
            session.close()

    def save_embedding(self, embedding_id, text_id, vector_path):
        session = self.Session()
        try:
            session.execute(
                self.embeddings.insert().values(
                    id=embedding_id,
                    text_id=text_id,
                    vector_path=vector_path
                )
            )
            session.commit()
        finally:
            session.close()

    def get_unprocessed_texts(self):
        session = self.Session()
        try:
            result = session.execute(
                self.text_data.select().where(self.text_data.c.processed_content.is_(None))
            )
            return result.fetchall()
        finally:
            session.close()

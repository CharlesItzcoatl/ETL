from sqlalchemy import Column, String, Integer
from base import Base

class Article(Base):
    __tablename__ = 'articles'

    # Se declara que las variables son columnas y el tipo de cada una,
    # La UID tiene el constraint PK.
    id = Column(String, primary_key = True)
    text = Column(String)
    host = Column(String)
    headline = Column(String)
    newspaper_uid = Column(String)
    text_tokens = Column(Integer)
    headline_tokens = Column(Integer)
    # La URL tiene el constraint unique.
    url = Column(String, unique = True)

    def __init__(self, uid, headline, text, url, newspaper_uid, host, headline_tokens, text_tokens):
        self.id = uid
        self.text = text
        self.host = host
        self.headline = headline
        self.newspaper_uid = newspaper_uid
        self.text_tokens = text_tokens
        self.headline_tokens = headline_tokens
        self.url = url

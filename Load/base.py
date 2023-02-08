from sqlalchemy import create_engine
# La clase declarative permite tener acceso a funcionalidades de ORM (Object Relational Mapper),
# que permite trabajar con objetos de Python en lugar de queries de SQL directamente.
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Indica que vamos a usar sqlite.
Engine = create_engine('sqlite:///newspaper.db')

Session = sessionmaker(bind = Engine)

Base = declarative_base()

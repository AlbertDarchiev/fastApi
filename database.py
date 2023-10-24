from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

URL_DATABASE = "postgresql://fl0user:Kj7obcqEh3LZ@ep-holy-breeze-83855958.eu-central-1.aws.neon.fl0.io:5432/database?sslmode=require"  # Actualiza con tus credenciales

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  

Base = declarative_base()

class UserBase(BaseModel):
    id: int
    username: str
    email: str
    password: str
    image: str
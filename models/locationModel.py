from sqlalchemy import Column, Integer, String, ForeignKey, Double, DateTime, ARRAY, Float
from datetime import datetime

from database import Base


class Location(Base):
    __tablename__ = "location"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    creation_date  = Column(String)
    country_id = Column(Integer, ForeignKey("country.id"))
    image_id = Column(Integer, ForeignKey("image.id"), nullable=True)
    longitude = Column(Float)
    latitude = Column(Float)

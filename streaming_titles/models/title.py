"""
    Declares the database model for title record objects.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY

from database.session import Base


class TitleRecord(Base):
    __tablename__ = "titles"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    show_id = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)
    director = Column(String(100))
    cast = Column(ARRAY(String(100)))
    country = Column(String(100))
    date_added = Column(String(20))
    release_year = Column(String(20))
    rating = Column(String(20))
    duration = Column(String(50))
    genres = Column(ARRAY(String(50)))
    description = Column(String(1000))
    platform = Column(String(50))

    def __repr__(self):
        return (
            f"<Title (title='{self.title}', type='{self.type}', "
            f"platform='{self.platform}')>"
        )

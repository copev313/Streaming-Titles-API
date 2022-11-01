import os

import databases
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base


# Initialize asynchronus database object:
db = databases.Database(os.getenv("DATABASE_URL"))

# https://docs.sqlalchemy.org/en/14/core/engines.html#postgresql
# USE "AUTOCOMMIT" TRANSACTIONS WITH BIT.IO:
engine = create_engine(
    url=os.getenv("DATABASE_URL"),
    isolation_level="AUTOCOMMIT",
    pool_pre_ping=True,
)

Base = declarative_base()

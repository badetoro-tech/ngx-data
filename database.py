# import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite DB conn string
# engine = create_engine("sqlite:///ngx_shares.db", connect_args={"check_same_thread": False})

# SQLite In-Memory conn string
# engine = create_engine('sqlite:///:memory:')

# MSSQL Database conn string
engine = create_engine('mssql+pyodbc://BAYO-DELL/ngx_shares_db?driver=SQL Server?Trusted_Connection=yes')
# engine = create_engine('mssql+pyodbc://irs:irs@BAYO-DELL:1521/ngx_shares_db')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

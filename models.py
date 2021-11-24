from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, Numeric, CheckConstraint, ForeignKey, Index
from sqlalchemy.types import Date, DateTime

metadata = MetaData()

instrument_type = Table('instrument_type', metadata,
                        Column('ins_type', Integer(), primary_key=True, index=True),
                        Column('description', String(250)),
                        Column('created_date', DateTime(), default=datetime.now),
                        Column('created_by', String(100)),
                        Column('last_modified', DateTime(), onupdate=datetime.now),
                        Column('modified_by', String(250))
                        )

instruments = Table('instruments', metadata,
                    Column('symbol', String(20), primary_key=True, index=True),
                    Column('name', String(250), nullable=True),
                    Column('ins_type', Integer(), ForeignKey('instrument_type.ins_type')),
                    Column('ins_details_url', String(250)),
                    Column('created_date', DateTime(), default=datetime.now),
                    Column('created_by', String(100)),
                    Column('last_modified', DateTime(), onupdate=datetime.now),
                    Column('modified_by', String(250))
                    )

daily_price = Table('daily_price', metadata,
                    Column('symbol', String(20), ForeignKey('instruments.symbol'), index=True),
                    Column('value_date', Date()),
                    Column('amount', Float()),
                    Column('created_date', DateTime(), default=datetime.now),
                    Column('created_by', String(100)),
                    Column('last_modified', DateTime(), onupdate=datetime.now),
                    Column('modified_by', String(250)),
                    CheckConstraint('amount >= 0', name='ck_amount_positive'),
                    Index('ix01_daily_price', 'value_date', 'symbol')
                    )

equity_info = Table('equity_info', metadata,
                    Column('id', Integer(), primary_key=True, index=True),
                    Column('symbol', String(20), ForeignKey('instruments.symbol')),
                    Column('trading_name', String(250), unique=True, nullable=False),
                    Column('ticker', String(20)),
                    Column('sector', String(250), nullable=False),
                    Column('sub_sector', String(250), nullable=False),
                    Column('market_classification', String(250)),
                    Column('nature_of_business', String(250)),
                    Column('market_cap_million', Numeric(20, 2)),
                    Column('shares_outstanding_million', Numeric(20, 2)),
                    Column('date_listed', DateTime()),
                    Column('created_date', DateTime(), default=datetime.now),
                    Column('created_by', String(100)),
                    Column('last_modified', DateTime(), onupdate=datetime.now),
                    Column('modified_by', String(250))
                    )

bond_info = Table('bond_info', metadata,
                  Column('id', Integer(), primary_key=True, index=True),
                  Column('symbol', String(20), ForeignKey('instruments.symbol')),
                  Column('issuer', String(250), index=True),
                  Column('description', String(250)),
                  Column('face_value', Float),
                  Column('issue_no', String(50)),
                  Column('issue_date', DateTime()),
                  Column('maturity_date', DateTime()),
                  Column('coupon', Float()),
                  Column('issue_price', Float()),
                  Column('bond_type', String(250)),
                  Column('created_date', DateTime(), default=datetime.now),
                  Column('created_by', String(100)),
                  Column('last_modified', DateTime(), onupdate=datetime.now),
                  Column('modified_by', String(250))
                  )

exc_fund_info = Table('exc_fund_info', metadata,
                      Column('id', Integer(), primary_key=True, index=True),
                      Column('symbol', String(20), ForeignKey('instruments.symbol')),
                      Column('description', String(250)),
                      Column('fund_manager', String(250)),
                      Column('issue_no', String(50)),
                      Column('index_tracked', String(250)),
                      Column('fund_sponsor', String(250)),
                      Column('trustee', String(250)),
                      Column('custodian', String(250)),
                      Column('liquidity_provider', String(250)),
                      Column('created_date', DateTime(), default=datetime.now),
                      Column('created_by', String(100)),
                      Column('last_modified', DateTime(), onupdate=datetime.now),
                      Column('modified_by', String(250))
                      )

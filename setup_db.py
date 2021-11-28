from models import instrument_type
from sqlalchemy import insert, select, func
from database import engine

connection = engine.connect()
setup_user = 'setup'


def check_setup_data(debug):
    # check if instrument_type has data
    s = select([func.count(instrument_type.c.ins_type).label('cnt')])
    rp = connection.execute(s)
    record = rp.first().cnt

    # if instrument_type is empty, populate with initial data
    if record <= 0:
        ins = insert(instrument_type)
        items = [
            {
                'ins_type': 0,
                'description': 'N/A',
                'created_by': setup_user
            },
            {
                'ins_type': 1,
                'description': 'Equity',
                'created_by': setup_user
            },
            {
                'ins_type': 2,
                'description': 'Bond',
                'created_by': setup_user
            },
            {
                'ins_type': 3,
                'description': 'Exchange Traded Funds',
                'created_by': setup_user
            },
        ]
        connection.execute(ins, items)
        if debug >= 1:  # 1
            print('Initialized setup data')
    else:
        if debug >= 1:  # 1
            print('Setup Data not required')

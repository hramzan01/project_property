import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Load environment variables
USER = os.environ.get('USER')
DOMAIN = os.environ.get('DOMAIN')
PASSWORD = os.environ.get('PASSWORD')

# Create engine
engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{DOMAIN}:5432/postgres')

'''PUSH TO POSTGRES'''
def push_to_postgres(df, table_name):
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print('Data uploaded to Postgres')
    except OperationalError as e:
        print(f"Error: {e}")


'''READ FROM POSTGRES'''
def read_from_postgres(table_name, limit):
    df = pd.read_sql(f'SELECT * FROM {table_name} LIMIT {limit}', engine)
    return df


# TEST FUNCTIONS
# df = pd.read_csv('data/processed_data/merged_data.csv')
# push_to_postgres(df, 'properties')

df = read_from_postgres('properties', 10)
print(df)

import psycopg2
import os

path = os.getcwd()
with open('postgres_queries/create_table.sql', 'r') as test:
    print(test.read())

conn = psycopg2.connect(database=os.environ.get('DATABASE_BANKING'), user=os.environ.get('DATABASE_BANKING_USER'),
                        password=os.environ.get('DATABASE_BANKING_PW'), host=os.environ.get('DATABASE_BANKING_HOST'),
                        port=os.environ.get('DATABASE_BANKING_PORT'))

curs = conn.cursor()
curs.execute('select * from public.dkb_transactions')
print(curs.fetchall())

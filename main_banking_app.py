import logging
import datetime
import pandas as pd
import os
from fints.client import FinTS3PinTanClient
import psycopg2

DKB_PW = os.environ.get('DKB_PW')
DKB_ACC = os.environ.get('DKB_ACC')


client_dkb = FinTS3PinTanClient('12030000', DKB_ACC, DKB_PW, 'https://banking-dkb.s-fints-pt-dkb.de/fints30')

accounts = client_dkb.get_sepa_accounts()
df_transactions = pd.DataFrame()

for account in accounts:
    transactions = client_dkb.get_statement(account, datetime.date(2018, 9, 1), datetime.date(2018, 9, 30))
    for transaction in transactions:
        df_transactions = df_transactions.append(pd.DataFrame(transaction.data, index=[0]), sort=False)


df_bewegung=pd.DataFrame(transactions[0].data, index=[0])



conn = psycopg2.connect(database='', user='', password='', host='', port='')

curs = conn.cursor()
curs.execute('select * from public.newtable')
print(curs.fetchall())
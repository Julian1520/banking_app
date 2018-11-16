import pandas as pd
import uuid
import re
import os
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from config_files.config_variables import TIME_FORMAT, DROP_COLUMNS_TRANSACTIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GiroData(object):

    def __init__(self, client):
        self.client = client

    def get_accounts(self):
        accounts = self.client.get_sepa_accounts()
        logger.info('Accounts fetched')
        return accounts

    def get_transactions_df(self, accounts, start_date, end_date):
        df_transactions = pd.DataFrame()
        start_date = datetime.strptime(start_date, TIME_FORMAT)
        end_date = datetime.strptime(end_date, TIME_FORMAT)
        for account in accounts:
            transactions = self.client.get_statement(account, start_date, end_date)
            for transaction in transactions:
                df_transactions = df_transactions.append(pd.DataFrame(transaction.data, index=[0]))
        return df_transactions

    @staticmethod
    def simplify_df_transactions(bank_name, bank_blz, transactions_dataframe):
        df_temp = transactions_dataframe[:]
        df_temp.drop(DROP_COLUMNS_TRANSACTIONS, inplace=True, axis=1)
        df_temp = df_temp.astype(str)
        df_temp.amount = df_temp.amount.apply(lambda x: float(re.search('(?<=<)(.*\n?)(?= )', x).groups(1)[0]))
        df_temp['bank_name'] = bank_name
        df_temp['bank_blz'] = bank_blz
        df_temp['transaction_uuid'] = df_temp.index.to_series().map(lambda x: str(uuid.uuid4()))
        return df_temp

    def get_balance(self, accounts):
        df_balance = pd.DataFrame()
        for account in accounts:
            balance = self.client.get_balance(account)
            df_balance_temp = pd.DataFrame([{'date': str(balance.date),
                                             'amount': balance.amount.amount,
                                             'currency': balance.amount.currency}])
            df_balance = df_balance.append(df_balance_temp)
        return df_balance


class DepotData(object):

    def __init__(self, login, password):
        self.login = login
        self.password = password

    @staticmethod
    def get_depot_dkb_df():
        web = webdriver.Chrome('/Users/jschmiss/Documents/banking_app/chromedriver')
        web.get('https://www.dkb.de/banking/depotstatus?$event=init')
        web.find_element_by_name('j_username').send_keys(os.environ.get('DKB_ACC'))
        web.find_element_by_name('j_password').send_keys(os.environ.get('DKB_PW'))
        web.find_element_by_id('buttonlogin').click()

        html = web.page_source
        soup = BeautifulSoup(html)
        table = soup.find('table', {'class': 'expandableTable portfolioOverviewTable'})
        res=[]
        for row in table.findAll('tr', attrs={'class': 'mainRow'}):
            td = row.find_all('td')
            line = [row.text.strip() for row in td if row.text.strip()]
            if line:
                res.append(line)

        df = pd.DataFrame(res)

        web.find_element_by_id('logout').click()
        web.quit()

        return df

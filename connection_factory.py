import pandas as pd
import uuid
import re
import logging
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from config_files.config_variables import TIME_FORMAT, DROP_COLUMNS_TRANSACTIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
options = webdriver.ChromeOptions()
options.add_argument('headless')


def get_df_from_html_table(html_table, table_class):
    soup = BeautifulSoup(html_table)
    table = soup.find('table', {'class': table_class})
    res = []
    for row in table.findAll('tr', attrs={'class': 'mainRow'}):
        td = row.find_all('td')
        line = [row.text.strip() for row in td if row.text.strip()]
        if line:
            res.append(line)
    df = pd.DataFrame(res)

    return df


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
        if len(transactions_dataframe) > 0:
            df_temp = transactions_dataframe[:]
            df_temp.drop(DROP_COLUMNS_TRANSACTIONS, inplace=True, axis=1)
            df_temp = df_temp.astype(str)
            df_temp.amount = df_temp.amount.apply(lambda x: float(re.search('(?<=<)(.*\n?)(?= )', x).groups(1)[0]))
            df_temp['bank_name'] = bank_name
            df_temp['bank_blz'] = bank_blz
            df_temp['transaction_uuid'] = df_temp.index.to_series().map(lambda x: str(uuid.uuid4()))
            return df_temp
        else:
            return transactions_dataframe

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

    def get_depot_dkb_html(self):
        web = webdriver.Chrome(os.environ.get('PATH_CHROME_DRIVER'), options=options)
        web.get('https://www.dkb.de/banking/depotstatus?$event=init')
        web.find_element_by_name('j_username').send_keys(self.login)
        web.find_element_by_name('j_password').send_keys(self.password)
        web.find_element_by_id('buttonlogin').click()
        html = web.page_source
        web.find_element_by_id('logout').click()
        web.quit()
        return html

    @staticmethod
    def simplify_df_depot(depot_dataframe):
        if len(depot_dataframe) > 0:
            temp_depot = depot_dataframe
            temp_depot[0] = temp_depot[0].apply(lambda x: re.sub(r'[\t\n\r]', '', x))
            temp_depot[0] = temp_depot[0].apply(lambda x: re.sub(r'[^a-zA-Z]+St\.$', '', x))
            temp_depot[1] = temp_depot[1].apply(lambda x: re.sub(r'Stück', '', x))
            temp_depot[2] = temp_depot[2].apply(lambda x: re.sub(r'[\s]', '', x))
            temp_depot[2] = temp_depot[2].apply(lambda x: re.sub(r'EUR', ' EUR ', x))
            temp_depot[3] = temp_depot[3].apply(lambda x: re.sub(r'[\s]', '', x))
            temp_depot[3] = temp_depot[3].apply(lambda x: re.sub(r'^[^a-zA-Z]+St\.', '', x))
            temp_depot[3] = temp_depot[3].apply(lambda x: re.sub(r'^[^a-zA-Z]+€[^a-zA-Z]+€', '', x))
            temp_depot[4] = temp_depot[4].apply(lambda x: re.sub(r'[^a-zA-Z]+%[^a-zA-Z]+€$', '', x))
            temp_depot[4] = temp_depot[4].apply(lambda x: re.sub(r'^[A-Z0-9]+', '', x))
            temp_depot.ix[:,0:3] = temp_depot.ix[:,0:3].applymap(lambda x: re.sub(r'[\s]', '', x))

            temp_depot['introduction_course'], temp_depot['introduction_value'] = temp_depot[2].str.split('EUR', 1).str
            temp_depot['course'], temp_depot['value'] = temp_depot[3].str.split('EUR', 1).str
            temp_depot['isin_wkn'], temp_depot['name'] = temp_depot[0].str.split('/', 1).str
            temp_depot['percent_change'], temp_depot['total_change'] = temp_depot[4].str.split('%', 1).str
            temp_depot.drop(columns=[0, 1, 2, 3, 4], inplace=True)
            temp_depot = temp_depot.applymap(lambda x: re.sub(r'EUR', '', x))
            temp_depot = temp_depot.applymap(lambda x: re.sub(r'[\t\n\r\s]', '', x))
            return temp_depot
        else:
            return depot_dataframe


class CreditCard(object):

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def get_credit_card_transactions_html(self, start_date, end_date):
        web = webdriver.Chrome(os.environ.get('PATH_CHROME_DRIVER'), options=options)
        web.get('https://www.dkb.de/banking/finanzstatus')
        web.find_element_by_name('j_username').send_keys(self.login)
        web.find_element_by_name('j_password').send_keys(self.password)
        web.find_element_by_id('buttonlogin').click()

        web.get('https://www.dkb.de/banking/finanzstatus/kreditkartenumsaetze?$event=init&caller=DkbTransactionBanking.content.banking.financialstatus.FinancialComposite')

        cc_start_date = datetime.strptime(start_date, TIME_FORMAT).strftime('%d.%m.%Y')
        cc_end_date = datetime.strptime(end_date, TIME_FORMAT).strftime('%d.%m.%Y')

        web.find_element_by_name('postingDate').send_keys(cc_start_date)
        web.find_element_by_name('toPostingDate').send_keys(cc_end_date)
        web.find_element_by_id('searchbutton').click()

        df_html_table = pd.DataFrame()

        condition = True
        while condition:
            html = web.page_source
            df_html_table = df_html_table.append(get_df_from_html_table(html, 'expandableTable dateHandling creditcardtransactionsTable'))

            condition = 'title="Nächste Seite"' in html

            if 'title="Nächste Seite"' in html:

                web.find_element_by_xpath('//*[@title="Nächste Seite"]').click()

        web.find_element_by_id('logout').click()
        web.quit()
        return df_html_table

    @staticmethod
    def simplify_df_cc(cc_dataframe):
        if len(cc_dataframe) > 0:
            temp_cc = cc_dataframe
            temp_cc['value_date'], temp_cc['voucher_date'] = temp_cc[0].str.split('\n', 1).str
            temp_cc['description'] = temp_cc[1]
            temp_cc['amount'], temp_cc['amount_foreign'] = temp_cc[2].str.split('\n', 1).str
            temp_cc['currency'], temp_cc['currency_foreign'] = temp_cc[3].str.split('\n', 1).str
            temp_cc['transaction_uuid'] = temp_cc.index.to_series().map(lambda x: str(uuid.uuid4()))
            temp_cc.drop(columns=[0, 1, 2, 3, 4], inplace=True)
            temp_cc = temp_cc.applymap(lambda x: re.sub(r'[\t\n\r\s]', '', x) if(pd.notnull(x)) else x)
            return temp_cc
        else:
            return cc_dataframe

from fints.client import FinTS3PinTanClient
from config_files.config_variables import TIME_FORMAT, DROP_COLUMNS_TRANSACTIONS
import pandas as pd
import uuid
from datetime import datetime


class GiroData(object):
    @staticmethod
    def get_client(blz, account_number, account_password, hbci_link):
        client = FinTS3PinTanClient(blz, account_number, account_password, hbci_link)
        return client

    @staticmethod
    def get_accounts(client):
        accounts = client.get_sepa_accounts()
        return accounts

    @staticmethod
    def get_transactions_df(client, accounts, start_date, end_date):
        df_transactions = pd.DataFrame()
        start_date = datetime.strptime(start_date, TIME_FORMAT)
        end_date = datetime.strptime(end_date, TIME_FORMAT)
        for account in accounts:
            transactions = client.get_statement(account, start_date, end_date)
            for transaction in transactions:
                df_transactions = df_transactions.append(pd.DataFrame(transaction.data, index=[0]))
        return df_transactions

    @staticmethod
    def simplify_df_transactions(bank_name, bank_blz, transactions_dataframe):
        df_temp = transactions_dataframe[:]
        df_temp.drop(DROP_COLUMNS_TRANSACTIONS, inplace=True, axis=1)
        df_temp = df_temp.astype(str)
        df_temp.amount = df_temp.amount.apply(lambda x: float(str(x).replace(' EUR>', '').replace('<', '')))
        df_temp['bank_name'] = bank_name
        df_temp['bank_blz'] = bank_blz
        df_temp['transaction_uuid'] = df_temp.index.to_series().map(lambda x: str(uuid.uuid4()))
        return df_temp

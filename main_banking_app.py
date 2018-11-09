from datetime import datetime
import pandas as pd
from fints.client import FinTS3PinTanClient
from config_variables import TIME_FORMAT, DROP_COLUMNS_TRANSACTIONS
from config_bank_connections import banks
import uuid


def get_client(blz, account_number, account_password, hbci_link):
    client = FinTS3PinTanClient(blz, account_number, account_password, hbci_link)
    return client


def get_accounts(client):
    accounts = client.get_sepa_accounts()
    client.get_holdings()
    return accounts


def get_transactions_df(client, accounts, start_date, end_date):
    df_transactions = pd.DataFrame()
    start_date = datetime.strptime(start_date, TIME_FORMAT)
    end_date = datetime.strptime(end_date, TIME_FORMAT)
    for account in accounts:
        transactions = client.get_statement(account, start_date, end_date)
        for transaction in transactions:
            df_transactions = df_transactions.append(pd.DataFrame(transaction.data, index=[0]))
    return df_transactions


def simplify_df_transactions(bank_name, bank_blz, transactions_dataframe):
    df_temp = transactions_dataframe[:]
    df_temp.drop(DROP_COLUMNS_TRANSACTIONS, inplace=True, axis=1)
    df_temp = df_temp.astype(str)
    df_temp.amount = df_temp.amount.apply(lambda x: float(str(x).replace(' EUR>', '').replace('<', '')))
    df_temp['bank_name'] = bank_name
    df_temp['bank_blz'] = bank_blz
    df_temp['transaction_uuid'] = df_temp.index.to_series().map(lambda x: str(uuid.uuid4()))
    return df_temp


if __name__ == '__main__':

    for bank in banks:
        print(bank.name)
        temp_client = get_client(bank.blz, bank.account_number, bank.account_password, bank.link)
        temp_accounts = get_accounts(temp_client)
        temp_transactions = get_transactions_df(temp_client, temp_accounts, '2018-07-01T00:00:00', '2018-07-31T00:00:00')
        temp_smpl_transactions = simplify_df_transactions(bank.name, bank.blz, temp_transactions)

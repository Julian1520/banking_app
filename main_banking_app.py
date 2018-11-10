import os
from config_files.config_connections import banks
from postgres_utils import BankingDatabase
from connection_factory import GiroData

if __name__ == '__main__':

    for bank in banks:
        giro_data = GiroData
        temp_client = giro_data.get_client(bank.blz,
                                           bank.account_number,
                                           bank.account_password,
                                           bank.link)

        temp_accounts = giro_data.get_accounts(temp_client)
        temp_transactions = giro_data.get_transactions_df(temp_client,
                                                          temp_accounts,
                                                          '2018-07-01T00:00:00',
                                                          '2018-07-31T00:00:00')

        temp_smpl_transactions = giro_data.simplify_df_transactions(bank.name, bank.blz, temp_transactions)

        send_data = BankingDatabase(database_name=os.environ.get('DATABASE_BANKING'),
                                    user=os.environ.get('DATABASE_BANKING_USER'),
                                    password=os.environ.get('DATABASE_BANKING_PW'),
                                    host=os.environ.get('DATABASE_BANKING_HOST'),
                                    port=os.environ.get('DATABASE_BANKING_PORT'))

        send_data.create_or_append_table(temp_smpl_transactions, 'public.'+bank.name+'_transactions', mode='replace')
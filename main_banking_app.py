import os
import argparse
from config_files.config_connections import banks
from postgres_utils import BankingDatabase
from connection_factory import GiroData
from fints.client import FinTS3PinTanClient

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--source_type", type=str, help='banks for giro accounts')
    parser.add_argument("--mode_database", type=str, help='replace or append')
    parser.add_argument("--start_date", type=str, help='format: YYYY-MM-DDThh:mm:ss')
    parser.add_argument("--end_date", type=str, help='format: YYYY-MM-DDThh:mm:ss')
    parsed_args = parser.parse_args()

    if parsed_args.source_type == 'banks':

        for bank in banks:
            print(bank.name)
            client = FinTS3PinTanClient(bank.blz, bank.account_number, bank.account_password, bank.link)
            giro_data = GiroData(client)

            temp_accounts = giro_data.get_accounts()
            temp_transactions = giro_data.get_transactions_df(temp_accounts,
                                                              parsed_args.start_date,
                                                              parsed_args.end_date)

            temp_smpl_transactions = giro_data.simplify_df_transactions(bank.name, bank.blz, temp_transactions)
            temp_balance = giro_data.get_balance(temp_accounts)

            send_data = BankingDatabase(database_name=os.environ.get('DATABASE_BANKING'),
                                        user=os.environ.get('DATABASE_BANKING_USER'),
                                        password=os.environ.get('DATABASE_BANKING_PW'),
                                        host=os.environ.get('DATABASE_BANKING_HOST'),
                                        port=os.environ.get('DATABASE_BANKING_PORT'))

            send_data.create_or_append_table(temp_smpl_transactions,
                                             f'{bank.name}_transactions',
                                             mode=parsed_args.mode_database)

            send_data.create_or_append_table(temp_balance, f'{bank.name}_balance', mode=parsed_args.mode_database)
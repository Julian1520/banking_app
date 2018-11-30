import os
import argparse
from config_files.config_connections import banks
from postgres_utils import BankingDatabase
from connection_factory import GiroData, DepotData, CreditCard, get_df_from_html_table
from fints.client import FinTS3PinTanClient

send_data = BankingDatabase(database_name=os.environ.get('DATABASE_BANKING'),
                            user=os.environ.get('DATABASE_BANKING_USER'),
                            password=os.environ.get('DATABASE_BANKING_PW'),
                            host=os.environ.get('DATABASE_BANKING_HOST'),
                            port=os.environ.get('DATABASE_BANKING_PORT'))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--source_type", type=str, help='banks_giro for giro accounts, dkb_depot for dkb depot,'
                                                        ' dkb_cc for dkb credit card')
    parser.add_argument("--mode_database", type=str, help='replace or append')
    parser.add_argument("--start_date", type=str, help='format: YYYY-MM-DDThh:mm:ss')
    parser.add_argument("--end_date", type=str, help='format: YYYY-MM-DDThh:mm:ss')
    parsed_args = parser.parse_args()

    if parsed_args.source_type == 'banks_giro':

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

            send_data.create_or_append_table(temp_smpl_transactions,
                                             f'{bank.name}_transactions',
                                             mode=parsed_args.mode_database)

            send_data.create_or_append_table(temp_balance, f'{bank.name}_balance', mode=parsed_args.mode_database)

    elif parsed_args.source_type == 'dkb_depot':
        depot_data = DepotData(os.environ.get('DKB_ACC'), os.environ.get('DKB_PW'))
        temp_dkb_depot_html = depot_data.get_depot_dkb_html()
        temp_dkb_depot_df = get_df_from_html_table(temp_dkb_depot_html, 'expandableTable portfolioOverviewTable')
        temp_dkb_depot_df_smpl = depot_data.simplify_df_depot(temp_dkb_depot_df)

        send_data.create_or_append_table(temp_dkb_depot_df_smpl, 'depot_data', mode=parsed_args.mode_database)

    elif parsed_args.source_type == 'dkb_cc':
        credit_card = CreditCard(os.environ.get('DKB_ACC'), os.environ.get('DKB_PW'))
        temp_credit_card_html = credit_card.get_credit_card_transactions_html(parsed_args.start_date,
                                                                              parsed_args.end_date)
        temp_credit_card_df = get_df_from_html_table(temp_credit_card_html,
                                                     'expandableTable dateHandling creditcardtransactionsTable')
        temp_credit_card_df_smpl = credit_card.simplify_df_cc(temp_credit_card_df)

        send_data.create_or_append_table(temp_credit_card_df_smpl, 'credit_card_data', mode=parsed_args.mode_database)

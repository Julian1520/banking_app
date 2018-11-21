import unittest
import pandas as pd
from unittest.mock import patch
from connection_factory import GiroData
from config_files.test_dummy_data import TEST_TEMP_TRANSACTIONS, TEST_TEMP_SMPL_TRANSACTIONS
from config_files.config_connections import banks
from collections import namedtuple
from datetime import date

balance = namedtuple('balance', 'amount date')
amount = namedtuple('amount', 'amount currency')


class TestConnectionFactory(unittest.TestCase):
    @patch('fints.client.FinTS3PinTanClient', autospec=True)
    def test_get_accounts(self, MockClient):
        for bank in banks:
            mock_client = MockClient(bank.blz, bank.account_number, bank.account_password, bank.link)
            mock_client.get_sepa_accounts.return_value = [1]

            test_giro = GiroData(mock_client)
            test_account = test_giro.get_accounts()

            self.assertIsInstance(test_account, list)
            self.assertEqual(len(test_account), 1)
            self.assertTrue(bank.blz.isdigit())
            self.assertTrue(bank.account_number.isdigit())
            self.assertTrue(bank.link.startswith('https://'))
            mock_client.get_sepa_accounts.assert_called_with()

    @patch('fints.client.FinTS3PinTanClient', autospec=True)
    def test_get_transactions_df(self, MockClient):

        mock_client = MockClient('123', '123', 'pw', 'link')
        mock_client.get_statement.return_value = [pd.DataFrame({'data': ['first']}), pd.DataFrame({'data': ['second']})]

        test_transactions_df = GiroData(mock_client).get_transactions_df([1],
                                                                         '2018-01-01T00:00:00',
                                                                         '2018-01-10T00:00:00')

        self.assertIsInstance(test_transactions_df, pd.DataFrame)
        self.assertEqual(len(test_transactions_df), 2)

    def test_simplify_df_transactions(self):
        test_df_transactions = GiroData.simplify_df_transactions('test_bank', '123', pd.DataFrame(TEST_TEMP_TRANSACTIONS))
        self.assertCountEqual(test_df_transactions.amount, pd.DataFrame(TEST_TEMP_SMPL_TRANSACTIONS).amount)

    @patch('fints.client.FinTS3PinTanClient', autospec=True)
    def test_get_balance(self, MockClient):
        mock_client = MockClient('123', '123', 'pw', 'link')
        mock_client.get_balance.return_value = balance(amount(123, 'EUR'), date(2018, 11, 19))

        test_balanace = GiroData(mock_client).get_balance([1])
        self.assertIsInstance(test_balanace, pd.DataFrame)
        self.assertDictEqual(test_balanace.to_dict(orient='list'), {'amount': [123], 'currency': ['EUR'], 'date': ['2018-11-19']})


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch
from connection_factory import GiroData
from config_files.config_connections import banks
import pandas as pd


class TestConnectionFactory(unittest.TestCase):
    @patch('fints.client.FinTS3PinTanClient')
    def test_get_accounts(self, MockClient):
        for bank in banks:
            mock_client = MockClient(bank.blz, bank.account_number, bank.account_password, bank.link)
            mock_client.get_sepa_accounts.return_value = [1]

            test_giro = GiroData(mock_client)
            test_account = test_giro.get_accounts()

            self.assertIsInstance(test_account, list)
            self.assertEqual(len(test_account), 1)

    def test_get_transactions_df(self, MockClient):

        mock_client = MockClient()
        mock_client.get_statement.return_value = [pd.DataFrame({'data': ['first']}), pd.DataFrame({'data': ['second']})]

        test_transactions_df = GiroData(mock_client).get_transactions_df([1],
                                                                         '2018-01-01T00:00:00',
                                                                         '2018-01-10T00:00:00')

        self.assertIsInstance(test_transactions_df, pd.DataFrame)
        self.assertEqual(len(test_transactions_df), 2)


if __name__ == '__main__':
    unittest.main()

import unittest
from connection_factory import GiroData
from config_files.config_connections import banks
from fints.client import FinTS3PinTanClient


class TestConnectionFactory(unittest.TestCase):

    def test_get_accounts(self):
        for bank in banks:
            test_client = FinTS3PinTanClient(bank.blz, bank.account_number, bank.account_password, bank.link)
            test_giro = GiroData(test_client)
            test_account = test_giro.get_accounts()
            self.assertIsInstance(test_account, list)
            self.assertEqual(len(test_account), 1)


if __name__ == '__main__':
    unittest.main()

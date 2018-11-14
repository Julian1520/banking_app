import unittest
from connection_factory import GiroData
from config_files.config_connections import banks


class TestConnectionFactory(unittest.TestCase):

    def test_get_accounts(self):
        for bank in banks:
            test_client = GiroData(bank.blz, bank.account_number, bank.account_password, bank.link)
            test_account = test_client.get_accounts()
            print(type(test_account))
            self.assertIsInstance(test_account, list)
            self.assertEquals(len(test_account), 1)


if __name__ == '__main__':
    unittest.main()

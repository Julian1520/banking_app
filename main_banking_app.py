import logging
import datetime
import getpass
import os
from fints.client import FinTS3PinTanClient

DKB_PW = os.environ.get('DKB_PW')
DKB_ACC = os.environ.get('DKB_ACC')
client_dkb = FinTS3PinTanClient('12030000', DKB_ACC, DKB_PW, 'https://banking-dkb.s-fints-pt-dkb.de/fints30')

konten = client_dkb.get_sepa_accounts()
<<<<<<< HEAD
=======

>>>>>>> f529c1d96bb1dc7edbfe64e9665c0c7de5e28656

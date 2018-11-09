from collections import namedtuple
import os
Bank = namedtuple('Bank', 'name blz account_number account_password link')

banks = [
Bank('DKB', '12030000', os.environ.get('DKB_ACC'), os.environ.get('DKB_PW'),\
     'https://banking-dkb.s-fints-pt-dkb.de/fints30'),
Bank('Sparkasse', '73150000', os.environ.get('SPK_ACC'), os.environ.get('SPK_PW'),\
     'https://banking-by5.s-fints-pt-by.de/fints30')
]
import os


def classify_giro_transaction(transactions_row):
    if transactions_row['applicant_iban'] == os.environ.get('DKB_IBAN')\
            or transactions_row['applicant_iban'] == os.environ.get('SPK_IBAN') \
            or transactions_row['applicant_iban'] == os.environ.get('VISA_IBAN'):
        return 'Internal transaction'
    if transactions_row['applicant_iban'] == os.environ.get('DB_IBAN'):
        return 'Fixed costs - rent and living'
    if os.environ.get('INSURANCE') in transactions_row['applicant_name']:
        return 'Fixed costs - Insurance'
    if os.environ.get('GYM') in transactions_row['applicant_name']:
        return 'Fixed costs - Gym'
    if os.environ.get('EMPLOYER') in transactions_row['applicant_name']:
        return 'Salary'
    if transactions_row['posting_text'] == 'WERTPAPIERE':
        return 'Stocks'
    return 'Other'


def classify_cc_transaction(transaction_row):
    if 'ATM' in transaction_row['description']:
        return 'Cash'
    if transaction_row['description'] == 'Einzahlung':
        return 'Internal transaction'
    return 'VISA Other'

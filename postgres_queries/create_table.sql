CREATE TABLE dkb_transactions(
   transaction_uuid CHAR(20) PRIMARY KEY,
   amount REAL,
   applicant_bin CHAR(50),
   applicant_name CHAR(20),
   currency CHAR(5),
   transaction_date CHAR(15),
   entry_date CHAR(15),
   posting_text CHAR(50),
   purpose CHAR(200),
   bank_name CHAR(10),
   bank_blz CHAR(20)
);
## private_banking
Data pipeline to extract transaction and balance data from the german banks Sparkasse and DKB.

# Data sources
* Sparkasse giro account
* DKB giro account (balance and transactions)
* DKB stock depot (balance)
* DKB credit card (balance and transactions)

# Usage
1. Setup config_files/config_connections.py:
The files config_files/config_connections.py saves the information to collect
balance and transaction data from the giro accounts of german banks. The files has
to store the connection information in the following format:
    ```
    banks = [
    Bank('{bank_name}', '{BIC}', os.environ.get('DKB_ACC'), os.environ.get('DKB_PW'),\
         '{fints link}'),
    Bank('{other_bank_name}', '{BIC}', os.environ.get('SPK_ACC'), os.environ.get('SPK_PW'),\
         '{fints links}')]
    ```
    The {bank_name} can be chosen by the user. It will be used to tag each transaction in
    the database with the information from which bank the transactions was retrieved.
    The fints link can be obtain online or from your bank. Password and user are collected from
    the environment. Make sure to name all variables accordingly.\
    The information from the DKB credit card and stock depot are collected via a crawler.
    This crawler only works for the DKB website.

2. Configure environment variables:
    ```
    export DKB_PW={password of your dkb online banking account}
    export DKB_ACC={account number of your dkb account}
    export SPK_PW={passowrd of your sparkasse online banking account}
    export SPK_ACC={account number of your sparkasse account}
    export DATABASE_BANKING={name of the database where the data should be stored}
    export DATABASE_BANKING_USER={user for the database}
    export DATABASE_BANKING_PW={password for the database}
    export DATABASE_BANKING_HOST={address of the database host}
    export DATABASE_BANKING_PORT={port of the database, for postgres it ist 5432}
    export PATH_CHROME_DRIVER={path were the chromedriver is located}
    ```

3. Set up a database:\
In order to store all data you need to set up a database. The scripts in this
repo are designed to use a postgres database. The connection details and the 
credentials have to be put in the environment variables as described above.

4. Execute main_banking_app.py:\
The main files needs several parameters.\
Example:
    ```
    --source_type giro_banks --mode_database replace --start_date 2017-01-01T00:00:00 --end_date 2018-12-25T00:00:00
    ```
    Please try the help function to see an overview of the parameters.
    
5. Interaction with other repos:\
This repo retrieves all mentioned data and stores it in a postgres database. To [run it regularly with Airflow](https://github.com/Julian1520/dags)
and [visualize the data with Dash](https://github.com/Julian1520/dash) check out my other repos.
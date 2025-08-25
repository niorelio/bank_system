import sqlite3
from uuid import UUID, uuid4
from core_entities import Client, Account, Transaction, TransactionType
from core_repositories import IClientRepository, IAccountRepository, ITransactionRepository, IUnitOfWork
from typing import Self
from datetime import datetime
from decimal import Decimal

class DBConnectMethods:
    def __init__(self, db: str):
        self.db_path = db
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self._create_tables()
    
    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients(
                id TEXT PRIMARY KEY NOT NULL,
                login TEXT NOT NULL UNIQUE,
                password_hash BLOB NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                balance TEXT NOT NULL DEFAULT '0.0',
                FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                amount TEXT NOT NULL,
                type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            )
        ''')
        # Создаем индексы для ускорения запросов
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_accounts_client ON accounts(client_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id)')
        self.connection.commit()
    
    def execute_query(self, query: str, *params) -> None:
        self.cursor.execute(query, params)
    
    def execute_get_data(self, query: str, *params) -> list:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def get_int(self, query: str, *params) -> int | None:
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()
        return result[0] if result else None
        
    def fetch_one(self, query: str, *params) -> sqlite3.Row | None:
        self.cursor.execute(query, params)
        return self.cursor.fetchone() 
    
    def get_lastrowid(self) -> int:
        return self.cursor.lastrowid
    
    def close(self) -> None:
        self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class SQLiteClientRepository(IClientRepository):
    def __init__(self, db_conn: DBConnectMethods):
        self.db = db_conn
    
    def add_client(self, client: Client) -> None:
        if client.id is None:
            client.id = uuid4()
        self.db.execute_query(
            'INSERT INTO clients (id, login, password_hash) VALUES (?, ?, ?)',
            str(client.id),
            client.login,
            client.password_hash
        )
    
    def get_by_client_id(self, client_id: UUID) -> Client | None:
        row = self.db.fetch_one(
            'SELECT id, login, password_hash FROM clients WHERE id = ?',
            str(client_id)
        )
        if not row:
            return None
        return Client(
            id=UUID(row['id']),
            login=row['login'],
            password_hash=row['password_hash']
        )

    def get_by_login(self, login: str) -> Client | None:
        row = self.db.fetch_one(
            'SELECT id, login, password_hash FROM clients WHERE login = ?',
            login
        )
        if not row:
            return None
        return Client(
            id=UUID(row['id']),
            login=row['login'],
            password_hash=row['password_hash']
        )
    
    def update(self, user: Client) -> None:
        self.db.execute_query(
            'UPDATE clients SET login = ?, password_hash = ? WHERE id = ?',
            user.login,
            user.password_hash,
            str(user.id)
        )

class SQLiteAccountRepository(IAccountRepository):
    def __init__(self, db_conn: DBConnectMethods):
        self.db = db_conn

    def add_account(self, account: Account) -> None:
        self.db.execute_query(
            'INSERT INTO accounts (client_id, balance) VALUES (?, ?)',
            str(account.client_id),
            str(account.balance)
        )
        account.id = self.db.get_lastrowid()

    def get_by_account_id(self, id: int) -> Account | None:
        row = self.db.fetch_one(
            'SELECT id, client_id, balance FROM accounts WHERE id = ?',
            id
        )
        if not row:
            return None
        return Account(
            id=row['id'],
            client_id=UUID(row['client_id']),
            balance=Decimal(row['balance'])
        )
    
    def get_by_client_id(self, client_id: UUID) -> list[Account]:
        rows = self.db.execute_get_data(
            'SELECT id, client_id, balance FROM accounts WHERE client_id = ?',
            str(client_id)
        )
        return [Account(
            id=row['id'],
            client_id=UUID(row['client_id']),
            balance=Decimal(row['balance'])
        ) for row in rows]
    
    def update(self, account: Account) -> None:
        self.db.execute_query(
            'UPDATE accounts SET balance = ? WHERE id = ?',
            str(account.balance),
            account.id
        )

class SQLiteTransactionRepository(ITransactionRepository):
    def __init__(self, db_conn: DBConnectMethods):
        self.db = db_conn
    
    def add(self, transaction: Transaction) -> None:
        self.db.execute_query(
            '''INSERT INTO transactions 
            (account_id, amount, type, timestamp) 
            VALUES (?, ?, ?, ?)''',
            transaction.account_id,
            str(transaction.amount),
            transaction.type.value,
            transaction.timestamp.isoformat()
        )
    
    def get_by_account_id(self, account_id: int) -> list[Transaction]:
        rows = self.db.execute_get_data(
            'SELECT id, account_id, amount, type, timestamp FROM transactions WHERE account_id = ?',
            account_id
        )
        transactions = []
        for row in rows:
            transactions.append(Transaction(
                id=row['id'],
                account_id=row['account_id'],
                amount=Decimal(row['amount']),
                type=TransactionType(row['type']),
                timestamp=datetime.fromisoformat(row['timestamp'])
            ))
        return transactions

class UnitOfWork(IUnitOfWork):
    def __init__(self, db_conn: DBConnectMethods):
        self.db = db_conn
        self.clients = SQLiteClientRepository(db_conn)
        self.accounts = SQLiteAccountRepository(db_conn)
        self.transactions = SQLiteTransactionRepository(db_conn)
    
    def __enter__(self) -> Self:
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
    
    def commit(self) -> None:
        self.db.connection.commit()
    
    def rollback(self) -> None:
        self.db.connection.rollback()

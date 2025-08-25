from core_entities import Client, Account, Transaction, TransactionType
from core_repositories import IUnitOfWork
from password_service import PasswordService
from decimal import Decimal, getcontext
from uuid import UUID

# Устанавливаем точность для Decimal
getcontext().prec = 28

class AuthorizationService:
    def __init__(self, uow: IUnitOfWork, password_service: PasswordService):
        self.uow = uow
        self.password_service = password_service
    
    def register(self, login: str, password: str) -> Client:
        with self.uow:
            if len(login) < 6:
                raise ValueError("Логин должен содержать минимум 6 символов")
        
            if len(password) < 8:
                raise ValueError("Пароль должен содержать минимум 8 символов")
            
            if ' ' in password:
                raise ValueError("Пароль не должен содержать пробелов")
            
            if self.uow.clients.get_by_login(login):
                raise ValueError("Пользователь с таким логином уже существует")

            password_hash = self.password_service.hash_password(password)
            new_client = Client(login=login, password_hash=password_hash)
            self.uow.clients.add_client(new_client)
            new_account = Account(client_id=new_client.id)
            self.uow.accounts.add_account(new_account)
            self.uow.commit()
        
        return Client(id=new_client.id, login=new_client.login)
    
    def login(self, login: str, password: str) -> Client:
        if len(login) < 6:
            raise ValueError("Неверный формат логина")
        
        user = self.uow.clients.get_by_login(login)

        if not user:
            raise ValueError("Пользователь не найден")
        
        if not self.password_service.check_password(password, user.password_hash):
            raise ValueError("Неверный пароль")
        
        return Client(id=user.id, login=user.login)

class AccountService: 
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def deposit(self, account_id: int, amount: Decimal) -> None:
        with self.uow:
            if amount <= Decimal('0'):
                raise ValueError("Сумма должна быть положительной")
            
            account = self.uow.accounts.get_by_account_id(account_id)
            if not account:
                raise ValueError("Счет не найден")
            
            new_balance = account.balance + amount            
            account.balance = new_balance
            self.uow.accounts.update(account)
            
            transaction = Transaction(
                account_id=account_id,
                amount=amount,
                type=TransactionType.DEPOSIT
            )
            self.uow.transactions.add(transaction)
            self.uow.commit()

    def withdraw(self, account_id: int, amount: Decimal) -> None:
        with self.uow:
            if amount <= Decimal('0'):
                raise ValueError("Сумма должна быть положительной")
            
            account = self.uow.accounts.get_by_account_id(account_id)
            if not account:
                raise ValueError("Счет не найден")
            
            if account.balance < amount:
                raise ValueError("Недостаточно средств")
            
            account.balance -= amount
            self.uow.accounts.update(account)
            
            transaction = Transaction(
                account_id=account_id,
                amount=amount,
                type=TransactionType.WITHDRAW
            )
            self.uow.transactions.add(transaction)
            self.uow.commit()

    def get_balance(self, account_id: int) -> Decimal:
        account = self.uow.accounts.get_by_account_id(account_id)
        if not account:
            raise ValueError("Счет не найден")
        return account.balance

    def get_transaction_history(self, account_id: int) -> list[Transaction]:
        return self.uow.transactions.get_by_account_id(account_id)
    
    def get_client_accounts(self, client_id: UUID) -> list[Account]:
        with self.uow:
            return self.uow.accounts.get_by_client_id(client_id)

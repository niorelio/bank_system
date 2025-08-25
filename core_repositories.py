from abc import ABC, abstractmethod
from core_entities import Client, Account, Transaction
from uuid import UUID
from typing import Self

class IClientRepository(ABC):
    @abstractmethod
    def add_client(self, client: Client) -> None:
        pass

    @abstractmethod
    def get_by_client_id(self, id: UUID) -> Client | None:
        pass

    @abstractmethod
    def get_by_login(self, login: str) -> Client | None:
        pass

    @abstractmethod
    def update(self, user: Client) -> None:
        pass

class IAccountRepository(ABC):
    @abstractmethod
    def add_account(self, account: Account) -> None:
        pass
    
    @abstractmethod
    def get_by_account_id(self, id: int) -> Account | None:
        pass
    
    @abstractmethod
    def get_by_client_id(self, client_id: UUID) -> list[Account]:
        pass
    
    @abstractmethod
    def update(self, account: Account) -> None:
        pass

class ITransactionRepository(ABC):
    @abstractmethod
    def add(self, transaction: Transaction) -> None:
        pass
    
    @abstractmethod
    def get_by_account_id(self, account_id: int) -> list[Transaction]:
        pass

class IUnitOfWork(ABC):
    clients: IClientRepository
    accounts: IAccountRepository
    transactions: ITransactionRepository
    
    @abstractmethod
    def __enter__(self) -> Self:  
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

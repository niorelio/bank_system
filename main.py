from password_service import PasswordService
from core_serviсes import AuthorizationService, AccountService
from infrastructure import DBConnectMethods, UnitOfWork
from ui import BankUI
import os

def main():
    DB_PATH = "bank.db"
          
    with DBConnectMethods(DB_PATH) as db_conn:
        # Инициализация Unit of Work
        uow = UnitOfWork(db_conn)
        
        # Создание сервисов
        password_service = PasswordService()
        auth_service = AuthorizationService(uow, password_service)
        account_service = AccountService(uow)
        
        # Создание и запуск UI
        ui = BankUI(auth_service, account_service)
        ui.run()

if __name__ == "__main__":
    main()

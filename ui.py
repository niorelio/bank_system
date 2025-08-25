from core_entities import Client, Account, Transaction, TransactionType
from core_serviсes import AuthorizationService, AccountService
from decimal import Decimal

class BankUI:
    def __init__(self,
                 auth_serv: AuthorizationService,
                 acc_serv: AccountService):
        self.auth_serv = auth_serv
        self.acc_serv = acc_serv
        self.current_client: Client | None = None
        self.current_account: Account | None = None

    def show_main_menu(self):
        print('\n' + '='*50)
        print('Добро пожаловать в банковскую систему!')
        print('='*50)
        print("""
        1. Авторизация
        2. Регистрация
        0. Выход
        """)

    def input_choice(self, prompt="Выберите действие: "):
        return input(prompt).strip()
    
    def input_credentials(self):
        login = input("Введите логин: ").strip()
        password = input("Введите пароль: ").strip()
        return login, password
    
    def input_amount(self) -> Decimal:
        while True:
            try:
                amount = Decimal(input("Введите сумму: ").strip())
                if amount <= Decimal('0'):
                    print("Сумма должна быть положительной!")
                    continue
                return amount
            except Exception:
                print("Ошибка! Введите числовое значение.")   

    def show_reg_menu(self):
        print("\n--- Регистрация ---")
        login, password = self.input_credentials()
    
        try:
            self.auth_serv.register(login, password)
            print(f"\nПользователь {login} успешно зарегистрирован!")
        except Exception as e:
            print(f"Ошибка регистрации: {str(e)}")

    def show_auth_menu(self):
        print("\n--- Авторизация ---")
        login, password = self.input_credentials()
        
        try:
            self.current_client = self.auth_serv.login(login, password)
            print("\nАвторизация успешна!")
            
            # Получаем первый счет клиента
            accounts = self.acc_serv.get_client_accounts(self.current_client.id)
            if accounts:
                self.current_account = accounts[0]
                self.show_account_menu()
            else:
                print("У вас нет счетов!")
                self.current_client = None
        except Exception as e:
            print(f"Ошибка авторизации: {str(e)}")
            self.current_client = None

    def show_account_menu(self):
        while True:
            print('\n' + '='*50)
            print(f"Личный кабинет: {self.current_client.login}")
            print(f"Номер счета: {self.current_account.id}")
            print('='*50)
            print("""
            1. Пополнить счет
            2. Вывести средства
            3. Просмотреть баланс
            4. Просмотреть историю операций
            0. Выход
            """)
            
            choice = self.input_choice()
            
            if choice == "1":  # Пополнение
                amount = self.input_amount()
                try:
                    self.acc_serv.deposit(self.current_account.id, amount)
                    print(f"\nСчет пополнен на {amount}!")
                except Exception as e:
                    print(f"Ошибка: {str(e)}")
            
            elif choice == "2":  # Снятие
                amount = self.input_amount()
                try:
                    self.acc_serv.withdraw(self.current_account.id, amount)
                    print(f"\nУспешно снято {amount}!")
                except Exception as e:
                    print(f"Ошибка: {str(e)}")
            
            elif choice == "3":  # Баланс
                balance = self.acc_serv.get_balance(self.current_account.id)
                print(f"\nТекущий баланс: {balance:.2f}")
            
            elif choice == "4":  # История операций
                history = self.acc_serv.get_transaction_history(self.current_account.id)
                print("\nИстория операций:")
                if not history:
                    print("  Нет операций")
                else:
                    for i, transaction in enumerate(history, 1):
                        op_type = "Пополнение" if transaction.type == TransactionType.DEPOSIT else "Снятие   "
                        dt = transaction.timestamp.strftime("%d.%m.%Y %H:%M")
                        print(f"{i}. {dt} | {op_type} | {transaction.amount:.2f}")
            
            elif choice == "5":  # Выход
                self.current_client = None
                self.current_account = None
                print("Возврат в главное меню...")
                break
            
            else:
                print("Неверный выбор. Попробуйте еще раз.")

    def run(self):
        while True:
            self.show_main_menu()
            choice = self.input_choice()

            match choice:
                case "1": self.show_auth_menu()
                case "2": self.show_reg_menu()
                case "0": 
                    print("Выход из программы.")
                    return
                case _: print("Неверный выбор. Попробуйте еще раз.")

import bcrypt


class PasswordService:
    @staticmethod
    def hash_password(password: str) -> bytes:
        """Генерирует хеш пароля с солью"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    @staticmethod
    def check_password(password: str, hashed_password: bytes) -> bool:
        """Проверяет пароль против хеша"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
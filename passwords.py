from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64
import dotenv
import hashlib
import string, random

dotenv.load_dotenv()

# Генерация и хранение ключа (в продакшене храните ключ в защищённом хранилище)
SECRET_KEY = os.urandom(32)  # 256-битный ключ


def encrypt_password(password):
    # Генерация случайного IV (Initialization Vector)
    iv = os.urandom(16)

    # Создание объекта шифра
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Добавление padding для выравнивания длины пароля
    padder = padding.PKCS7(128).padder()
    padded_password = padder.update(password.encode()) + padder.finalize()

    # Шифрование
    encrypted_password = encryptor.update(padded_password) + encryptor.finalize()

    # Возвращаем IV и зашифрованный пароль, закодированные в base64
    return base64.b64encode(iv + encrypted_password).decode()


def decrypt_password(encrypted_password):
    # Декодируем данные из base64
    encrypted_data = base64.b64decode(encrypted_password)

    # Извлекаем IV и зашифрованный пароль
    iv = encrypted_data[:16]
    encrypted_password = encrypted_data[16:]

    # Создание объекта шифра
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Расшифровка
    padded_password = decryptor.update(encrypted_password) + decryptor.finalize()

    # Удаление padding
    unpadder = padding.PKCS7(128).unpadder()
    password = unpadder.update(padded_password) + unpadder.finalize()

    return password.decode()

# Хэширование мастер-пароля, который для входа в бота
def hash_master_password(password):
    password = password
    salt = os.getenv('SALT')
    password_with_salt = password + salt
    hashed_password = hashlib.sha512(password_with_salt.encode())
    return hashed_password.hexdigest()

# Генерация пароля
def generate_password(length=15):
    characters = string.ascii_letters + string.digits 
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# Пример использования
if __name__ == "__main__":
    original_password = "MySecurePassword123"
    encrypted = encrypt_password(original_password)
    decrypted = decrypt_password(encrypted)

    print(f"Original: {original_password}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")

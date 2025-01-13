import os
import hashlib
import dotenv

dotenv.load_dotenv()

SALT = os.getenv('SALT')


def hash_master_password(password):
    password = password
    password_with_salt = password + SALT
    hashed_password = hashlib.sha512(password_with_salt.encode())
    return hashed_password.hexdigest()

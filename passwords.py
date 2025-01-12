import hashlib
import config

def hash_master_password(password):
    password = password
    salt = config.SALT
    password_with_salt = password + salt
    hashed_password = hashlib.sha512(password_with_salt.encode())
    return hashed_password.hexdigest()

    hash_master_password(password)
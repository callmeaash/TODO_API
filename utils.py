from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'])


def hash_password(password) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

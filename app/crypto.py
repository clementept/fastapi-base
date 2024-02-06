from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_hash(string: str):
    return pwd_context.hash(string)


def verify_hash(plain_string, hashed_string):
    return pwd_context.verify(plain_string, hashed_string)

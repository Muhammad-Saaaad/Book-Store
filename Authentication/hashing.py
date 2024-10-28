from passlib.context import CryptContext


pwd_ctx = CryptContext(schemes=['bcrypt'] , deprecated = 'auto')

def encrypt_pss(password : str):
    return pwd_ctx.encrypt(password)

def varify_pass(plain_pass , hashed_pass):
    return pwd_ctx.verify(plain_pass , hashed_pass)
from datetime import datetime , timedelta
from jose import jwt , JWTError

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

def create_access_token(username , password , user_type):
    try:
        to_encode = {'sub':username , 'pass' : password , 'user_type' : user_type}
        time = datetime.utcnow() + timedelta(hours=24) 
        to_encode.update({'exp':time})

        return jwt.encode(to_encode , SECRET_KEY , algorithm=ALGORITHM)
    except JWTError:
        print('Error in create access token')
    

def verify_token(token : str , credentials):
    try:
        payload = jwt.decode(token , SECRET_KEY , algorithms=[ALGORITHM])
        # print(payload)
        return payload

    except JWTError:
        raise credentials
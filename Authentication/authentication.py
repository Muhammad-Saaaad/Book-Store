import threading
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends , APIRouter , status , HTTPException

from Authentication.schemas_authentication import user_input
from Authentication.schemas_authentication import signUp_output
from Authentication import hashing
import model
from Authentication import jwt_token
import Email_and_otp
from database import db_dependency


router = APIRouter(tags=['authentication'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/signUp')

# pep8

@router.post('/signUp' , response_model=signUp_output   ,status_code=status.HTTP_201_CREATED)
async def signUp(db : db_dependency ,  req : user_input = Depends(user_input.as_form)):

    if not db.query(model.User).filter(model.User.email == req.email).first():
        if db.query(model.User).filter(model.User.email == req.email , model.User.is_verified == True).first():
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED , detail='email already verified')
        else:            
            #generate otp
            # incache memory redis

            otp = Email_and_otp.generate_otp(req.email)
            if Email_and_otp.SendEmail(req.email, otp): # email sent sucessfully
                hashed_password = hashing.encrypt_pss(req.password)
                data = model.User(email = req.email  ,username = req.username , password = hashed_password, 
                                  user_type = req.user_type , otp = otp)
                db.add(data)
                db.commit()
                db.refresh(data)

                t1 = threading.Thread(target=Email_and_otp.thread_function , args=[req.email ,db])
                t1.start() # here this thread will wait for 5 mintues and insert the otp and after 5 minutes delete the otp
                return data
            else:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE , detail='email not sent')
    else:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED , detail='email already exists')
    

@router.post('/Verify_otp')
async def verify_otp(user_otp :str , email : str  , db : db_dependency):

    validate_email = db.query(model.User).filter(model.User.email == email).first()

    if validate_email: 

        if not validate_email.otp :
           raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='OTP Expired')

        if validate_email.otp == user_otp:
            validate_email.is_verified= True
            validate_email.otp = ''
            db.commit()
            return {'data' : 'Email verified'}
        else:
           raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Invalid OTP')
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='Email not found')

@router.post('/signIn' , status_code=status.HTTP_202_ACCEPTED)
def SignIn(db:db_dependency , req : user_input = Depends(user_input.as_form)):

    email = db.query(model.User).filter(model.User.email == req.email).first()
    
    if email :

        if email.username == req.username:

            hashed_password = email.password

            if hashing.varify_pass(req.password , hashed_password):

                if email.user_type == req.user_type:

                    access_token = jwt_token.create_access_token(req.email , hashed_password , req.user_type)

                    return {'acess_token':access_token , 'token_type':'bearer'}
                
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='Invalid usertype')
        
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='Invalid Password')
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='Invalid username')
    
    raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED ,detail='Invalid email')


def get_current_user(data : Annotated[str , oauth2_scheme]):
    credentials = HTTPException(status_code=401 , detail='User UnAthorize' , headers={"WWW.Authenticate":"Bearer"})
    return jwt_token.verify_token(data , credentials=credentials)

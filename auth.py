from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .database import session
from .models import User
from jose import JWTError, ExpiredSignatureError





from passlib.context import CryptContext 

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain_pass,hash_pass):
    return pwd_context.verify(plain_pass,hash_pass)


from jose import jwt

secret_key="mysecretkey"
Algorithm = 'HS256'



def create_token(payload):
    return jwt.encode(payload,secret_key,algorithm=Algorithm)




def decode_token(token):
    return jwt.decode(token,secret_key,algorithms=[Algorithm])





from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer() 



def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    session_id = payload.get("session_id")

    if user_id is None or session_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    db=session()
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    if str(db_user.session_id) != str(session_id):
        raise HTTPException(status_code=401, detail="Session expired due to login from another device")

    return db_user

    
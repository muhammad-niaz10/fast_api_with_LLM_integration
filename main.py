from fastapi import FastAPI,Depends, HTTPException
from .database import engine,session
from .models import Base
from .schemas import UserCreate,UserResponse,UserLogin
from sqlalchemy.orm import Session
from .auth import hash_password,create_token,verify_password,get_current_user
from .models import User
import uuid
from datetime import datetime, timedelta

app = FastAPI()

Base.metadata.create_all(engine)


@app.get("/")
def root():
    return {"message": "FastAPI is running!"}


def get_db():
    db=session()
    try:
        yield db
    finally:
        db.close()


@app.post('/signup',response_model=UserResponse)
def signup(user:UserCreate,db:Session = Depends(get_db)):

    exsisting_user = db.query(User).filter(User.email == user.email).first()

    if exsisting_user:
        raise HTTPException(status_code=400,detail='email already exsist')



    hash_pass = hash_password(user.password)
    
    new_user = User(
    name=user.name,
    email=user.email,
    hashed_password=hash_pass
)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login")
def userlogin(user:UserLogin,db:Session=Depends(get_db)):

    db_user=db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400,detail="invalid credentials")

    if not verify_password(user.password,db_user.hashed_password):
        raise HTTPException(status_code=400,detail="invalid credentials")

    if not db_user.is_active:
        raise HTTPException(status_code=403,detail="inactice user")


    session_id=str(uuid.uuid4())

    expiration_time=datetime.utcnow()+timedelta(minutes=15)

    payload={
        "sub":str(db_user.id),
        "session_id":session_id,
        "exp":expiration_time
    }

    token = create_token(payload)

    db_user.session_id=session_id
    db.commit()
    db.refresh(db_user)

    return {
        "access_token":token,
        "token_type":"bearer"
    }
    

        
@app.get("/profile")
def profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }




from fastapi import FastAPI, Depends, HTTPException
from app.auth import get_current_user  
from app.llm import ask_openai
from pydantic import BaseModel


class LLMRequest(BaseModel):
    prompt: str

class LLMResponse(BaseModel):
    response: str

@app.post("/ask-llm", response_model=LLMResponse)
def ask_llm_endpoint(data: LLMRequest, current_user=Depends(get_current_user)):
    # current_user JWT se validate ho chuka hai
    result = ask_openai(data.prompt)
    return {"response": result}
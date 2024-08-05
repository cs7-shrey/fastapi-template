from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime, timezone
import jwt
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models, utils, oauth2
router = APIRouter(tags=['Authentication'])



# def login (user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
@router.get('/login', response_model=schemas.Token)
def login (user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first() 
    # fastapi stores users credentials in a field called username
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    # create a token
    access_token = oauth2.create_access_token(data={"user_id": user.id})                                # the header is created default
    return {"access_token": access_token, "token_type": "bearer"}
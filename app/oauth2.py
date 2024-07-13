import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated
from . import schemas, database, models
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')            # oauth2_scheme is a callable object that can be used as a dependency
# tokenUrl contains the URL that the client (the frontend running in the user's browser) will use to send the username and password 
# in order to get a token --> For documentation purposes
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()
    if expire_delta:
        expire_time = datetime.now(timezone.utc) + expire_delta
    else:
        expire_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire_time})                           # updates the dictionary with the elements from another dictionary
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    ...
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("user_id")
        # print(id)
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)                                # better to use if multiple fields in payload
    # except ExpiredSignatureError:
    except InvalidTokenError:
        # print("hahahaha", e)
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)): # This dependency will provide a str that is assigned to the parameter token of the path operation function
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't not validate credentials",
    headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user

""" 
What (oauth2_scheme) does
It will go and look in the request for that Authorization header, check if the value is Bearer plus some token, 
and will return the token as a str.
If it doesn't see an Authorization header, or the value doesn't have a Bearer token, 
it will respond with a 401 status code error (UNAUTHORIZED) directly.
"""

async def get_current_active_user(
    current_user: Annotated[schemas.UserCreate, Depends(get_current_user)],      # Annotated is used to provide type hints with additional context
):                # current_user is a dependency that will call get_current_user same as current_user: User = Depends(get_current_user)
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
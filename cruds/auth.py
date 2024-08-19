import os
from fastapi import Depends, HTTPException, status
import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from schemas import TokenData


class Autharization:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
    SECRET_KEY = os.getenv("SECRET_KEY")
    REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

    def hash_password(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, password, hashed_password):
        return self.pwd_context.verify(password, hashed_password)

    def encode_token(self, data: TokenData, expire: timedelta = timedelta(minutes=1)):
        token_data = data.dict()
        token_data["expire"] = (datetime.now(timezone.utc) + expire).isoformat()
        token = jwt.encode(token_data, self.SECRET_KEY, algorithm='HS256')
        return token

    def encode_refresh_token(self, data: TokenData, expire: timedelta = timedelta(days=7)):
        token_data = data.dict()
        token_data["expire"] = (datetime.now(timezone.utc) + expire).isoformat()
        token = jwt.encode(token_data, self.REFRESH_SECRET_KEY, algorithm='HS256')
        return token

    def decode_refresh_token(self, token: str):
        try:
            payload = jwt.decode(token, self.REFRESH_SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        refresh_token = TokenData(**payload)
        return refresh_token

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        access_token = TokenData(**payload)
        return access_token

    def auth_wrapper(self, token: str = Depends(oauth2_scheme)):
        return self.decode_token(token)

    def refresh_wrapper(self, token: str):
        return self.decode_refresh_token(token)





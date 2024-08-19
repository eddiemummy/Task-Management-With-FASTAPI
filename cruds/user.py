from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.models import User
from database.db import get_db
from schemas import CreateUser, UserSchema, TokenResponse, TokenData, RefreshRequest, UpdateUser
from cruds.auth import Autharization
from fastapi.security import OAuth2PasswordRequestForm

user_router = APIRouter(
    tags=["users"]
)

auth = Autharization()


@user_router.post("/register", status_code=status.HTTP_201_CREATED,
                  response_model=UserSchema, response_description="User registered")
async def create_user(request: CreateUser, db: Session = Depends(get_db)):
    if request.password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Passwords must match.")
    new_user = User(
        username=request.username,
        email=request.email,
        password=auth.hash_password(request.password),
        is_admin=request.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@user_router.post("/login", status_code=status.HTTP_201_CREATED,response_description="User logged in")
async def login(request: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not auth.verify_password(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')
    access_token = auth.encode_token(TokenData(username=user.username, id=user.id,
                                               email=user.email))
    refresh_token = auth.encode_refresh_token(TokenData(username=user.username, id=user.id,
                                               email=user.email))
    return TokenResponse(access_token=access_token, refresh_token= refresh_token, token_type ="bearer")


# @user_router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
# async def refresh_token(request: RefreshRequest):
#     try:
#         token_data = auth.refresh_wrapper(request.refresh_token)
#     except HTTPException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#
#     # Generate new access token
#     access_token = auth.encode_token(TokenData(username=token_data.username, id=token_data.id, email=token_data.email))
#
#     new_refresh_token = auth.encode_refresh_token(
#         TokenData(username=token_data.username, id=token_data.id, email=token_data.email))
#
#     return TokenResponse(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")


@user_router.get('/me', response_description="User info", response_model=UserSchema)
async def get_user(user: TokenData = Depends(auth.auth_wrapper), db: Session = Depends(get_db)):
    me = db.query(User).filter(User.username == user.username).first()
    if not me:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User Not Found')
    return me


# @user_router.post('/update', response_model=UserSchema, status_code=status.HTTP_200_OK)
# async def update_user(request: UpdateUser, db: Session = Depends(get_db),
#                       user_data: TokenData = Depends(auth.auth_wrapper)):
#     user_data = user_data.dict()
#     user = db.query(User).filter(User.username == user_data.get('username')).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User Not Found')
#     user.username = request.username if request.username else user.username
#     user.email = request.email if request.email else user.email
#     user.password = auth.hash_password(request.password) if request.password else user.password
#     user.is_admin = request.is_admin if request.is_admin else user.is_admin
#     db.commit()
#     db.refresh(user)
#
#     new_access_token = auth.encode_token(TokenData(username=user.username, id=user.id, email=user.email))
#     new_refresh_token = auth.encode_refresh_token(TokenData(username=user.username, id=user.id, email=user.email))
#
#     return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")


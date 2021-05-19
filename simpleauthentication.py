from datetime import timedelta, datetime
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
import secrets
import uvicorn

# fake database for authenticationg user
database = {
    "username": "anupam",
    "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    "booking_code": "anupam",
}
# ---------------------------------------

# pydantic model for response
class Booking(BaseModel):
    customer_name: str
    booking_code: str
    address: int


# ----------------------------

SECRET = secrets.token_urlsafe(10)
EXPIRE = 20
ALGORITHM = "HS256"

# pydantic model for reponse of token
class Token(BaseModel):
    access_token: str
    token_type: str


# ------------------------------------

app = FastAPI()
authenticate = OAuth2PasswordBearer(tokenUrl="token")

# dependency injected to @app.post path operation to verify user
def verify_user(username, password):
    if username not in database.get("username"):
        return False
    if password not in database.get("password"):
        return False


# ---------------------------------------------------------------

# --takes in username and expire(the time upto which token exist)
# returns JWT token for authentication
def create_token(data: dict, expire):
    user_dict = data.copy()
    expiry = datetime.utcnow() + expire
    user_dict.update({"exp": expiry})
    encoded_jwt = jwt.encode(user_dict, SECRET, algorithm=ALGORITHM)
    return encoded_jwt


# ---------------------------------------------------------------

# path operation to check and provide us JWT token-----------------
@app.post("/book", response_model=Token)
async def book_me(authenticate_me: OAuth2PasswordRequestForm = Depends()):
    user = verify_user(authenticate_me.username, authenticate_me.password)
    if user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not acceptable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expiry_date = timedelta(minutes=EXPIRE)
    token = create_token(data={"name": authenticate_me.username}, expire=expiry_date)
    return {"access_token": token, "token_type": "bearer"}


# -------------------------------------------------------------------


@app.get("/user", response_model=Booking)
async def read_booking(auth: str = Depends(authenticate)):
    return database


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

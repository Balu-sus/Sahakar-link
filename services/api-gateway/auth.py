import os
import datetime
from passlib.context import CryptContext
from jose import jwt, JWTError
import psycopg2
from psycopg2.extras import RealDictCursor

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sahakar_link_super_secret_jwt_key_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://sahakar:sahakar_dev_password@localhost:5432/sahakar_link")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_connection():
    return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

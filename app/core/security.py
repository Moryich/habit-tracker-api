from typing import Any
from jose import jwt
import bcrypt
from datetime import datetime, timedelta, timezone

from app.core.config import config

def hash_password(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(int(config.BCRYPT_SALT_ROUNDS))).decode("utf-8")

dummy_hash = hash_password("dummy_hash")

def verify_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=int(config.EXPIRE_MINUTES))
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)

def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])

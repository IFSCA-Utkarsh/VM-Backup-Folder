"""
Authentication helpers:
- verify_csv_credentials(user_id, password)
- create_access_token(sub)
- get_current_user(authorization_header) -> raises HTTPException on error
"""

import os
import csv
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Header
from typing import Optional

SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MIN", "60"))
EMP_CSV = os.getenv("EMP_CSV", "employees.csv")

def create_access_token(sub: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_csv_credentials(user_id: str, password: str) -> bool:
    """
    CSV expected format:
      id,password
      emp001,pass123
    """
    if not os.path.exists(EMP_CSV):
        return False
    with open(EMP_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id") == user_id and row.get("password") == password:
                return True
    return False

def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """
    FastAPI dependency replacement: call with Depends(get_current_user)
    Expects Authorization: Bearer <token>
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
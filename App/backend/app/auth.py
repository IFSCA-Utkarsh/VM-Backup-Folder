import csv
import jwt
import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from app.config import settings

router = APIRouter()

EMPLOYEE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "employees.csv")


class LoginRequest(BaseModel):
    user_id: str
    password: str


# --- JWT Helpers ---
def create_access_token(sub: str, expires_minutes: int = settings.JWT_EXPIRE_MIN) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    return decode_access_token(token)


# --- CSV Employee Auth ---
def validate_employee(user_id: str, password: str) -> bool:
    try:
        with open(EMPLOYEE_FILE, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["user_id"] == user_id and row["password"] == password:
                    return True
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Employee file not found")
    return False


# --- Login Endpoint ---
@router.post("/login")
async def login(data: LoginRequest):
    if validate_employee(data.user_id, data.password):
        token = create_access_token(sub=data.user_id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_MIN,
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

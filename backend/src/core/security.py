# src/core/security.py
# Xử lý bảo mật: hash password và tạo/giải mã JWT token

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.core.config import get_settings

settings = get_settings()

# Dùng bcrypt để hash password — tự động thêm salt, an toàn nhất hiện tại
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password trước khi lưu vào DB. KHÔNG BAO GIỜ lưu plain-text."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Kiểm tra password người dùng nhập có khớp hash trong DB không."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT token.
    - payload chứa: user_id (sub), role, thời gian hết hạn (exp)
    - signature ký bằng JWT_SECRET_KEY → chống giả mạo
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Giải mã JWT token.
    Raise JWTError nếu token bị giả mạo, hết hạn, hoặc sai định dạng.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
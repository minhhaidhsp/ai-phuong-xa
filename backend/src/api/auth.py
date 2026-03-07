# src/api/auth.py
# Endpoints xử lý Authentication
#   POST /api/v1/auth/login   → đăng nhập, trả JWT token
#   GET  /api/v1/auth/me      → xem thông tin user đang login
#   POST /api/v1/auth/logout  → đăng xuất

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.db.database import get_db
from src.db.models import NguoiDung
from src.db.repositories.user_repo import get_user_by_username, update_last_login
from src.core.security import verify_password, create_access_token
from src.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["🔐 Authentication"])


# ── Pydantic Schemas — định nghĩa cấu trúc request/response ──────────

class TokenResponse(BaseModel):
    """Response trả về khi login thành công"""
    access_token: str       # JWT token — client lưu để gửi kèm mọi request
    token_type: str = "bearer"
    user_id: str
    ho_ten: str
    vai_tro: str            # can_bo | lanh_dao | admin


class UserMeResponse(BaseModel):
    """Thông tin user hiện tại"""
    id: str
    ten_dang_nhap: str
    ho_ten: str
    vai_tro: str
    email: str | None
    is_active: bool


# ── Endpoints ─────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(
    # OAuth2PasswordRequestForm tự động đọc form: username + password
    # Swagger UI hiện form điền trực tiếp tại nút "Authorize"
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Đăng nhập — trả về JWT token.
    Client lưu token và gửi kèm mọi request:
    Header: Authorization: Bearer <token>
    """
    # Bước 1: tìm user
    user = await get_user_by_username(db, form_data.username)

    # Bước 2: kiểm tra user + password
    # Gộp 2 lỗi thành 1 thông báo → không lộ "username đúng nhưng sai pass"
    if not user or not verify_password(form_data.password, user.mat_khau_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Bước 3: kiểm tra tài khoản có bị khóa không
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa. Liên hệ Quản trị viên."
        )

    # Bước 4: tạo JWT token
    token = create_access_token({"sub": user.id, "role": user.vai_tro})

    # Bước 5: ghi nhận thời gian login cuối
    await update_last_login(db, user.id)
    await db.commit()

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        ho_ten=user.ho_ten,
        vai_tro=user.vai_tro,
    )


@router.get("/me", response_model=UserMeResponse)
async def get_me(
    # get_current_user tự động xác thực token và trả về NguoiDung object
    current_user: Annotated[NguoiDung, Depends(get_current_user)]
):
    """Lấy thông tin user đang đăng nhập. Yêu cầu token hợp lệ."""
    return UserMeResponse(
        id=current_user.id,
        ten_dang_nhap=current_user.ten_dang_nhap,
        ho_ten=current_user.ho_ten,
        vai_tro=current_user.vai_tro,
        email=current_user.email,
        is_active=current_user.is_active,
    )


@router.post("/logout")
async def logout(
    current_user: Annotated[NguoiDung, Depends(get_current_user)]
):
    """
    Đăng xuất.
    JWT là stateless nên server không xóa được token.
    Client tự xóa token khỏi storage là đủ.
    """
    return {"message": f"Đăng xuất thành công. Tạm biệt {current_user.ho_ten}!"}
# src/core/dependencies.py
# FastAPI Dependencies: inject user đã xác thực vào route handlers
#
# Cách dùng trong bất kỳ route nào:
#   async def my_route(user: Annotated[NguoiDung, Depends(get_current_user)]):
#
# FastAPI tự động: đọc token → decode → query DB → inject user

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.models import NguoiDung, VaiTro
from src.db.repositories.user_repo import get_user_by_id
from src.core.security import decode_token

# Tự động đọc "Bearer <token>" từ header Authorization
# tokenUrl dùng cho nút Authorize trên Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> NguoiDung:
    """
    Dependency cơ bản: xác thực token → trả về user hiện tại.
    Luồng: extract token → decode JWT → query DB → kiểm tra active.
    Raise 401 nếu token invalid/hết hạn/user không tồn tại.
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        # "sub" (subject) = user_id theo chuẩn JWT RFC 7519
        user_id: str = payload.get("sub")
        if not user_id:
            raise exc
    except JWTError:
        raise exc

    user = await get_user_by_id(db, user_id)
    if not user:
        raise exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa. Liên hệ admin để được hỗ trợ."
        )
    return user


async def require_can_bo(
    current_user: Annotated[NguoiDung, Depends(get_current_user)]
) -> NguoiDung:
    """
    RBAC Level 1 — can_bo, lanh_dao, admin đều vào được.
    Dùng cho: tiếp nhận hồ sơ, tra cứu AI, xem thông tin cá nhân.
    """
    return current_user


async def require_lanh_dao(
    current_user: Annotated[NguoiDung, Depends(get_current_user)]
) -> NguoiDung:
    """
    RBAC Level 2 — chỉ lanh_dao và admin.
    Dùng cho: xem tất cả hồ sơ, phê duyệt, dashboard, phân công.
    """
    if current_user.vai_tro not in [VaiTro.LANH_DAO, VaiTro.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chức năng này yêu cầu quyền Lãnh đạo trở lên"
        )
    return current_user


async def require_admin(
    current_user: Annotated[NguoiDung, Depends(get_current_user)]
) -> NguoiDung:
    """
    RBAC Level 3 — chỉ admin.
    Dùng cho: quản lý users, audit log, cấu hình hệ thống.
    """
    if current_user.vai_tro != VaiTro.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Quản trị viên mới có quyền này"
        )
    return current_user
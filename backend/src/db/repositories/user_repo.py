# src/db/repositories/user_repo.py
# Tất cả query liên quan bảng nguoi_dung
# Tách DB logic ra khỏi API layer → dễ test, dễ bảo trì

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import NguoiDung


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[NguoiDung]:
    """Tìm user theo username (không phân biệt hoa thường). Trả None nếu không có."""
    result = await db.execute(
        select(NguoiDung).where(NguoiDung.ten_dang_nhap == username.lower())
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[NguoiDung]:
    """Tìm user theo UUID. Dùng khi xác thực token."""
    result = await db.execute(
        select(NguoiDung).where(NguoiDung.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_all_users(
    db: AsyncSession, skip: int = 0, limit: int = 50, only_active: bool = True
) -> list[NguoiDung]:
    """Lấy danh sách users có phân trang. skip/limit dùng cho pagination."""
    query = select(NguoiDung)
    if only_active:
        query = query.where(NguoiDung.is_active == True)
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_user(db: AsyncSession, **kwargs) -> NguoiDung:
    """
    Tạo user mới. flush() để lấy ID tự động nhưng chưa commit.
    Caller tự quyết định commit hay rollback.
    """
    user = NguoiDung(**kwargs)
    db.add(user)
    await db.flush()
    return user


async def update_last_login(db: AsyncSession, user_id: str) -> None:
    """Cập nhật thời điểm đăng nhập cuối — gọi sau khi login thành công."""
    await db.execute(
        update(NguoiDung)
        .where(NguoiDung.id == user_id)
        .values(last_login_at=datetime.now(timezone.utc))
    )
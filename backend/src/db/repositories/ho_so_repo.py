# src/db/repositories/ho_so_repo.py
# Tất cả query liên quan bảng ho_so
# Tách DB logic ra khỏi API layer → dễ test, dễ bảo trì

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import HoSo, TrangThaiHoSo


# ── Transitions hợp lệ của State Machine ─────────────────────────────
# Key: trạng thái hiện tại → Value: danh sách trạng thái được phép chuyển sang
VALID_TRANSITIONS = {
    TrangThaiHoSo.CHO_TIEP_NHAN:   [TrangThaiHoSo.DANG_XU_LY],
    TrangThaiHoSo.DANG_XU_LY:      [TrangThaiHoSo.YEU_CAU_BO_SUNG,
                                     TrangThaiHoSo.CHO_PHE_DUYET,
                                     TrangThaiHoSo.TU_CHOI],
    TrangThaiHoSo.YEU_CAU_BO_SUNG: [TrangThaiHoSo.DANG_XU_LY],
    TrangThaiHoSo.CHO_PHE_DUYET:   [TrangThaiHoSo.HOAN_THANH,
                                     TrangThaiHoSo.DANG_XU_LY],
    TrangThaiHoSo.HOAN_THANH:      [],   # Trạng thái cuối — không chuyển được
    TrangThaiHoSo.TU_CHOI:         [],   # Trạng thái cuối — không chuyển được
}


def is_valid_transition(tu_trang_thai: str, den_trang_thai: str) -> bool:
    """Kiểm tra chuyển trạng thái có hợp lệ không theo state machine."""
    allowed = VALID_TRANSITIONS.get(tu_trang_thai, [])
    return den_trang_thai in allowed


async def get_ho_so_by_id(
    db: AsyncSession, ho_so_id: str
) -> Optional[HoSo]:
    """Lấy hồ sơ theo UUID, kèm thông tin thu_tuc và can_bo."""
    result = await db.execute(
        select(HoSo)
        # selectinload: load relationship trong 1 query → tránh N+1 problem
        .options(
            selectinload(HoSo.thu_tuc),
            selectinload(HoSo.can_bo_thu_ly)
        )
        .where(HoSo.id == ho_so_id)
    )
    return result.scalar_one_or_none()


async def get_ho_so_by_ma(
    db: AsyncSession, ma_ho_so: str
) -> Optional[HoSo]:
    """
    Lấy hồ sơ theo mã (VD: HT-20260307-A1B2).
    Dùng cho tra cứu công khai — không cần đăng nhập.
    """
    result = await db.execute(
        select(HoSo).where(HoSo.ma_ho_so == ma_ho_so.upper())
    )
    return result.scalar_one_or_none()


async def get_danh_sach_ho_so(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    trang_thai: Optional[str] = None,
    can_bo_id: Optional[str] = None,
    linh_vuc: Optional[str] = None,
) -> tuple[list[HoSo], int]:
    """
    Lấy danh sách hồ sơ có lọc + phân trang.
    Trả về (danh_sach, tong_so) để frontend hiển thị pagination.
    """
    # Base query
    query = select(HoSo).options(
        selectinload(HoSo.thu_tuc),
        selectinload(HoSo.can_bo_thu_ly)
    )
    count_query = select(func.count(HoSo.id))

    # Áp dụng filters nếu có
    if trang_thai:
        query = query.where(HoSo.trang_thai == trang_thai)
        count_query = count_query.where(HoSo.trang_thai == trang_thai)
    if can_bo_id:
        query = query.where(HoSo.can_bo_thu_ly_id == can_bo_id)
        count_query = count_query.where(HoSo.can_bo_thu_ly_id == can_bo_id)

    # Đếm tổng số bản ghi (cho pagination)
    total = await db.scalar(count_query)

    # Lấy dữ liệu với phân trang, sắp xếp mới nhất trước
    query = query.order_by(HoSo.ngay_tiep_nhan.desc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return list(result.scalars().all()), total or 0


async def create_ho_so(db: AsyncSession, **kwargs) -> HoSo:
    """
    Tạo hồ sơ mới. flush() để lấy ID nhưng chưa commit.
    Caller tự quyết định commit hay rollback.
    """
    ho_so = HoSo(**kwargs)
    db.add(ho_so)
    await db.flush()
    return ho_so


async def update_trang_thai(
    db: AsyncSession,
    ho_so_id: str,
    trang_thai_moi: str,
    ghi_chu: Optional[str] = None,
) -> Optional[HoSo]:
    """
    Cập nhật trạng thái hồ sơ.
    Nếu HOAN_THANH → tự động set ngay_hoan_thanh = now().
    """
    values = {"trang_thai": trang_thai_moi}

    # Ghi chú nội bộ nếu có
    if ghi_chu:
        values["ghi_chu_noi_bo"] = ghi_chu

    # Tự động đánh dấu ngày hoàn thành
    if trang_thai_moi == TrangThaiHoSo.HOAN_THANH:
        values["ngay_hoan_thanh"] = datetime.now(timezone.utc)

    await db.execute(
        update(HoSo).where(HoSo.id == ho_so_id).values(**values)
    )
    # Trả về hồ sơ đã cập nhật
    return await get_ho_so_by_id(db, ho_so_id)
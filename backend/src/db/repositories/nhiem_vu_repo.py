"""
src/db/repositories/nhiem_vu_repo.py
Sprint 7 - CRUD cho bảng nhiem_vu
"""
from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import NhiemVu


def _load_options():
    return [
        selectinload(NhiemVu.nguoi_giao),
        selectinload(NhiemVu.nguoi_nhan),
    ]


async def create_nhiem_vu(
    db: AsyncSession,
    tieu_de: str,
    nguoi_giao_id: UUID,
    nguoi_nhan_id: UUID,
    han_hoan_thanh: date,
    mo_ta: Optional[str] = None,
    muc_do_uu_tien: str = "TRUNG_BINH",
    ho_so_id: Optional[UUID] = None,
) -> NhiemVu:
    nv = NhiemVu(
        tieu_de=tieu_de,
        mo_ta=mo_ta,
        nguoi_giao_id=nguoi_giao_id,
        nguoi_nhan_id=nguoi_nhan_id,
        ngay_giao=date.today(),
        han_hoan_thanh=han_hoan_thanh,
        muc_do_uu_tien=muc_do_uu_tien,
        ho_so_id=ho_so_id,
        trang_thai="CHUA_BAT_DAU",
    )
    db.add(nv)
    await db.commit()

    # Reload với relationships để tránh MissingGreenlet
    return await get_nhiem_vu(db, nv.id)


async def get_nhiem_vu(db: AsyncSession, nv_id: UUID) -> Optional[NhiemVu]:
    q = (
        select(NhiemVu)
        .options(*_load_options())
        .where(NhiemVu.id == nv_id)
    )
    return (await db.execute(q)).scalar_one_or_none()


async def list_nhiem_vu(
    db: AsyncSession,
    nguoi_nhan_id: Optional[UUID] = None,
    nguoi_giao_id: Optional[UUID] = None,
    trang_thai: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    conditions = []
    if nguoi_nhan_id:
        conditions.append(NhiemVu.nguoi_nhan_id == nguoi_nhan_id)
    if nguoi_giao_id:
        conditions.append(NhiemVu.nguoi_giao_id == nguoi_giao_id)
    if trang_thai:
        conditions.append(NhiemVu.trang_thai == trang_thai)

    base_q = select(NhiemVu).options(*_load_options())
    if conditions:
        base_q = base_q.where(and_(*conditions))

    count_q = select(func.count()).select_from(NhiemVu)
    if conditions:
        count_q = count_q.where(and_(*conditions))
    total = (await db.execute(count_q)).scalar() or 0

    items_q = (
        base_q
        .order_by(NhiemVu.han_hoan_thanh, NhiemVu.muc_do_uu_tien.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = (await db.execute(items_q)).scalars().all()

    return {"items": list(items), "total": total, "page": page, "page_size": page_size}


async def update_trang_thai(
    db: AsyncSession,
    nv_id: UUID,
    trang_thai_moi: str,
    ket_qua: Optional[str] = None,
) -> Optional[NhiemVu]:
    nv = await get_nhiem_vu(db, nv_id)
    if not nv:
        return None

    nv.trang_thai = trang_thai_moi
    if trang_thai_moi == "HOAN_THANH":
        nv.ngay_hoan_thanh_thuc_te = date.today()
    if ket_qua:
        nv.ket_qua = ket_qua

    await db.commit()

    # Reload sau commit
    return await get_nhiem_vu(db, nv_id)


async def delete_nhiem_vu(db: AsyncSession, nv_id: UUID) -> bool:
    nv = await get_nhiem_vu(db, nv_id)
    if not nv:
        return False
    await db.delete(nv)
    await db.commit()
    return True

"""
src/api/nhiem_vu.py
Sprint 7 - API Nhiệm vụ + KPI
"""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.core.dependencies import get_current_user, require_role
from src.db.models import NguoiDung
from src.db.repositories.nhiem_vu_repo import (
    create_nhiem_vu, get_nhiem_vu, list_nhiem_vu,
    update_trang_thai, delete_nhiem_vu,
)
from src.report.kpi import get_kpi_all, get_kpi_one
from loguru import logger

router = APIRouter(prefix="/api/v1", tags=["NhiemVu & KPI"])


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class TaoNhiemVuRequest(BaseModel):
    tieu_de: str
    mo_ta: Optional[str] = None
    nguoi_nhan_id: UUID
    han_hoan_thanh: date
    muc_do_uu_tien: str = "TRUNG_BINH"
    ho_so_id: Optional[UUID] = None


class CapNhatTrangThaiRequest(BaseModel):
    trang_thai: str
    ket_qua: Optional[str] = None


def _nv_to_dict(nv) -> dict:
    return {
        "id": str(nv.id),
        "tieu_de": nv.tieu_de,
        "mo_ta": nv.mo_ta,
        "nguoi_giao": nv.nguoi_giao.ho_ten if nv.nguoi_giao else None,
        "nguoi_nhan": nv.nguoi_nhan.ho_ten if nv.nguoi_nhan else None,
        "nguoi_nhan_id": str(nv.nguoi_nhan_id),
        "ngay_giao": str(nv.ngay_giao),
        "han_hoan_thanh": str(nv.han_hoan_thanh),
        "ngay_hoan_thanh_thuc_te": str(nv.ngay_hoan_thanh_thuc_te) if nv.ngay_hoan_thanh_thuc_te else None,
        "trang_thai": nv.trang_thai,
        "muc_do_uu_tien": nv.muc_do_uu_tien,
        "ket_qua": nv.ket_qua,
        "ho_so_id": str(nv.ho_so_id) if nv.ho_so_id else None,
    }


# ── Nhiệm Vụ Endpoints ───────────────────────────────────────────────────────

VALID_TRANG_THAI = [
    "CHUA_BAT_DAU", "DANG_THUC_HIEN",
    "HOAN_THANH", "QUA_HAN", "DA_HUY"
]
VALID_UU_TIEN = ["THAP", "TRUNG_BINH", "CAO", "KHAN_CAP"]


@router.post("/nhiem-vu", status_code=201)
async def tao_nhiem_vu(
    req: TaoNhiemVuRequest,
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["lanh_dao", "admin"])),
):
    """Lãnh đạo giao nhiệm vụ cho cán bộ."""
    if req.muc_do_uu_tien not in VALID_UU_TIEN:
        raise HTTPException(400, f"muc_do_uu_tien phải là: {VALID_UU_TIEN}")
    if req.han_hoan_thanh < date.today():
        raise HTTPException(400, "han_hoan_thanh không được là ngày trong quá khứ")

    nv = await create_nhiem_vu(
        db,
        tieu_de=req.tieu_de,
        nguoi_giao_id=current_user.id,
        nguoi_nhan_id=req.nguoi_nhan_id,
        han_hoan_thanh=req.han_hoan_thanh,
        mo_ta=req.mo_ta,
        muc_do_uu_tien=req.muc_do_uu_tien,
        ho_so_id=req.ho_so_id,
    )
    logger.info(f"Tạo nhiệm vụ: {nv.tieu_de} → {req.nguoi_nhan_id}")
    return {"status": "ok", "data": _nv_to_dict(nv)}


@router.get("/nhiem-vu")
async def danh_sach_nhiem_vu(
    nguoi_nhan_id: Optional[UUID] = None,
    trang_thai: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    """
    Danh sách nhiệm vụ.
    - Cán bộ: chỉ thấy nhiệm vụ của mình
    - Lãnh đạo/Admin: thấy tất cả, có thể lọc theo nguoi_nhan_id
    """
    # Cán bộ chỉ được xem của mình
    if current_user.vai_tro == "can_bo":
        nguoi_nhan_id = current_user.id

    result = await list_nhiem_vu(
        db,
        nguoi_nhan_id=nguoi_nhan_id,
        trang_thai=trang_thai,
        page=page,
        page_size=page_size,
    )
    return {
        "status": "ok",
        "data": {
            "items": [_nv_to_dict(nv) for nv in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
        }
    }


@router.get("/nhiem-vu/{nv_id}")
async def chi_tiet_nhiem_vu(
    nv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    nv = await get_nhiem_vu(db, nv_id)
    if not nv:
        raise HTTPException(404, "Không tìm thấy nhiệm vụ")
    # Cán bộ chỉ xem được nhiệm vụ của mình
    if current_user.vai_tro == "can_bo" and nv.nguoi_nhan_id != current_user.id:
        raise HTTPException(403, "Không có quyền xem nhiệm vụ này")
    return {"status": "ok", "data": _nv_to_dict(nv)}


@router.put("/nhiem-vu/{nv_id}")
async def cap_nhat_trang_thai(
    nv_id: UUID,
    req: CapNhatTrangThaiRequest,
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    """Cán bộ cập nhật tiến độ. Lãnh đạo có thể hủy."""
    if req.trang_thai not in VALID_TRANG_THAI:
        raise HTTPException(400, f"trang_thai phải là: {VALID_TRANG_THAI}")

    nv = await get_nhiem_vu(db, nv_id)
    if not nv:
        raise HTTPException(404, "Không tìm thấy nhiệm vụ")

    # Chỉ người nhận hoặc lãnh đạo/admin được cập nhật
    if (current_user.vai_tro == "can_bo"
            and nv.nguoi_nhan_id != current_user.id):
        raise HTTPException(403, "Chỉ người được giao mới cập nhật được")

    # Chỉ lãnh đạo/admin mới được hủy
    if (req.trang_thai == "DA_HUY"
            and current_user.vai_tro == "can_bo"):
        raise HTTPException(403, "Chỉ lãnh đạo mới được hủy nhiệm vụ")

    nv = await update_trang_thai(db, nv_id, req.trang_thai, req.ket_qua)
    return {"status": "ok", "data": _nv_to_dict(nv)}


@router.delete("/nhiem-vu/{nv_id}", status_code=204)
async def xoa_nhiem_vu(
    nv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(
        require_role(["lanh_dao", "admin"])
    ),
):
    """Lãnh đạo/Admin xóa nhiệm vụ."""
    ok = await delete_nhiem_vu(db, nv_id)
    if not ok:
        raise HTTPException(404, "Không tìm thấy nhiệm vụ")


# ── KPI Endpoints ─────────────────────────────────────────────────────────────

@router.get("/kpi")
async def kpi_tat_ca(
    tu_ngay: Optional[date] = None,
    den_ngay: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(
        require_role(["lanh_dao", "admin"])
    ),
):
    """KPI tất cả cán bộ — chỉ lãnh đạo/admin."""
    data = await get_kpi_all(db, tu_ngay=tu_ngay, den_ngay=den_ngay)
    return {"status": "ok", "total": len(data), "data": data}


@router.get("/kpi/me")
async def kpi_ban_than(
    tu_ngay: Optional[date] = None,
    den_ngay: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    """Cán bộ xem KPI của chính mình."""
    data = await get_kpi_one(db, current_user.id, tu_ngay, den_ngay)
    data["can_bo"] = {
        "id": str(current_user.id),
        "ho_ten": current_user.ho_ten,
    }
    return {"status": "ok", "data": data}


@router.get("/kpi/{user_id}")
async def kpi_mot_can_bo(
    user_id: UUID,
    tu_ngay: Optional[date] = None,
    den_ngay: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(
        require_role(["lanh_dao", "admin"])
    ),
):
    """KPI 1 cán bộ cụ thể — chỉ lãnh đạo/admin."""
    from sqlalchemy import select
    from src.db.models import NguoiDung as ND
    cb = (await db.execute(select(ND).where(ND.id == user_id))).scalar_one_or_none()
    if not cb:
        raise HTTPException(404, "Không tìm thấy cán bộ")

    data = await get_kpi_one(db, user_id, tu_ngay, den_ngay)
    data["can_bo"] = {"id": str(cb.id), "ho_ten": cb.ho_ten}
    return {"status": "ok", "data": data}

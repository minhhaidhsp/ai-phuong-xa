"""
src/report/kpi.py
Sprint 7 - Tính KPI cán bộ
Kết hợp dữ liệu từ ho_so + nhiem_vu
"""
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import HoSo, NguoiDung, ThuTucHanhChinh, NhiemVu


async def get_kpi_all(
    db: AsyncSession,
    tu_ngay: Optional[date] = None,
    den_ngay: Optional[date] = None,
) -> list:
    """
    KPI tất cả cán bộ trong khoảng thời gian.
    Mặc định: 30 ngày gần nhất.
    """
    den_ngay = den_ngay or date.today()
    tu_ngay = tu_ngay or (den_ngay - timedelta(days=30))

    # Lấy danh sách cán bộ có vai trò can_bo
    q_cb = select(NguoiDung).where(
        and_(NguoiDung.vai_tro == "can_bo", NguoiDung.is_active == True)
    )
    can_bos = (await db.execute(q_cb)).scalars().all()

    result = []
    for cb in can_bos:
        kpi = await get_kpi_one(db, cb.id, tu_ngay, den_ngay)
        kpi["can_bo"] = {"id": str(cb.id), "ho_ten": cb.ho_ten, "email": cb.email}
        result.append(kpi)

    # Sắp xếp theo điểm KPI tổng
    result.sort(key=lambda x: x["diem_kpi"], reverse=True)
    return result


async def get_kpi_one(
    db: AsyncSession,
    user_id: UUID,
    tu_ngay: Optional[date] = None,
    den_ngay: Optional[date] = None,
) -> dict:
    """
    KPI chi tiết 1 cán bộ.
    """
    den_ngay = den_ngay or date.today()
    tu_ngay = tu_ngay or (den_ngay - timedelta(days=30))

    # ── KPI từ Hồ Sơ ─────────────────────────────────────────
    q_hs = (
        select(
            func.count(HoSo.id).label("tong_ho_so"),
            func.sum(
                case((HoSo.trang_thai == "HOAN_THANH", 1), else_=0)
            ).label("da_hoan_thanh"),
            func.sum(
                case(
                    (
                        and_(
                            HoSo.trang_thai == "HOAN_THANH",
                            HoSo.ngay_hoan_thanh <= HoSo.han_giai_quyet
                        ),
                        1
                    ),
                    else_=0
                )
            ).label("dung_han"),
            func.sum(
                case(
                    (
                        and_(
                            HoSo.trang_thai.not_in(["HOAN_THANH", "TU_CHOI"]),
                            HoSo.han_giai_quyet < den_ngay
                        ),
                        1
                    ),
                    else_=0
                )
            ).label("qua_han"),
            func.avg(
                case(
                    (
                        HoSo.trang_thai == "HOAN_THANH",
                        func.extract(
                            'day',
                            HoSo.ngay_hoan_thanh - HoSo.ngay_tiep_nhan
                        )
                    ),
                    else_=None
                )
            ).label("tb_ngay_xu_ly"),
        )
        .where(
            and_(
                HoSo.can_bo_thu_ly_id == user_id,
                HoSo.ngay_tiep_nhan >= tu_ngay,
                HoSo.ngay_tiep_nhan <= den_ngay,
            )
        )
    )
    row_hs = (await db.execute(q_hs)).one()

    tong_hs = row_hs.tong_ho_so or 0
    da_ht = row_hs.da_hoan_thanh or 0
    dung_han = row_hs.dung_han or 0
    qua_han = row_hs.qua_han or 0
    tb_ngay = round(float(row_hs.tb_ngay_xu_ly), 1) if row_hs.tb_ngay_xu_ly else 0.0

    ty_le_ht = round(da_ht / tong_hs * 100, 1) if tong_hs > 0 else 0.0
    ty_le_dung_han = round(dung_han / da_ht * 100, 1) if da_ht > 0 else 0.0

    # ── KPI từ Nhiệm vụ ───────────────────────────────────────
    q_nv = (
        select(
            func.count(NhiemVu.id).label("tong_nhiem_vu"),
            func.sum(
                case((NhiemVu.trang_thai == "HOAN_THANH", 1), else_=0)
            ).label("nv_hoan_thanh"),
            func.sum(
                case(
                    (
                        and_(
                            NhiemVu.trang_thai == "HOAN_THANH",
                            NhiemVu.ngay_hoan_thanh_thuc_te <= NhiemVu.han_hoan_thanh
                        ),
                        1
                    ),
                    else_=0
                )
            ).label("nv_dung_han"),
        )
        .where(
            and_(
                NhiemVu.nguoi_nhan_id == user_id,
                NhiemVu.ngay_giao >= tu_ngay,
                NhiemVu.ngay_giao <= den_ngay,
                NhiemVu.trang_thai != "DA_HUY",
            )
        )
    )
    row_nv = (await db.execute(q_nv)).one()

    tong_nv = row_nv.tong_nhiem_vu or 0
    nv_ht = row_nv.nv_hoan_thanh or 0
    nv_dung_han = row_nv.nv_dung_han or 0
    ty_le_nv_dung_han = round(nv_dung_han / nv_ht * 100, 1) if nv_ht > 0 else 0.0

    # ── Tính điểm KPI tổng (0-100) ───────────────────────────
    # Công thức: 50% tỷ lệ đúng hạn hồ sơ + 30% khối lượng + 20% nhiệm vụ
    diem_dung_han = ty_le_dung_han * 0.5
    diem_khoi_luong = min(tong_hs / 10 * 30, 30)  # max 30đ khi >= 10 hs
    diem_nhiem_vu = ty_le_nv_dung_han * 0.2
    diem_kpi = round(diem_dung_han + diem_khoi_luong + diem_nhiem_vu, 1)

    return {
        "tu_ngay": str(tu_ngay),
        "den_ngay": str(den_ngay),
        # Hồ sơ
        "ho_so": {
            "tong": tong_hs,
            "hoan_thanh": da_ht,
            "dung_han": dung_han,
            "qua_han": qua_han,
            "ty_le_hoan_thanh_pct": ty_le_ht,
            "ty_le_dung_han_pct": ty_le_dung_han,
            "tb_ngay_xu_ly": tb_ngay,
        },
        # Nhiệm vụ
        "nhiem_vu": {
            "tong": tong_nv,
            "hoan_thanh": nv_ht,
            "dung_han": nv_dung_han,
            "ty_le_dung_han_pct": ty_le_nv_dung_han,
        },
        # Điểm tổng
        "diem_kpi": diem_kpi,
        "xep_loai": _xep_loai(diem_kpi),
    }


def _xep_loai(diem: float) -> str:
    if diem >= 90:
        return "XUAT_SAC"
    elif diem >= 75:
        return "TOT"
    elif diem >= 60:
        return "KHA"
    elif diem >= 50:
        return "TRUNG_BINH"
    else:
        return "YEU"

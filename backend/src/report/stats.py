"""
src/report/stats.py
Sprint 6 - Thong ke ho so cho Dashboard & Bao cao
"""
from datetime import date, timedelta
from typing import Optional
from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import HoSo, NguoiDung, ThuTucHanhChinh
from loguru import logger


# ── Tong quan Dashboard ───────────────────────────────────────────────────────

async def get_dashboard_stats(db: AsyncSession) -> dict:
    """
    Tong hop thong ke cho Dashboard lanh dao.
    Tra ve mot dict day du de render Frontend.
    """
    today = date.today()

    # 1. Tong so ho so theo trang thai
    q_trang_thai = (
        select(HoSo.trang_thai, func.count().label("so_luong"))
        .group_by(HoSo.trang_thai)
    )
    rows = (await db.execute(q_trang_thai)).all()
    theo_trang_thai = {r.trang_thai: r.so_luong for r in rows}

    tong_ho_so = sum(theo_trang_thai.values())
    dang_xu_ly = (
        theo_trang_thai.get("DANG_XU_LY", 0)
        + theo_trang_thai.get("YEU_CAU_BO_SUNG", 0)
        + theo_trang_thai.get("CHO_PHE_DUYET", 0)
        + theo_trang_thai.get("CHO_TIEP_NHAN", 0)
    )
    hoan_thanh = theo_trang_thai.get("HOAN_THANH", 0)
    tu_choi = theo_trang_thai.get("TU_CHOI", 0)

    # 2. Ho so qua han (han_giai_quyet < today, chua hoan thanh)
    q_qua_han = (
        select(func.count())
        .where(
            and_(
                HoSo.han_giai_quyet < today,
                HoSo.trang_thai.not_in(["HOAN_THANH", "TU_CHOI"])
            )
        )
    )
    qua_han = (await db.execute(q_qua_han)).scalar() or 0

    # 3. Ho so sap han (con 1-2 ngay)
    ngay_sap_han = today + timedelta(days=2)
    q_sap_han = (
        select(func.count())
        .where(
            and_(
                HoSo.han_giai_quyet >= today,
                HoSo.han_giai_quyet <= ngay_sap_han,
                HoSo.trang_thai.not_in(["HOAN_THANH", "TU_CHOI"])
            )
        )
    )
    sap_han = (await db.execute(q_sap_han)).scalar() or 0

    # 4. Ho so theo linh vuc
    q_linh_vuc = (
        select(ThuTucHanhChinh.linh_vuc, func.count().label("so_luong"))
        .join(HoSo, HoSo.thu_tuc_id == ThuTucHanhChinh.id)
        .group_by(ThuTucHanhChinh.linh_vuc)
        .order_by(func.count().desc())
    )
    rows_lv = (await db.execute(q_linh_vuc)).all()
    theo_linh_vuc = [{"linh_vuc": r.linh_vuc, "so_luong": r.so_luong} for r in rows_lv]

    # 5. Ho so tiep nhan trong 30 ngay qua (trend)
    ngay_30 = today - timedelta(days=30)
    q_trend = (
        select(
            func.date(HoSo.ngay_tiep_nhan).label("ngay"),
            func.count().label("so_luong")
        )
        .where(HoSo.ngay_tiep_nhan >= ngay_30)
        .group_by(func.date(HoSo.ngay_tiep_nhan))
        .order_by(func.date(HoSo.ngay_tiep_nhan))
    )
    rows_trend = (await db.execute(q_trend)).all()
    trend_30_ngay = [
        {"ngay": str(r.ngay), "so_luong": r.so_luong}
        for r in rows_trend
    ]

    # 6. Ti le giai quyet dung han (trong 30 ngay qua)
    q_dung_han = (
        select(
            func.count().label("tong"),
            func.sum(
                case(
                    (HoSo.ngay_hoan_thanh <= HoSo.han_giai_quyet, 1),
                    else_=0
                )
            ).label("dung_han")
        )
        .where(
            and_(
                HoSo.trang_thai == "HOAN_THANH",
                HoSo.ngay_tiep_nhan >= ngay_30
            )
        )
    )
    row_dh = (await db.execute(q_dung_han)).one()
    tong_ht = row_dh.tong or 0
    dung_han_ct = row_dh.dung_han or 0
    ty_le_dung_han = round(dung_han_ct / tong_ht * 100, 1) if tong_ht > 0 else 0.0

    return {
        "ngay_cap_nhat": str(today),
        "tong_ho_so": tong_ho_so,
        "dang_xu_ly": dang_xu_ly,
        "hoan_thanh": hoan_thanh,
        "tu_choi": tu_choi,
        "qua_han": qua_han,
        "sap_han": sap_han,
        "theo_trang_thai": theo_trang_thai,
        "theo_linh_vuc": theo_linh_vuc,
        "trend_30_ngay": trend_30_ngay,
        "ty_le_dung_han_pct": ty_le_dung_han,
    }


# ── Canh bao ho so qua/sap han ────────────────────────────────────────────────

async def get_alerts(db: AsyncSession, ngay_canh_bao: int = 2) -> dict:
    """
    Lay danh sach ho so can canh bao:
    - da_qua_han: han_giai_quyet < today
    - sap_han: con <= ngay_canh_bao ngay
    """
    today = date.today()
    ngay_limit = today + timedelta(days=ngay_canh_bao)

    # Ho so da qua han
    q_qua = (
        select(
            HoSo.id, HoSo.ma_ho_so, HoSo.trang_thai,
            HoSo.han_giai_quyet, HoSo.cong_dan_ho_ten,
            ThuTucHanhChinh.ten.label("ten_thu_tuc"),
            NguoiDung.ho_ten.label("can_bo_xu_ly"),
        )
        .outerjoin(ThuTucHanhChinh, HoSo.thu_tuc_id == ThuTucHanhChinh.id)
        .outerjoin(NguoiDung, HoSo.can_bo_thu_ly_id == NguoiDung.id)
        .where(
            and_(
                HoSo.han_giai_quyet < today,
                HoSo.trang_thai.not_in(["HOAN_THANH", "TU_CHOI"])
            )
        )
        .order_by(HoSo.han_giai_quyet)
    )
    rows_qua = (await db.execute(q_qua)).all()

    # Ho so sap han
    q_sap = (
        select(
            HoSo.id, HoSo.ma_ho_so, HoSo.trang_thai,
            HoSo.han_giai_quyet, HoSo.cong_dan_ho_ten,
            ThuTucHanhChinh.ten.label("ten_thu_tuc"),
            NguoiDung.ho_ten.label("can_bo_xu_ly"),
        )
        .outerjoin(ThuTucHanhChinh, HoSo.thu_tuc_id == ThuTucHanhChinh.id)
        .outerjoin(NguoiDung, HoSo.can_bo_thu_ly_id == NguoiDung.id)
        .where(
            and_(
                HoSo.han_giai_quyet >= today,
                HoSo.han_giai_quyet <= ngay_limit,
                HoSo.trang_thai.not_in(["HOAN_THANH", "TU_CHOI"])
            )
        )
        .order_by(HoSo.han_giai_quyet)
    )
    rows_sap = (await db.execute(q_sap)).all()

    def row_to_dict(r):
        so_ngay = (r.han_giai_quyet - today).days
        return {
            "ma_ho_so": r.ma_ho_so,
            "trang_thai": r.trang_thai,
            "ten_thu_tuc": r.ten_thu_tuc or "—",
            "cong_dan": r.cong_dan_ho_ten,
            "han_giai_quyet": str(r.han_giai_quyet),
            "so_ngay_con_lai": so_ngay,
            "can_bo_xu_ly": r.can_bo_xu_ly or "Chưa giao",
        }

    return {
        "ngay_kiem_tra": str(today),
        "da_qua_han": [row_to_dict(r) for r in rows_qua],
        "sap_den_han": [row_to_dict(r) for r in rows_sap],
        "tong_can_xu_ly": len(rows_qua) + len(rows_sap),
    }


# ── Bao cao dinh ky ───────────────────────────────────────────────────────────

async def get_bao_cao_thang(
    db: AsyncSession,
    thang: int,
    nam: int
) -> dict:
    """
    Bao cao tong hop trong mot thang cu the.
    Dung de xuat PDF / Excel.
    """
    from calendar import monthrange
    ngay_dau = date(nam, thang, 1)
    ngay_cuoi = date(nam, thang, monthrange(nam, thang)[1])

    # Tiep nhan trong thang
    q_tiep_nhan = (
        select(func.count())
        .where(
            and_(
                HoSo.ngay_tiep_nhan >= ngay_dau,
                HoSo.ngay_tiep_nhan <= ngay_cuoi
            )
        )
    )
    tong_tiep_nhan = (await db.execute(q_tiep_nhan)).scalar() or 0

    # Hoan thanh trong thang
    q_ht = (
        select(func.count())
        .where(
            and_(
                HoSo.trang_thai == "HOAN_THANH",
                HoSo.ngay_hoan_thanh >= ngay_dau,
                HoSo.ngay_hoan_thanh <= ngay_cuoi
            )
        )
    )
    tong_hoan_thanh = (await db.execute(q_ht)).scalar() or 0

    # Tu choi trong thang
    q_tc = (
        select(func.count())
        .where(
            and_(
                HoSo.trang_thai == "TU_CHOI",
                HoSo.ngay_hoan_thanh >= ngay_dau,
                HoSo.ngay_hoan_thanh <= ngay_cuoi
            )
        )
    )
    tong_tu_choi = (await db.execute(q_tc)).scalar() or 0

    # Thong ke theo linh vuc (trong thang)
    q_lv = (
        select(ThuTucHanhChinh.linh_vuc, func.count().label("so_luong"))
        .join(HoSo, HoSo.thu_tuc_id == ThuTucHanhChinh.id)
        .where(
            and_(
                HoSo.ngay_tiep_nhan >= ngay_dau,
                HoSo.ngay_tiep_nhan <= ngay_cuoi
            )
        )
        .group_by(ThuTucHanhChinh.linh_vuc)
        .order_by(func.count().desc())
    )
    rows_lv = (await db.execute(q_lv)).all()
    theo_linh_vuc = [{"linh_vuc": r.linh_vuc, "so_luong": r.so_luong} for r in rows_lv]

    # Hieu suat can bo (top 10)
    q_cb = (
        select(
            NguoiDung.ho_ten,
            func.count(HoSo.id).label("so_ho_so"),
            func.sum(
                case((HoSo.trang_thai == "HOAN_THANH", 1), else_=0)
            ).label("da_xong"),
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
            ).label("dung_han")
        )
        .join(HoSo, HoSo.can_bo_thu_ly_id == NguoiDung.id)
        .where(
            and_(
                HoSo.ngay_tiep_nhan >= ngay_dau,
                HoSo.ngay_tiep_nhan <= ngay_cuoi
            )
        )
        .group_by(NguoiDung.id, NguoiDung.ho_ten)
        .order_by(func.count(HoSo.id).desc())
        .limit(10)
    )
    rows_cb = (await db.execute(q_cb)).all()
    hieu_suat_can_bo = [
        {
            "ho_ten": r.ho_ten,
            "so_ho_so": r.so_ho_so,
            "da_xong": r.da_xong or 0,
            "dung_han": r.dung_han or 0,
            "ty_le_dung_han": round((r.dung_han or 0) / r.da_xong * 100, 1) if r.da_xong else 0,
        }
        for r in rows_cb
    ]

    return {
        "thang": thang,
        "nam": nam,
        "tu_ngay": str(ngay_dau),
        "den_ngay": str(ngay_cuoi),
        "tong_tiep_nhan": tong_tiep_nhan,
        "tong_hoan_thanh": tong_hoan_thanh,
        "tong_tu_choi": tong_tu_choi,
        "con_xu_ly": tong_tiep_nhan - tong_hoan_thanh - tong_tu_choi,
        "theo_linh_vuc": theo_linh_vuc,
        "hieu_suat_can_bo": hieu_suat_can_bo,
    }

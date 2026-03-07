"""
src/api/report.py
Sprint 6 - Bao cao & Dashboard endpoints
"""
import io
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.core.dependencies import get_current_user, require_role
from src.db.models import NguoiDung
from src.report.stats import get_dashboard_stats, get_alerts, get_bao_cao_thang
from src.report.exporter import export_excel, export_pdf
from loguru import logger

router = APIRouter(prefix="/api/v1/report", tags=["Report"])


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard")
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    """
    Tong quan dashboard: so ho so, trang thai, linh vuc, trend 30 ngay.
    Tat ca vai tro deu xem duoc.
    """
    try:
        data = await get_dashboard_stats(db)
        return {"status": "ok", "data": data}
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Canh bao ─────────────────────────────────────────────────────────────────

@router.get("/alerts")
async def alerts(
    ngay_canh_bao: int = Query(default=2, ge=1, le=7,
                               description="Canh bao truoc bao nhieu ngay"),
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    """
    Canh bao ho so da qua han va sap den han.
    """
    try:
        data = await get_alerts(db, ngay_canh_bao=ngay_canh_bao)
        return {"status": "ok", "data": data}
    except Exception as e:
        logger.error(f"Alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Bao cao thang ─────────────────────────────────────────────────────────────

@router.get("/thang")
async def bao_cao_thang(
    thang: int = Query(default=None, ge=1, le=12),
    nam: int = Query(default=None, ge=2020, le=2099),
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    """
    Thong ke tong hop trong mot thang (mac dinh: thang hien tai).
    """
    today = date.today()
    thang = thang or today.month
    nam = nam or today.year

    try:
        data = await get_bao_cao_thang(db, thang=thang, nam=nam)
        return {"status": "ok", "data": data}
    except Exception as e:
        logger.error(f"Bao cao thang error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Xuat Excel ────────────────────────────────────────────────────────────────

@router.get("/export/excel")
async def export_excel_endpoint(
    thang: int = Query(default=None, ge=1, le=12),
    nam: int = Query(default=None, ge=2020, le=2099),
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(
        require_role(["lanh_dao", "admin"])
    ),
):
    """
    Xuat bao cao thang ra file .xlsx.
    Chi lanh_dao va admin.
    """
    today = date.today()
    thang = thang or today.month
    nam = nam or today.year

    try:
        bao_cao = await get_bao_cao_thang(db, thang=thang, nam=nam)
        xlsx_bytes = export_excel(bao_cao)
        filename = f"bao_cao_{thang:02d}_{nam}.xlsx"
        return StreamingResponse(
            io.BytesIO(xlsx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except RuntimeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        logger.error(f"Export Excel error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Xuat PDF ─────────────────────────────────────────────────────────────────

@router.get("/export/pdf")
async def export_pdf_endpoint(
    thang: int = Query(default=None, ge=1, le=12),
    nam: int = Query(default=None, ge=2020, le=2099),
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(
        require_role(["lanh_dao", "admin"])
    ),
):
    """
    Xuat bao cao thang ra file .pdf.
    Chi lanh_dao va admin.
    """
    today = date.today()
    thang = thang or today.month
    nam = nam or today.year

    try:
        bao_cao = await get_bao_cao_thang(db, thang=thang, nam=nam)
        pdf_bytes = export_pdf(bao_cao)
        filename = f"bao_cao_{thang:02d}_{nam}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except RuntimeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        logger.error(f"Export PDF error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""
src/lgsp/client.py
Sprint 8 — LGSP Integration (Cổng dịch vụ công TP.HCM)

Mock server chạy tại /lgsp-mock/... trên cùng server.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

import httpx
from loguru import logger

from src.core.config import settings

# ── Config ────────────────────────────────────────────────────────────────

LGSP_BASE_URL  = getattr(settings, "LGSP_BASE_URL",  "http://localhost:8000/lgsp-mock")
LGSP_API_KEY   = getattr(settings, "LGSP_API_KEY",   "dev-mock-key")
LGSP_WARD_CODE = getattr(settings, "LGSP_WARD_CODE", "79280001")

# ── Trạng thái mapping ────────────────────────────────────────────────────

TRANG_THAI_TO_LGSP = {
    "CHO_TIEP_NHAN":   "RECEIVED",
    "DANG_XU_LY":      "PROCESSING",
    "YEU_CAU_BO_SUNG": "ADDITIONAL_DOCS_REQUIRED",
    "CHO_PHE_DUYET":   "PENDING_APPROVAL",
    "TU_CHOI":         "REJECTED",
    "HOAN_THANH":      "COMPLETED",
}

LGSP_TO_TRANG_THAI = {v: k for k, v in TRANG_THAI_TO_LGSP.items()}


# ── LGSP Client ───────────────────────────────────────────────────────────

class LGSPClient:
    def __init__(self):
        # Đảm bảo không có trailing slash
        self.base_url = LGSP_BASE_URL.rstrip("/")
        self.headers = {
            "X-API-Key": LGSP_API_KEY,
            "X-Ward-Code": LGSP_WARD_CODE,
            "Content-Type": "application/json",
        }

    async def ping(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(
                    f"{self.base_url}/api/health",
                    headers=self.headers,
                )
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"LGSP ping failed: {e}")
            return False

    async def get_pending_ho_so(self, limit: int = 50) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.base_url}/api/v1/ho-so/pending",
                    headers=self.headers,
                    params={"ward_code": LGSP_WARD_CODE, "limit": limit},
                )
                resp.raise_for_status()
                return resp.json().get("items", [])
        except httpx.HTTPError as e:
            logger.error(f"LGSP get_pending error: {e}")
            return []

    async def sync_trang_thai(
        self,
        lgsp_ma_ho_so: str,
        trang_thai_moi: str,
        ghi_chu: Optional[str] = None,
    ) -> bool:
        lgsp_status = TRANG_THAI_TO_LGSP.get(trang_thai_moi)
        if not lgsp_status:
            logger.warning(f"Không map được trạng thái: {trang_thai_moi}")
            return False

        payload = {
            "ma_ho_so": lgsp_ma_ho_so,
            "status": lgsp_status,
            "updated_at": datetime.now().isoformat(),
            "note": ghi_chu or "",
            "ward_code": LGSP_WARD_CODE,
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{self.base_url}/api/v1/ho-so/update-status",
                    headers=self.headers,
                    json=payload,
                )
                resp.raise_for_status()
                logger.info(f"LGSP sync OK: {lgsp_ma_ho_so} → {lgsp_status}")
                return True
        except httpx.HTTPError as e:
            logger.error(f"LGSP sync error for {lgsp_ma_ho_so}: {e}")
            return False

    async def acknowledge(self, lgsp_ma_ho_so: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{self.base_url}/api/v1/ho-so/acknowledge",
                    headers=self.headers,
                    json={"ma_ho_so": lgsp_ma_ho_so, "ward_code": LGSP_WARD_CODE},
                )
                return resp.status_code == 200
        except Exception as e:
            logger.error(f"LGSP acknowledge error: {e}")
            return False


# ── Ingestion service (FR-INT-001) ────────────────────────────────────────

async def ingest_from_lgsp(db) -> dict:
    from sqlalchemy import select
    from src.db.models import HoSo, ThuTucHanhChinh
    from src.core.intake import tinh_han_giai_quyet

    client = LGSPClient()

    if not await client.ping():
        logger.warning("LGSP không kết nối được — skip ingest")
        return {"created": 0, "skipped": 0, "errors": 1, "reason": "LGSP offline"}

    pending = await client.get_pending_ho_so()
    created = skipped = errors = 0

    for item in pending:
        lgsp_id = item.get("ma_ho_so_lgsp")
        if not lgsp_id:
            errors += 1
            continue

        # Idempotent check
        existing = (await db.execute(
            select(HoSo).where(HoSo.ma_ho_so == f"LGSP-{lgsp_id}")
        )).scalar_one_or_none()
        if existing:
            skipped += 1
            continue

        ma_thu_tuc = item.get("ma_thu_tuc", "")
        thu_tuc = (await db.execute(
            select(ThuTucHanhChinh).where(ThuTucHanhChinh.ma_thu_tuc == ma_thu_tuc)
        )).scalar_one_or_none()

        if not thu_tuc:
            logger.warning(f"LGSP: không tìm thấy thủ tục {ma_thu_tuc}")
            errors += 1
            continue

        try:
            ngay_tiep_nhan = date.today()
            hs = HoSo(
                ma_ho_so=f"LGSP-{lgsp_id}",
                thu_tuc_id=thu_tuc.id,
                trang_thai="CHO_TIEP_NHAN",
                nguon_tiep_nhan="lgsp",
                cong_dan_ho_ten=item.get("ho_ten", ""),
                cong_dan_cccd=item.get("cccd", ""),
                cong_dan_dia_chi=item.get("dia_chi", ""),
                cong_dan_sdt=item.get("sdt", ""),
                ngay_tiep_nhan=ngay_tiep_nhan,
                han_giai_quyet=tinh_han_giai_quyet(ngay_tiep_nhan, thu_tuc.thoi_han_ngay),
            )
            db.add(hs)
            await db.commit()
            await client.acknowledge(lgsp_id)
            created += 1
            logger.info(f"LGSP ingest: tạo hồ sơ LGSP-{lgsp_id}")
        except Exception as e:
            logger.error(f"LGSP ingest error for {lgsp_id}: {e}")
            await db.rollback()
            errors += 1

    return {"created": created, "skipped": skipped, "errors": errors}

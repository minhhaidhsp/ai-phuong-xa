"""
src/api/lgsp.py
Sprint 8 — LGSP endpoints + Mock server tích hợp
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.core.dependencies import get_current_user, require_role
from src.db.models import NguoiDung
from src.lgsp.client import LGSPClient, TRANG_THAI_TO_LGSP, ingest_from_lgsp
from loguru import logger

router = APIRouter(prefix="/api/v1/lgsp", tags=["LGSP Integration"])

# ── Mock LGSP server (dùng cho dev/test) ─────────────────────────────────
mock_router = APIRouter(prefix="/lgsp-mock", tags=["LGSP Mock Server"])

# In-memory mock data
_mock_pending: list[dict] = [
    {
        "ma_ho_so_lgsp": "LGSP-2026030801",
        "ma_thu_tuc": "HT-001",
        "ho_ten": "Nguyễn Thị Bình",
        "cccd": "079304012345",
        "dia_chi": "123 Nguyễn Văn Cừ, P.1, Q.5",
        "sdt": "0901234567",
        "ngay_nop": str(date.today()),
        "status": "PENDING",
    },
    {
        "ma_ho_so_lgsp": "LGSP-2026030802",
        "ma_thu_tuc": "CT-001",
        "ho_ten": "Trần Văn Minh",
        "cccd": "079304067890",
        "dia_chi": "456 Lê Văn Sỹ, P.3, Q.3",
        "sdt": "0912345678",
        "ngay_nop": str(date.today()),
        "status": "PENDING",
    },
]
_mock_acknowledged: set[str] = set()
_mock_status_updates: list[dict] = []


@mock_router.get("/api/health")
async def mock_health():
    return {"status": "ok", "service": "LGSP Mock Server"}


@mock_router.get("/api/v1/ho-so/pending")
async def mock_get_pending(ward_code: str = "", limit: int = 50):
    items = [i for i in _mock_pending
             if i["ma_ho_so_lgsp"] not in _mock_acknowledged
             and i["status"] == "PENDING"]
    return {"items": items[:limit], "total": len(items)}


@mock_router.post("/api/v1/ho-so/update-status")
async def mock_update_status(payload: dict):
    _mock_status_updates.append(payload)
    return {"status": "ok", "message": "Status updated"}


@mock_router.post("/api/v1/ho-so/acknowledge")
async def mock_acknowledge(payload: dict):
    _mock_acknowledged.add(payload.get("ma_ho_so", ""))
    return {"status": "ok"}


@mock_router.get("/api/v1/status-log")
async def mock_status_log():
    """Xem log các status update đã nhận (dùng để test)."""
    return {"updates": _mock_status_updates}


# ── LGSP Integration Endpoints ────────────────────────────────────────────

@router.get("/status")
async def lgsp_status(
    current_user: NguoiDung = Depends(require_role(["admin"])),
):
    """Kiểm tra kết nối LGSP."""
    client = LGSPClient()
    online = await client.ping()
    return {
        "status": "ok",
        "lgsp_online": online,
        "lgsp_url": client.base_url,
    }


@router.post("/ingest")
async def trigger_ingest(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["admin"])),
):
    """
    Kéo thủ công hồ sơ mới từ LGSP.
    Thông thường chạy tự động qua scheduler.
    """
    result = await ingest_from_lgsp(db)
    logger.info(f"LGSP manual ingest: {result}")
    return {"status": "ok", "data": result}


class SyncStatusRequest(BaseModel):
    ma_ho_so_noi_bo: str   # mã hồ sơ trong hệ thống (có prefix LGSP-)
    trang_thai_moi: str
    ghi_chu: Optional[str] = None


@router.post("/sync-status")
async def sync_status_to_lgsp(
    req: SyncStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["admin", "lanh_dao"])),
):
    """
    Đồng bộ trạng thái hồ sơ từ hệ thống nội bộ lên LGSP.
    FR-INT-002
    """
    if req.trang_thai_moi not in TRANG_THAI_TO_LGSP:
        raise HTTPException(
            400,
            f"Trạng thái không hợp lệ. Hợp lệ: {list(TRANG_THAI_TO_LGSP.keys())}"
        )

    # Chỉ sync hồ sơ có nguồn lgsp
    if not req.ma_ho_so_noi_bo.startswith("LGSP-"):
        raise HTTPException(400, "Chỉ sync được hồ sơ nguồn LGSP (ma_ho_so bắt đầu bằng LGSP-)")

    lgsp_id = req.ma_ho_so_noi_bo.replace("LGSP-", "")

    client = LGSPClient()
    ok = await client.sync_trang_thai(lgsp_id, req.trang_thai_moi, req.ghi_chu)

    if not ok:
        raise HTTPException(502, "Không sync được lên LGSP — kiểm tra kết nối")

    return {
        "status": "ok",
        "data": {
            "ma_ho_so": req.ma_ho_so_noi_bo,
            "trang_thai": req.trang_thai_moi,
            "lgsp_status": TRANG_THAI_TO_LGSP[req.trang_thai_moi],
            "synced": True,
        }
    }


@router.get("/pending")
async def get_lgsp_pending(
    current_user: NguoiDung = Depends(require_role(["admin"])),
):
    """Xem danh sách hồ sơ đang chờ nhận từ LGSP."""
    client = LGSPClient()
    items = await client.get_pending_ho_so()
    return {"status": "ok", "total": len(items), "data": items}

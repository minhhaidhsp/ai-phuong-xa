# src/api/ho_so.py
# Endpoints quản lý hồ sơ hành chính
#
# Public (không cần login):
#   GET  /api/v1/ho-so/tra-cuu/{ma}     → tra cứu trạng thái
#
# Protected (cần JWT token):
#   POST /api/v1/ho-so/tiep-nhan        → tiếp nhận hồ sơ mới
#   GET  /api/v1/ho-so                  → danh sách hồ sơ (có lọc)
#   GET  /api/v1/ho-so/{id}             → chi tiết 1 hồ sơ
#   PUT  /api/v1/ho-so/{id}/trang-thai  → cập nhật trạng thái

from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.db.database import get_db
from src.db.models import NguoiDung, TrangThaiHoSo, NhatKyHeThong
from src.db.repositories.ho_so_repo import (
    get_ho_so_by_id, get_ho_so_by_ma,
    get_danh_sach_ho_so, create_ho_so,
    update_trang_thai, is_valid_transition,
)
from src.db.repositories.user_repo import get_user_by_id
from src.core.dependencies import require_can_bo, require_lanh_dao
from src.core.intake import gen_ma_ho_so, tinh_han_giai_quyet

router = APIRouter(prefix="/api/v1/ho-so", tags=["📋 Hồ Sơ"])


# ── Pydantic Schemas ──────────────────────────────────────────────────

class TiepNhanRequest(BaseModel):
    """Request body khi tiếp nhận hồ sơ mới"""
    # Thông tin thủ tục
    thu_tuc_id: str             # UUID của thủ tục hành chính
    thu_tuc_ten: str            # Tên thủ tục (để hiển thị)
    linh_vuc: str               # ho_tich | cu_tru | dat_dai | ...
    thoi_han_ngay: int          # Số ngày giải quyết

    # Thông tin công dân
    cong_dan_ho_ten: str
    cong_dan_cccd: str
    cong_dan_sdt: Optional[str] = None
    cong_dan_email: Optional[str] = None
    cong_dan_dia_chi: Optional[str] = None
    cong_dan_ngay_sinh: Optional[str] = None

    # Ghi chú
    ghi_chu_noi_bo: Optional[str] = None


class UpdateTrangThaiRequest(BaseModel):
    """Request body khi cập nhật trạng thái hồ sơ"""
    trang_thai_moi: str         # Trạng thái mới
    ghi_chu: Optional[str] = None


class HoSoPublicResponse(BaseModel):
    """Response công khai — che thông tin nhạy cảm nội bộ"""
    ma_ho_so: str
    trang_thai: str
    ngay_tiep_nhan: datetime
    han_giai_quyet: datetime
    ngay_hoan_thanh: Optional[datetime] = None
    thong_bao: str              # Thông báo thân thiện cho công dân


class HoSoDetailResponse(BaseModel):
    """Response đầy đủ cho cán bộ — có thông tin nội bộ"""
    id: str
    ma_ho_so: str
    thu_tuc_id: str
    trang_thai: str
    cong_dan_ho_ten: str
    cong_dan_cccd: str
    cong_dan_sdt: Optional[str] = None
    cong_dan_email: Optional[str] = None
    can_bo_thu_ly_id: Optional[str] = None
    can_bo_ten: Optional[str] = None    # Tên cán bộ phụ trách
    ngay_tiep_nhan: datetime
    han_giai_quyet: datetime
    ngay_hoan_thanh: Optional[datetime] = None
    ai_phan_loai: Optional[str] = None
    ai_confidence: Optional[float] = None
    ghi_chu_noi_bo: Optional[str] = None


class DanhSachResponse(BaseModel):
    """Response danh sách hồ sơ kèm thông tin pagination"""
    items: list[HoSoDetailResponse]
    total: int
    skip: int
    limit: int


# ── Helper: tạo thông báo thân thiện cho công dân ────────────────────
TRANG_THAI_MESSAGES = {
    TrangThaiHoSo.CHO_TIEP_NHAN:   "Hồ sơ đang chờ tiếp nhận",
    TrangThaiHoSo.DANG_XU_LY:      "Hồ sơ đang được xử lý",
    TrangThaiHoSo.YEU_CAU_BO_SUNG: "Hồ sơ cần bổ sung thêm giấy tờ. Vui lòng liên hệ bộ phận tiếp nhận",
    TrangThaiHoSo.CHO_PHE_DUYET:   "Hồ sơ đang chờ lãnh đạo phê duyệt",
    TrangThaiHoSo.HOAN_THANH:      "Hồ sơ đã được giải quyết. Mời đến nhận kết quả",
    TrangThaiHoSo.TU_CHOI:         "Hồ sơ không đủ điều kiện giải quyết. Vui lòng liên hệ để biết thêm chi tiết",
}


# ── Endpoints ─────────────────────────────────────────────────────────

@router.get("/tra-cuu/{ma_ho_so}", response_model=HoSoPublicResponse)
async def tra_cuu_ho_so(
    ma_ho_so: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Tra cứu trạng thái hồ sơ — KHÔNG cần đăng nhập.
    Công dân dùng mã hồ sơ (VD: HT-20260307-A1B2) để tra cứu.
    Chỉ trả thông tin công khai, không lộ dữ liệu nội bộ.
    """
    ho_so = await get_ho_so_by_ma(db, ma_ho_so)
    if not ho_so:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ có mã: {ma_ho_so}"
        )
    return HoSoPublicResponse(
        ma_ho_so=ho_so.ma_ho_so,
        trang_thai=ho_so.trang_thai,
        ngay_tiep_nhan=ho_so.ngay_tiep_nhan,
        han_giai_quyet=ho_so.han_giai_quyet,
        ngay_hoan_thanh=ho_so.ngay_hoan_thanh,
        thong_bao=TRANG_THAI_MESSAGES.get(ho_so.trang_thai, "Đang xử lý"),
    )


@router.post("/tiep-nhan", response_model=HoSoDetailResponse,
             status_code=status.HTTP_201_CREATED)
async def tiep_nhan_ho_so(
    body: TiepNhanRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    # require_can_bo: chỉ cán bộ trở lên mới tiếp nhận được
    current_user: Annotated[NguoiDung, Depends(require_can_bo)],
):
    """
    Tiếp nhận hồ sơ mới.
    - Tự động sinh mã hồ sơ duy nhất
    - Tự động tính hạn giải quyết
    - Gán cán bộ tiếp nhận là người đang đăng nhập
    - Ghi audit log
    """
    # Bước 1: Sinh mã hồ sơ
    ma_ho_so = gen_ma_ho_so(body.linh_vuc, body.cong_dan_cccd)

    # Bước 2: Tính hạn giải quyết
    han_giai_quyet = tinh_han_giai_quyet(body.thoi_han_ngay)

    # Bước 3: Tạo hồ sơ trong DB
    ho_so = await create_ho_so(
        db,
        ma_ho_so=ma_ho_so,
        thu_tuc_id=body.thu_tuc_id,
        can_bo_thu_ly_id=current_user.id,  # Gán cán bộ tiếp nhận
        cong_dan_ho_ten=body.cong_dan_ho_ten,
        cong_dan_cccd=body.cong_dan_cccd,
        cong_dan_sdt=body.cong_dan_sdt,
        cong_dan_email=body.cong_dan_email,
        cong_dan_dia_chi=body.cong_dan_dia_chi,
        trang_thai=TrangThaiHoSo.DANG_XU_LY,  # Tiếp nhận xong → xử lý luôn
        han_giai_quyet=han_giai_quyet,
        ghi_chu_noi_bo=body.ghi_chu_noi_bo,
    )

    # Bước 4: Ghi audit log
    log = NhatKyHeThong(
        nguoi_dung_id=current_user.id,
        hanh_dong="TIEP_NHAN_HO_SO",
        doi_tuong="ho_so",
        doi_tuong_id=ho_so.id,
        du_lieu_moi={
            "ma_ho_so": ma_ho_so,
            "cong_dan": body.cong_dan_ho_ten,
            "thu_tuc_id": body.thu_tuc_id,
        },
    )
    db.add(log)
    await db.commit()

    # Bước 5: Reload để lấy relationships
    ho_so = await get_ho_so_by_id(db, ho_so.id)

    return HoSoDetailResponse(
        id=ho_so.id,
        ma_ho_so=ho_so.ma_ho_so,
        thu_tuc_id=ho_so.thu_tuc_id,
        trang_thai=ho_so.trang_thai,
        cong_dan_ho_ten=ho_so.cong_dan_ho_ten,
        cong_dan_cccd=ho_so.cong_dan_cccd,
        cong_dan_sdt=ho_so.cong_dan_sdt,
        cong_dan_email=ho_so.cong_dan_email,
        can_bo_thu_ly_id=ho_so.can_bo_thu_ly_id,
        can_bo_ten=ho_so.can_bo_thu_ly.ho_ten if ho_so.can_bo_thu_ly else None,
        ngay_tiep_nhan=ho_so.ngay_tiep_nhan,
        han_giai_quyet=ho_so.han_giai_quyet,
        ngay_hoan_thanh=ho_so.ngay_hoan_thanh,
        ai_phan_loai=ho_so.ai_phan_loai,
        ai_confidence=ho_so.ai_confidence,
        ghi_chu_noi_bo=ho_so.ghi_chu_noi_bo,
    )


@router.get("", response_model=DanhSachResponse)
async def get_danh_sach(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[NguoiDung, Depends(require_can_bo)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    trang_thai: Optional[str] = Query(default=None),
    # can_bo_id filter: cán bộ thường chỉ xem của mình
    # lãnh đạo/admin xem tất cả
):
    """
    Lấy danh sách hồ sơ có lọc và phân trang.
    - Cán bộ: chỉ thấy hồ sơ mình phụ trách
    - Lãnh đạo/Admin: thấy tất cả
    """
    from src.db.models import VaiTro

    # Cán bộ thường chỉ xem hồ sơ của mình
    can_bo_filter = None
    if current_user.vai_tro == VaiTro.CAN_BO:
        can_bo_filter = current_user.id

    items, total = await get_danh_sach_ho_so(
        db, skip=skip, limit=limit,
        trang_thai=trang_thai,
        can_bo_id=can_bo_filter,
    )

    return DanhSachResponse(
        items=[
            HoSoDetailResponse(
                id=hs.id,
                ma_ho_so=hs.ma_ho_so,
                thu_tuc_id=hs.thu_tuc_id,
                trang_thai=hs.trang_thai,
                cong_dan_ho_ten=hs.cong_dan_ho_ten,
                cong_dan_cccd=hs.cong_dan_cccd,
                cong_dan_sdt=hs.cong_dan_sdt,
                cong_dan_email=hs.cong_dan_email,
                can_bo_thu_ly_id=hs.can_bo_thu_ly_id,
                can_bo_ten=hs.can_bo_thu_ly.ho_ten if hs.can_bo_thu_ly else None,
                ngay_tiep_nhan=hs.ngay_tiep_nhan,
                han_giai_quyet=hs.han_giai_quyet,
                ngay_hoan_thanh=hs.ngay_hoan_thanh,
                ai_phan_loai=hs.ai_phan_loai,
                ai_confidence=hs.ai_confidence,
                ghi_chu_noi_bo=hs.ghi_chu_noi_bo,
            )
            for hs in items
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{ho_so_id}", response_model=HoSoDetailResponse)
async def get_chi_tiet(
    ho_so_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[NguoiDung, Depends(require_can_bo)],
):
    """Chi tiết 1 hồ sơ theo UUID."""
    ho_so = await get_ho_so_by_id(db, ho_so_id)
    if not ho_so:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ"
        )
    return HoSoDetailResponse(
        id=ho_so.id,
        ma_ho_so=ho_so.ma_ho_so,
        thu_tuc_id=ho_so.thu_tuc_id,
        trang_thai=ho_so.trang_thai,
        cong_dan_ho_ten=ho_so.cong_dan_ho_ten,
        cong_dan_cccd=ho_so.cong_dan_cccd,
        cong_dan_sdt=ho_so.cong_dan_sdt,
        cong_dan_email=ho_so.cong_dan_email,
        can_bo_thu_ly_id=ho_so.can_bo_thu_ly_id,
        can_bo_ten=ho_so.can_bo_thu_ly.ho_ten if ho_so.can_bo_thu_ly else None,
        ngay_tiep_nhan=ho_so.ngay_tiep_nhan,
        han_giai_quyet=ho_so.han_giai_quyet,
        ngay_hoan_thanh=ho_so.ngay_hoan_thanh,
        ai_phan_loai=ho_so.ai_phan_loai,
        ai_confidence=ho_so.ai_confidence,
        ghi_chu_noi_bo=ho_so.ghi_chu_noi_bo,
    )


@router.put("/{ho_so_id}/trang-thai", response_model=HoSoDetailResponse)
async def cap_nhat_trang_thai(
    ho_so_id: str,
    body: UpdateTrangThaiRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[NguoiDung, Depends(require_can_bo)],
):
    """
    Cập nhật trạng thái hồ sơ theo state machine.
    Chỉ cho phép các transition hợp lệ:
    CHO_TIEP_NHAN → DANG_XU_LY
    DANG_XU_LY → YEU_CAU_BO_SUNG | CHO_PHE_DUYET | TU_CHOI
    YEU_CAU_BO_SUNG → DANG_XU_LY
    CHO_PHE_DUYET → HOAN_THANH | DANG_XU_LY
    """
    # Lấy hồ sơ hiện tại
    ho_so = await get_ho_so_by_id(db, ho_so_id)
    if not ho_so:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ"
        )

    # Kiểm tra transition có hợp lệ không
    if not is_valid_transition(ho_so.trang_thai, body.trang_thai_moi):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể chuyển từ '{ho_so.trang_thai}' sang '{body.trang_thai_moi}'"
        )

    # Lưu trạng thái cũ để ghi audit log
    trang_thai_cu = ho_so.trang_thai

    # Cập nhật trạng thái
    ho_so = await update_trang_thai(
        db, ho_so_id, body.trang_thai_moi, body.ghi_chu
    )

    # Ghi audit log
    log = NhatKyHeThong(
        nguoi_dung_id=current_user.id,
        hanh_dong="UPDATE_TRANG_THAI",
        doi_tuong="ho_so",
        doi_tuong_id=ho_so_id,
        du_lieu_cu={"trang_thai": trang_thai_cu},
        du_lieu_moi={"trang_thai": body.trang_thai_moi, "ghi_chu": body.ghi_chu},
    )
    db.add(log)
    await db.commit()

    return HoSoDetailResponse(
        id=ho_so.id,
        ma_ho_so=ho_so.ma_ho_so,
        thu_tuc_id=ho_so.thu_tuc_id,
        trang_thai=ho_so.trang_thai,
        cong_dan_ho_ten=ho_so.cong_dan_ho_ten,
        cong_dan_cccd=ho_so.cong_dan_cccd,
        cong_dan_sdt=ho_so.cong_dan_sdt,
        cong_dan_email=ho_so.cong_dan_email,
        can_bo_thu_ly_id=ho_so.can_bo_thu_ly_id,
        can_bo_ten=ho_so.can_bo_thu_ly.ho_ten if ho_so.can_bo_thu_ly else None,
        ngay_tiep_nhan=ho_so.ngay_tiep_nhan,
        han_giai_quyet=ho_so.han_giai_quyet,
        ngay_hoan_thanh=ho_so.ngay_hoan_thanh,
        ai_phan_loai=ho_so.ai_phan_loai,
        ai_confidence=ho_so.ai_confidence,
        ghi_chu_noi_bo=ho_so.ghi_chu_noi_bo,
    )
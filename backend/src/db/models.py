# backend/src/db/models.py
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Boolean, Text, Integer, Float,
    DateTime, Date, ForeignKey, ARRAY, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.database import Base


def gen_uuid():
    return str(uuid.uuid4())


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENUM-like constants (dÃ¹ng String thay ENUM
# Ä‘á»ƒ dá»… migrate sau nÃ y)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class VaiTro:
    CAN_BO    = "can_bo"
    LANH_DAO  = "lanh_dao"
    ADMIN     = "admin"

class TrangThaiHoSo:
    CHO_TIEP_NHAN    = "CHO_TIEP_NHAN"
    DANG_XU_LY       = "DANG_XU_LY"
    YEU_CAU_BO_SUNG  = "YEU_CAU_BO_SUNG"
    CHO_PHE_DUYET    = "CHO_PHE_DUYET"
    HOAN_THANH       = "HOAN_THANH"
    TU_CHOI          = "TU_CHOI"

class NguonTiepNhan:
    TRUC_TIEP  = "TRUC_TIEP"
    LGSP       = "LGSP"
    ONLINE     = "ONLINE"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Báº¢NG: nguoi_dung
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=gen_uuid
    )
    ten_dang_nhap: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    mat_khau_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    ho_ten: Mapped[str] = mapped_column(String(150), nullable=False)
    vai_tro: Mapped[str] = mapped_column(String(30), nullable=False, default=VaiTro.CAN_BO)
    email: Mapped[Optional[str]] = mapped_column(String(150), unique=True)
    so_dien_thoai: Mapped[Optional[str]] = mapped_column(String(15))
    linh_vuc: Mapped[Optional[list]] = mapped_column(ARRAY(String))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    ho_so_phu_trach: Mapped[list["HoSo"]] = relationship(back_populates="can_bo_thu_ly")
    nhat_ky: Mapped[list["NhatKyHeThong"]] = relationship(back_populates="nguoi_dung")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Báº¢NG: thu_tuc_hanh_chinh
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class ThuTucHanhChinh(Base):
    __tablename__ = "thu_tuc_hanh_chinh"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    ma_thu_tuc: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    ten: Mapped[str] = mapped_column(Text, nullable=False)
    linh_vuc: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    ma_linh_vuc: Mapped[str] = mapped_column(String(5), nullable=False)
    thoi_han_ngay: Mapped[int] = mapped_column(Integer, nullable=False)
    phi_xu_ly: Mapped[int] = mapped_column(Integer, default=0)
    yeu_cau_giay_to: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    can_cu_phap_ly: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    mau_van_ban: Mapped[Optional[str]] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cap_nhat_luc: Mapped[Optional[datetime]] = mapped_column(Date)

    # Relationships
    ho_so: Mapped[list["HoSo"]] = relationship(back_populates="thu_tuc")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Báº¢NG: ho_so (cá»‘t lÃµi)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class HoSo(Base):
    __tablename__ = "ho_so"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    ma_ho_so: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)

    # FK
    thu_tuc_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("thu_tuc_hanh_chinh.id"), nullable=False
    )
    can_bo_thu_ly_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), ForeignKey("nguoi_dung.id"), index=True
    )

    # ThÃ´ng tin cÃ´ng dÃ¢n
    cong_dan_ho_ten: Mapped[str] = mapped_column(String(150), nullable=False)
    cong_dan_cccd: Mapped[str] = mapped_column(String(20), nullable=False)
    cong_dan_ngay_sinh: Mapped[Optional[datetime]] = mapped_column(Date)
    cong_dan_sdt: Mapped[Optional[str]] = mapped_column(String(15))
    cong_dan_email: Mapped[Optional[str]] = mapped_column(String(150))
    cong_dan_dia_chi: Mapped[Optional[str]] = mapped_column(Text)

    # Tráº¡ng thÃ¡i & tiáº¿n Ä‘á»™
    trang_thai: Mapped[str] = mapped_column(
        String(30), nullable=False,
        default=TrangThaiHoSo.CHO_TIEP_NHAN, index=True
    )
    nguon_tiep_nhan: Mapped[str] = mapped_column(
        String(20), nullable=False, default=NguonTiepNhan.TRUC_TIEP
    )
    lgsp_ma_ho_so: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    ngay_tiep_nhan: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    han_giai_quyet: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ngay_hoan_thanh: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # AI results
    ai_phan_loai: Mapped[Optional[str]] = mapped_column(String(30))
    ai_kiem_duyet: Mapped[Optional[dict]] = mapped_column(JSONB)
    ai_van_ban_path: Mapped[Optional[str]] = mapped_column(String(500))
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float)

    # Ná»™i bá»™
    ghi_chu_noi_bo: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    thu_tuc: Mapped["ThuTucHanhChinh"] = relationship(back_populates="ho_so")
    can_bo_thu_ly: Mapped[Optional["NguoiDung"]] = relationship(back_populates="ho_so_phu_trach")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Báº¢NG: nhat_ky_he_thong (Audit Log)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class NhatKyHeThong(Base):
    __tablename__ = "nhat_ky_he_thong"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nguoi_dung_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), ForeignKey("nguoi_dung.id"), index=True
    )
    hanh_dong: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    doi_tuong: Mapped[Optional[str]] = mapped_column(String(50))
    doi_tuong_id: Mapped[Optional[str]] = mapped_column(String(50))
    du_lieu_cu: Mapped[Optional[dict]] = mapped_column(JSONB)
    du_lieu_moi: Mapped[Optional[dict]] = mapped_column(JSONB)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    # Relationships
    nguoi_dung: Mapped[Optional["NguoiDung"]] = relationship(back_populates="nhat_ky")
    



class MauVanBan(Base):
    __tablename__ = "mau_van_ban"

    id:           Mapped[uuid.UUID]        = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ma_mau:       Mapped[str]              = mapped_column(String(30), unique=True, nullable=False, index=True)
    ten_mau:      Mapped[str]              = mapped_column(String(200), nullable=False)
    loai_van_ban: Mapped[str]              = mapped_column(String(50), nullable=False)
    linh_vuc:     Mapped[Optional[str]]    = mapped_column(String(50))
    file_path:    Mapped[Optional[str]]    = mapped_column(String(500))
    placeholders: Mapped[Optional[dict]]   = mapped_column(JSONB)
    huong_dan:    Mapped[Optional[str]]    = mapped_column(Text)
    is_active:    Mapped[bool]             = mapped_column(Boolean, default=True, nullable=False)
    created_at:   Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:   Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

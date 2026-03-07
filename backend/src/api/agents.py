from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from loguru import logger

from src.core.dependencies import get_current_user
from src.db.models import NguoiDung
from src.agents.classifier import classify_ho_so
from src.agents.validator import validate_giay_to
from src.agents.drafter import (
    draft_van_ban, get_loai_van_ban, list_templates,
    get_placeholders_from_template, TEMPLATE_DIR, OUTPUT_DIR,
)

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


class ClassifyRequest(BaseModel):
    mo_ta: str
    danh_sach_thu_tuc: list[dict]

class ClassifyResponse(BaseModel):
    ma_thu_tuc: Optional[str] = None
    ten_thu_tuc: Optional[str] = None
    do_tin_cay: float = 0.0
    ly_do: str = ""
    cac_lua_chon_khac: list[str] = []


class ValidateRequest(BaseModel):
    ma_thu_tuc: str
    ten_thu_tuc: str
    yeu_cau_giay_to: list[str]
    giay_to_da_co: list[str]

class ValidateResponse(BaseModel):
    du_giay_to: bool
    ty_le_hoan_thanh: float
    giay_to_con_thieu: list[str]
    giay_to_da_co: list[str]
    ghi_chu: str


class DraftRequest(BaseModel):
    loai_van_ban: str
    thong_tin_ho_so: dict
    template_path: Optional[str] = None
    mapping: Optional[dict] = None
    mo_ta_tu_do: Optional[str] = None

class DraftResponse(BaseModel):
    phuong_thuc: str
    loai_van_ban: str
    ten_loai: str
    noi_dung: str
    file_path: Optional[str] = None
    placeholders_da_dien: Optional[dict] = None
    placeholders_chua_dien: Optional[list] = None
    huong_dan: str


@router.post("/classify", response_model=ClassifyResponse)
async def classify(
    body: ClassifyRequest,
    current_user: Annotated[NguoiDung, Depends(get_current_user)],
):
    """Phan loai ho so -> goi y ma thu tuc phu hop."""
    if not body.mo_ta.strip():
        raise HTTPException(status_code=400, detail="Mo ta khong duoc trong")
    try:
        return ClassifyResponse(**(await classify_ho_so(body.mo_ta, body.danh_sach_thu_tuc)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=ValidateResponse)
async def validate(
    body: ValidateRequest,
    current_user: Annotated[NguoiDung, Depends(get_current_user)],
):
    """Kiem tra giay to ho so da du chua."""
    try:
        return ValidateResponse(**(await validate_giay_to(
            body.ma_thu_tuc, body.ten_thu_tuc,
            body.yeu_cau_giay_to, body.giay_to_da_co,
        )))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draft", response_model=DraftResponse)
async def draft(
    body: DraftRequest,
    current_user: Annotated[NguoiDung, Depends(get_current_user)],
):
    """
    Soan thao van ban hanh chinh (2 luong):

    Luong 1 - Co mau .docx:
      template_path = "mau_so_15.docx"
      mapping = {"{{HO_TEN}}": "Nguyen Van A", ...}
      HOAC mo_ta_tu_do = "Ong A CCCD 012..." (LLM tu extract)

    Luong 2 - LLM tu do:
      loai_van_ban = "thong_bao_bo_sung"
      thong_tin_ho_so = {...}
    """
    try:
        return DraftResponse(**(await draft_van_ban(
            loai_van_ban=body.loai_van_ban,
            thong_tin_ho_so=body.thong_tin_ho_so,
            template_path=body.template_path,
            mapping=body.mapping,
            mo_ta_tu_do=body.mo_ta_tu_do,
        )))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Draft error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/draft/download/{filename}")
async def download_van_ban(
    filename: str,
    current_user: Annotated[NguoiDung, Depends(get_current_user)],
):
    """Tai ve file .docx da soan thao."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File khong ton tai")
    return FileResponse(
        path=str(file_path), filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.get("/templates")
async def get_templates(current_user: Annotated[NguoiDung, Depends(get_current_user)]):
    """Liet ke file mau .docx co san trong data/templates/."""
    return {"templates": list_templates()}


@router.get("/templates/{filename}/placeholders")
async def get_placeholders(
    filename: str,
    current_user: Annotated[NguoiDung, Depends(get_current_user)],
):
    """Lay danh sach placeholder cua 1 file mau."""
    file_path = TEMPLATE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Khong tim thay: {filename}")
    return {"filename": filename, "placeholders": get_placeholders_from_template(str(file_path))}


@router.get("/loai-van-ban")
async def get_loai(current_user: Annotated[NguoiDung, Depends(get_current_user)]):
    """Danh sach loai van ban LLM tu do ho tro."""
    return {"loai_van_ban": get_loai_van_ban()}

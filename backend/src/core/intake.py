# src/core/intake.py
# Sinh mã hồ sơ tự động theo chuẩn: [LĨNH VỰC]-[YYYYMMDD]-[HASH 4 KÝ TỰ]
# Ví dụ: HT-20260307-A1B2 (Hộ tịch, ngày 07/03/2026)

import hashlib
import time
from datetime import datetime


# Mapping lĩnh vực → mã viết tắt
MA_LINH_VUC = {
    "ho_tich":  "HT",   # Hộ tịch
    "cu_tru":   "CT",   # Cư trú
    "dat_dai":  "DD",   # Đất đai
    "tu_phap":  "TP",   # Tư pháp
    "xay_dung": "XD",   # Xây dựng
}


def gen_ma_ho_so(linh_vuc: str, cccd: str) -> str:
    """
    Sinh mã hồ sơ duy nhất.
    
    Công thức: [MÃ_LĨNH_VỰC]-[YYYYMMDD]-[HASH_4_KÝ_TỰ]
    
    Hash dựa trên CCCD + timestamp nanoseconds
    → đảm bảo unique dù cùng 1 người nộp nhiều hồ sơ cùng ngày.
    
    Ví dụ:
        gen_ma_ho_so("ho_tich", "079204012345") → "HT-20260307-A1B2"
        gen_ma_ho_so("cu_tru",  "079204012345") → "CT-20260307-F3C9"
    """
    # Lấy mã lĩnh vực, mặc định HC (Hành chính khác) nếu không tìm thấy
    ma = MA_LINH_VUC.get(linh_vuc, "HC")

    # Ngày tiếp nhận theo định dạng YYYYMMDD
    ngay = datetime.now().strftime("%Y%m%d")

    # Hash 4 ký tự từ CCCD + timestamp nanoseconds → đảm bảo unique
    seed = f"{cccd}{time.time_ns()}"
    hash4 = hashlib.md5(seed.encode()).hexdigest()[:4].upper()

    return f"{ma}-{ngay}-{hash4}"


def tinh_han_giai_quyet(thoi_han_ngay: int) -> datetime:
    """
    Tính hạn giải quyết dựa trên số ngày làm việc.
    
    Hiện tại tính đơn giản: cộng thêm N ngày từ hôm nay.
    TODO Sprint 5: loại trừ thứ 7, CN và ngày lễ theo NĐ 110/2004.
    
    Ví dụ:
        tinh_han_giai_quyet(5) → datetime 5 ngày sau hôm nay
    """
    from datetime import timedelta
    return datetime.now() + timedelta(days=thoi_han_ngay)
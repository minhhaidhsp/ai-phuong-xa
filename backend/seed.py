# backend/seed.py
# Tạo dữ liệu mẫu ban đầu — chạy 1 lần sau khi migrate
# Lệnh: python seed.py

import asyncio
from src.db.database import AsyncSessionLocal
from src.db.models import VaiTro
from src.db.repositories.user_repo import get_user_by_username, create_user
from src.core.security import hash_password


async def seed():
    async with AsyncSessionLocal() as db:
        await seed_thu_tuc(db)
        # Admin — toàn quyền hệ thống
        if not await get_user_by_username(db, "admin"):
            u = await create_user(db,
                ten_dang_nhap="admin",
                mat_khau_hash=hash_password("Admin@123"),
                ho_ten="Quản trị viên",
                vai_tro=VaiTro.ADMIN,
                email="admin@phuong.gov.vn",
            )
            await db.commit()
            print(f"✅ admin      — {u.ho_ten}")
        else:
            print("⏭️  admin đã tồn tại")

        # Cán bộ — tiếp nhận và xử lý hồ sơ
        if not await get_user_by_username(db, "canbo01"):
            u = await create_user(db,
                ten_dang_nhap="canbo01",
                mat_khau_hash=hash_password("CanBo@123"),
                ho_ten="Nguyễn Văn An",
                vai_tro=VaiTro.CAN_BO,
                email="canbo01@phuong.gov.vn",
                linh_vuc=["ho_tich", "cu_tru"],
            )
            await db.commit()
            print(f"✅ canbo01    — {u.ho_ten}")
        else:
            print("⏭️  canbo01 đã tồn tại")

        # Lãnh đạo — xem dashboard, phê duyệt, phân công
        if not await get_user_by_username(db, "lanhdao01"):
            u = await create_user(db,
                ten_dang_nhap="lanhdao01",
                mat_khau_hash=hash_password("LanhDao@123"),
                ho_ten="Trần Thị Bình",
                vai_tro=VaiTro.LANH_DAO,
                email="lanhdao01@phuong.gov.vn",
            )
            await db.commit()
            print(f"✅ lanhdao01  — {u.ho_ten}")
        else:
            print("⏭️  lanhdao01 đã tồn tại")

    print("\n🎉 Seed xong!")
    print("─" * 35)
    print("  admin      / Admin@123")
    print("  canbo01    / CanBo@123")
    print("  lanhdao01  / LanhDao@123")
    print("─" * 35)
    print("👉 Test: http://localhost:8000/docs")

# Seed thủ tục hành chính mẫu
async def seed_thu_tuc(db):
    from src.db.models import ThuTucHanhChinh
    from sqlalchemy import select
    import uuid

    # Kiểm tra đã có chưa
    result = await db.execute(select(ThuTucHanhChinh).limit(1))
    if result.scalar_one_or_none():
        print("⏭️  Thu tuc đã tồn tại")
        return

    thu_tucs = [
        ThuTucHanhChinh(
            id="00000000-0000-0000-0000-000000000001",
            ma_thu_tuc="HT-001",
            ten="Đăng ký kết hôn",
            linh_vuc="Hộ tịch",
            ma_linh_vuc="HT",      # ← đổi từ "ho_tich" → "HT"
            thoi_han_ngay=5,
            phi_xu_ly=0,
            yeu_cau_giay_to={"giay_to": ["CCCD", "Giấy xác nhận tình trạng hôn nhân"]},
        ),
        ThuTucHanhChinh(
            id=str(uuid.uuid4()),
            ma_thu_tuc="HT-002",
            ten="Đăng ký khai sinh",
            linh_vuc="Hộ tịch",
            ma_linh_vuc="HT",      # ← "HT"
            thoi_han_ngay=3,
            phi_xu_ly=0,
            yeu_cau_giay_to={"giay_to": ["CCCD bố/mẹ", "Giấy chứng sinh"]},
        ),
        ThuTucHanhChinh(
            id=str(uuid.uuid4()),
            ma_thu_tuc="CT-001",
            ten="Đăng ký thường trú",
            linh_vuc="Cư trú",
            ma_linh_vuc="CT",      # ← "CT"
            thoi_han_ngay=7,
            phi_xu_ly=0,
            yeu_cau_giay_to={"giay_to": ["CCCD", "Giấy tờ nhà"]},
        ),
        ThuTucHanhChinh(
            id=str(uuid.uuid4()),
            ma_thu_tuc="CT-002",
            ten="Xác nhận thường trú",
            linh_vuc="Cư trú",
            ma_linh_vuc="CT",      # ← "CT"
            thoi_han_ngay=3,
            phi_xu_ly=0,
            yeu_cau_giay_to={"giay_to": ["CCCD"]},
        ),
    ]
    
    
    for tt in thu_tucs:
        db.add(tt)
    await db.commit()
    print(f"✅ Đã tạo {len(thu_tucs)} thủ tục hành chính")
    
if __name__ == "__main__":
    asyncio.run(seed())
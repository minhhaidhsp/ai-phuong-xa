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


if __name__ == "__main__":
    asyncio.run(seed())
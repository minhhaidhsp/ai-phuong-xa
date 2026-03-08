# seed_ho_so.py — chạy từ D:\Projects\ai-phuong-xa\backend\
# Tạo 25 hồ sơ mẫu với đủ trạng thái
import asyncio, sys, os, random
from datetime import datetime, timedelta
sys.path.insert(0, '.')

async def main():
    from src.core.config import settings
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text

    engine = create_async_engine(settings.DATABASE_URL)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Lấy dữ liệu cần thiết
    async with Session() as db:
        # Thu tuc IDs
        r = await db.execute(text("SELECT id, thoi_han_ngay FROM thu_tuc_hanh_chinh WHERE is_active=true"))
        thu_tucs = r.fetchall()

        # Can bo IDs
        r2 = await db.execute(text("SELECT id FROM nguoi_dung WHERE vai_tro IN ('can_bo','admin')"))
        can_bos = [row[0] for row in r2.fetchall()]

        if not thu_tucs or not can_bos:
            print("ERROR: Khong co thu_tuc hoac can_bo trong DB")
            return

    TRANG_THAI = [
        'CHO_TIEP_NHAN', 'CHO_TIEP_NHAN',
        'DANG_XU_LY', 'DANG_XU_LY', 'DANG_XU_LY', 'DANG_XU_LY',
        'YEU_CAU_BO_SUNG', 'YEU_CAU_BO_SUNG', 'YEU_CAU_BO_SUNG',
        'CHO_PHE_DUYET', 'CHO_PHE_DUYET',
        'HOAN_THANH', 'HOAN_THANH', 'HOAN_THANH', 'HOAN_THANH', 'HOAN_THANH',
        'TU_CHOI',
    ]

    CONG_DAN = [
        ('Nguyễn Thị Mai Lan', '079085012345', '0901234567', '142/5 Trần Quý Khoách, P.Tân Định, Q.1'),
        ('Trần Văn Hùng',      '079012345678', '0912345678', '22 Nguyễn Trãi, P.Bến Thành, Q.1'),
        ('Lê Thị Bích Ngọc',   '079087654321', '0923456789', '55 Lê Lợi, P.Bến Nghé, Q.1'),
        ('Phạm Minh Tuấn',     '079011112222', '0934567890', '88 Hai Bà Trưng, P.Đa Kao, Q.1'),
        ('Võ Thị Thu Hà',      '079099887766', '0945678901', '10 Đinh Tiên Hoàng, P.Đa Kao, Q.1'),
        ('Đỗ Văn Long',        '079055443322', '0956789012', '33 Phạm Ngũ Lão, Q.1'),
        ('Bùi Thị Lan',        '079044332211', '0967890123', '5 Ngô Đức Kế, Q.1'),
        ('Hoàng Văn Nam',      '079033221100', '0978901234', '120 Đinh Tiên Hoàng, Q.Bình Thạnh'),
        ('Nguyễn Thanh Bình',  '079022110099', '0989012345', '77 Lý Tự Trọng, Q.1'),
        ('Trần Thị Hoa',       '079011009988', '0990123456', '200 Lê Văn Sỹ, Q.3'),
        ('Lý Văn Đức',         '079088776655', '0901122334', '45 Cách Mạng Tháng 8, Q.3'),
        ('Mai Thị Kim Anh',    '079077665544', '0912233445', '67 Điện Biên Phủ, Q.Bình Thạnh'),
        ('Ngô Văn Phúc',       '079066554433', '0923344556', '89 Phan Đình Phùng, Q.Phú Nhuận'),
        ('Dương Thị Mỹ Duyên', '079011223344', '0934455667', '12 Hoàng Diệu, Q.4'),
        ('Tô Minh Khoa',       '079022334455', '0945566778', '34 Bến Vân Đồn, Q.4'),
        ('Lưu Thị Thu Thủy',   '079033445566', '0956677889', '56 Nguyễn Tất Thành, Q.4'),
        ('Vũ Văn Kiên',        '079044556677', '0967788990', '78 Trần Xuân Soạn, Q.7'),
        ('Phan Thị Yến',       '079055667788', '0978899001', '90 Lê Văn Lương, Q.7'),
        ('Đinh Văn Sơn',       '079066778899', '0989900112', '102 Nguyễn Thị Thập, Q.7'),
        ('Chu Thị Ngân',       '079077889900', '0990011223', '5 Đỗ Xuân Hợp, Q.9'),
        ('Lê Hoàng Phát',      '079088990011', '0901234560', '23 Nguyễn Xiển, Q.12'),
        ('Trịnh Thị Bảo Châu', '079099001122', '0912345670', '45 Quang Trung, Q.Gò Vấp'),
        ('Nguyễn Văn Tú',      '079010112233', '0923456780', '67 Lê Đức Thọ, Q.Gò Vấp'),
        ('Phạm Thị Mỹ Linh',   '079021223344', '0934567800', '89 Nguyễn Oanh, Q.Gò Vấp'),
        ('Cao Văn Hải',        '079032334455', '0945678900', '11 Phan Văn Trị, Q.Bình Thạnh'),
    ]

    NGUON = ['TRUC_TIEP', 'TRUC_TIEP', 'TRUC_TIEP', 'BUU_CHINH', 'LGSP']

    import uuid as _uuid
    from datetime import date

    async with Session() as db:
        count = 0
        for i, (ho_ten, cccd, sdt, dia_chi) in enumerate(CONG_DAN):
            tt_row = random.choice(thu_tucs)
            tt_id, thoi_han = tt_row[0], tt_row[1]
            trang_thai = random.choice(TRANG_THAI)
            nguon = random.choice(NGUON)
            cb_id = random.choice(can_bos)

            # Ngày nộp trong 30 ngày qua
            days_ago = random.randint(1, 30)
            ngay_nop = datetime.now() - timedelta(days=days_ago)
            han_gq = ngay_nop + timedelta(days=thoi_han)
            ngay_ht = han_gq if trang_thai == 'HOAN_THANH' else None

            ma_ho_so = f"HC-{ngay_nop.strftime('%Y%m%d')}-{_uuid.uuid4().hex[:4].upper()}"

            try:
                await db.execute(text("""
                    INSERT INTO ho_so (
                        id, ma_ho_so, thu_tuc_id, can_bo_thu_ly_id,
                        cong_dan_ho_ten, cong_dan_cccd, cong_dan_sdt, cong_dan_email,
                        cong_dan_dia_chi, cong_dan_ngay_sinh,
                        trang_thai, nguon_tiep_nhan,
                        ngay_tiep_nhan, han_giai_quyet, ngay_hoan_thanh,
                        ghi_chu_noi_bo
                    ) VALUES (
                        gen_random_uuid(), :ma, :tt_id, :cb_id,
                        :ho_ten, :cccd, :sdt, '',
                        :dia_chi, NULL,
                        :trang_thai, :nguon,
                        :ngay_nop, :han_gq, :ngay_ht,
                        ''
                    )
                """), {
                    'ma': ma_ho_so, 'tt_id': tt_id, 'cb_id': cb_id,
                    'ho_ten': ho_ten, 'cccd': cccd, 'sdt': sdt, 'dia_chi': dia_chi,
                    'trang_thai': trang_thai, 'nguon': nguon,
                    'ngay_nop': ngay_nop, 'han_gq': han_gq, 'ngay_ht': ngay_ht,
                })
                count += 1
                print(f"  + {ma_ho_so} | {ho_ten} | {trang_thai}")
            except Exception as e:
                print(f"  ! Loi {ho_ten}: {e}")

        await db.commit()
        print(f"\nDone! Da them {count} ho so mau.")

    await engine.dispose()

asyncio.run(main())

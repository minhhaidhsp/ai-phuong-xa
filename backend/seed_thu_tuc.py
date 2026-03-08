# seed_thu_tuc.py — chạy từ D:\Projects\ai-phuong-xa\backend\
import asyncio, sys, json
sys.path.insert(0, '.')

THU_TUC = [
  dict(ma='HT-001', ten='Đăng ký kết hôn', linh_vuc='Hộ tịch', ma_lv='HT', thoi_han=5,
    giay_to=['Tờ khai đăng ký kết hôn (Mẫu TP/HT-2015)','CCCD/Hộ chiếu 2 người','Giấy xác nhận tình trạng hôn nhân','Ảnh 3×4 (2 tấm/người)','Sổ hộ khẩu (nếu có)'],
    phap_ly=['Luật Hộ tịch 2014','Nghị định 123/2015/NĐ-CP','Thông tư 04/2020/TT-BTP']),
  dict(ma='HT-002', ten='Đăng ký khai sinh', linh_vuc='Hộ tịch', ma_lv='HT', thoi_han=3,
    giay_to=['Giấy chứng sinh do cơ sở y tế cấp','CCCD cha và mẹ','Giấy đăng ký kết hôn của cha mẹ','Sổ hộ khẩu'],
    phap_ly=['Luật Hộ tịch 2014','Nghị định 123/2015/NĐ-CP']),
  dict(ma='HT-003', ten='Xác nhận tình trạng hôn nhân', linh_vuc='Hộ tịch', ma_lv='HT', thoi_han=3,
    giay_to=['Tờ khai xác nhận tình trạng hôn nhân','CCCD','Sổ hộ khẩu'],
    phap_ly=['Luật Hộ tịch 2014','Nghị định 123/2015/NĐ-CP']),
  dict(ma='HT-004', ten='Đăng ký khai tử', linh_vuc='Hộ tịch', ma_lv='HT', thoi_han=2,
    giay_to=['Giấy báo tử của cơ sở y tế hoặc công an','CCCD người thân','Sổ hộ khẩu'],
    phap_ly=['Luật Hộ tịch 2014','Nghị định 123/2015/NĐ-CP']),
  dict(ma='HT-005', ten='Đăng ký lại khai sinh', linh_vuc='Hộ tịch', ma_lv='HT', thoi_han=5,
    giay_to=['Tờ khai đăng ký lại khai sinh','CCCD','Giấy tờ chứng minh nội dung khai sinh','Sổ hộ khẩu'],
    phap_ly=['Luật Hộ tịch 2014','Thông tư 04/2020/TT-BTP']),
  dict(ma='CT-001', ten='Đăng ký thường trú', linh_vuc='Cư trú', ma_lv='CT', thoi_han=7,
    giay_to=['CCCD','Giấy tờ chứng minh chỗ ở hợp pháp','Phiếu báo thay đổi hộ khẩu (HK01)','Sổ hộ khẩu (nếu có)'],
    phap_ly=['Luật Cư trú 2020','Nghị định 62/2021/NĐ-CP']),
  dict(ma='CT-002', ten='Đăng ký tạm trú', linh_vuc='Cư trú', ma_lv='CT', thoi_han=3,
    giay_to=['CCCD','Giấy tờ chứng minh chỗ ở','Phiếu khai báo tạm trú CT01'],
    phap_ly=['Luật Cư trú 2020','Nghị định 62/2021/NĐ-CP']),
  dict(ma='CT-003', ten='Xóa đăng ký thường trú', linh_vuc='Cư trú', ma_lv='CT', thoi_han=3,
    giay_to=['Đơn đề nghị xóa đăng ký thường trú','CCCD','Sổ hộ khẩu'],
    phap_ly=['Luật Cư trú 2020']),
  dict(ma='CT-004', ten='Tách hộ khẩu', linh_vuc='Cư trú', ma_lv='CT', thoi_han=5,
    giay_to=['Đơn đề nghị tách hộ khẩu','CCCD','Giấy tờ chứng minh chỗ ở mới','Sổ hộ khẩu gốc'],
    phap_ly=['Luật Cư trú 2020','Nghị định 62/2021/NĐ-CP']),
  dict(ma='DD-001', ten='Cấp giấy phép xây dựng nhà ở', linh_vuc='Đất đai', ma_lv='DD', thoi_han=15,
    giay_to=['Đơn đề nghị cấp phép xây dựng','Giấy tờ hợp pháp về đất','Bản vẽ thiết kế','CCCD chủ hộ'],
    phap_ly=['Luật Xây dựng 2014 sửa đổi 2020','Nghị định 15/2021/NĐ-CP']),
  dict(ma='DD-002', ten='Xác nhận thông tin đất đai', linh_vuc='Đất đai', ma_lv='DD', thoi_han=3,
    giay_to=['Đơn đề nghị xác nhận','CCCD','Giấy chứng nhận quyền sử dụng đất (bản photo)'],
    phap_ly=['Luật Đất đai 2024','Nghị định 101/2024/NĐ-CP']),
  dict(ma='DD-003', ten='Chứng thực hợp đồng mua bán nhà đất', linh_vuc='Đất đai', ma_lv='DD', thoi_han=2,
    giay_to=['Hợp đồng mua bán (3 bản)','CCCD các bên','Giấy CN quyền sử dụng đất bản gốc'],
    phap_ly=['Luật Đất đai 2024','Nghị định 23/2015/NĐ-CP về chứng thực']),
  dict(ma='KD-001', ten='Đăng ký hộ kinh doanh', linh_vuc='Kinh doanh', ma_lv='KD', thoi_han=3,
    giay_to=['Giấy đề nghị đăng ký hộ kinh doanh','CCCD chủ hộ','Giấy tờ chứng minh địa điểm kinh doanh'],
    phap_ly=['Luật Doanh nghiệp 2020','Nghị định 01/2021/NĐ-CP']),
  dict(ma='KD-002', ten='Tạm ngừng hoạt động hộ kinh doanh', linh_vuc='Kinh doanh', ma_lv='KD', thoi_han=3,
    giay_to=['Thông báo tạm ngừng kinh doanh','CCCD chủ hộ','Giấy chứng nhận đăng ký hộ kinh doanh'],
    phap_ly=['Luật Doanh nghiệp 2020','Nghị định 01/2021/NĐ-CP']),
  dict(ma='CT2-001', ten='Chứng thực bản sao từ bản chính', linh_vuc='Chứng thực', ma_lv='CT2', thoi_han=1,
    giay_to=['Bản chính cần chứng thực','CCCD người yêu cầu'],
    phap_ly=['Nghị định 23/2015/NĐ-CP','Thông tư 01/2020/TT-BTP']),
]

async def main():
    from src.core.config import settings
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text

    engine = create_async_engine(settings.DATABASE_URL)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        # Xem schema thực tế
        r = await db.execute(text("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name='thu_tuc_hanh_chinh'
            ORDER BY ordinal_position
        """))
        cols = r.fetchall()
        print("Schema:")
        for col in cols:
            print(f"  {col[0]}: {col[1]} ({col[2]})")

        await db.execute(text("UPDATE thu_tuc_hanh_chinh SET is_active=false"))

        for tt in THU_TUC:
            giay_to_json = json.dumps({'giay_to': tt['giay_to']}, ensure_ascii=False)
            # can_cu_phap_ly là TEXT[] array
            phap_ly_arr = tt['phap_ly']

            r = await db.execute(
                text("SELECT id FROM thu_tuc_hanh_chinh WHERE ma_thu_tuc=:ma"),
                {'ma': tt['ma']}
            )
            exists = r.fetchone()

            params = {
                'ten': tt['ten'], 'lv': tt['linh_vuc'], 'ma_lv': tt['ma_lv'],
                'thoi_han': tt['thoi_han'], 'giay_to': giay_to_json,
                'phap_ly': phap_ly_arr, 'ma': tt['ma']
            }

            if exists:
                await db.execute(text("""
                    UPDATE thu_tuc_hanh_chinh SET
                        ten=:ten, linh_vuc=:lv, ma_linh_vuc=:ma_lv,
                        thoi_han_ngay=:thoi_han,
                        yeu_cau_giay_to=cast(:giay_to as jsonb),
                        can_cu_phap_ly=:phap_ly,
                        is_active=true
                    WHERE ma_thu_tuc=:ma
                """), params)
                print(f"  ~ UPDATE {tt['ma']} {tt['ten']}")
            else:
                await db.execute(text("""
                    INSERT INTO thu_tuc_hanh_chinh
                        (id, ma_thu_tuc, ten, linh_vuc, ma_linh_vuc,
                         thoi_han_ngay, yeu_cau_giay_to, can_cu_phap_ly, is_active)
                    VALUES
                        (gen_random_uuid(), :ma, :ten, :lv, :ma_lv,
                         :thoi_han, cast(:giay_to as jsonb), :phap_ly, true)
                """), params)
                print(f"  + INSERT {tt['ma']} {tt['ten']}")

        await db.commit()
        r = await db.execute(text("SELECT COUNT(*) FROM thu_tuc_hanh_chinh WHERE is_active=true"))
        print(f"\nDone! Tong {r.scalar()} thu tuc active.")

    await engine.dispose()

asyncio.run(main())

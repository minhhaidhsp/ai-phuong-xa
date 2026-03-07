import asyncio
import httpx

BASE_URL = "http://localhost:8000"
TOKEN = None

async def main():
    async with httpx.AsyncClient() as client:
        # Login
        r = await client.post(f"{BASE_URL}/api/v1/auth/login",
            data={"username": "admin", "password": "Admin@123"})
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Login OK")

        # Danh sach van ban mau
        van_bans = [
            {
                "ten_van_ban": "Luật Hôn nhân và Gia đình 2014",
                "loai": "luat",
                "dieu_khoan": "Điều 8 - Điều kiện kết hôn",
                "noi_dung": "Nam, nữ kết hôn với nhau phải tuân theo các điều kiện sau đây: Nam từ đủ 20 tuổi trở lên, nữ từ đủ 18 tuổi trở lên; Việc kết hôn do nam và nữ tự nguyện quyết định; Không bị mất năng lực hành vi dân sự; Việc kết hôn không thuộc một trong các trường hợp cấm kết hôn theo quy định tại Điều 5 của Luật này.",
                "url": "https://thuvienphapluat.vn/van-ban/Hon-nhan-gia-dinh/Luat-Hon-nhan-va-gia-dinh-2014-238640.aspx"
            },
            {
                "ten_van_ban": "Luật Hôn nhân và Gia đình 2014",
                "loai": "luat",
                "dieu_khoan": "Điều 9 - Đăng ký kết hôn",
                "noi_dung": "Việc kết hôn phải được đăng ký và do cơ quan nhà nước có thẩm quyền thực hiện theo quy định của Luật này và pháp luật về hộ tịch. Việc kết hôn không được đăng ký theo quy định tại khoản này thì không có giá trị pháp lý. Vợ chồng đã ly hôn muốn xác lập lại quan hệ vợ chồng thì phải đăng ký kết hôn.",
                "url": "https://thuvienphapluat.vn/van-ban/Hon-nhan-gia-dinh/Luat-Hon-nhan-va-gia-dinh-2014-238640.aspx"
            },
            {
                "ten_van_ban": "Luật Cư trú 2020",
                "loai": "luat",
                "dieu_khoan": "Điều 20 - Điều kiện đăng ký thường trú",
                "noi_dung": "Công dân được đăng ký thường trú tại chỗ ở hợp pháp do mình thuê, mượn, ở nhờ tại tỉnh, thành phố trực thuộc trung ương khác nơi đang thường trú khi thuộc một trong các trường hợp: Có quan hệ là cha, mẹ đẻ, cha mẹ nuôi, vợ, chồng, con đẻ, con nuôi với người có sổ hộ khẩu tại chỗ ở đó; Người chưa thành niên không có người giám hộ ở địa phương.",
                "url": "https://thuvienphapluat.vn/van-ban/Quyen-dan-su/Luat-Cu-tru-2020-382512.aspx"
            },
            {
                "ten_van_ban": "Nghị định 123/2015/NĐ-CP",
                "loai": "nghi_dinh",
                "dieu_khoan": "Điều 9 - Thủ tục đăng ký khai sinh",
                "noi_dung": "Người đi đăng ký khai sinh nộp tờ khai theo mẫu quy định và giấy chứng sinh cho cơ quan đăng ký hộ tịch. Trường hợp không có giấy chứng sinh thì nộp văn bản xác nhận của người làm chứng. Ngay sau khi nhận đủ giấy tờ theo quy định, nếu thấy thông tin khai sinh đầy đủ và phù hợp, công chức tư pháp - hộ tịch ghi nội dung khai sinh vào Sổ đăng ký khai sinh.",
                "url": "https://thuvienphapluat.vn/van-ban/Thu-tuc-To-tung/Nghi-dinh-123-2015-ND-CP-thu-tuc-ho-tich-290874.aspx"
            },
            {
                "ten_van_ban": "Luật Hộ tịch 2014",
                "loai": "luat",
                "dieu_khoan": "Điều 16 - Thẩm quyền đăng ký khai sinh",
                "noi_dung": "Ủy ban nhân dân cấp xã nơi cư trú của người cha hoặc người mẹ thực hiện việc đăng ký khai sinh. Trường hợp trẻ em bị bỏ rơi thì Ủy ban nhân dân cấp xã nơi phát hiện trẻ em bị bỏ rơi thực hiện việc đăng ký khai sinh. Trường hợp trẻ em sinh ra tại cơ sở y tế thì Thủ trưởng cơ sở y tế có trách nhiệm thông báo cho Ủy ban nhân dân cấp xã.",
                "url": "https://thuvienphapluat.vn/van-ban/Thu-tuc-To-tung/Luat-Ho-tich-2014-259708.aspx"
            },
        ]

        # Index tung van ban
        for i, vb in enumerate(van_bans, 1):
            r = await client.post(
                f"{BASE_URL}/api/v1/rag/index",
                json=vb,
                headers=headers,
                timeout=60.0
            )
            if r.status_code == 200:
                print(f"✅ [{i}/{len(van_bans)}] Indexed: {vb['ten_van_ban']} - {vb['dieu_khoan']}")
            else:
                print(f"❌ [{i}/{len(van_bans)}] Error: {r.text}")

        # Kiem tra stats
        r = await client.get(f"{BASE_URL}/api/v1/rag/stats", headers=headers)
        print(f"\n📊 Qdrant stats: {r.json()}")

        # Test query
        print("\n🤖 Test RAG query...")
        r = await client.post(
            f"{BASE_URL}/api/v1/rag/query",
            json={"question": "Điều kiện đăng ký kết hôn là gì?", "top_k": 3},
            headers=headers,
            timeout=120.0
        )
        result = r.json()
        print(f"\n❓ Câu hỏi: {result['question']}")
        print(f"\n💬 Trả lời:\n{result['answer']}")
        print(f"\n📚 Nguồn ({result['found_docs']} docs):")
        for s in result['sources']:
            print(f"  - {s['ten_van_ban']} [{s['score']}]")

asyncio.run(main())

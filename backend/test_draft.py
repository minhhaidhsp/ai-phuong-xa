import asyncio, httpx, json

BASE = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(f"{BASE}/api/v1/auth/login",
            data={"username":"admin","password":"Admin@123"})
        h = {"Authorization": f"Bearer {r.json()['access_token']}"}

        # ── TEST A: Dien mau 15 bang mapping thu cong ─────────────────
        print("=== TEST A: MAU 15 - DIEN THU CONG ===")
        r = await client.post(f"{BASE}/api/v1/agents/draft", headers=h, json={
            "loai_van_ban": "don_de_nghi_cham_dut",
            "thong_tin_ho_so": {"ma_ho_so": "TE-20260307-A1B2"},
            "template_path": "mau_so_15_template.docx",
            "mapping": {
                "{{KINH_GUI}}":             "Chu tich UBND Phuong Ben Nghe, Quan 1, TP.HCM",
                "{{HO_TEN_NGUOI_VIET_DON}}":"Nguyen Van An",
                "{{DIA_CHI_CU_TRU}}":       "123 Le Loi, Phuong Ben Nghe, Quan 1, TP.HCM",
                "{{HO_TEN_TRE}}":           "Tran Thi Bich",
                "{{NGAY_SINH_TRE}}":        "15",
                "{{THANG_SINH_TRE}}":       "06",
                "{{NAM_SINH_TRE}}":         "2018",
                "{{SO_QUYET_DINH}}":        "123/QD-UBND",
                "{{NGAY_QD}}":              "01",
                "{{THANG_QD}}":             "03",
                "{{NAM_QD}}":              "2024",
                "{{NGAY_CHAM_DUT}}":        "20",
                "{{THANG_CHAM_DUT}}":       "03",
                "{{NAM_CHAM_DUT}}":         "2026",
                "{{LY_DO_1}}":              "Hoan canh kinh te gia dinh kho khan, khong dam bao dieu kien nuoi duong",
                "{{LY_DO_2}}":              "Nguoi nhan cham soc bi benh nan, kha nang cham soc han che",
                "{{LY_DO_3}}":              "Co nguoi than ruot thit co nhu cau va dieu kien nhan cham soc tre",
                "{{NGAY_KY}}":              "07",
                "{{THANG_KY}}":             "03",
                "{{NAM_KY}}":              "26",
            }
        })
        d = r.json()
        print(f"Phuong thuc: {d.get('phuong_thuc')}")
        print(f"File: {d.get('file_path')}")
        print(f"Chua dien: {d.get('placeholders_chua_dien')}")
        print(f"Preview (300 ky tu):\n{d.get('noi_dung','')[:300]}\n")

        # ── TEST B: Dien mau 15 bang LLM extract tu mo ta ────────────
        print("=== TEST B: MAU 15 - LLM TU EXTRACT ===")
        r = await client.post(f"{BASE}/api/v1/agents/draft", headers=h, json={
            "loai_van_ban": "don_de_nghi_cham_dut",
            "thong_tin_ho_so": {"ma_ho_so": "TE-20260307-C3D4"},
            "template_path": "mau_so_15_template.docx",
            "mo_ta_tu_do": (
                "Ba Nguyen Thi Mai, cu tru tai 45 Nguyen Hue Phuong Ben Thanh Quan 1, "
                "muon cham dut viec cham soc thay the cho chau Pham Van Khoa sinh ngay 10/05/2019, "
                "theo Quyet dinh so 88/QD-UBND ngay 15/01/2024. "
                "Ly do: gia dinh co viec dot xuat phai chuyen vung. "
                "Cham dut tu ngay 01/04/2026. Don ky ngay 07/03/2026."
            )
        })
        d2 = r.json()
        print(f"Phuong thuc: {d2.get('phuong_thuc')}")
        print(f"File: {d2.get('file_path')}")
        print(f"Da dien: {json.dumps(d2.get('placeholders_da_dien'), ensure_ascii=False, indent=2)}")
        print(f"Chua dien: {d2.get('placeholders_chua_dien')}\n")

        # ── TEST C: Download file ─────────────────────────────────────
        if d.get('file_path'):
            fname = d['file_path'].split('\\')[-1].split('/')[-1]
            print(f"=== TEST C: DOWNLOAD {fname} ===")
            r = await client.get(f"{BASE}/api/v1/agents/draft/download/{fname}", headers=h)
            print(f"HTTP {r.status_code}, size={len(r.content)} bytes")
            with open(f"output_{fname}", "wb") as f:
                f.write(r.content)
            print(f"Da luu: output_{fname}")

asyncio.run(main())

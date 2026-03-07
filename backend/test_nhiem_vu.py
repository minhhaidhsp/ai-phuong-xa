"""
test_nhiem_vu.py
Sprint 7 - Test Nhiệm vụ & KPI

Chạy:
    cd D:\Projects\ai-phuong-xa\backend
    .\venv\Scripts\Activate.ps1
    python test_nhiem_vu.py
"""
import asyncio
import httpx
from datetime import date, timedelta

BASE = "http://localhost:8000/api/v1"
nv_id = None  # lưu lại để dùng ở các test sau


async def login(client, username, password):
    resp = await client.post(
        f"{BASE}/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, f"Login thất bại: {resp.text}"
    return resp.json()["access_token"]


async def test_tao_nhiem_vu(client, ld_token, cb_token):
    global nv_id
    print("\n=== TEST: POST /nhiem-vu (lãnh đạo giao việc) ===")

    # Lấy ID canbo01
    resp = await client.get(
        f"{BASE}/auth/me",
        headers={"Authorization": f"Bearer {cb_token}"},
    )
    cb_id = resp.json()["id"]

    han = str(date.today() + timedelta(days=7))
    resp = await client.post(
        f"{BASE}/nhiem-vu",
        json={
            "tieu_de": "Kiểm tra hồ sơ tồn đọng tháng 3",
            "mo_ta": "Rà soát và xử lý hồ sơ chưa hoàn thành",
            "nguoi_nhan_id": cb_id,
            "han_hoan_thanh": han,
            "muc_do_uu_tien": "CAO",
        },
        headers={"Authorization": f"Bearer {ld_token}"},
    )
    assert resp.status_code == 201, f"Lỗi: {resp.text}"
    data = resp.json()["data"]
    nv_id = data["id"]
    print(f"  Tạo nhiệm vụ   : {data['tieu_de']}")
    print(f"  ID              : {nv_id}")
    print(f"  Trạng thái      : {data['trang_thai']}")
    print(f"  Hạn hoàn thành  : {data['han_hoan_thanh']}")
    print("  [PASS]")


async def test_can_bo_khong_tao_duoc(client, cb_token, cb_id):
    print("\n=== TEST: can_bo không tạo được nhiệm vụ ===")
    han = str(date.today() + timedelta(days=5))
    resp = await client.post(
        f"{BASE}/nhiem-vu",
        json={
            "tieu_de": "Test không hợp lệ",
            "nguoi_nhan_id": cb_id,
            "han_hoan_thanh": han,
        },
        headers={"Authorization": f"Bearer {cb_token}"},
    )
    assert resp.status_code == 403, f"Phải là 403, nhận được: {resp.status_code}"
    print("  can_bo -> POST /nhiem-vu: 403 Forbidden [PASS]")


async def test_danh_sach(client, ld_token, cb_token):
    print("\n=== TEST: GET /nhiem-vu ===")

    # Lãnh đạo xem tất cả
    resp = await client.get(
        f"{BASE}/nhiem-vu",
        headers={"Authorization": f"Bearer {ld_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    print(f"  Lãnh đạo thấy  : {data['total']} nhiệm vụ")

    # Cán bộ chỉ thấy của mình
    resp2 = await client.get(
        f"{BASE}/nhiem-vu",
        headers={"Authorization": f"Bearer {cb_token}"},
    )
    assert resp2.status_code == 200
    data2 = resp2.json()["data"]
    print(f"  Cán bộ thấy    : {data2['total']} nhiệm vụ (chỉ của mình)")
    print("  [PASS]")


async def test_cap_nhat_trang_thai(client, cb_token):
    print("\n=== TEST: PUT /nhiem-vu/{id} ===")
    resp = await client.put(
        f"{BASE}/nhiem-vu/{nv_id}",
        json={"trang_thai": "DANG_THUC_HIEN"},
        headers={"Authorization": f"Bearer {cb_token}"},
    )
    assert resp.status_code == 200, f"Lỗi: {resp.text}"
    data = resp.json()["data"]
    assert data["trang_thai"] == "DANG_THUC_HIEN"
    print(f"  Trạng thái mới  : {data['trang_thai']} [PASS]")

    # Hoàn thành
    resp2 = await client.put(
        f"{BASE}/nhiem-vu/{nv_id}",
        json={"trang_thai": "HOAN_THANH", "ket_qua": "Đã xử lý xong 5 hồ sơ tồn đọng"},
        headers={"Authorization": f"Bearer {cb_token}"},
    )
    assert resp2.status_code == 200
    data2 = resp2.json()["data"]
    assert data2["trang_thai"] == "HOAN_THANH"
    print(f"  Hoàn thành      : {data2['ngay_hoan_thanh_thuc_te']} [PASS]")


async def test_kpi(client, ld_token, cb_token):
    print("\n=== TEST: GET /kpi (lãnh đạo) ===")
    resp = await client.get(
        f"{BASE}/kpi",
        headers={"Authorization": f"Bearer {ld_token}"},
    )
    assert resp.status_code == 200, f"Lỗi: {resp.text}"
    data = resp.json()
    print(f"  Tổng cán bộ     : {data['total']}")
    for cb in data["data"]:
        print(f"  {cb['can_bo']['ho_ten']:20s} | Điểm KPI: {cb['diem_kpi']:5.1f} | {cb['xep_loai']}")
    print("  [PASS]")

    print("\n=== TEST: GET /kpi/me (cán bộ tự xem) ===")
    resp2 = await client.get(
        f"{BASE}/kpi/me",
        headers={"Authorization": f"Bearer {cb_token}"},
    )
    assert resp2.status_code == 200
    d = resp2.json()["data"]
    print(f"  Hồ sơ tổng      : {d['ho_so']['tong']}")
    print(f"  Tỷ lệ đúng hạn  : {d['ho_so']['ty_le_dung_han_pct']}%")
    print(f"  Nhiệm vụ        : {d['nhiem_vu']['tong']} (xong: {d['nhiem_vu']['hoan_thanh']})")
    print(f"  Điểm KPI        : {d['diem_kpi']} — {d['xep_loai']}")
    print("  [PASS]")


async def main():
    print("=" * 55)
    print("  SPRINT 7 — NHIỆM VỤ & KPI — TEST SUITE")
    print("=" * 55)

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            await client.get(f"{BASE.replace('/api/v1', '')}/docs")
        except Exception:
            print("\n[ERROR] Server không chạy!\n")
            return

        ld_token = await login(client, "lanhdao01", "LanhDao@123")
        cb_token = await login(client, "canbo01", "CanBo@123")
        print(f"[LOGIN] lãnh đạo OK | cán bộ OK")

        # Lấy cb_id để dùng test phan quyen
        resp = await client.get(
            f"{BASE}/auth/me",
            headers={"Authorization": f"Bearer {cb_token}"},
        )
        cb_id = resp.json()["id"]

        await test_tao_nhiem_vu(client, ld_token, cb_token)
        await test_can_bo_khong_tao_duoc(client, cb_token, cb_id)
        await test_danh_sach(client, ld_token, cb_token)
        await test_cap_nhat_trang_thai(client, cb_token)
        await test_kpi(client, ld_token, cb_token)

    print("\n" + "=" * 55)
    print("  TẤT CẢ TEST SPRINT 7 HOÀN THÀNH")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())

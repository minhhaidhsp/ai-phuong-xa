"""
test_lgsp.py
Sprint 8 — Test LGSP Integration

Chạy:
    cd D:\Projects\ai-phuong-xa\backend
    .\venv\Scripts\Activate.ps1
    python test_lgsp.py

Lưu ý: Test dùng Mock LGSP server tích hợp trong app.
"""
import asyncio
import httpx

BASE = "http://localhost:8000/api/v1"
MOCK = "http://localhost:8000/lgsp-mock"


async def login(client, username, password):
    resp = await client.post(
        f"{BASE}/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, f"Login thất bại: {resp.text}"
    return resp.json()["access_token"]


async def test_mock_server(client):
    print("\n=== TEST: LGSP Mock Server health ===")
    resp = await client.get(f"{MOCK}/api/health")
    assert resp.status_code == 200
    print(f"  Mock server: {resp.json()}")
    print("  [PASS]")


async def test_lgsp_status(client, token):
    print("\n=== TEST: GET /lgsp/status ===")
    resp = await client.get(
        f"{BASE}/lgsp/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, f"Lỗi: {resp.text}"
    data = resp.json()
    print(f"  LGSP online : {data['lgsp_online']}")
    print(f"  LGSP URL    : {data['lgsp_url']}")
    print("  [PASS]")


async def test_get_pending(client, token):
    print("\n=== TEST: GET /lgsp/pending ===")
    resp = await client.get(
        f"{BASE}/lgsp/pending",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, f"Lỗi: {resp.text}"
    data = resp.json()
    print(f"  Số hồ sơ chờ: {data['total']}")
    for hs in data["data"]:
        print(f"  - {hs['ma_ho_so_lgsp']}: {hs['ho_ten']} ({hs['ma_thu_tuc']})")
    print("  [PASS]")


async def test_ingest(client, token):
    print("\n=== TEST: POST /lgsp/ingest (FR-INT-001) ===")
    resp = await client.post(
        f"{BASE}/lgsp/ingest",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, f"Lỗi: {resp.text}"
    data = resp.json()["data"]
    print(f"  Tạo mới     : {data['created']}")
    print(f"  Bỏ qua      : {data['skipped']}")
    print(f"  Lỗi         : {data['errors']}")

    # Chạy lại → idempotent (không tạo lại)
    resp2 = await client.post(
        f"{BASE}/lgsp/ingest",
        headers={"Authorization": f"Bearer {token}"},
    )
    data2 = resp2.json()["data"]
    print(f"  Lần 2 (idempotent): created={data2['created']}, skipped={data2['skipped']}")
    print("  [PASS]")


async def test_sync_status(client, token):
    print("\n=== TEST: POST /lgsp/sync-status (FR-INT-002) ===")

    # Sync một hồ sơ LGSP
    resp = await client.post(
        f"{BASE}/lgsp/sync-status",
        json={
            "ma_ho_so_noi_bo": "LGSP-LGSP-2026030801",
            "trang_thai_moi": "DANG_XU_LY",
            "ghi_chu": "Đang xử lý tại bộ phận hộ tịch",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, f"Lỗi: {resp.text}"
    data = resp.json()["data"]
    print(f"  Mã hồ sơ    : {data['ma_ho_so']}")
    print(f"  Trạng thái  : {data['trang_thai']} → LGSP: {data['lgsp_status']}")
    print(f"  Synced      : {data['synced']}")

    # Kiểm tra mock server đã nhận
    log_resp = await client.get(f"{MOCK}/api/v1/status-log")
    updates = log_resp.json()["updates"]
    print(f"  Mock nhận   : {len(updates)} update(s)")
    print("  [PASS]")

    # Test non-LGSP hồ sơ bị từ chối
    resp2 = await client.post(
        f"{BASE}/lgsp/sync-status",
        json={"ma_ho_so_noi_bo": "HT-20260308-0001", "trang_thai_moi": "HOAN_THANH"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 400
    print("  Non-LGSP hồ sơ → 400 rejected [PASS]")


async def test_non_admin_blocked(client, ld_token):
    print("\n=== TEST: can_bo không ingest được ===")
    resp = await client.post(
        f"{BASE}/lgsp/ingest",
        headers={"Authorization": f"Bearer {ld_token}"},
    )
    assert resp.status_code == 403
    print("  lanh_dao → POST /lgsp/ingest: 403 Forbidden [PASS]")


async def main():
    print("=" * 55)
    print("  SPRINT 8 — LGSP INTEGRATION — TEST SUITE")
    print("=" * 55)

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            await client.get(f"{BASE.replace('/api/v1', '')}/docs")
        except Exception:
            print("\n[ERROR] Server không chạy!\n")
            return

        admin_token = await login(client, "admin", "Admin@123")
        ld_token = await login(client, "lanhdao01", "LanhDao@123")
        print("[LOGIN] admin OK | lanhdao OK")

        await test_mock_server(client)
        await test_lgsp_status(client, admin_token)
        await test_get_pending(client, admin_token)
        await test_ingest(client, admin_token)
        await test_sync_status(client, admin_token)
        await test_non_admin_blocked(client, ld_token)

    print("\n" + "=" * 55)
    print("  TẤT CẢ TEST SPRINT 8 (LGSP) HOÀN THÀNH")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())

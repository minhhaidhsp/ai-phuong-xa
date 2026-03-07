"""
test_report.py
Sprint 6 - Test Bao cao & Dashboard

Chay:
    cd D:\Projects\ai-phuong-xa\backend
    .\venv\Scripts\Activate.ps1
    python test_report.py
"""
import asyncio
import httpx
import json
from datetime import date

BASE = "http://localhost:8000/api/v1"
TOKEN = None  # set sau khi login


async def login(client: httpx.AsyncClient) -> str:
    resp = await client.post(
        f"{BASE}/auth/login",
        data={"username": "lanhdao01", "password": "LanhDao@123"},
    )
    assert resp.status_code == 200, f"Login that bai: {resp.text}"
    token = resp.json()["access_token"]
    print(f"[LOGIN] OK — vai tro lanh_dao")
    return token


async def test_dashboard(client: httpx.AsyncClient, token: str):
    print("\n=== TEST: GET /report/dashboard ===")
    resp = await client.get(
        f"{BASE}/report/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, f"Loi: {resp.text}"
    data = resp.json()["data"]

    print(f"  Tong ho so      : {data['tong_ho_so']}")
    print(f"  Dang xu ly      : {data['dang_xu_ly']}")
    print(f"  Hoan thanh      : {data['hoan_thanh']}")
    print(f"  Qua han         : {data['qua_han']}")
    print(f"  Sap han         : {data['sap_han']}")
    print(f"  Ty le dung han  : {data['ty_le_dung_han_pct']}%")
    print(f"  Theo linh vuc   : {data['theo_linh_vuc']}")
    print(f"  Trend (ngay)    : {len(data['trend_30_ngay'])} diem du lieu")
    print("  [PASS]")


async def test_alerts(client: httpx.AsyncClient, token: str):
    print("\n=== TEST: GET /report/alerts ===")
    resp = await client.get(
        f"{BASE}/report/alerts?ngay_canh_bao=3",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, f"Loi: {resp.text}"
    data = resp.json()["data"]

    print(f"  Da qua han      : {len(data['da_qua_han'])} ho so")
    print(f"  Sap den han     : {len(data['sap_den_han'])} ho so")
    print(f"  Tong can xu ly  : {data['tong_can_xu_ly']}")
    if data["da_qua_han"]:
        hs = data["da_qua_han"][0]
        print(f"  Vi du qua han   : {hs['ma_ho_so']} — {hs['so_ngay_con_lai']} ngay")
    print("  [PASS]")


async def test_bao_cao_thang(client: httpx.AsyncClient, token: str):
    today = date.today()
    print(f"\n=== TEST: GET /report/thang?thang={today.month}&nam={today.year} ===")
    resp = await client.get(
        f"{BASE}/report/thang?thang={today.month}&nam={today.year}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, f"Loi: {resp.text}"
    data = resp.json()["data"]

    print(f"  Ky bao cao      : {data['tu_ngay']} -> {data['den_ngay']}")
    print(f"  Tiep nhan       : {data['tong_tiep_nhan']}")
    print(f"  Hoan thanh      : {data['tong_hoan_thanh']}")
    print(f"  Tu choi         : {data['tong_tu_choi']}")
    print(f"  Con xu ly       : {data['con_xu_ly']}")
    print(f"  Can bo KPI      : {len(data['hieu_suat_can_bo'])} nguoi")
    print("  [PASS]")


async def test_export_excel(client: httpx.AsyncClient, token: str):
    today = date.today()
    print(f"\n=== TEST: GET /report/export/excel ===")
    resp = await client.get(
        f"{BASE}/report/export/excel?thang={today.month}&nam={today.year}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 501:
        print("  [SKIP] openpyxl chua cai: pip install openpyxl --break-system-packages")
        return
    assert resp.status_code == 200, f"Loi: {resp.text}"
    ct = resp.headers.get("content-type", "")
    assert "spreadsheetml" in ct, f"Content-type sai: {ct}"
    size_kb = len(resp.content) / 1024
    print(f"  File size       : {size_kb:.1f} KB")
    print(f"  Content-Type    : {ct}")
    print("  [PASS]")


async def test_export_pdf(client: httpx.AsyncClient, token: str):
    today = date.today()
    print(f"\n=== TEST: GET /report/export/pdf ===")
    resp = await client.get(
        f"{BASE}/report/export/pdf?thang={today.month}&nam={today.year}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 501:
        print("  [SKIP] reportlab chua cai: pip install reportlab --break-system-packages")
        return
    assert resp.status_code == 200, f"Loi: {resp.text}"
    ct = resp.headers.get("content-type", "")
    assert "pdf" in ct, f"Content-type sai: {ct}"
    size_kb = len(resp.content) / 1024
    print(f"  File size       : {size_kb:.1f} KB")
    assert resp.content[:4] == b"%PDF", "Khong phai PDF hop le"
    print(f"  PDF header      : OK (%PDF)")
    print("  [PASS]")


async def test_phan_quyen(client: httpx.AsyncClient):
    """Can bo khong duoc xuat PDF/Excel"""
    print("\n=== TEST: Phan quyen — can_bo khong xuat duoc bao cao ===")
    # login can bo
    resp = await client.post(
        f"{BASE}/auth/login",
        data={"username": "canbo01", "password": "CanBo@123"},
    )
    cb_token = resp.json()["access_token"]

    resp2 = await client.get(
        f"{BASE}/report/export/excel",
        headers={"Authorization": f"Bearer {cb_token}"},
    )
    assert resp2.status_code == 403, f"Phai la 403, nhan duoc: {resp2.status_code}"
    print("  can_bo -> /export/excel: 403 Forbidden [PASS]")

    resp3 = await client.get(
        f"{BASE}/report/export/pdf",
        headers={"Authorization": f"Bearer {cb_token}"},
    )
    assert resp3.status_code == 403, f"Phai la 403, nhan duoc: {resp3.status_code}"
    print("  can_bo -> /export/pdf  : 403 Forbidden [PASS]")


async def main():
    print("=" * 55)
    print("  SPRINT 6 — BAO CAO & DASHBOARD — TEST SUITE")
    print("=" * 55)

    async with httpx.AsyncClient(timeout=30) as client:
        # Kiem tra server con song
        try:
            await client.get(f"{BASE.replace('/api/v1', '')}/docs")
        except Exception:
            print("\n[ERROR] Server khong chay. Hay chay uvicorn truoc!\n")
            return

        token = await login(client)
        await test_dashboard(client, token)
        await test_alerts(client, token)
        await test_bao_cao_thang(client, token)
        await test_export_excel(client, token)
        await test_export_pdf(client, token)
        await test_phan_quyen(client)

    print("\n" + "=" * 55)
    print("  TAT CA TEST SPRINT 6 HOAN THANH")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())

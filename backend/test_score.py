import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.post("http://localhost:8000/api/v1/auth/login",
            data={"username": "admin", "password": "Admin@123"})
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test voi min_score=0 de xem tat ca ket qua
        r = await client.post(
            "http://localhost:8000/api/v1/rag/query",
            json={
                "question": "Điều kiện đăng ký kết hôn là gì?",
                "top_k": 5,
                "min_score": 0.0   # Tat bo loc de xem het
            },
            headers=headers,
            timeout=120.0
        )
        result = r.json()
        print(f"Found: {result['found_docs']} docs")
        print("Nguon:")
        for s in result['sources']:
            print(f"  [{s['score']}] {s['ten_van_ban']} - {s['dieu_khoan']}")

asyncio.run(main())

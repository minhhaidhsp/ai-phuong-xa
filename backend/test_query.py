import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.post("http://localhost:8000/api/v1/auth/login",
            data={"username": "admin", "password": "Admin@123"})
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await client.post(
            "http://localhost:8000/api/v1/rag/query",
            json={
                "question": "Dieu kien dang ky ket hon la gi?",
                "top_k": 5,
                "min_score": 0.0
            },
            headers=headers,
            timeout=120.0
        )
        result = r.json()
        print(f"Found: {result['found_docs']} docs")
        print(f"\nTra loi:\n{result['answer']}")
        print(f"\nNguon:")
        for s in result['sources']:
            print(f"  [{s['score']}] {s['ten_van_ban']} - {s['dieu_khoan']}")

asyncio.run(main())

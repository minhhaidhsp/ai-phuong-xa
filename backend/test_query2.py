import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(timeout=300.0) as client:
        r = await client.post("http://localhost:8000/api/v1/auth/login",
            data={"username": "admin", "password": "Admin@123"})
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print("Dang goi LLM... (co the mat 1-3 phut)")
        r = await client.post(
            "http://localhost:8000/api/v1/rag/query",
            json={"question": "Dieu kien ket hon la gi?", "top_k": 5, "min_score": 0.0},
            headers=headers,
        )
        result = r.json()
        print(f"Found: {result['found_docs']} docs")
        print(f"\nTra loi:\n{result['answer']}")
        for s in result['sources']:
            print(f"  [{s['score']}] {s['ten_van_ban']}")

asyncio.run(main())

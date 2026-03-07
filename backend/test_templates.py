import asyncio, httpx

async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post("http://localhost:8000/api/v1/auth/login",
            data={"username":"admin","password":"Admin@123"})
        h = {"Authorization": f"Bearer {r.json()['access_token']}"}

        # Xem danh sach templates
        r = await client.get("http://localhost:8000/api/v1/agents/templates", headers=h)
        print("Templates:", r.json())

        # Xem placeholders cua mau 15
        r = await client.get("http://localhost:8000/api/v1/agents/templates/mau_so_15_template.docx/placeholders", headers=h)
        print("\nPlaceholders mau 15:", r.json())

asyncio.run(main())

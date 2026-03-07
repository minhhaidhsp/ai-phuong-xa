import asyncio
from qdrant_client import AsyncQdrantClient

async def main():
    client = AsyncQdrantClient(host="localhost", port=6333, check_compatibility=False)
    await client.delete_collection("van_ban_phap_luat")
    print("Da xoa collection cu")
    await client.close()

asyncio.run(main())

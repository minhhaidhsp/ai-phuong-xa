"""
test_ragas.py
Sprint 8 — Test RAGAS evaluation

Chạy:
    cd D:\Projects\ai-phuong-xa\backend
    .\venv\Scripts\Activate.ps1
    python test_ragas.py

Lưu ý: Mỗi test gọi ~4 LLM calls → mất 30-90 giây tùy máy.
"""
import asyncio
import httpx
import json

BASE = "http://localhost:8000/api/v1"


async def login(client, username, password):
    resp = await client.post(
        f"{BASE}/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, f"Login thất bại: {resp.text}"
    return resp.json()["access_token"]


async def test_evaluate_sample(client, token):
    print("\n=== TEST: POST /ragas/evaluate-sample ===")

    # Sample có sẵn (không cần RAG live)
    payload = {
        "question": "Điều kiện đăng ký kết hôn là gì?",
        "answer": "Theo Luật Hôn nhân và Gia đình 2014, điều kiện kết hôn gồm: nam từ đủ 20 tuổi, nữ từ đủ 18 tuổi; không bị mất năng lực hành vi dân sự; không thuộc các trường hợp cấm kết hôn.",
        "contexts": [
            "Điều 8 Luật Hôn nhân và Gia đình 2014: Nam từ đủ 20 tuổi trở lên, nữ từ đủ 18 tuổi trở lên.",
            "Điều 8: Người muốn kết hôn phải không bị mất năng lực hành vi dân sự.",
            "Điều 5: Cấm kết hôn giữa những người có quan hệ huyết thống trong phạm vi ba đời.",
        ],
        "ground_truth": "Nam đủ 20 tuổi, nữ đủ 18 tuổi, tự nguyện, không bị mất năng lực hành vi dân sự.",
    }

    resp = await client.post(
        f"{BASE}/ragas/evaluate-sample",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, f"Lỗi: {resp.text}"
    data = resp.json()["data"]

    print(f"  Câu hỏi         : {data['question'][:50]}...")
    print(f"  Faithfulness    : {data['scores']['faithfulness']:.2f}")
    print(f"  Answer Relevancy: {data['scores']['answer_relevancy']:.2f}")
    print(f"  Context Recall  : {data['scores']['context_recall']:.2f}")
    print(f"  Context Precision: {data['scores']['context_precision']:.2f}")
    print(f"  Overall         : {data['overall']} → Grade: {data['grade']}")
    print("  [PASS]")
    return data


async def test_get_test_set(client, token):
    print("\n=== TEST: GET /ragas/test-set ===")
    resp = await client.get(
        f"{BASE}/ragas/test-set",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, f"Lỗi: {resp.text}"
    data = resp.json()["data"]
    print(f"  Số câu hỏi mẫu  : {len(data)}")
    for q in data:
        print(f"  - {q['question'][:60]}")
    print("  [PASS]")


async def test_non_admin_blocked(client, cb_token):
    print("\n=== TEST: can_bo không được dùng RAGAS ===")
    resp = await client.get(
        f"{BASE}/ragas/test-set",
        headers={"Authorization": f"Bearer {cb_token}"},
    )
    assert resp.status_code == 403, f"Phải 403, nhận: {resp.status_code}"
    print("  can_bo → /ragas/test-set: 403 Forbidden [PASS]")


async def test_run_full_eval(client, token):
    print("\n=== TEST: POST /ragas/run-eval (2 samples) ===")
    print("  (Đang chạy LLM judge... ~60-120s)")

    payload = {
        "test_set": [
            {
                "question": "Điều kiện đăng ký kết hôn là gì?",
                "answer": "Nam từ đủ 20 tuổi, nữ từ đủ 18 tuổi, tự nguyện, không cận huyết.",
                "contexts": [
                    "Điều 8 Luật HN&GĐ: Nam đủ 20, nữ đủ 18 tuổi.",
                    "Không bị mất năng lực hành vi dân sự.",
                ],
                "ground_truth": "Nam đủ 20, nữ đủ 18, tự nguyện, không bị cấm.",
            },
            {
                "question": "Thủ tục đăng ký khai sinh cần giấy tờ gì?",
                "answer": "Cần giấy chứng sinh, CCCD của cha mẹ, hộ khẩu.",
                "contexts": [
                    "Đăng ký khai sinh cần: Giấy chứng sinh do cơ sở y tế cấp.",
                    "CCCD hoặc hộ chiếu còn hiệu lực của người đi đăng ký.",
                ],
                "ground_truth": "Giấy chứng sinh, CCCD cha mẹ, sổ hộ khẩu (nếu có).",
            },
        ]
    }

    resp = await client.post(
        f"{BASE}/ragas/run-eval",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=300,  # 5 phút timeout cho LLM
    )
    assert resp.status_code == 200, f"Lỗi: {resp.text}"
    result = resp.json()["data"]
    summary = result["summary"]

    print(f"  Tổng samples    : {summary['total_samples']}")
    print(f"  Avg Faithfulness: {summary['avg_scores'].get('faithfulness', 0):.2f}")
    print(f"  Avg Relevancy   : {summary['avg_scores'].get('answer_relevancy', 0):.2f}")
    print(f"  Avg Recall      : {summary['avg_scores'].get('context_recall', 0):.2f}")
    print(f"  Avg Precision   : {summary['avg_scores'].get('context_precision', 0):.2f}")
    print(f"  Avg Overall     : {summary['avg_overall']}")
    print(f"  Grade dist      : {summary['grade_distribution']}")
    print("  [PASS]")


async def main():
    print("=" * 55)
    print("  SPRINT 8 — RAGAS EVALUATION — TEST SUITE")
    print("=" * 55)

    async with httpx.AsyncClient(timeout=300) as client:
        try:
            await client.get(f"{BASE.replace('/api/v1', '')}/docs")
        except Exception:
            print("\n[ERROR] Server không chạy!\n")
            return

        admin_token = await login(client, "admin", "Admin@123")
        cb_token = await login(client, "canbo01", "CanBo@123")
        print(f"[LOGIN] admin OK | canbo01 OK")

        await test_get_test_set(client, admin_token)
        await test_non_admin_blocked(client, cb_token)
        await test_evaluate_sample(client, admin_token)
        await test_run_full_eval(client, admin_token)

    print("\n" + "=" * 55)
    print("  TẤT CẢ TEST SPRINT 8 (RAGAS) HOÀN THÀNH")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())

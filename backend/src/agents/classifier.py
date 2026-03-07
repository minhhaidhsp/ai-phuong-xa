import json
import ollama
from loguru import logger
from src.core.config import get_settings

settings = get_settings()

CLASSIFY_PROMPT = """Ban la he thong phan loai ho so hanh chinh phuong/xa TP.HCM.

Danh sach thu tuc hanh chinh co the chon:
{thu_tuc_list}

Nhiem vu: Dua vao mo ta ho so, chon thu tuc phu hop nhat.

Quy tac:
1. Chi chon TU danh sach thu tuc da cho, khong tu tao ma moi
2. Tra ve JSON duy nhat, khong giai thich them
3. Format JSON bat buoc:
{{"ma_thu_tuc":"ma_phu_hop","ten_thu_tuc":"ten day du","do_tin_cay":0.95,"ly_do":"giai thich ngan","cac_lua_chon_khac":["ma1","ma2"]}}"""


async def classify_ho_so(mo_ta: str, danh_sach_thu_tuc: list[dict]) -> dict:
    thu_tuc_text = "\n".join([
        f"- {t['ma_thu_tuc']}: {t['ten']} (Linh vuc: {t['linh_vuc']})"
        for t in danh_sach_thu_tuc
    ])
    prompt = CLASSIFY_PROMPT.format(thu_tuc_list=thu_tuc_text)
    try:
        client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
        response = await client.chat(
            model=settings.LLM_MODEL_FAST,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user",   "content": f"Mo ta ho so: {mo_ta}"},
            ],
            options={"temperature": 0.0, "num_ctx": 2048},
        )
        raw = response.message.content.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        result = json.loads(raw)
        logger.info(f"Classify: '{mo_ta[:50]}' -> {result.get('ma_thu_tuc')} ({result.get('do_tin_cay')})")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error classify: {e}")
        return {"ma_thu_tuc": None, "ten_thu_tuc": None, "do_tin_cay": 0.0,
                "ly_do": "Khong the phan loai tu dong", "cac_lua_chon_khac": []}
    except Exception as e:
        logger.error(f"Classify error: {e}")
        raise

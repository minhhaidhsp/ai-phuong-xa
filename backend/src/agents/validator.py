import json
import ollama
from loguru import logger
from src.core.config import get_settings

settings = get_settings()

VALIDATE_PROMPT = """Ban la he thong kiem tra giay to ho so hanh chinh.

Thu tuc: {ten_thu_tuc} ({ma_thu_tuc})
Giay to YEU CAU:
{yeu_cau}

Giay to DA CO:
{da_co}

So sanh va tra ve JSON duy nhat:
{{"du_giay_to":true,"ty_le_hoan_thanh":0.85,"giay_to_con_thieu":["..."],"giay_to_da_co":["..."],"ghi_chu":"..."}}"""


async def validate_giay_to(
    ma_thu_tuc: str,
    ten_thu_tuc: str,
    yeu_cau_giay_to: list[str],
    giay_to_da_co: list[str],
) -> dict:
    yeu_cau_text = "\n".join([f"- {g}" for g in yeu_cau_giay_to]) if yeu_cau_giay_to else "Khong co yeu cau cu the"
    da_co_text   = "\n".join([f"- {g}" for g in giay_to_da_co])   if giay_to_da_co   else "Chua co giay to nao"
    prompt = VALIDATE_PROMPT.format(
        ten_thu_tuc=ten_thu_tuc, ma_thu_tuc=ma_thu_tuc,
        yeu_cau=yeu_cau_text, da_co=da_co_text,
    )
    try:
        client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
        response = await client.chat(
            model=settings.LLM_MODEL_FAST,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user",   "content": "Kiem tra va tra ve JSON."},
            ],
            options={"temperature": 0.0, "num_ctx": 2048},
        )
        raw = response.message.content.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        result = json.loads(raw)
        logger.info(f"Validate {ma_thu_tuc}: du={result.get('du_giay_to')}, ty_le={result.get('ty_le_hoan_thanh')}")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error validate: {e}")
        return {"du_giay_to": False, "ty_le_hoan_thanh": 0.0,
                "giay_to_con_thieu": [], "giay_to_da_co": giay_to_da_co,
                "ghi_chu": "Khong the kiem tra tu dong, vui long kiem tra thu cong"}
    except Exception as e:
        logger.error(f"Validate error: {e}")
        raise

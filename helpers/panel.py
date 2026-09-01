import re

_TG = re.compile(r"</?tg-emoji[^>]*>", re.I)


async def paint(query, text, kb):
    clean = _TG.sub("", text or "")
    try:
        await query.edit_message_caption(caption=clean, parse_mode="HTML", reply_markup=kb)
        return True
    except Exception:
        pass
    try:
        await query.edit_message_caption(caption=clean, reply_markup=kb)
        return True
    except Exception:
        pass
    try:
        await query.edit_message_text(
            clean, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True
        )
        return True
    except Exception:
        pass
    try:
        await query.edit_message_text(clean, reply_markup=kb, disable_web_page_preview=True)
        return True
    except Exception:
        return False

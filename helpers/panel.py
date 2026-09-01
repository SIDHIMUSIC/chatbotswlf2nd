import re

_TG = re.compile(r'<tg-emoji emoji-id="\d+">(.*?)</tg-emoji>', re.I)
_TAG = re.compile(r"</?[^>]+>")


def _plain(text: str) -> str:
    text = _TG.sub(r"\1", text or "")
    return _TAG.sub("", text)


async def paint(query, text, kb):
    """Same message edit. HTML fail ho to plain retry — HOME dead na ho."""
    variants = [text, _TG.sub(r"\1", text or ""), _plain(text)]
    seen = []
    for raw in variants:
        if raw in seen:
            continue
        seen.append(raw)
        for mode in ("HTML", None):
            try:
                kwargs = {"caption": raw, "reply_markup": kb}
                if mode:
                    kwargs["parse_mode"] = mode
                await query.edit_message_caption(**kwargs)
                return True
            except Exception:
                pass
            try:
                kwargs = {
                    "text": raw,
                    "reply_markup": kb,
                    "disable_web_page_preview": True,
                }
                if mode:
                    kwargs["parse_mode"] = mode
                await query.edit_message_text(**kwargs)
                return True
            except Exception:
                pass
    try:
        await query.answer("Home")
    except Exception:
        pass
    return False

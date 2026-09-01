async def paint(query, text, kb):
    """Same message pe khol — neeche naya msg mat bhejo."""
    try:
        await query.edit_message_caption(
            caption=text, parse_mode="HTML", reply_markup=kb
        )
        return True
    except Exception:
        pass
    try:
        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=kb,
            disable_web_page_preview=True,
        )
        return True
    except Exception:
        return False

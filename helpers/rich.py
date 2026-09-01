from telegram import MessageEntity

from helpers.ui import PE

# Custom emoji entity length Telegram expect karta hai ~2 UTF-16 units
MARK = "🔥"


def u16(s: str) -> int:
    return len((s or "").encode("utf-16-le")) // 2


class Rich:
    def __init__(self):
        self.parts = []

    def t(self, s):
        self.parts.append(s or "")
        return self

    def e(self, key, fallback=None):
        self.parts.append((MARK, (PE.get(key) or "").strip()))
        return self

    def build(self):
        text = ""
        ents = []
        for p in self.parts:
            if isinstance(p, tuple):
                fb, eid = p
                start = u16(text)
                text += fb
                if eid.isdigit():
                    ents.append(
                        MessageEntity(
                            type="custom_emoji",
                            offset=start,
                            length=u16(fb),
                            custom_emoji_id=eid,
                        )
                    )
            else:
                text += p
        return text, ents

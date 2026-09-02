import time
from helpers.database import chat_logs

KEEP = 14 * 24 * 3600


def purge_old_logs():
    cut = time.time() - KEEP
    try:
        res = chat_logs.delete_many({"time": {"$lt": cut}})
        print("logs purged:", getattr(res, "deleted_count", 0))
    except Exception as e:
        print("purge skip:", e)

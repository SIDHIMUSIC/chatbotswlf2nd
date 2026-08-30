from helpers.database import users


def get_memory(user_id: int) -> dict:
    user = users.find_one({"user_id": user_id})
    if user and isinstance(user.get("memory"), dict):
        return user["memory"]
    return {}


def set_memory(user_id: int, key: str, value: str):
    key = (key or "").strip()[:80]
    value = (value or "").strip()[:300]
    if not key or not value:
        return
    users.update_one(
        {"user_id": user_id},
        {"$set": {f"memory.{key}": value}},
        upsert=True,
    )

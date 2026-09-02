import time
from helpers.database import db

clones = db.cloned_bots


def save_clone(owner_id, bot_token, bot_username, bot_id, bot_name, approved=False):
    clones.update_one(
        {"bot_id": bot_id},
        {"$set": {
            "owner_id": owner_id,
            "bot_token": bot_token,
            "bot_username": bot_username,
            "bot_name": bot_name,
            "bot_id": bot_id,
            "created_at": time.time(),
            "is_active": True,
            "approved": bool(approved),
        }},
        upsert=True,
    )


def set_approved(bot_id, approved=True):
    clones.update_one({"bot_id": int(bot_id)}, {"$set": {"approved": bool(approved)}})


def get_user_clones(owner_id):
    return list(clones.find({"owner_id": owner_id, "is_active": True}))


def get_all_clones(approved_only=False):
    q = {"is_active": True}
    if approved_only:
        q["approved"] = True
    return list(clones.find(q))


def get_clone(bot_id):
    return clones.find_one({"bot_id": int(bot_id), "is_active": True})


def delete_clone(bot_id):
    clones.update_one({"bot_id": int(bot_id)}, {"$set": {"is_active": False, "approved": False}})


def get_clone_by_token(token):
    return clones.find_one({"bot_token": token, "is_active": True})

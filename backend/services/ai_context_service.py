context_store = {}
context_meta = {}


def reset_user_context(user_id, context_key=""):
    context_store[user_id] = []
    context_meta[user_id] = {"context_pack_id": context_key}


def trim_context(user_id, max_messages=18):
    if len(context_store[user_id]) > max_messages:
        context_store[user_id] = context_store[user_id][-max_messages:]


def needs_context_reset(user_id, context_key="", reset_context=False):
    return (
        user_id not in context_store
        or reset_context
        or context_meta.get(user_id, {}).get("context_pack_id", "") != context_key
    )


def append_exchange(user_id, user_message, assistant_reply, max_messages=18):
    context_store[user_id].append({"role": "user", "content": user_message})
    context_store[user_id].append({"role": "assistant", "content": assistant_reply})
    trim_context(user_id, max_messages=max_messages)


def get_user_context(user_id):
    return context_store.get(user_id, [])


def clear_user_context(user_id):
    context_store.pop(user_id, None)
    context_meta.pop(user_id, None)

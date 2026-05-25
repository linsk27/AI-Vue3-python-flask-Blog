from services import ai_context_service as context_service


def test_context_service_resets_appends_and_trims():
    user_id = "u-test"
    context_service.clear_user_context(user_id)
    context_service.reset_user_context(user_id, "pack-1")

    assert context_service.needs_context_reset(user_id, "pack-1") is False
    assert context_service.needs_context_reset(user_id, "pack-2") is True

    for index in range(12):
        context_service.append_exchange(user_id, f"q{index}", f"a{index}", max_messages=6)

    context = context_service.get_user_context(user_id)
    assert len(context) == 6
    assert context[0]["content"] == "q9"
    assert context[-1]["content"] == "a11"

    context_service.clear_user_context(user_id)
    assert context_service.get_user_context(user_id) == []

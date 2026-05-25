from services import ai_rag_service


class FakeEngine:
    def connect(self):
        return self

    def __enter__(self):
        return object()

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_retrieve_context_pack_snippets_uses_keyword_fallback(monkeypatch):
    pack = {
        "id": 7,
        "name": "RAG 资料包",
        "type": "project",
        "stage": "Draft",
        "sources": [{"id": 1}],
        "tags": ["RAG"],
    }
    chunks = [
        {
            "source_id": 1,
            "ref_type": "custom",
            "ref_id": None,
            "title": "RAG 检索方案",
            "source_type": "文档",
            "weight": "高",
            "chunk_index": 0,
            "content": "RAG 检索会先分块，再召回相关片段。",
            "tokens_estimate": 30,
        }
    ]

    monkeypatch.setattr(ai_rag_service, "engine", FakeEngine())
    monkeypatch.setattr(ai_rag_service, "ensure_context_pack_tables", lambda conn: None)
    monkeypatch.setattr(ai_rag_service, "get_pack_or_404", lambda conn, pack_id: pack)
    monkeypatch.setattr(ai_rag_service, "get_pack_chunks", lambda conn, pack_id: chunks)
    monkeypatch.setattr(
        ai_rag_service,
        "get_embedding_config",
        lambda conn: {"configured": False, "enabled": False, "model": ""},
    )

    context_prompt, returned_pack, retrieval, error = ai_rag_service.retrieve_context_pack_snippets(
        7,
        "RAG 检索",
        allow_embedding=True,
        user={"id": 1},
        can_view_pack=lambda user, pack: True,
    )

    assert error is None
    assert returned_pack == pack
    assert "[S1] RAG 检索方案" in context_prompt
    assert retrieval["mode"] == "keyword"
    assert retrieval["semantic_unavailable_reason"] == "embedding_not_configured"
    assert retrieval["snippets"][0]["id"] == "S1"


def test_retrieve_context_pack_snippets_rejects_invisible_pack(monkeypatch):
    monkeypatch.setattr(ai_rag_service, "engine", FakeEngine())
    monkeypatch.setattr(ai_rag_service, "ensure_context_pack_tables", lambda conn: None)
    monkeypatch.setattr(ai_rag_service, "get_pack_or_404", lambda conn, pack_id: {"id": pack_id})
    monkeypatch.setattr(ai_rag_service, "get_pack_chunks", lambda conn, pack_id: [])
    monkeypatch.setattr(ai_rag_service, "get_embedding_config", lambda conn: {"configured": False, "enabled": False})

    context_prompt, pack, retrieval, error = ai_rag_service.retrieve_context_pack_snippets(
        9,
        "任意问题",
        user={"id": 2},
        can_view_pack=lambda user, pack: False,
    )

    assert context_prompt == ""
    assert pack is None
    assert retrieval is None
    assert error == "无权访问该上下文包"

import json

from services import context_pack_service as service


def test_pack_quality_and_token_budget_are_stable():
    assert service.compute_pack_quality(0, False, False, 0) == 34
    assert service.compute_pack_quality(10, True, True, 10) == 98
    assert service.estimate_token_budget([{"content": "一" * 1600}]) == "1.0k"
    assert service.estimate_token_budget([]) == "0.8k"


def test_build_markdown_includes_sources_and_tags():
    markdown = service.build_markdown(
        {
            "name": "论文资料包",
            "type": "paper",
            "stage": "Draft",
            "quality": 88,
            "tokenBudget": "1.2k",
            "intent": "整理证据",
            "summary": "已有三篇资料",
            "keyPoints": ["RAG", "引用"],
            "sources": [
                {
                    "title": "资料 A",
                    "type": "网页",
                    "weight": "高",
                    "status": "已接入",
                    "content": "<p>第一段<br>第二段</p>",
                }
            ],
            "tags": ["RAG", "AI"],
        }
    )

    assert "# 论文资料包" in markdown
    assert "### 1. 资料 A" in markdown
    assert "第一段" in markdown
    assert "第二段" in markdown
    assert "#RAG #AI" in markdown


def test_add_article_sources_inserts_and_indexes_new_articles(monkeypatch):
    inserted_values = []
    refreshed_sources = []

    monkeypatch.setattr(
        service.repo,
        "fetch_articles_by_ids",
        lambda conn, article_ids: [
            {
                "id": 3,
                "title": "RAG 检索",
                "content": "正文",
                "summary": "摘要",
                "category": "ai",
            }
        ],
    )
    monkeypatch.setattr(service.repo, "fetch_existing_article_ref_ids", lambda conn, pack_id, article_ids: set())

    def fake_insert(conn, values):
        inserted_values.append(values)
        return 12

    monkeypatch.setattr(service.repo, "insert_context_pack_source", fake_insert)
    monkeypatch.setattr(service, "refresh_source_chunks", lambda conn, source_id: refreshed_sources.append(source_id))

    result = service.add_article_sources(object(), 9, ["3", "3", "bad"])

    assert result == {"added": 1, "found": 1, "duplicates": 0}
    assert inserted_values[0]["pack_id"] == 9
    assert inserted_values[0]["ref_type"] == "article"
    assert inserted_values[0]["weight"] == "高"
    assert refreshed_sources == [12]


def test_refresh_pack_embeddings_without_config_returns_before_network(monkeypatch):
    monkeypatch.setattr(service, "get_embedding_config", lambda conn: {"configured": False})
    monkeypatch.setattr(
        service.repo,
        "fetch_chunks_for_embedding",
        lambda conn, pack_id: (_ for _ in ()).throw(AssertionError("should not fetch chunks")),
    )

    stats, error = service.refresh_pack_embeddings(object(), 1)

    assert stats is None
    assert "Embedding 未配置" in error


def test_update_context_pack_fields_normalizes_internal_payload(monkeypatch):
    updated = {}
    refreshed = []

    monkeypatch.setattr(service.repo, "update_context_pack", lambda conn, pack_id, fields: updated.update(fields))
    monkeypatch.setattr(service, "refresh_pack_metrics", lambda conn, pack_id: refreshed.append(pack_id))

    changed = service.update_context_pack_fields(
        object(),
        5,
        {
            "name": "新名称",
            "tags": "RAG，AI",
            "keyPoints": ["检索", "引用"],
        },
    )

    assert changed is True
    assert updated["name"] == "新名称"
    assert json.loads(updated["tags"]) == ["RAG", "AI"]
    assert json.loads(updated["key_points"]) == ["检索", "引用"]
    assert refreshed == [5]

import pytest

from services.rag_utils import (
    clamp_context_token_budget,
    cosine_similarity,
    estimate_tokens,
    extract_query_terms,
    is_pack_overview_query,
    normalize_source_content,
    parse_embedding,
    score_chunk,
    serialize_embedding,
    split_text_into_chunks,
)


def test_estimate_tokens_handles_cjk_and_ascii():
    assert estimate_tokens("") == 0
    assert estimate_tokens("上下文检索") >= 3
    assert estimate_tokens("retrieval augmented generation") >= 4


def test_context_budget_is_clamped_to_safe_range():
    assert clamp_context_token_budget(None) == 2600
    assert clamp_context_token_budget(100) == 800
    assert clamp_context_token_budget(99999) == 6000
    assert clamp_context_token_budget("1800") == 1800


def test_extract_query_terms_keeps_search_terms_and_removes_overview_words():
    terms = extract_query_terms("请帮我总结 RAG 检索流程")
    assert "rag" in terms
    assert "总结" not in terms
    assert "检索" in terms


def test_overview_query_detection():
    assert is_pack_overview_query("帮我概括这个上下文包")
    assert not is_pack_overview_query("检索 Flask 部署错误")


def test_normalize_source_content_strips_html_noise():
    text = normalize_source_content("<p>第一段<br>第二段</p><script>bad()</script>")
    assert "第一段" in text
    assert "第二段" in text
    assert "script" not in text
    assert "bad()" not in text


def test_split_text_into_chunks_respects_size_and_overlap():
    content = "一" * 240
    chunks = split_text_into_chunks(content, max_chars=100, overlap=20)
    assert len(chunks) == 3
    assert all(len(chunk) <= 100 for chunk in chunks)
    assert chunks[1].startswith("一")


def test_score_chunk_weights_title_and_source_priority():
    query_terms = ["检索", "rag"]
    source = {"title": "RAG 检索方案", "weight": "高"}
    high_score = score_chunk(query_terms, source, "这里介绍 rag 和检索。")
    low_score = score_chunk(query_terms, {**source, "weight": "低"}, "这里介绍 rag 和检索。")
    assert high_score > low_score
    assert score_chunk([], source, "无查询词") == 0


def test_embedding_serialization_and_similarity():
    encoded = serialize_embedding([1.0, 0.0, 1.0])
    assert parse_embedding(encoded) == [1.0, 0.0, 1.0]
    assert parse_embedding("{bad json}") == []
    assert cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine_similarity([1, 0], [1]) == 0.0

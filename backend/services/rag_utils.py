import html
import json
import math
import re
from typing import Any, Mapping, Sequence


DEFAULT_CONTEXT_TOKEN_BUDGET = 2600
MAX_CONTEXT_TOKEN_BUDGET = 6000
MIN_CONTEXT_TOKEN_BUDGET = 800
MAX_RAG_SNIPPETS = 6

QUERY_STOP_TERMS = {
    "的",
    "了",
    "和",
    "是",
    "我",
    "你",
    "它",
    "在",
    "有",
    "把",
    "这",
    "那",
    "这个",
    "那个",
    "一下",
    "什么",
    "怎么",
    "如何",
    "请问",
    "可以",
    "帮我",
}

PACK_OVERVIEW_TERMS = {
    "总结",
    "概括",
    "梳理",
    "归纳",
    "介绍",
    "上下文包",
    "资料",
    "内容",
    "整体",
}


def estimate_tokens(text_value: str | None) -> int:
    if not text_value:
        return 0
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text_value))
    other_chars = max(len(text_value) - cjk_chars, 0)
    return max(1, math.ceil(cjk_chars / 1.6 + other_chars / 4))


def clamp_context_token_budget(value: Any) -> int:
    try:
        budget = int(value)
    except (TypeError, ValueError):
        budget = DEFAULT_CONTEXT_TOKEN_BUDGET
    return max(MIN_CONTEXT_TOKEN_BUDGET, min(MAX_CONTEXT_TOKEN_BUDGET, budget))


def extract_query_terms(query: str | None) -> list[str]:
    text_value = (query or "").lower()
    words = re.findall(r"[a-z0-9_+#.-]{2,}", text_value)
    cjk_chars = re.findall(r"[\u4e00-\u9fff]", text_value)
    cjk_bigrams = ["".join(cjk_chars[index : index + 2]) for index in range(max(len(cjk_chars) - 1, 0))]
    terms = words + cjk_bigrams
    if not terms:
        terms = cjk_chars
    return list(
        dict.fromkeys(
            [
                term
                for term in terms
                if term.strip() and term not in QUERY_STOP_TERMS and term not in PACK_OVERVIEW_TERMS
            ]
        )
    )


def is_pack_overview_query(query: str | None) -> bool:
    return any(term in (query or "") for term in PACK_OVERVIEW_TERMS)


def normalize_source_content(content: str | None) -> str:
    if not content:
        return ""

    text_content = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", content, flags=re.I | re.S)
    text_content = re.sub(r"<br\s*/?>", "\n", text_content, flags=re.I)
    text_content = re.sub(r"</p\s*>", "\n", text_content, flags=re.I)
    text_content = re.sub(r"<[^>]+>", "", text_content)
    return html.unescape(re.sub(r"\n{3,}", "\n\n", text_content).strip())


def split_text_into_chunks(content: str | None, max_chars: int = 900, overlap: int = 120) -> list[str]:
    content = normalize_source_content(content)
    if not content:
        return []

    step = max(max_chars - overlap, 1)
    paragraphs = [item.strip() for item in re.split(r"\n{2,}", content) if item.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(paragraph):
                chunk = paragraph[start : start + max_chars].strip()
                if chunk:
                    chunks.append(chunk)
                start += step
            continue

        next_text = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(next_text) > max_chars and current:
            chunks.append(current.strip())
            current = paragraph
        else:
            current = next_text

    if current:
        chunks.append(current.strip())

    return chunks


def split_source_into_chunks(content: str | None, max_chars: int = 900, overlap: int = 120) -> list[str]:
    return split_text_into_chunks(content, max_chars=max_chars, overlap=overlap)


def source_weight_score(weight: str | None) -> float:
    return {
        "高": 1.35,
        "中": 1.0,
        "低": 0.75,
    }.get(weight or "中", 1.0)


def score_chunk(query_terms: Sequence[str], source: Mapping[str, Any], chunk: str | None) -> float:
    title = (source.get("title") or "").lower()
    chunk_lower = (chunk or "").lower()

    if not query_terms:
        return 0

    score = 0.0
    for term in query_terms:
        if term in title:
            score += 8
        score += min(chunk_lower.count(term), 5)

    return score * source_weight_score(source.get("weight"))


def build_pack_profile(pack: Mapping[str, Any]) -> str:
    profile_parts = [
        f"上下文包：{pack.get('name')}",
        f"类型：{pack.get('type') or '未设置'}",
        f"阶段：{pack.get('stage') or '未设置'}",
    ]
    if pack.get("intent"):
        profile_parts.append(f"目标：{pack.get('intent')}")
    if pack.get("summary"):
        profile_parts.append(f"摘要：{pack.get('summary')}")
    if pack.get("tags"):
        profile_parts.append("标签：" + "、".join(pack.get("tags") or []))
    return "\n".join(profile_parts)


def serialize_embedding(vector: Sequence[float] | None) -> str:
    return json.dumps(vector or [], ensure_ascii=False, separators=(",", ":"))


def parse_embedding(value: Any) -> list[float]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        vector = json.loads(value)
    except Exception:
        return []
    return vector if isinstance(vector, list) else []


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0
    for left_value, right_value in zip(left, right):
        dot += left_value * right_value
        left_norm += left_value * left_value
        right_norm += right_value * right_value

    if not left_norm or not right_norm:
        return 0.0
    return dot / math.sqrt(left_norm * right_norm)

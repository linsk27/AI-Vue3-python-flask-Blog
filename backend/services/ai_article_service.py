import json
import re


def extract_json_text(value):
    text_value = (value or "").strip()
    fenced = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", text_value, re.IGNORECASE)
    candidate = fenced.group(1).strip() if fenced else text_value
    if candidate.startswith("{") and candidate.endswith("}"):
        return candidate
    match = re.search(r"\{[\s\S]*\}", candidate)
    return match.group(0) if match else ""


def decode_jsonish_string(value):
    try:
        return json.loads(f'"{value}"')
    except Exception:
        return (
            value
            .replace("\\r\\n", "\n")
            .replace("\\n", "\n")
            .replace("\\r", "\n")
            .replace("\\t", "\t")
            .replace('\\"', '"')
            .replace("\\\\", "\\")
        )


def read_jsonish_string_field(source, field):
    for key in [f'"{field}"', f"'{field}'"]:
        key_index = source.find(key)
        if key_index < 0:
            continue

        colon_index = source.find(":", key_index + len(key))
        if colon_index < 0:
            continue

        cursor = colon_index + 1
        while cursor < len(source) and source[cursor].isspace():
            cursor += 1

        if cursor >= len(source) or source[cursor] not in ('"', "'"):
            continue

        quote = source[cursor]
        cursor += 1
        chars = []
        escaped = False

        while cursor < len(source):
            char = source[cursor]

            if escaped:
                chars.append(f"\\{char}")
                escaped = False
                cursor += 1
                continue

            if char == "\\":
                escaped = True
                cursor += 1
                continue

            if char == quote:
                rest = source[cursor + 1:]
                if re.match(r"\s*(,|\})", rest):
                    return decode_jsonish_string("".join(chars)).strip()

            chars.append(char)
            cursor += 1

    return ""


def read_jsonish_tags(source):
    match = re.search(r'["\']tags["\']\s*:\s*\[([\s\S]*?)\]', source)
    if not match:
        return []

    body = match.group(1)
    try:
        parsed = json.loads(f"[{body}]")
        if isinstance(parsed, list):
            return [str(tag).strip() for tag in parsed if str(tag).strip()]
    except Exception:
        pass

    return [tag.strip() for tag in re.findall(r'["\']([^"\']+)["\']', body) if tag.strip()]


def repair_article_payload(value):
    if not isinstance(value, str):
        return None

    candidate = extract_json_text(value) or value.strip()
    if not re.search(r'["\'](?:title|content|summary|category|tags)["\']\s*:', candidate):
        return None

    content = read_jsonish_string_field(candidate, "content")
    if not content:
        return None

    return {
        "title": read_jsonish_string_field(candidate, "title"),
        "content": content,
        "summary": read_jsonish_string_field(candidate, "summary"),
        "category": read_jsonish_string_field(candidate, "category"),
        "tags": read_jsonish_tags(candidate),
    }


def looks_like_article_json_envelope(value):
    return bool(isinstance(value, str) and value.strip().startswith("{") and re.search(r'["\']content["\']\s*:', value))


def normalize_article_payload(raw_content, topic):
    article_data = None

    for candidate in [extract_json_text(raw_content), raw_content]:
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate.strip())
            if isinstance(parsed, dict):
                article_data = parsed
                break
        except Exception:
            continue

    if article_data is None:
        article_data = repair_article_payload(raw_content)

    if article_data is None:
        if looks_like_article_json_envelope(raw_content):
            raise ValueError("AI 返回了无法解析的 JSON 外壳")
        article_data = {
            "title": topic[:28],
            "content": raw_content.strip(),
            "summary": "",
            "category": "other",
            "tags": ["AI生成"],
        }

    nested_content = article_data.get("content")
    if isinstance(nested_content, str):
        nested_data = None
        for candidate in [extract_json_text(nested_content), nested_content]:
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate.strip())
                if isinstance(parsed, dict) and (parsed.get("content") or parsed.get("title")):
                    nested_data = parsed
                    break
            except Exception:
                continue
        if nested_data is None:
            nested_data = repair_article_payload(nested_content)
        if nested_data:
            article_data.update({key: value for key, value in nested_data.items() if value})

    content = article_data.get("content")
    if not isinstance(content, str):
        raise ValueError("AI 返回的 content 不是文本")

    content = decode_jsonish_string(content).strip()
    repaired_content = repair_article_payload(content)
    if repaired_content:
        article_data.update({key: value for key, value in repaired_content.items() if value})
        content = repaired_content["content"].strip()

    if not content or looks_like_article_json_envelope(content):
        raise ValueError("AI 返回的正文仍是 JSON 外壳")

    allowed_categories = {"frontend", "backend", "database", "algorithm", "devops", "architecture", "ai", "other"}
    title = article_data.get("title") if isinstance(article_data.get("title"), str) else ""
    summary = article_data.get("summary") if isinstance(article_data.get("summary"), str) else ""
    category = article_data.get("category") if article_data.get("category") in allowed_categories else "other"
    tags = article_data.get("tags") if isinstance(article_data.get("tags"), list) else []
    tags = [str(tag).strip() for tag in tags if str(tag).strip()][:6]

    return {
        "title": title.strip() or topic[:28],
        "content": content,
        "summary": summary.strip() or content[:150].replace("\n", " ") + "...",
        "category": category,
        "tags": tags or ["AI生成"],
    }

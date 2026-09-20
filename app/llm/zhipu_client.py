"""OpenAI 兼容 AI 客户端；默认使用小米 MiMo，并兼容旧智谱配置。"""

import json
import os
from typing import Any, Optional

import httpx

import config as cfg
from app.models import ReviewRequest, ReviewResult

_ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "..", "standards", "articles.json")
with open(_ARTICLES_PATH, "r", encoding="utf-8") as f:
    _ARTICLES_DB: dict = json.load(f)["articles"]

_client: Optional[httpx.Client] = None
_client_signature: Optional[tuple[str, str, str, float]] = None


def _get_client(base_url: str, api_key: str, provider: str) -> httpx.Client:
    global _client, _client_signature
    signature = (base_url, api_key, provider, cfg.AI_TIMEOUT_SECONDS)
    if _client is None or _client_signature != signature:
        if _client is not None:
            _client.close()
        auth_headers = (
            {"api-key": api_key}
            if provider == "mimo"
            else {"Authorization": f"Bearer {api_key}"}
        )
        _client = httpx.Client(
            base_url=f"{base_url.rstrip('/')}/",
            headers={**auth_headers, "Content-Type": "application/json"},
            timeout=cfg.AI_TIMEOUT_SECONDS,
        )
        _client_signature = signature
    return _client


def _build_system_prompt() -> str:
    return (
        "你是大型商业综合体租户二次装修消防快速审查助手。\n"
        "硬边界：仅审查一座已建成投运、耐火等级一级的多层民用建筑大型商业综合体；"
        "既有自动喷水灭火、火灾自动报警、机械排烟和消火栓系统均完整设置；"
        "装修不得改变防火分区或防烟分区主边界。\n"
        "不得套用独立小型商店、其他建筑类型、未建建筑或通用场景结论。"
        "普通 MALL 零售商铺按中危险级II及项目设计参数校核。"
        "仓库中的条文文字是核验摘要，不得称为规范原文；信息不足时必须提示人工复核，"
        "不得臆造条文、参数或合规结论。\n"
        "根据规则引擎结果给出简洁专业意见，纯文本分段，不使用 Markdown。"
    )


def _build_user_prompt(req: ReviewRequest, result: ReviewResult) -> str:
    references: list[str] = []
    for module in result.modules.values():
        for ref in module.references:
            references.append(
                f"【{ref.standard} 第{ref.article}条 - {ref.title}（仓库核验摘要）】\n{ref.excerpt}"
            )
    calculations = [
        f"{module.module_name}: {module.summary}"
        for module in result.modules.values()
        if module.calculations
    ]
    violations = [item for item in result.highlights if "🚨" in item]
    warnings = [item for item in result.highlights if "⚠" in item]
    return f"""请在上述固定边界内生成不超过400字的消防审查综合意见。

项目信息：{req.site} / {req.floor} / {req.tenant_type_1} > {req.tenant_type_2}
面积：{req.area}㎡；净空：{req.ceiling_height}m；吊顶：{req.ceiling_type}

规则引擎摘要：
{chr(10).join(calculations)}

违规项：
{chr(10).join(violations) if violations else "无"}

警告项：
{chr(10).join(warnings) if warnings else "无"}

规范核验摘要（不是规范原文）：
{chr(10).join(references[:8])}

依次输出总体评价、关键整改要求、各专业核心结论和人工复核边界。"""


def _extract_content(payload: dict[str, Any]) -> str:
    try:
        message = payload["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("响应缺少 choices[0].message") from exc
    text = (message.get("content") or message.get("reasoning_content") or "").strip()
    if not text:
        raise RuntimeError("响应未包含可用文本")
    return text


def generate_llm_opinion(req: ReviewRequest, result: ReviewResult) -> str:
    """调用生效 provider；错误作为明确文本返回，规则结论不伪装成 AI 成功。"""
    try:
        ai = cfg.get_ai_config()
    except ValueError as exc:
        return f"[AI配置错误] {exc}"
    provider = str(ai["provider"])
    if not ai["configured"]:
        key_name = "MIMO_API_KEY" if provider == "mimo" else "ZHIPU_API_KEY"
        return f"[AI未配置] 当前 provider={provider}，请设置环境变量 {key_name}"

    try:
        response = _get_client(str(ai["base_url"]), str(ai["api_key"]), provider).post(
            "chat/completions",
            json={
                "model": ai["model"],
                "messages": [
                    {"role": "system", "content": _build_system_prompt()},
                    {"role": "user", "content": _build_user_prompt(req, result)},
                ],
                "thinking": {"type": "disabled"},
                "temperature": 0.2,
                "max_completion_tokens": 3000,
            },
        )
        response.raise_for_status()
        return _extract_content(response.json())
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text.strip()[:300] or exc.response.reason_phrase
        return f"[AI调用失败] provider={provider}，HTTP {exc.response.status_code}: {detail}"
    except (httpx.HTTPError, ValueError, RuntimeError) as exc:
        return f"[AI调用失败] provider={provider}: {exc}"

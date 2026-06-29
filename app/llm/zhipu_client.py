"""
智谱GLM客户端
- 基于规则引擎预计算结果，生成专业审查综合意见
- 精确注入相关标准条文原文，保证知识精度
"""

import json
import os
from typing import Optional

from zhipuai import ZhipuAI

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config as cfg
from app.models import ReviewRequest, ReviewResult

# 条文库路径
_ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "..", "standards", "articles.json")
with open(_ARTICLES_PATH, "r", encoding="utf-8") as f:
    _ARTICLES_DB: dict = json.load(f)["articles"]

_client: Optional[ZhipuAI] = None


def _get_client() -> ZhipuAI:
    global _client
    if _client is None:
        if cfg.ZHIPU_API_KEY == "your_api_key_here":
            raise ValueError("请在 config.py 或 .env 文件中配置 ZHIPU_API_KEY")
        kwargs = {"api_key": cfg.ZHIPU_API_KEY}
        if cfg.ZHIPU_BASE_URL:
            kwargs["base_url"] = cfg.ZHIPU_BASE_URL
        _client = ZhipuAI(**kwargs)
    return _client


def _build_system_prompt() -> str:
    return (
        "你是一名专业的建筑消防审查工程师，具备以下专业背景：\n"
        "1. 熟悉中国现行消防技术标准（GB50016、GB50084、GB50116、GB50222、GB51251、GB51309、GB50974、GB50140）\n"
        "2. 审查对象：耐火等级一级的大型商业综合体（多层民用建筑），地上地下耐火等级均为一级\n"
        "3. 既有消防设施完整：已有自动喷水灭火系统、火灾自动报警系统、机械排烟系统\n"
        "4. 二次装修不改变防火分区及防烟分区主边界\n\n"
        "你的任务：\n"
        "- 基于规则引擎的预计算结果，生成简洁、专业的综合审查意见\n"
        "- 必须引用具体的规范编号和条文号\n"
        "- 指出关键风险点和整改建议\n"
        "- 语气专业、简洁，每点不超过2句话\n"
        "- 输出格式：纯文本，用 \\n 分段，不使用markdown标记"
    )


def _build_user_prompt(req: ReviewRequest, result: ReviewResult) -> str:
    # 收集相关条文
    relevant_articles: list[str] = []
    for mod in result.modules.values():
        for ref in mod.references:
            relevant_articles.append(
                f"【{ref.standard} 第{ref.article}条 - {ref.title}】\n{ref.excerpt}"
            )
    articles_text = "\n\n".join(relevant_articles[:8])  # 最多注入8条条文，控制token

    # 计算摘要
    calc_summary = []
    for mod_key, mod in result.modules.items():
        if mod.calculations:
            calc_summary.append(f"{mod.module_name}: {mod.summary}")

    violations = [h for h in result.highlights if "🚨" in h]
    warnings = [h for h in result.highlights if "⚠" in h]

    prompt = f"""请基于以下信息，生成一份简洁的消防审查综合意见（不超过400字）：

【项目信息】
站点：{req.site} / 楼层：{req.floor}
租户名称：{req.tenant_name or "未填写"}
业态：{req.tenant_type_1} > {req.tenant_type_2}
建筑面积：{req.area}㎡ / 净空高度：{req.ceiling_height}m / 吊顶类型：{req.ceiling_type}

【规则引擎计算结果摘要】
{chr(10).join(calc_summary)}

【违规项（须立即整改）】
{chr(10).join(violations) if violations else "无"}

【警告项（须核实）】
{chr(10).join(warnings) if warnings else "无"}

【相关规范条文（精确引用）】
{articles_text}

请输出：
1. 总体审查评价（1-2句）
2. 关键整改要求（如有违规）
3. 各专业核心结论（一句话/专业）
4. 人工复核提示
"""
    return prompt


def generate_llm_opinion(req: ReviewRequest, result: ReviewResult) -> str:
    """调用GLM生成综合审查意见，失败时返回空字符串（不影响主流程）"""
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=cfg.ZHIPU_MODEL,
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": _build_user_prompt(req, result)},
            ],
            temperature=0.2,   # 低温度，保证专业准确性
            max_tokens=3000,
        )
        msg = response.choices[0].message
        # 兼容推理模型（GLM-4.7 等）：content 为空时回退到 reasoning_content
        text = (msg.content or "").strip()
        if not text and hasattr(msg, "reasoning_content") and msg.reasoning_content:
            text = msg.reasoning_content.strip()
        return text
    except ValueError as e:
        return f"[GLM未配置] {e}"
    except Exception as e:
        return f"[GLM调用失败] {str(e)}"

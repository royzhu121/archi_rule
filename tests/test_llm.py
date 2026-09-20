import httpx

import config
from app.llm import zhipu_client
from app.models import ReviewRequest
from app.rules.engine import run_review


def _review_pair():
    request = ReviewRequest(
        floor="1F",
        tenant_type_1="普通商业零售类",
        tenant_type_2="服装/鞋履/箱包/化妆品/珠宝/钟表",
        area=200,
        ceiling_type="无吊顶",
    )
    return request, run_review(request)


def test_mimo_success_uses_official_openai_compatible_shape(monkeypatch):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["api_key"] = request.headers.get("api-key")
        captured["body"] = request.read().decode()
        return httpx.Response(200, json={"choices": [{"message": {"content": "审查意见"}}]})

    client = httpx.Client(
        base_url="https://api.xiaomimimo.com/v1/",
        headers={"api-key": "test-key"},
        transport=httpx.MockTransport(handler),
    )
    monkeypatch.setattr(
        config,
        "get_ai_config",
        lambda: {
            "provider": "mimo",
            "api_key": "test-key",
            "model": "mimo-v2.5-pro",
            "base_url": "https://api.xiaomimimo.com/v1",
            "configured": True,
        },
    )
    monkeypatch.setattr(zhipu_client, "_get_client", lambda *_: client)

    request, result = _review_pair()
    assert zhipu_client.generate_llm_opinion(request, result) == "审查意见"
    assert captured["url"].endswith("/v1/chat/completions")
    assert captured["api_key"] == "test-key"
    assert '"model":"mimo-v2.5-pro"' in captured["body"]
    assert '"max_completion_tokens":3000' in captured["body"]


def test_mimo_http_failure_is_explicit(monkeypatch):
    client = httpx.Client(
        base_url="https://api.xiaomimimo.com/v1/",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(401, text="invalid credential", request=request)
        ),
    )
    monkeypatch.setattr(
        config,
        "get_ai_config",
        lambda: {
            "provider": "mimo",
            "api_key": "bad-key",
            "model": "mimo-v2.5-pro",
            "base_url": "https://api.xiaomimimo.com/v1",
            "configured": True,
        },
    )
    monkeypatch.setattr(zhipu_client, "_get_client", lambda *_: client)
    request, result = _review_pair()

    opinion = zhipu_client.generate_llm_opinion(request, result)
    assert opinion == "[AI调用失败] provider=mimo，HTTP 401 Unauthorized"
    assert "invalid credential" not in opinion
    assert "bad-key" not in opinion


def test_mimo_missing_key_is_explicit_without_network(monkeypatch):
    monkeypatch.setattr(
        config,
        "get_ai_config",
        lambda: {
            "provider": "mimo",
            "api_key": "",
            "model": "mimo-v2.5-pro",
            "base_url": "https://api.xiaomimimo.com/v1",
            "configured": False,
        },
    )
    monkeypatch.setattr(
        zhipu_client,
        "_get_client",
        lambda *_: (_ for _ in ()).throw(AssertionError("network must not be used")),
    )
    request, result = _review_pair()
    assert zhipu_client.generate_llm_opinion(request, result) == (
        "[AI未配置] 当前 provider=mimo，请设置环境变量 MIMO_API_KEY"
    )

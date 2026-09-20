import asyncio
import importlib
import json

import httpx
import pytest

import config as cfg
from app.llm import zhipu_client
from app.main import health
from app.models import ReviewRequest, ReviewResult


@pytest.fixture(autouse=True)
def reset_client():
    zhipu_client._client = None
    zhipu_client._client_signature = None
    yield
    if zhipu_client._client is not None:
        zhipu_client._client.close()
    zhipu_client._client = None
    zhipu_client._client_signature = None


@pytest.fixture
def review_input():
    request = ReviewRequest(
        floor="1F",
        tenant_type_1="普通商业零售类",
        tenant_type_2="服装",
        area=100,
        ceiling_type="无吊顶",
    )
    result = ReviewResult(
        requires_manual=False,
        manual_reasons=[],
        overall_status="review_complete",
        overall_summary="通过",
        modules={},
        highlights=[],
    )
    return request, result


def configure(monkeypatch, provider, api_key="test-key"):
    monkeypatch.setattr(cfg, "AI_PROVIDER", provider)
    monkeypatch.setattr(cfg, "QWEN_API_KEY", api_key if provider == "qwen" else "")
    monkeypatch.setattr(cfg, "MIMO_API_KEY", api_key if provider == "mimo" else "")
    monkeypatch.setattr(cfg, "ZHIPU_API_KEY", api_key if provider == "zhipu" else "")


def install_transport(monkeypatch, handler):
    real_client = httpx.Client

    def client_factory(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return real_client(*args, **kwargs)

    monkeypatch.setattr(zhipu_client.httpx, "Client", client_factory)


def test_qwen_uses_bearer_url_and_compatible_payload(monkeypatch, review_input):
    configure(monkeypatch, "qwen")
    captured = {}

    def handler(request):
        captured["request"] = request
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "千问审查意见"}}]},
        )

    install_transport(monkeypatch, handler)
    assert zhipu_client.generate_llm_opinion(*review_input) == "千问审查意见"

    request = captured["request"]
    payload = captured["payload"]
    assert str(request.url) == (
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    )
    assert request.headers["Authorization"] == "Bearer test-key"
    assert "api-key" not in request.headers
    assert payload["model"] == "qwen-plus"
    assert payload["max_tokens"] == 3000
    assert "thinking" not in payload
    assert "max_completion_tokens" not in payload
    assert [message["role"] for message in payload["messages"]] == ["system", "user"]


def test_qwen_401_does_not_leak_key_or_response_body(monkeypatch, review_input):
    secret = "secret-qwen-key"
    configure(monkeypatch, "qwen", secret)

    def handler(request):
        return httpx.Response(401, text=f"invalid key {secret}")

    install_transport(monkeypatch, handler)
    opinion = zhipu_client.generate_llm_opinion(*review_input)
    assert opinion == "[AI调用失败] provider=qwen，HTTP 401 Unauthorized"
    assert secret not in opinion


def test_qwen_without_key_is_explicit(monkeypatch, review_input):
    configure(monkeypatch, "qwen", "")
    opinion = zhipu_client.generate_llm_opinion(*review_input)
    assert opinion.startswith("[AI未配置] 当前 provider=qwen")
    assert "QWEN_API_KEY" in opinion


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        (("qwen", "mimo", "zhipu"), "qwen"),
        (("", "mimo", "zhipu"), "mimo"),
        (("", "", "zhipu"), "zhipu"),
        (("", "", ""), "qwen"),
    ],
)
def test_auto_provider_priority(monkeypatch, keys, expected):
    monkeypatch.setattr(cfg, "AI_PROVIDER", "auto")
    monkeypatch.setattr(cfg, "QWEN_API_KEY", keys[0])
    monkeypatch.setattr(cfg, "MIMO_API_KEY", keys[1])
    monkeypatch.setattr(cfg, "ZHIPU_API_KEY", keys[2])
    assert cfg.get_ai_config()["provider"] == expected


def test_invalid_provider_lists_supported_values(monkeypatch):
    monkeypatch.setattr(cfg, "AI_PROVIDER", "unknown")
    with pytest.raises(ValueError, match="auto、qwen、mimo 或 zhipu"):
        cfg.get_ai_config()


def test_dashscope_api_key_alias(monkeypatch):
    with monkeypatch.context() as env:
        env.delenv("QWEN_API_KEY", raising=False)
        env.setenv("DASHSCOPE_API_KEY", "alias-key")
        reloaded = importlib.reload(cfg)
        assert reloaded.QWEN_API_KEY == "alias-key"
    importlib.reload(cfg)


def test_health_exposes_metadata_without_key(monkeypatch):
    secret = "health-secret-key"
    configure(monkeypatch, "qwen", secret)
    payload = asyncio.run(health())
    assert payload["ai"] == {
        "provider": "qwen",
        "model": "qwen-plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "configured": True,
    }
    assert secret not in json.dumps(payload, ensure_ascii=False)


@pytest.mark.parametrize(
    ("provider", "header_name", "header_value", "extra_field"),
    [
        ("mimo", "api-key", "test-key", "thinking"),
        ("zhipu", "Authorization", "Bearer test-key", "max_tokens"),
    ],
)
def test_existing_providers_regression(
    monkeypatch,
    review_input,
    provider,
    header_name,
    header_value,
    extra_field,
):
    configure(monkeypatch, provider)
    captured = {}

    def handler(request):
        captured["request"] = request
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "审查意见"}}]},
        )

    install_transport(monkeypatch, handler)
    assert zhipu_client.generate_llm_opinion(*review_input) == "审查意见"
    assert captured["request"].headers[header_name] == header_value
    assert extra_field in captured["payload"]

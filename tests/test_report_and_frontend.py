from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from fastapi.testclient import TestClient

from app.main import app
from app.models import ReviewRequest
from app.rules.engine import run_review


ROOT = Path(__file__).resolve().parents[1]


def _payload() -> dict:
    request = ReviewRequest(
        site="测试MALL",
        floor="1F",
        tenant_type_1="普通商业零售类",
        tenant_type_2="服装/鞋履/箱包/化妆品/珠宝/钟表",
        area=200,
        ceiling_type="无吊顶",
    )
    result = run_review(request)
    result.llm_opinion = "[AI未配置] 测试"
    return {"request": request.model_dump(), "result": result.model_dump()}


def test_word_download_headers_a4_and_key_sections():
    response = TestClient(app).post("/api/review/report", json=_payload())
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert "filename*=UTF-8''" in response.headers["content-disposition"]
    assert "%E6%B5%8B%E8%AF%95MALL-%E6%B6%88%E9%98%B2%E5%AE%A1%E5%9B%BE%E7%BB%93%E6%9E%9C.docx" in (
        response.headers["content-disposition"]
    )

    document = Document(BytesIO(response.content))
    section = document.sections[0]
    assert round(section.page_width.cm, 1) == 21.0
    assert round(section.page_height.cm, 1) == 29.7
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "一、项目基本信息" in text
    assert "二、总体结论" in text
    assert "三、各专业审查结果" in text
    assert "整改建议" in text
    assert "规范依据（仓库核验摘要，非规范原文）" in text
    assert "四、免责声明" in text

    with ZipFile(BytesIO(response.content)) as archive:
        assert "word/document.xml" in archive.namelist()


def test_frontend_download_button_state_and_trigger_contract():
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    assert 'id="downloadBtn"' in html
    assert 'onclick="downloadReport()" disabled' in html
    assert "downloadBtn.disabled = true;" in html
    assert "currentReview = { request: payload, result: data };" in html
    assert "downloadBtn.disabled = false;" in html
    assert "async function downloadReport()" in html
    assert "fetch(`${API}/api/review/report`" in html
    assert "anchor.download = filename;" in html
    assert "Word 报告下载失败" in html
    assert "@media (max-width: 900px)" in html

"""
FastAPI 主程序
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models import ReviewRequest, ReviewResult
from app.rules.engine import run_review
from app.llm.zhipu_client import generate_llm_opinion
from app.rules.tenant_profiles import LEVEL1_TO_LEVEL2, TENANT_PROFILES
import config as cfg

app = FastAPI(
    title="租户二次消防审图工具",
    description="耐火等级一级多层民用建筑（商业综合体）租户二次装修消防快速审查",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载前端静态文件
_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(_FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=_FRONTEND_DIR), name="static")


# ── 路由 ───────────────────────────────────────────────────

@app.get("/", response_class=FileResponse)
async def serve_frontend():
    index_path = os.path.join(_FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="前端文件未找到")
    return FileResponse(index_path)


@app.get("/api/tenant-profiles")
async def get_tenant_profiles():
    """返回业态数据（用于前端动态生成下拉菜单）"""
    return {
        "level1_options": list(LEVEL1_TO_LEVEL2.keys()),
        "level1_to_level2": LEVEL1_TO_LEVEL2,
        "profiles": {
            k: {
                "sprinkler_hazard": v.get("sprinkler_hazard"),
                "auto_review": v.get("auto_review"),
                "fire_risk": v.get("fire_risk"),
                "description": v.get("description", ""),
            }
            for k, v in TENANT_PROFILES.items()
        },
    }


@app.post("/api/review", response_model=ReviewResult)
async def review(req: ReviewRequest):
    """
    核心接口：提交审图参数，返回六大专业模块审查结论
    """
    # 1. 规则引擎计算
    result = run_review(req)

    # 2. GLM生成综合意见（失败不影响主结论）
    opinion = generate_llm_opinion(req, result)
    result.llm_opinion = opinion

    return result


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "model": cfg.ZHIPU_MODEL,
        "building_context": cfg.BUILDING_CONTEXT["description"],
    }

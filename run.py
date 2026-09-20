"""
启动脚本 - 消防审图工具
运行：python run.py
"""
import os
import sys
import subprocess

# 确保工作目录正确
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    try:
        import fastapi, uvicorn, httpx, docx, pydantic
    except ImportError:
        print("正在安装依赖（安装失败不影响启动，可手动运行 pip install -r requirements.txt）...")
        try:
            subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        except Exception:
            pass

def main():
    check_dependencies()

    import config as cfg
    ai = cfg.get_ai_config()
    if not ai["configured"]:
        print("=" * 60)
        print(f"⚠  提示：未配置 {ai['provider']} API Key")
        print("   请复制 .env.example 为 .env 并仅在环境变量中填写密钥。")
        print("   规则引擎仍可运行，AI 综合意见会明确显示未配置状态。")
        print("=" * 60)

    import uvicorn
    print(f"\n🔥 消防审图系统启动中...")
    print(f"   地址: http://{cfg.HOST}:{cfg.PORT}")
    print(f"   AI: {ai['provider']} / {ai['model']}")
    print(f"   按 Ctrl+C 停止\n")
    uvicorn.run(
        "app.main:app",
        host=cfg.HOST,
        port=cfg.PORT,
        reload=True,
        log_level="info",
    )

if __name__ == "__main__":
    main()

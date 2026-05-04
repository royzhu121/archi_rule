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
        import fastapi, uvicorn, zhipuai, pydantic
    except ImportError:
        print("正在安装依赖（安装失败不影响启动，可手动运行 pip install -r requirements.txt）...")
        try:
            subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        except Exception:
            pass

def main():
    check_dependencies()

    import config as cfg
    if cfg.ZHIPU_API_KEY == "your_api_key_here":
        print("=" * 60)
        print("⚠  提示：未配置智谱 GLM API Key")
        print("   请在 config.py 中修改 ZHIPU_API_KEY，或创建 .env 文件：")
        print("   ZHIPU_API_KEY=your_actual_key")
        print("   ZHIPU_MODEL=glm-4-plus")
        print("   (规则引擎仍可正常运行，GLM综合意见将显示提示)")
        print("=" * 60)

    import uvicorn
    print(f"\n🔥 消防审图系统启动中...")
    print(f"   地址: http://{cfg.HOST}:{cfg.PORT}")
    print(f"   模型: {cfg.ZHIPU_MODEL}")
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

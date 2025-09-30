import sys
from quiz_agents.ui.app import build_ui
from quiz_agents.api.app import app as api_app
import uvicorn

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [ui|api]")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "ui":
        demo = build_ui()
        demo.launch()
    elif mode == "api":
        uvicorn.run(api_app, host="0.0.0.0", port=8000)
    else:
        print("Invalid mode. Use 'ui' for Gradio UI or 'api' for FastAPI.")
        sys.exit(1)

if __name__ == "__main__":
    main()
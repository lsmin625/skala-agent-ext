import gradio as gr
from quiz_agents.nodes.graph import build_graph
from quiz_agents.ui.state import init_state
from quiz_agents.config import settings

quiz_app = build_graph()

def chat_fn(user_input, state):
    """사용자 입력을 처리하고 상태를 업데이트합니다."""

    app_state = state["app_state"]
    app_state.setdefault("chat_history", []).append(("user", user_input))
    app_state["user_input"] = user_input

    new_state = quiz_app.invoke(app_state)
    state["app_state"] = new_state

    chat_display = [{"role": r, "content": c} for r, c in new_state.get("chat_history", [])]
    return chat_display, state

def build_ui():
    """Gradio UI를 빌드합니다."""
    
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        ### 🧩 멀티 에이전트 퀴즈/리포트 (LangGraph)
        - 학생 예: `1반 홍길동 S25B101 010-1111-1001` → 확인 후 `퀴즈 시작`
        - 교수 예: `2025-07-07 2반 리포트 출력` / `오답 리포트` / `성적 리포트`
        """)
        chatbot = gr.Chatbot(
            label="명탐정 코난 퀴즈 챗봇",
            height=400,
            avatar_images=(str(settings.DATA_DIR/"avatar_user.png"), str(settings.DATA_DIR/"avatar_conan.png")),
            type="messages",
        )
        txt = gr.Textbox(placeholder="메시지를 입력해보세요!", show_label=False)
        state = gr.State(init_state())

        txt.submit(chat_fn, inputs=[txt, state], outputs=[chatbot, state])
        txt.submit(lambda: "", None, txt)
    return demo

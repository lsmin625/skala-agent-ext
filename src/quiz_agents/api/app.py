from fastapi import FastAPI
from quiz_agents.nodes.graph import build_graph
from quiz_agents.ui.state import init_state

app = FastAPI()
quiz_app = build_graph()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Quiz Agents API"}

@app.post("/chat")
def chat(user_input: str, state: dict = None):
    """Process user input and return the updated state."""
    if state is None:
        state = init_state()

    app_state = state["app_state"]
    app_state.setdefault("chat_history", []).append(("user", user_input))
    app_state["user_input"] = user_input

    new_state = quiz_app.invoke(app_state)
    state["app_state"] = new_state

    chat_display = [{"role": r, "content": c} for r, c in new_state.get("chat_history", [])]
    return {"chat": chat_display, "state": state}
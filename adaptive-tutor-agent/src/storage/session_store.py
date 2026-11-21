from src.models.session_state import SessionState


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, SessionState] = {}

    def get(self, session_id: str, student_id: str) -> SessionState:
        return self._sessions.setdefault(
            session_id,
            SessionState(session_id=session_id, student_id=student_id),
        )

    def update(self, state: SessionState) -> SessionState:
        self._sessions[state.session_id] = state
        return state

    def append_message(self, state: SessionState, role: str, text: str) -> SessionState:
        state.messages.append({"role": role, "text": text})
        return self.update(state)

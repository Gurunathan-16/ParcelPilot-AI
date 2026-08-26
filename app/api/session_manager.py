from typing import Dict, Any


_sessions: Dict[str, Dict[str, Any]] = {}


def get_session(session_id: str) -> Dict[str, Any]:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "history": [],
            "pending_action": None,
        }

    return _sessions[session_id]


def add_message(
    session_id: str,
    role: str,
    content: str
):
    session = get_session(session_id)

    session["history"].append({
        "role": role,
        "content": content,
    })


def set_pending_action(
    session_id: str,
    action: Dict[str, Any]
):
    session = get_session(session_id)
    session["pending_action"] = action


def get_pending_action(
    session_id: str
):
    session = get_session(session_id)

    return session.get("pending_action")


def clear_pending_action(
    session_id: str
):
    session = get_session(session_id)
    session["pending_action"] = None


def clear_session(
    session_id: str
):
    _sessions.pop(session_id, None)
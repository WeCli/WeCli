"""
Flask frontend proxy routes for TeamBot runtime APIs.
"""

from flask import jsonify, request, session
import requests


def register_teambot_routes(
    app,
    *,
    port_agent: int,
    internal_token: str,
) -> None:
    base_url = f"http://127.0.0.1:{port_agent}"

    def _internal_auth_headers():
        return {"X-Internal-Token": internal_token}

    @app.route("/proxy_teambot_subagents")
    def proxy_teambot_subagents():
        user_id = session.get("user_id", "")
        try:
            response = requests.get(
                f"{base_url}/teambot/subagents",
                params={"user_id": user_id},
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_subagent_history", methods=["POST"])
    def proxy_teambot_subagent_history():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/subagents/history",
                json={
                    "user_id": user_id,
                    "agent_ref": body.get("agent_ref", ""),
                    "limit": body.get("limit", 12),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_subagent_cancel", methods=["POST"])
    def proxy_teambot_subagent_cancel():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/subagents/cancel",
                json={
                    "user_id": user_id,
                    "agent_ref": body.get("agent_ref", ""),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_tool_policy")
    def proxy_teambot_tool_policy():
        user_id = session.get("user_id", "")
        try:
            response = requests.get(
                f"{base_url}/teambot/tool-policy",
                params={"user_id": user_id},
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_tool_policy", methods=["POST"])
    def proxy_teambot_tool_policy_update():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/tool-policy",
                json={
                    "user_id": user_id,
                    "policy": body.get("policy") or {},
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_session_runtime")
    def proxy_teambot_session_runtime():
        user_id = session.get("user_id", "")
        session_id = request.args.get("session_id", "")
        try:
            response = requests.get(
                f"{base_url}/teambot/session-runtime",
                params={"user_id": user_id, "session_id": session_id},
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_session_mode", methods=["POST"])
    def proxy_teambot_session_mode():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/session-mode",
                json={
                    "user_id": user_id,
                    "session_id": body.get("session_id", ""),
                    "mode": body.get("mode", "execute"),
                    "reason": body.get("reason", ""),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_session_inbox")
    def proxy_teambot_session_inbox():
        user_id = session.get("user_id", "")
        try:
            response = requests.get(
                f"{base_url}/teambot/session-inbox",
                params={
                    "user_id": user_id,
                    "session_id": request.args.get("session_id", ""),
                    "target_ref": request.args.get("target_ref", ""),
                    "status": request.args.get("status", "queued"),
                    "limit": request.args.get("limit", 20),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_session_inbox_send", methods=["POST"])
    def proxy_teambot_session_inbox_send():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/session-inbox/send",
                json={
                    "user_id": user_id,
                    "session_id": body.get("session_id", ""),
                    "target_ref": body.get("target_ref", ""),
                    "body": body.get("body", ""),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_session_inbox_deliver", methods=["POST"])
    def proxy_teambot_session_inbox_deliver():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/session-inbox/deliver",
                json={
                    "user_id": user_id,
                    "session_id": body.get("session_id", ""),
                    "target_ref": body.get("target_ref", ""),
                    "limit": body.get("limit", 20),
                    "force": bool(body.get("force", False)),
                },
                headers=_internal_auth_headers(),
                timeout=20,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_run_interrupt", methods=["POST"])
    def proxy_teambot_run_interrupt():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/runs/interrupt",
                json={
                    "user_id": user_id,
                    "session_id": body.get("session_id", ""),
                    "run_id": body.get("run_id", ""),
                    "agent_ref": body.get("agent_ref", ""),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_voice", methods=["POST"])
    def proxy_teambot_voice():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/voice",
                json={
                    "user_id": user_id,
                    "session_id": body.get("session_id", ""),
                    "enabled": bool(body.get("enabled", False)),
                    "auto_read_aloud": bool(body.get("auto_read_aloud", False)),
                    "last_transcript": body.get("last_transcript", ""),
                    "tts_model": body.get("tts_model", ""),
                    "tts_voice": body.get("tts_voice", ""),
                    "stt_model": body.get("stt_model", ""),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_bridge_attach", methods=["POST"])
    def proxy_teambot_bridge_attach():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/bridge/attach",
                json={
                    "user_id": user_id,
                    "session_id": body.get("session_id", ""),
                    "role": body.get("role", "viewer"),
                    "label": body.get("label", ""),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_bridge_detach", methods=["POST"])
    def proxy_teambot_bridge_detach():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/bridge/detach",
                json={
                    "user_id": user_id,
                    "bridge_id": body.get("bridge_id", ""),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_kairos", methods=["POST"])
    def proxy_teambot_kairos():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/kairos",
                json={
                    "user_id": user_id,
                    "session_id": body.get("session_id", ""),
                    "enabled": bool(body.get("enabled", False)),
                    "reason": body.get("reason", ""),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_dream", methods=["POST"])
    def proxy_teambot_dream():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/dream",
                json={
                    "user_id": user_id,
                    "session_id": body.get("session_id", ""),
                    "reason": body.get("reason", ""),
                },
                headers=_internal_auth_headers(),
                timeout=30,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_buddy", methods=["POST"])
    def proxy_teambot_buddy():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/buddy",
                json={
                    "user_id": user_id,
                    "session_id": body.get("session_id", ""),
                    "action": body.get("action", "pet"),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/proxy_teambot_tool_approval_resolve", methods=["POST"])
    def proxy_teambot_tool_approval_resolve():
        user_id = session.get("user_id", "")
        body = request.get_json(force=True) if request.is_json else {}
        try:
            response = requests.post(
                f"{base_url}/teambot/tool-approvals/resolve",
                json={
                    "user_id": user_id,
                    "approval_id": body.get("approval_id", ""),
                    "action": body.get("action", "approve"),
                    "reason": body.get("reason", ""),
                    "remember": bool(body.get("remember", False)),
                    "session_id": body.get("session_id", ""),
                },
                headers=_internal_auth_headers(),
                timeout=15,
            )
            return jsonify(response.json()), response.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

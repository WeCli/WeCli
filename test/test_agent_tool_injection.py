import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from langchain_core.messages import AIMessage, ToolMessage

from core.agent import UserAwareToolNode


class _FakeToolNode:
    def __init__(self):
        self.captured_state = None

    async def ainvoke(self, state, config):
        self.captured_state = state
        call_id = state["messages"][-1].tool_calls[0]["id"]
        return {"messages": [ToolMessage(content="ok", tool_call_id=call_id)]}


def _passthrough_hook_outcome(*_call_args, args=None, **_kwargs):
    return type("HookOutcome", (), {"args": dict(args or {}), "decision": None})()


class UserAwareToolNodeTests(unittest.IsolatedAsyncioTestCase):
    async def test_team_tools_auto_inject_username_and_team(self):
        node = UserAwareToolNode(
            [],
            lambda: [],
            find_internal_session_meta_fn=lambda user_id, session_id: {"team": "alpha"},
        )
        fake_tool_node = _FakeToolNode()
        node.tool_node = fake_tool_node

        state = {
            "user_id": "alice",
            "session_id": "sess-1",
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "skill_list", "args": {}, "id": "call_1", "type": "tool_call"}],
                )
            ],
        }

        with patch("core.agent.get_session_mode", return_value={"mode": "default"}), patch(
            "core.agent.resolve_permission_context",
            return_value=type(
                "Permission",
                (),
                {
                    "allowed": True,
                    "requires_approval": False,
                    "reason": "",
                    "matched_rule": None,
                    "policy": {},
                    "approval": None,
                },
            )(),
        ), patch("core.agent.run_tool_policy_hooks", side_effect=_passthrough_hook_outcome):
            result = await node(state, config={})

        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["messages"][0].content, "ok")
        injected_call = fake_tool_node.captured_state["messages"][-1].tool_calls[0]
        self.assertEqual(injected_call["args"]["username"], "alice")
        self.assertEqual(injected_call["args"]["team"], "alpha")


if __name__ == "__main__":
    unittest.main()

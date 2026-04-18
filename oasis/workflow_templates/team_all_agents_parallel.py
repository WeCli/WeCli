import asyncio
from pathlib import Path
import sys

# Make the project root importable even when this file lives under data/user_files/.../oasis/python/
_HERE = Path(__file__).resolve()
for _parent in [_HERE.parent, *_HERE.parents]:
    if (_parent / "oasis").is_dir() and (_parent / "src").is_dir():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from oasis.python_workflow_cli import StandaloneWorkflowContext, run_cli


async def main(ctx: StandaloneWorkflowContext):
    agents = [a for a in ctx.list_agents() if a.get("id")]
    if not agents:
        ctx.set_conclusion("No agents available.")
        ctx.set_result({"ok": False, "error": "no agents available", "team": ctx.team, "question": ctx.question})
        return

    ordered_agents = sorted(
        agents,
        key=lambda a: (
            str(a.get("kind", "")),
            str(a.get("tag", "")),
            str(a.get("name", "")),
            str(a.get("id", "")),
        ),
    )

    await ctx.publish(
        f"Parallel workflow started with {len(ordered_agents)} agents in scope '{ctx.team or 'default'}'.",
        author="workflowpy",
    )

    async def ask_agent(agent):
        reply = await ctx.send_agent(agent["id"], ctx.question)
        return {
            "agent_id": agent["id"],
            "agent_name": agent.get("name", agent["id"]),
            "agent_tag": agent.get("tag", ""),
            "ok": reply.ok,
            "content": (reply.content or "").strip(),
            "error": reply.error,
        }

    raw_results = await asyncio.gather(
        *[ask_agent(agent) for agent in ordered_agents],
        return_exceptions=True,
    )

    results = []
    for agent, item in zip(ordered_agents, raw_results):
        if isinstance(item, Exception):
            normalized = {
                "agent_id": agent["id"],
                "agent_name": agent.get("name", agent["id"]),
                "agent_tag": agent.get("tag", ""),
                "ok": False,
                "content": "",
                "error": str(item),
            }
        else:
            normalized = item
        results.append(normalized)
        if normalized["ok"]:
            await ctx.publish(normalized["content"] or "(empty reply)", author=str(normalized["agent_name"])[:80])
        else:
            await ctx.publish(
                f"FAILED: {normalized['error'] or 'unknown error'}",
                author=str(normalized["agent_name"])[:80],
            )

    success_count = sum(1 for item in results if item["ok"])
    ctx.set_conclusion(
        f"Parallel workflow completed: {success_count}/{len(ordered_agents)} agents succeeded."
    )
    ctx.set_result({
        "ok": True,
        "mode": "parallel",
        "team": ctx.team,
        "question": ctx.question,
        "agent_count": len(ordered_agents),
        "results": results,
    })


if __name__ == "__main__":
    raise SystemExit(run_cli(main))

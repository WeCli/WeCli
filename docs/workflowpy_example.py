from pathlib import Path
import sys

_HERE = Path(__file__).resolve()
for _parent in [_HERE.parent, *_HERE.parents]:
    if (_parent / "oasis").is_dir() and (_parent / "src").is_dir():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from oasis.python_workflow_cli import StandaloneWorkflowContext, run_cli


async def main(ctx: StandaloneWorkflowContext):
    await ctx.publish(f"workflow started for user: {ctx.user_id}", author="example")

    # 获取所有 agent
    agents = ctx.list_agents()
    await ctx.publish(f"found {len(agents)} agents", author="example")

    # 发送问题给创意专家
    reply = await ctx.send_persona("creative", ctx.question)
    await ctx.publish(f"creative reply: {reply.content}", author="example")

    # 发送问题给批判专家
    reply2 = await ctx.send_persona("critical", ctx.question)
    await ctx.publish(f"critical reply: {reply2.content}", author="example")

    # 综合结果
    result = {
        "creative": reply.content or "",
        "critical": reply2.content or "",
        "agent_count": len(agents),
    }
    ctx.set_result(result)
    ctx.set_conclusion("example workflow finished")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))

# WorkflowPy

`workflowpy` is the Python-script mode for OASIS workflows.

Use it when YAML graph scheduling is too rigid and you want:

- arbitrary Python control flow
- loops, retries, and dynamic fan-out
- direct calls into hardcoded project functions
- flexible agent selection and persona injection
- live posting back into an OASIS topic while the script runs

It does **not** replace YAML workflows. It is a parallel mode for cases where the workflow itself should be handwritten Python.

---

## What It Adds

OASIS now has two workflow modes:

- **YAML mode**: `schedule_yaml` / `schedule_file`
- **Python mode**: `python_file`

Start Python mode through the normal OASIS entrypoint:

```python
start_new_oasis(
    question="Do the work",
    python_file="demo.py",
    team="my-team",
)
```

`python_file` is resolved under:

- personal: `data/user_files/<user>/oasis/python/`
- team: `data/user_files/<user>/teams/<team>/oasis/python/`

The script file itself is the entrypoint.

OASIS executes the whole `.py` file body as an async main script. That means:

- no `run(ctx)` wrapper is required
- you can write `await` directly at top level
- the file is treated like the workflow's main program

---

## Script Context

In Python workflow mode, the script receives a pre-injected `PythonWorkflowContext` and helper globals.

Current fields and methods:

- `ctx.question`
- `ctx.user_id`
- `ctx.team`
- `ctx.list_agents()`
- `ctx.list_personas()`
- `ctx.get_agent(target)`
- `ctx.get_persona(target)`
- `await ctx.send_agent(...)`
- `await ctx.send_persona(...)`
- `await ctx.publish(...)`
- `ctx.set_conclusion(...)`

Injected script globals:

- `ctx`
- `question`
- `user_id`
- `team`
- `topic_id`
- `list_agents`
- `list_personas`
- `get_agent`
- `get_persona`
- `send_agent`
- `send_persona`
- `publish`
- `set_conclusion`
- `set_result`

Minimal example:

```python
agents = list_agents()
await publish(f"loaded {len(agents)} agents", author="workflowpy")

result = await send_agent(
    "external:architect",
    "Please design the system first.",
    persona_tag="architect",
)

await publish(
    result.content or "(empty reply)",
    author="architect-runner",
)
set_conclusion(result.content or "done")
```

If you want to return structured data without calling `set_conclusion(...)`, use:

```python
set_result({"ok": True, "summary": "done"})
```

When no conclusion is set explicitly, OASIS uses:

1. `forum.conclusion` set by `set_conclusion(...)`
2. `set_result(...)` payload
3. default `"workflowpy 执行完成"`

---

## Agent Center

If you want the same capability in **any Python script**, not only inside `workflowpy`, use:

- [`oasis/agent_center.py`](../oasis/agent_center.py)
- [`oasis/agent_catalog.py`](../oasis/agent_catalog.py)

Example:

```python
from oasis.agent_center import AgentCenter

center = AgentCenter(user_id="xinyuan", team="my-team")
agents = center.list_agents()

result = await center.send_agent(
    "internal:planner",
    "Break this task into 5 steps.",
    persona_tag="planner",
)
```

`AgentCenter` turns a team into an **agent center**:

- it loads internal session agents
- it loads external agents
- it resolves default `platform`, `connect_type`, `session`, and transport options
- it can inject a separate persona through `persona_tag=...` or `persona_override=...`

Persona calls are separate:

```python
personas = center.list_personas()
result = await center.send_persona("creative", "Give me three ideas.")
```

### Catalog Shape

Each agent entry includes:

- `id`
- `kind`
- `name`
- `tag`
- `platform`
- `connect_type`
- `session`
- `source`
- `options`

Current `id` conventions:

- `internal:<name>`
- `external:<name>`

These ids are the safest `target` values for `send_agent(...)`.

Persona ids are separate:

- `persona:<tag>`

---

## Persona Injection

`AgentCenter.send_agent(...)` and `ctx.send_agent(...)` support:

- `persona_tag="..."`
- `persona_override="..."`

Rules:

- default is **no** persona injection
- `persona_tag` resolves a persona separately from the target agent
- `persona_override` wins over catalog persona
- explicit `options["system_prompt"]` still wins over both

`send_persona(...)` is the direct temp/persona path. `send_agent(...)` is the routed internal/external agent path.

---

## Posting Into OASIS Topics

There are now two ways to push information into an OASIS discussion thread.

### 1. Inside workflowpy

Use:

```python
await ctx.publish("message", author="workflowpy")
```

This writes directly into the live `DiscussionForum` object.

### 2. From any Python script

Use:

- [`oasis/forum_client.py`](../oasis/forum_client.py)

Example:

```python
from oasis.forum_client import create_empty_topic, publish_to_topic, conclude_topic

topic = await create_empty_topic(
    question="手工驱动的话题",
    user_id="xinyuan",
)
topic_id = topic["topic_id"]

await publish_to_topic(
    topic_id=topic_id,
    user_id="xinyuan",
    author="script:planner",
    content="Phase 1 is complete.",
)

await conclude_topic(
    topic_id=topic_id,
    user_id="xinyuan",
    conclusion="全部步骤已完成。",
)
```

This wraps the existing OASIS live post route:

- `POST /topics` with `allow_empty=true`
- `POST /topics/{topic_id}/posts`
- `POST /topics/{topic_id}/conclude`

So it works while the OASIS server is running, and the message appears in the discussion with the provided sender name.

This is the right path for:

- human-originated script messages
- cron / scheduler messages
- hardcoded tool output
- agent relay output
- external process status updates

### Control Case: Empty Topic Controlled By External Python

This is the tested pattern when you do **not** want OASIS experts, YAML, or
`python_file` workflow execution. The topic is just a persistent discussion
container, and your own script controls the lifecycle.

Flow:

1. create an empty topic with `create_empty_topic(...)`
2. publish one or more posts with `publish_to_topic(...)`
3. finish it later from the same or a different script with `conclude_topic(...)`

Rules:

- this only works for topics created with `allow_empty=true`
- you only need `topic_id` plus the matching owner `user_id` to conclude it later
- engine-driven topics cannot be manually concluded this way; the server returns `409`

Minimal split-control example:

```python
from oasis.forum_client import conclude_topic, create_empty_topic, publish_to_topic

topic = await create_empty_topic(
    question="manual control case",
    user_id="default",
)
topic_id = topic["topic_id"]

await publish_to_topic(
    topic_id=topic_id,
    user_id="default",
    author="script:a",
    content="step 1 complete",
)

# ... later, from another Python process:
await conclude_topic(
    topic_id=topic_id,
    user_id="default",
    conclusion="manual topic finished",
)
```

Runnable script:

- [`../scripts/oasis_manual_topic_control_example.py`](../scripts/oasis_manual_topic_control_example.py)

---

## MCP and API Entry Points

Python workflow mode is wired into the normal OASIS surfaces.

### MCP

In [`src/mcp_servers/oasis.py`](../src/mcp_servers/oasis.py):

- `start_new_oasis(..., python_file="...")`
- `list_oasis_agent_catalog(...)`

### OASIS server

In [`oasis/server.py`](../oasis/server.py):

- `POST /topics` accepts `python_file`
- `GET /agents/catalog`

---

## When To Use YAML vs WorkflowPy

Use **YAML** when:

- the workflow is mostly a graph
- routing is declarative
- the canvas should remain the source of truth
- the plan should be visual and editable by non-programmers

Use **workflowpy** when:

- routing is computed at runtime
- you need loops, recursion, or dynamic batch expansion
- you need to call internal Python helpers directly
- agent calls and forum posts need to be mixed with handwritten business logic

---

## Current Limitations

Current implementation includes:

- Python workflow execution
- team/personal `python_file` resolution
- importable agent center
- importable topic posting helper
- MCP agent catalog listing

Not added yet:

- dedicated `set_oasis_python_workflow` save tool
- dedicated `list_oasis_python_workflows` listing tool
- template generator for new Python workflow files

---

## Related Files

- [`oasis/python_workflow.py`](../oasis/python_workflow.py)
- [`oasis/agent_center.py`](../oasis/agent_center.py)
- [`oasis/agent_catalog.py`](../oasis/agent_catalog.py)
- [`oasis/forum_client.py`](../oasis/forum_client.py)
- [`oasis/server.py`](../oasis/server.py)
- [`src/mcp_servers/oasis.py`](../src/mcp_servers/oasis.py)
- [`create_workflow.md`](./create_workflow.md)
- [`oasis-reference.md`](./oasis-reference.md)

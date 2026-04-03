# TeamClaw — Install, Configure & Debug Guide

> This is the complete operator manual for installing, configuring, running, and troubleshooting TeamClaw.
> For agent behavior rules and task routing, see [`AGENTS.md`](./AGENTS.md).
> For the product overview, see [`README.md`](./README.md).

---

## Standard Install Flow

### Quick Start (Zero Questions)

The simplest install — no questions asked, no manual config required:

```bash
# Linux / macOS
bash selfskill/scripts/run.sh setup          # installs uv, venv, deps, and acpx (ACP plugin)
bash selfskill/scripts/run.sh configure --init
bash selfskill/scripts/run.sh start
# → Open http://127.0.0.1:51209
# → First login: use passwordless localhost login
# → Setup wizard appears automatically if LLM not configured
```

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 setup   # installs uv, venv, deps, and acpx
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 configure --init
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 start
# → Open http://127.0.0.1:51209
```

The `setup` command automatically:
1. Installs `uv` package manager if missing
2. Creates a Python 3.11+ virtual environment
3. Installs Python dependencies from `config/requirements.txt`
4. **Installs `acpx` (ACP exchange plugin) via `npm install -g acpx@latest`** — used for external AI agent communication

The `start` command automatically:
1. Creates `config/.env` from template if missing
2. Starts all services regardless of LLM config status
3. Warms an installed OpenClaw gateway and refreshes runtime `OPENCLAW_*` values without importing OpenClaw's LLM config
4. Starts **Cloudflare Tunnel** (unless already running), then prints **`🔗 Magic link`** with correct HMAC tokens: **local** and **remote** (when `PUBLIC_DOMAIN` is set). Operators and AI agents **must** pass these links to the user after install/start — remote HTTPS login (e.g. phone) requires the remote magic link.

After startup, the frontend setup wizard handles LLM configuration via the web UI. The wizard detects local OpenClaw and Antigravity-Manager and offers one-click import buttons.

### Auto-import OpenClaw LLM (new behavior)
During `start` / `start-foreground`, if `config/.env` has no real `LLM_API_KEY` (missing or the default placeholder `your_api_key_here`), the startup scripts will auto-import provider/model/api settings from OpenClaw and write them back into `config/.env`.
If you already set a real `LLM_API_KEY`, startup will not overwrite it.

### Magic Prompts for AI Code CLI

After the first login, users can send these prompts to their AI code CLI agent:

- `阅读SKILL帮我安装并配置OpenClaw/AntiGravity`
- `帮我自动选择目前能用的最好的LLM模型`
- `帮OpenClaw安装微信插件并绑定`

---

## OpenClaw Integration (Optional)

Only install OpenClaw when the user explicitly asks for it.

Check whether OpenClaw exists:

- Linux / macOS: `command -v openclaw >/dev/null 2>&1`
- Windows PowerShell: `Get-Command openclaw -ErrorAction SilentlyContinue`

If the user explicitly wants OpenClaw integration and it is missing, use this flow:

1. Ensure `Node.js >= 22`
2. Install CLI: `npm install -g openclaw@latest --ignore-scripts`
3. Run onboarding:
   - Windows / automation: `openclaw onboard --non-interactive --accept-risk --install-daemon`
   - If you want OpenClaw to reuse an existing OpenAI key: append `--openai-api-key <LLM_API_KEY>`
   - Linux / macOS local interactive flow: `openclaw onboard --install-daemon`
4. Enable HTTP compatibility: `openclaw config set gateway.http.endpoints.chatCompletions.enabled true`
5. Restart gateway: `openclaw gateway restart`
6. Web entry points after the gateway is up:
   - OpenClaw dashboard / Control UI: `http://127.0.0.1:18789/`
   - OpenClaw OpenAI-compatible HTTP API: `http://127.0.0.1:18789/v1/chat/completions`
7. Sync TeamClaw integration:
   - Linux / macOS: `bash selfskill/scripts/run.sh check-openclaw`
   - Windows: `powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 check-openclaw`
8. If the OpenClaw dashboard shows `gateway token missing`, either:
   - paste `OPENCLAW_GATEWAY_TOKEN` into Control UI settings, or
   - for loopback-only local development, switch to no-auth:
     - `openclaw config set gateway.auth.mode none`
     - `openclaw config unset gateway.auth.token`
     - `openclaw gateway restart`
9. If TeamClaw was already running before OpenClaw was installed or reconfigured, restart TeamClaw so OASIS reloads the `openclaw` CLI.

### Provider Switching Notes

- **DeepSeek**: Update TeamClaw `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, and `LLM_PROVIDER` together. For OpenClaw, define a DeepSeek custom provider in `~/.openclaw/openclaw.json`. See [docs/openclaw-commands.md § 4](./docs/openclaw-commands.md) for the full JSON snippet. Tested stable pair: TeamClaw `LLM_BASE_URL=https://api.deepseek.com`, `LLM_MODEL=deepseek-chat`, `LLM_PROVIDER=deepseek`.
- **Antigravity-Manager** (local reverse proxy, free 67+ models via Google One Pro): `LLM_BASE_URL=http://127.0.0.1:8045`, `LLM_API_KEY=sk-antigravity`, `LLM_MODEL=gemini-3.1-pro`, `LLM_PROVIDER=antigravity`. See [docs/openclaw-commands.md § 4.1](./docs/openclaw-commands.md).
- **MiniMax** (1M context): `LLM_BASE_URL=https://api.minimaxi.com`, `LLM_MODEL=MiniMax-M2.7`, `LLM_PROVIDER=minimax`. See [docs/openclaw-commands.md § 4.2](./docs/openclaw-commands.md).

### OpenClaw Weixin Channel

Use this only when the user explicitly wants Weixin / 微信 integration.

Windows-specific notes:

1. In PowerShell, use `openclaw.cmd`, not bare `openclaw`, if script execution policy blocks `openclaw.ps1`.
2. The official installer may fail on Windows PowerShell (`npx -y @tencent-weixin/openclaw-weixin-cli@latest install`) because it shells out to `which openclaw`.
3. If that happens, use the manual Windows flow:

```powershell
openclaw.cmd plugins install "@tencent-weixin/openclaw-weixin"
openclaw.cmd config set plugins.entries.openclaw-weixin.enabled true
openclaw.cmd channels login --channel openclaw-weixin
openclaw.cmd channels list --json
openclaw.cmd gateway restart
```

4. `openclaw status` showing `openclaw-weixin | ON | SETUP | no token` means the plugin is installed but login hasn't completed.
5. After QR login succeeds, bind the Weixin account:

```powershell
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 bind-openclaw-channel main openclaw-weixin:<account_id>
```

Or via TeamClaw CLI:

```bash
uv run scripts/cli.py openclaw channels
uv run scripts/cli.py openclaw bind --data '{"agent":"main","channel":"openclaw-weixin:<account_id>"}'
```

6. After binding, verify: `uv run scripts/cli.py openclaw bindings --agent main`

---

## Advanced: Manual CLI Configuration

For users who prefer CLI over the web UI, or for automation scripts:

```bash
# Linux / macOS
bash selfskill/scripts/run.sh configure LLM_API_KEY sk-xxx
bash selfskill/scripts/run.sh configure LLM_BASE_URL https://api.example.com
bash selfskill/scripts/run.sh auto-model
bash selfskill/scripts/run.sh configure LLM_MODEL <model>
```

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 configure LLM_API_KEY sk-xxx
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 configure LLM_BASE_URL https://api.example.com
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 auto-model
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 configure LLM_MODEL <model>
```

Reverse sync to OpenClaw:

```bash
bash selfskill/scripts/run.sh sync-openclaw-llm
```

`configure` auto-syncs safe LLM updates when the TeamClaw config is complete. Partial edits intentionally stop short of rewriting OpenClaw.

For managed terminals, CI, or agent runners that clean up child processes, use `start-foreground` instead of `start`.

### Windows WSL Fallback

Use WSL only when the user wants it or native PowerShell is not suitable.

- Install WSL in an elevated PowerShell window: `wsl --install -d Ubuntu`
- Prefer a Linux-side copy of the repo instead of running directly from `/mnt/c/...`
- Keep WSL and native Windows installs on separate copies and separate ports

---

## Configuration Reference

### Recommended Keys

These keys are recommended but **not required before first start**:

| Key | Purpose |
|---|---|
| `LLM_API_KEY` | Provider API key |
| `LLM_BASE_URL` | OpenAI-compatible base URL |
| `LLM_MODEL` | Model name chosen explicitly or after `auto-model` |

If left blank, TeamClaw starts normally but LLM-dependent features won't work until configured via the web UI setup wizard.

### Optional Audio Configuration

| Key | Purpose |
|---|---|
| `TTS_MODEL` | Text-to-speech model |
| `TTS_VOICE` | Voice preset |
| `STT_MODEL` | Speech-to-text model |

Blank values follow the current LLM provider automatically.

---

## Startup Expectations

After `start`, these services should come up:

| Service | Port variable | Default |
|---|---|---|
| Agent | `PORT_AGENT` | `51200` |
| Scheduler | `PORT_SCHEDULER` | `51201` |
| OASIS | `PORT_OASIS` | `51202` |
| Frontend | `PORT_FRONTEND` | `51209` |

Useful checks:

- `bash selfskill/scripts/run.sh status` / `run.ps1 status`
- `GET http://127.0.0.1:<PORT_AGENT>/v1/models`
- Open `http://127.0.0.1:<PORT_FRONTEND>`

Notes:

- On Windows, default ports may be auto-remapped; always trust `config/.env` or `status`.
- Local `127.0.0.1` access supports passwordless login; **non-localhost / HTTPS** access uses the **magic link** from `start`, `status`, `tunnel-status`, or `start-tunnel` (not `cli.py status` alone).
- TeamClaw starts even without LLM configured. The setup wizard prompts on first login.
- `chatbot/setup.py` requires an interactive terminal. In non-interactive contexts, `launcher.py` automatically skips the chatbot menu. Force with `TEAMBOT_HEADLESS=1`.

**Mandatory for anyone guiding a user after `start`:** Reproduce or summarize the **Magic link** block (local + remote when available). Do not end the handoff with only “open localhost” if the user needs phone or HTTPS access.

---

## Common Operations

### Runtime

```bash
bash selfskill/scripts/run.sh status
bash selfskill/scripts/run.sh stop
bash selfskill/scripts/run.sh configure --show
```

**Magic link** (local + remote when Tunnel is ready) is printed by **`run.sh` / `run.ps1`** after `start` (once Tunnel has run), and again by **`status`**, **`tunnel-status`**, and **`start-tunnel`** — each uses `cli.py token generate` so the HMAC token is correct. It is **not** part of `uv run scripts/cli.py status`. Those commands also print a line **directed at AI assistants** asking them to copy the URLs into the user reply.

**Magic link user id** defaults to **`default`** (the `user_id` in `?user=` and in `token generate -u`). To generate links for another user, set **`TEAMCLAW_MAGIC_LINK_USER`** before running the script (Linux/macOS: `export TEAMCLAW_MAGIC_LINK_USER=admin`). Note: CLI chat defaults to `admin` for `-u`; magic link scripts intentionally used `default` unless you override.

```powershell
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 status
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 stop
powershell -ExecutionPolicy Bypass -File selfskill/scripts/run.ps1 configure --show
```

### CLI

```bash
uv run scripts/cli.py --help
uv run scripts/cli.py teams --help
uv run scripts/cli.py workflows --help
uv run scripts/cli.py openclaw --help
```

### Workflow Monitoring

Prefer non-blocking checks:

```bash
uv run scripts/cli.py topics show --topic-id <ID>
```

Avoid `topics watch` or `workflows conclusion` when you need a quick status snapshot.

### Team Data Layout

Team-specific data lives under:

```text
data/user_files/{user_id}/teams/{team_name}/
```

See [docs/repo-index.md](./docs/repo-index.md) and [docs/example_team.md](./docs/example_team.md).

---

## Debug Guide

### Python 2 vs Python 3

On macOS, the system `python` may point to **Python 2.7**. TeamClaw requires **Python 3.11+**.

**Symptom**: `SyntaxError: Non-ASCII character '\xe5'`

**Fix** (in order of preference):

1. Always use the canonical startup: `bash selfskill/scripts/run.sh start`
2. Activate the venv first: `source .venv/bin/activate && python scripts/launcher.py`
3. Use the venv python directly: `.venv/bin/python scripts/launcher.py`

**Never** run `cd src && python front.py` or `python3 src/front.py` directly.

Safety guards: `launcher.py` includes a Python version check and `run.sh` verifies after venv activation.

### EOFError on Startup

**Symptom**: `EOFError: EOF when reading a line` from `chatbot/setup.py`

**Cause**: Non-interactive terminal (agent runners, CI, piped scripts).

**Fix**: Use `selfskill/scripts/run.sh start` (which backgrounds `launcher.py` correctly), or set `TEAMBOT_HEADLESS=1`.

### OpenClaw Gateway Warnings

**Symptom**: `openclaw gateway status` prints RPC probe warning even when things work.

**Fix**: Confirm real health via:
- Browser: `http://127.0.0.1:18789/`
- API: `http://127.0.0.1:18789/v1/chat/completions`
- CLI: `openclaw.cmd channels list --json`

### OpenClaw 401 After Provider Switch

**Symptom**: HTTP 401 from OpenClaw after switching to Antigravity or another provider.

**Fix**: Check `openclaw config get gateway.auth`. If mode is `token`, switch to no-auth for local use:

```bash
openclaw config set gateway.auth.mode none
openclaw config unset gateway.auth.token
openclaw gateway restart
```

### TeamClaw API Returns "认证失败"

**Symptom**: Direct POST to `http://127.0.0.1:<PORT_AGENT>/v1/chat/completions` returns auth error.

**Cause**: TeamClaw's Agent API is authenticated. This doesn't mean LLM config is wrong.

**Fix**: Verify the stack with `run.sh status` or test the LLM directly:

```bash
uv run python -c "
from dotenv import load_dotenv; load_dotenv('config/.env')
from src.llm_factory import create_chat_model, extract_text
resp = create_chat_model(max_tokens=8).invoke('Reply with OK only.')
print(extract_text(resp.content))
"
```

### Ports Conflict or Auto-Remapped

**Symptom**: Services don't start or wrong port in browser.

**Fix**: On Windows, ports may auto-remap. Always trust `config/.env` or `status` output, not hardcoded ports. See [docs/ports.md](./docs/ports.md) for the complete service map.

### OpenClaw onboard Overwrites Config

**Symptom**: Re-running `openclaw onboard` changes gateway auth, default model, or provider.

**Fix**: After every `onboard`, re-check:

```bash
openclaw.cmd gateway status
openclaw.cmd models status --json
uv run scripts/cli.py openclaw bindings --agent main
```

### Windows PowerShell Execution Policy

**Symptom**: `openclaw` commands fail with `PSSecurityException`.

**Fix**: Use `openclaw.cmd` instead of bare `openclaw`:

```powershell
openclaw.cmd channels login --channel openclaw-weixin
```

---

## Reference Docs

- [AGENTS.md](./AGENTS.md) — agent behavior rules and task router
- [docs/index.md](./docs/index.md) — canonical task-based docs map
- [docs/repo-index.md](./docs/repo-index.md) — codebase and file index
- [docs/overview.md](./docs/overview.md) — product overview
- [docs/team-creator.md](./docs/team-creator.md) — Team Creator flow
- [docs/oasis-reference.md](./docs/oasis-reference.md) — OASIS runtime and orchestration
- [docs/runtime-reference.md](./docs/runtime-reference.md) — architecture and auth
- [docs/teambot-agent-runtime.md](./docs/teambot-agent-runtime.md) — TeamBot subagents and profiles
- [docs/cli.md](./docs/cli.md) — CLI reference
- [docs/build_team.md](./docs/build_team.md) — Team creation and member config
- [docs/create_workflow.md](./docs/create_workflow.md) — workflow YAML format
- [docs/example_team.md](./docs/example_team.md) — example Team files
- [docs/openclaw-commands.md](./docs/openclaw-commands.md) — OpenClaw commands
- [docs/tinyfish-monitor.md](./docs/tinyfish-monitor.md) — TinyFish monitor
- [docs/ports.md](./docs/ports.md) — service map and ports

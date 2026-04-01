const { test, expect } = require('@playwright/test');

async function installMockWebSocket(page) {
  await page.addInitScript(() => {
    const sockets = [];
    window.__teamclawSocketUrls = [];
    window.__teamclawSocketSends = [];

    class MockWebSocket {
      static CONNECTING = 0;
      static OPEN = 1;
      static CLOSING = 2;
      static CLOSED = 3;

      constructor(url) {
        this.url = url;
        this.readyState = MockWebSocket.CONNECTING;
        this.onopen = null;
        this.onmessage = null;
        this.onerror = null;
        this.onclose = null;
        sockets.push(this);
        window.__teamclawSocketUrls.push(url);
        setTimeout(() => {
          this.readyState = MockWebSocket.OPEN;
          if (typeof this.onopen === 'function') this.onopen({ type: 'open' });
        }, 0);
      }

      send(data) {
        window.__teamclawSocketSends.push({ url: this.url, data: String(data || '') });
      }

      close() {
        this.readyState = MockWebSocket.CLOSED;
        if (typeof this.onclose === 'function') this.onclose({ type: 'close' });
      }
    }

    window.WebSocket = MockWebSocket;
    window.__emitTeamClawSocket = (payload) => {
      const data = JSON.stringify(payload);
      sockets.forEach((socket) => {
        if (socket.readyState === MockWebSocket.OPEN && typeof socket.onmessage === 'function') {
          socket.onmessage({ data });
        }
      });
    };
  });
}

async function stubStudioNetwork(page, calls, options = {}) {
  const teambotState = {
    approvals: [
      {
        approval_id: 'approval-1',
        tool_name: 'run_command',
        status: 'pending',
        request_reason: 'Need shell access for verification',
      },
    ],
  };
  const currentRuntimeState = {
    status: 'success',
    session_id: 'main-session',
    session_role: 'main',
    workspace: '/tmp/teamclaw/main',
    mode: { mode: 'execute', reason: 'Runtime panel smoke' },
    plan: {
      title: 'Main session plan',
      status: 'active',
      items: [{ step: 'Keep runtime panel synced', status: 'in_progress' }],
    },
    todos: {
      items: [{ title: 'Deliver inbox', status: 'pending' }],
    },
    verifications: [],
    approvals: [],
    inbox: [
      {
        message_id: 'inbox-1',
        source_label: 'planner',
        source_session: 'subagent__planner__ada',
        body: 'Need the current session to confirm rollout timing.',
        status: 'queued',
      },
    ],
    artifacts: [],
    runs: [],
    active_run: null,
    relationships: { parent_session: '', children: [] },
    memory: {
      summary: '3 entries · kairos off',
      project_slug: 'teamclaw-main',
      entry_count: 3,
      can_dream: true,
      kairos_enabled: false,
      relevant_entries: [{ name: 'deploy_notes' }],
    },
    bridge: {
      status: 'detached',
      attached: false,
      connection_count: 0,
      sessions: [],
      primary: null,
    },
    voice: {
      enabled: false,
      auto_read_aloud: false,
      recording_supported: true,
      tts_model: 'gpt-4o-mini-tts',
      tts_voice: 'alloy',
      stt_model: 'whisper-1',
      last_transcript: '',
      status: 'disabled',
    },
    buddy: {
      compact_face: '^_^',
      name: 'Mochi',
      species: 'capybara',
      rarity: 'rare',
      personality: 'Calm but opinionated',
      reaction: 'Waiting by the prompt',
      available_actions: ['pet', 'bridge'],
    },
  };
  const subagentRuntimeState = {
    status: 'success',
    session_id: 'subagent__coder__curie',
    workspace: '/tmp/teamclaw/worktree/curie',
    plan: {
      title: 'Claude-style runtime audit',
      status: 'active',
      items: [
        { step: 'Inspect TeamBot runtime surface', status: 'completed' },
        { step: 'Verify approval roundtrip', status: 'in_progress' },
      ],
    },
    todos: {
      items: [
        { title: 'Update docs', status: 'completed' },
        { title: 'Add smoke coverage', status: 'pending' },
      ],
    },
    verifications: [
      {
        verification_id: 'verify-curie-1',
        title: 'Flask proxy chain',
        status: 'passed',
        details: 'Integration proxy verified',
      },
    ],
    approvals: teambotState.approvals,
    bridge: {
      status: 'detached',
      attached: false,
      connection_count: 0,
      sessions: [],
      primary: null,
    },
    voice: {
      enabled: false,
      auto_read_aloud: false,
      recording_supported: true,
      tts_model: 'gpt-4o-mini-tts',
      tts_voice: 'alloy',
      stt_model: 'whisper-1',
      last_transcript: '',
      status: 'disabled',
    },
    buddy: {
      compact_face: '^_^',
      name: 'Mochi',
      species: 'capybara',
      rarity: 'rare',
      personality: 'Calm but opinionated',
      reaction: 'Watching Curie work',
      available_actions: ['pet', 'bridge'],
    },
    memory: {
      summary: '2 entries · kairos off',
      project_slug: 'teamclaw-curie',
      entry_count: 2,
      can_dream: true,
      kairos_enabled: false,
      relevant_entries: [{ name: 'runtime_gap_matrix' }],
    },
    artifacts: [],
    runs: [],
    active_run: null,
    relationships: { parent_session: 'main-session', children: [] },
  };

  if (options.currentRuntime) Object.assign(currentRuntimeState, options.currentRuntime);
  if (options.subagentRuntime) Object.assign(subagentRuntimeState, options.subagentRuntime);
  const setupStatus = Object.assign(
    {
      llm_configured: true,
      openclaw_installed: true,
      antigravity_running: false,
      password_set: true,
      current_provider: 'openai',
      current_model: 'gpt-5.4',
      current_base_url: 'https://api.openai.com',
    },
    options.setupStatus || {}
  );
  const proxySettings = Object.assign(
    {
      LLM_PROVIDER: 'openai',
      LLM_API_KEY: '****saved-key',
      LLM_BASE_URL: 'https://api.openai.com',
      LLM_MODEL: 'gpt-5.4',
      TINYFISH_API_KEY: '****tinyfish',
      TINYFISH_BASE_URL: 'https://agent.tinyfish.ai',
      TINYFISH_MONITOR_DB_PATH: '/tmp/tinyfish_monitor.db',
      TINYFISH_MONITOR_TARGETS_PATH: '/tmp/tinyfish_targets.json',
      TINYFISH_MONITOR_ENABLED: 'false',
      TINYFISH_MONITOR_CRON: '',
    },
    options.proxySettings || {}
  );
  const importOpenClawPayload = Object.assign(
    {
      provider: 'openai',
      api_key: 'sk-imported',
      base_url: 'https://api.openai.com',
      model: 'gpt-5.4',
    },
    options.importOpenClawPayload || {}
  );
  const discoverModelsPayload = options.discoverModelsPayload || { models: ['gpt-5.4', 'gpt-4o'] };
  const exportOpenClawPayload = Object.assign(
    {
      ok: true,
      model_ref: 'openai/gpt-5.4',
      restarted: true,
    },
    options.exportOpenClawResponse || {}
  );

  const json = (route, payload, status = 200) =>
    route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(payload),
    });

  await page.route(/https:\/\/cdn\.tailwindcss\.com\/?.*/, (route) =>
    route.fulfill({
      contentType: 'application/javascript',
      body: 'window.tailwind = window.tailwind || {};',
    })
  );
  await page.route(/https:\/\/cdnjs\.cloudflare\.com\/.*marked.*\.js/, (route) =>
    route.fulfill({
      contentType: 'application/javascript',
      body: `
        window.marked = {
          __teamclawConfigured: false,
          parse: (value) => value,
          setOptions() {},
        };
      `,
    })
  );
  await page.route(/https:\/\/cdnjs\.cloudflare\.com\/.*highlight.*\.js/, (route) =>
    route.fulfill({
      contentType: 'application/javascript',
      body: `
        window.hljs = {
          getLanguage() { return true; },
          highlight(code) { return { value: code }; },
          highlightElement() {},
        };
      `,
    })
  );
  await page.route(/https:\/\/cdnjs\.cloudflare\.com\/.*highlight.*\.css/, (route) =>
    route.fulfill({
      contentType: 'text/css',
      body: '',
    })
  );

  await page.route('**/proxy_check_session', (route) => json(route, { valid: true, user_id: 'smoke-user' }));
  await page.route('**/proxy_tools', (route) => json(route, []));
  await page.route('**/proxy_oasis/topics', (route) => json(route, []));
  await page.route('**/proxy_sessions', (route) => json(route, { sessions: [] }));
  await page.route('**/proxy_sessions_status', (route) => json(route, { sessions: [] }));
  await page.route('**/proxy_session_history', (route) => json(route, { messages: [] }));
  await page.route('**/proxy_tunnel/status', (route) => json(route, { running: false, public_domain: '' }));
  await page.route('**/teams', (route) => json(route, { teams: ['Smoke Team'] }));
  await page.route('**/proxy_visual/experts*', (route) => json(route, []));
  await page.route('**/proxy_openclaw_sessions', (route) => json(route, { available: true, agents: [] }));
  await page.route('**/proxy_teambot_subagents', (route) =>
    json(route, {
      status: 'success',
      subagents: [
        {
          agent_id: 'worker-curie',
          name: 'Curie',
          session_id: 'subagent__coder__curie',
          agent_type: 'coder',
          description: 'Runtime smoke worker',
          parent_session: 'main-session',
          status: 'running',
          stored_status: 'running',
          updated_at: '2026-03-31T12:00:00',
          created_at: '2026-03-31T11:55:00',
          last_result: 'Collected runtime evidence.',
          workspace: '/tmp/teamclaw/worktree/curie',
          latest_run: { run_id: 'run-curie-1', status: 'running' },
        },
      ],
    })
  );
  await page.route('**/proxy_teambot_session_runtime?*', (route) =>
    {
      const url = new URL(route.request().url());
      const sessionId = url.searchParams.get('session_id') || '';
      if (sessionId === 'subagent__coder__curie') {
        return json(route, { ...subagentRuntimeState, session_id: sessionId });
      }
      currentRuntimeState.session_id = sessionId || currentRuntimeState.session_id || 'main-session';
      return json(route, { ...currentRuntimeState });
    }
  );
  await page.route('**/proxy_teambot_tool_approval_resolve', async (route) => {
    calls.approvalActions.push(await route.request().postDataJSON());
    teambotState.approvals = [
      {
        ...teambotState.approvals[0],
        status: 'approved',
      },
    ];
    subagentRuntimeState.approvals = teambotState.approvals;
    return json(route, {
      status: 'success',
      approval: {
        approval_id: 'approval-1',
        tool_name: 'run_command',
        status: 'approved',
        remember: true,
      },
    });
  });
  await page.route('**/proxy_teambot_session_inbox_deliver', async (route) => {
    calls.inboxDeliveries = (calls.inboxDeliveries || 0) + 1;
    currentRuntimeState.inbox = currentRuntimeState.inbox.map(item => ({ ...item, status: 'delivered' }));
    return json(route, { status: 'success', delivered: currentRuntimeState.inbox.length });
  });
  await page.route('**/proxy_teambot_voice', async (route) => {
    const payload = await route.request().postDataJSON();
    calls.voiceUpdates = calls.voiceUpdates || [];
    calls.voiceUpdates.push(payload);
    currentRuntimeState.voice = {
      ...currentRuntimeState.voice,
      enabled: !!payload.enabled,
      status: payload.enabled ? 'enabled' : 'disabled',
      auto_read_aloud: !!payload.auto_read_aloud,
      tts_model: payload.tts_model || currentRuntimeState.voice.tts_model,
      tts_voice: payload.tts_voice || currentRuntimeState.voice.tts_voice,
      stt_model: payload.stt_model || currentRuntimeState.voice.stt_model,
      last_transcript: payload.last_transcript || currentRuntimeState.voice.last_transcript,
    };
    return json(route, { status: 'success', voice: currentRuntimeState.voice });
  });
  await page.route('**/proxy_teambot_bridge_attach', async (route) => {
    const payload = await route.request().postDataJSON();
    calls.bridgeAttach = (calls.bridgeAttach || 0) + 1;
    const sessionId = payload.session_id || currentRuntimeState.session_id || 'main-session';
    currentRuntimeState.session_id = sessionId;
    currentRuntimeState.bridge = {
      status: 'attached',
      attached: true,
      connection_count: 0,
      sessions: [
        {
          bridge_id: 'bridge-main-1',
          session_id: sessionId,
          role: payload.role || 'viewer',
          attach_code: 'ATTACH-42',
          websocket_path: '/teambot/ws/smoke-user/bridge-main-1',
          status: 'attached',
          connection_count: 0,
        },
      ],
      primary: {
        bridge_id: 'bridge-main-1',
        session_id: sessionId,
        role: payload.role || 'viewer',
        attach_code: 'ATTACH-42',
        websocket_path: '/teambot/ws/smoke-user/bridge-main-1',
        status: 'attached',
        connection_count: 0,
      },
    };
    return json(route, {
      status: 'success',
      bridge: currentRuntimeState.bridge.primary,
    });
  });
  await page.route('**/proxy_teambot_bridge_detach', async (route) => {
    calls.bridgeDetach = (calls.bridgeDetach || 0) + 1;
    currentRuntimeState.bridge = {
      status: 'detached',
      attached: false,
      connection_count: 0,
      sessions: [],
      primary: null,
    };
    return json(route, {
      status: 'success',
      bridge: {
        bridge_id: 'bridge-main-1',
        status: 'detached',
      },
    });
  });
  await page.route('**/proxy_teambot_kairos', async (route) => {
    const payload = await route.request().postDataJSON();
    calls.kairosUpdates = calls.kairosUpdates || [];
    calls.kairosUpdates.push(payload);
    currentRuntimeState.memory = {
      ...currentRuntimeState.memory,
      kairos_enabled: !!payload.enabled,
      summary: `3 entries · kairos ${payload.enabled ? 'on' : 'off'}`,
    };
    return json(route, { status: 'success', memory: currentRuntimeState.memory });
  });
  await page.route('**/proxy_teambot_dream', async (route) => {
    calls.dreamRuns = (calls.dreamRuns || 0) + 1;
    currentRuntimeState.memory = {
      ...currentRuntimeState.memory,
      summary: '4 entries · kairos on · last dream just now',
      entry_count: 4,
      kairos_enabled: true,
      can_dream: false,
    };
    return json(route, { status: 'success', memory: currentRuntimeState.memory });
  });
  await page.route('**/proxy_teambot_buddy', async (route) => {
    const payload = await route.request().postDataJSON();
    calls.buddyActions = calls.buddyActions || [];
    calls.buddyActions.push(payload);
    currentRuntimeState.buddy = {
      ...currentRuntimeState.buddy,
      reaction: 'Purring after a bridge sync',
    };
    return json(route, { status: 'success', buddy: currentRuntimeState.buddy });
  });
  await page.route('**/proxy_teambot_tool_policy', async (route) => {
    if (route.request().method() !== 'GET') {
      return json(route, {
        status: 'success',
        policy: {
          default_approval: 'manual',
          tools: {
            run_command: { approval: 'manual' },
          },
        },
      });
    }
    return json(route, {
      status: 'success',
      policy: {
        default_approval: 'manual',
        tools: {
          run_command: { approval: 'manual' },
        },
        source: 'user',
        definition_path: '/tmp/teamclaw/policy.json',
      },
    });
  });
  await page.route('**/api/setup_status', (route) =>
    json(route, setupStatus)
  );
  await page.route('**/proxy_settings_full', async (route) => {
    if (route.request().method() !== 'GET') {
      return json(route, { status: 'success', updated: [] });
    }
    return json(route, { settings: proxySettings });
  });
  await page.route('**/api/tinyfish/status*', (route) =>
    json(route, {
      ok: true,
      config: {
        api_key_configured: true,
        targets_path_exists: true,
        base_url: 'https://agent.tinyfish.ai',
        targets_path: '/tmp/tinyfish_targets.json',
        db_path: '/tmp/tinyfish_monitor.db',
        cron: '',
        enabled: false,
      },
      pending_runs: 0,
      recent_runs: [],
      sites: [],
      recent_changes: [],
    })
  );
  await page.route('**/api/import_openclaw_config', (route) => {
    calls.importOpenClaw += 1;
    return json(route, importOpenClawPayload);
  });
  await page.route('**/api/discover_models', (route) => json(route, discoverModelsPayload));
  await page.route('**/api/export_openclaw_config', async (route) => {
    calls.exportOpenClaw += 1;
    const payload = await route.request().postDataJSON();
    calls.lastExportPayload = payload;
    return json(route, exportOpenClawPayload);
  });
  await page.route('**/api/tinyfish/run', async (route) => {
    calls.tinyfishRun += 1;
    return json(route, {
      ok: true,
      run_ids: ['run-smoke-1'],
    });
  });
}

test('studio workflow tab and settings actions stay responsive', async ({ page }) => {
  const calls = {
    importOpenClaw: 0,
    exportOpenClaw: 0,
    tinyfishRun: 0,
    lastExportPayload: null,
    approvalActions: [],
  };
  const pageErrors = [];

  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('dialog', async (dialog) => {
    pageErrors.push(`unexpected dialog: ${dialog.message()}`);
    await dialog.dismiss();
  });

  await stubStudioNetwork(page, calls);
  await page.addInitScript(() => {
    window.alert = () => {};
    window.confirm = () => true;
    localStorage.removeItem('teamclawStudioFirstVisitV2');
    localStorage.setItem('oasisTownModeEnabled', '1');
    localStorage.setItem('oasisTownWorkspaceView', 'graph');
  });

  await page.goto('/studio');

  await expect(page.locator('#chat-screen')).toBeVisible();
  await expect(page.locator('#tab-chat')).toHaveClass(/active/);
  await expect(page.locator('#oasis-panel')).toHaveClass(/collapsed-panel/);
  await expect(page.locator('#oasis-town-mode-btn')).toContainText('OFF');
  await expect.poll(() => page.evaluate(() => localStorage.getItem('oasisTownModeEnabled'))).toBe('0');
  await expect.poll(() => page.evaluate(() => localStorage.getItem('oasisTownWorkspaceView'))).toBe('town');

  await page.locator('#tab-orchestrate').click();
  await expect(page.locator('#tab-orchestrate')).toHaveClass(/active/);
  await expect(page.locator('#page-orchestrate')).toHaveClass(/active/);
  await expect.poll(async () => {
    return page.locator('#page-loading-overlay').evaluate((el) => el.classList.contains('loading-visible'));
  }).toBe(false);

  await page.locator('.hamburger-btn').click();
  await page.locator('#hamburger-panel button[onclick*="openSettings(); closeHamburgerMenu();"]').click();

  await expect(page.locator('#settings-modal')).toBeVisible();
  await expect(page.locator('#settings-export-openclaw-btn')).toBeEnabled();
  await expect(page.locator('#tinyfish-run-btn')).toBeVisible();

  await page.locator('#settings-import-openclaw-btn').click();
  await expect.poll(() => calls.importOpenClaw).toBe(1);

  await page.locator('#settings-export-openclaw-btn').click();
  await expect.poll(() => calls.exportOpenClaw).toBe(1);
  expect(calls.lastExportPayload).toMatchObject({
    provider: 'openai',
    base_url: 'https://api.openai.com',
    model: 'gpt-5.4',
  });

  await page.locator('#tinyfish-run-btn').click();
  await expect.poll(() => calls.tinyfishRun).toBe(1);

  expect(pageErrors).toEqual([]);
});

test('studio settings export button allows keyless ollama sync', async ({ page }) => {
  const calls = {
    importOpenClaw: 0,
    exportOpenClaw: 0,
    tinyfishRun: 0,
    lastExportPayload: null,
    approvalActions: [],
  };
  const pageErrors = [];

  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('dialog', async (dialog) => {
    pageErrors.push(`unexpected dialog: ${dialog.message()}`);
    await dialog.dismiss();
  });

  await stubStudioNetwork(page, calls, {
    setupStatus: {
      current_provider: 'ollama',
      current_model: 'llama3.2:latest',
      current_base_url: 'http://127.0.0.1:11434',
    },
    proxySettings: {
      LLM_PROVIDER: 'ollama',
      LLM_API_KEY: '',
      LLM_BASE_URL: 'http://127.0.0.1:11434',
      LLM_MODEL: 'llama3.2:latest',
    },
    discoverModelsPayload: { models: ['llama3.2:latest', 'qwen2.5:latest'] },
    exportOpenClawResponse: {
      ok: true,
      model_ref: 'ollama/llama3.2:latest',
      restarted: true,
    },
  });
  await page.addInitScript(() => {
    window.alert = () => {};
    window.confirm = () => true;
    localStorage.removeItem('teamclawStudioFirstVisitV2');
  });

  await page.goto('/studio');
  await page.locator('.hamburger-btn').click();
  await page.locator('#hamburger-panel button[onclick*="openSettings(); closeHamburgerMenu();"]').click();

  await expect(page.locator('#settings-modal')).toBeVisible();
  await expect(page.locator('#settings-llm-provider')).toHaveValue('ollama');
  await expect(page.locator('#settings-llm-key')).toHaveValue('');
  await page.locator('#settings-export-openclaw-btn').click();

  await expect.poll(() => calls.exportOpenClaw).toBe(1);
  expect(calls.lastExportPayload).toMatchObject({
    provider: 'ollama',
    api_key: '',
    base_url: 'http://127.0.0.1:11434',
    model: 'llama3.2:latest',
  });

  expect(pageErrors).toEqual([]);
});

test('studio teambot current runtime card stays synced over bridge websocket', async ({ page }) => {
  const calls = {
    importOpenClaw: 0,
    exportOpenClaw: 0,
    tinyfishRun: 0,
    lastExportPayload: null,
    approvalActions: [],
    bridgeAttach: 0,
    bridgeDetach: 0,
    voiceUpdates: [],
    buddyActions: [],
    kairosUpdates: [],
    dreamRuns: 0,
    inboxDeliveries: 0,
  };
  const pageErrors = [];

  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('dialog', async (dialog) => {
    pageErrors.push(`unexpected dialog: ${dialog.message()}`);
    await dialog.dismiss();
  });

  await installMockWebSocket(page);
  await stubStudioNetwork(page, calls);
  await page.addInitScript(() => {
    window.alert = () => {};
    window.confirm = () => true;
    localStorage.removeItem('teamclawSessionRuntimePanelHeightV1');
  });

  await page.goto('/studio');
  await page.locator('.hamburger-btn').click();
  await page.locator('#hamburger-panel button[onclick*="toggleSessionSidebar(); closeHamburgerMenu();"]').click();

  await expect(page.locator('#teambot-current-session')).toBeVisible();
  await expect(page.locator('#teambot-current-session')).toContainText('Current Session');
  await expect(page.locator('#teambot-current-session')).toContainText('Main session plan');
  await expect(page.locator('#teambot-current-session')).toContainText('Memory');
  await expect(page.locator('#teambot-current-session')).toContainText('Buddy');
  await expect(page.locator('#teambot-current-session')).toContainText('Waiting by the prompt');

  await page.locator('#teambot-current-session button').filter({ hasText: 'Attach' }).click();
  await expect.poll(() => calls.bridgeAttach).toBe(1);
  await expect.poll(() => page.evaluate(() => window.__teamclawSocketUrls.length)).toBe(1);
  await expect(page.locator('#teambot-current-session')).toContainText('attach=ATTACH-42');

  const currentSessionId = await page.locator('#teambot-current-session .teambot-current-card-caption').evaluate((el) => {
    return String(el.textContent || '').split(' · ')[0].trim();
  });

  await page.evaluate(({ sessionId }) => {
    window.__emitTeamClawSocket({
      type: 'runtime_update',
      changed_session_id: sessionId,
      runtime: {
        status: 'success',
        session_id: sessionId,
        session_role: 'main',
        workspace: '/tmp/teamclaw/main',
        mode: { mode: 'execute', reason: 'Bridge live update' },
        plan: {
          title: 'Main session plan',
          status: 'active',
          items: [{ step: 'Keep runtime panel synced', status: 'completed' }],
        },
        todos: { items: [{ title: 'Deliver inbox', status: 'completed' }] },
        verifications: [],
        approvals: [],
        inbox: [{ message_id: 'inbox-1', source_label: 'planner', body: 'Delivered from socket', status: 'delivered' }],
        artifacts: [],
        runs: [],
        active_run: null,
        relationships: { parent_session: '', children: [] },
        memory: {
          summary: '4 entries · kairos on · last dream just now',
          project_slug: 'teamclaw-main',
          entry_count: 4,
          can_dream: false,
          kairos_enabled: true,
          relevant_entries: [{ name: 'deploy_notes' }],
        },
        bridge: {
          status: 'attached',
          attached: true,
          connection_count: 1,
          sessions: [{
            bridge_id: 'bridge-main-1',
            session_id: sessionId,
            role: 'viewer',
            attach_code: 'ATTACH-42',
            websocket_path: '/teambot/ws/smoke-user/bridge-main-1',
            status: 'attached',
            connection_count: 1,
          }],
          primary: {
            bridge_id: 'bridge-main-1',
            session_id: sessionId,
            role: 'viewer',
            attach_code: 'ATTACH-42',
            websocket_path: '/teambot/ws/smoke-user/bridge-main-1',
            status: 'attached',
            connection_count: 1,
          },
        },
        voice: {
          enabled: true,
          auto_read_aloud: false,
          recording_supported: true,
          tts_model: 'gpt-4o-mini-tts',
          tts_voice: 'alloy',
          stt_model: 'whisper-1',
          last_transcript: 'Bridge runtime synced',
          status: 'enabled',
        },
        buddy: {
          compact_face: '^_^',
          name: 'Mochi',
          species: 'capybara',
          rarity: 'rare',
          personality: 'Calm but opinionated',
          reaction: 'Bridge sync received',
          available_actions: ['pet', 'bridge'],
        },
      },
    });
  }, { sessionId: currentSessionId });

  await expect(page.locator('#teambot-current-session')).toContainText('socket=live');
  await expect(page.locator('#teambot-current-session')).toContainText('clients=1');
  await expect(page.locator('#teambot-current-session')).toContainText('Bridge sync received');
  await expect(page.locator('#teambot-current-session')).toContainText('Bridge runtime synced');
  await expect(page.locator('#teambot-current-session')).toContainText('kairos on');

  await page.locator('#teambot-current-session button').filter({ hasText: 'Pet' }).click();
  await expect.poll(() => calls.buddyActions.length).toBe(1);
  await expect(page.locator('#teambot-current-session')).toContainText('Purring after a bridge sync');

  expect(pageErrors).toEqual([]);
});

test('studio teambot runtime sidebar shows runtime state and resolves approvals', async ({ page }) => {
  const calls = {
    importOpenClaw: 0,
    exportOpenClaw: 0,
    tinyfishRun: 0,
    lastExportPayload: null,
    approvalActions: [],
  };
  const pageErrors = [];

  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('dialog', async (dialog) => {
    pageErrors.push(`unexpected dialog: ${dialog.message()}`);
    await dialog.dismiss();
  });

  await stubStudioNetwork(page, calls);
  await page.addInitScript(() => {
    window.alert = () => {};
    window.confirm = () => true;
    localStorage.removeItem('teamclawSessionRuntimePanelHeightV1');
  });

  await page.goto('/studio');
  await page.locator('.hamburger-btn').click();
  await page.locator('#hamburger-panel button[onclick*="toggleSessionSidebar(); closeHamburgerMenu();"]').click();

  await expect(page.locator('#session-sidebar')).toBeVisible();
  const runtimePanel = page.locator('#teambot-subagent-panel');
  const divider = page.locator('#session-panel-divider');
  const runtimeHeightBefore = await runtimePanel.evaluate((el) => Math.round(el.getBoundingClientRect().height));
  const dividerBox = await divider.boundingBox();
  await page.mouse.move(dividerBox.x + dividerBox.width / 2, dividerBox.y + dividerBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(dividerBox.x + dividerBox.width / 2, dividerBox.y + dividerBox.height / 2 + 48, { steps: 8 });
  await page.mouse.up();
  const runtimeHeightAfter = await runtimePanel.evaluate((el) => Math.round(el.getBoundingClientRect().height));
  expect(runtimeHeightAfter).toBeLessThan(runtimeHeightBefore);
  await expect.poll(() => page.evaluate(() => localStorage.getItem('teamclawSessionRuntimePanelHeightV1'))).not.toBeNull();

  await expect(page.locator('#teambot-subagent-list')).toContainText('Curie');
  await expect(page.locator('#teambot-subagent-detail')).toContainText('Claude-style runtime audit');
  await expect(page.locator('#teambot-subagent-detail')).toContainText('/tmp/teamclaw/worktree/curie');
  await expect(page.locator('#teambot-subagent-detail')).toContainText('Flask proxy chain');

  await page
    .locator('#teambot-subagent-detail button')
    .filter({ hasText: /批准并记住|Approve \+ remember/ })
    .click();

  await expect.poll(() => calls.approvalActions.length).toBe(1);
  expect(calls.approvalActions[0]).toMatchObject({
    approval_id: 'approval-1',
    action: 'approve',
    remember: true,
    session_id: 'subagent__coder__curie',
  });

  await expect(page.locator('#teambot-policy-status')).toContainText(/Approval 已处理|Approval resolved/);
  await expect(page.locator('#teambot-subagent-detail')).toContainText(/approved|APPROVED/);

  expect(pageErrors).toEqual([]);
});

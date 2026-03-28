// ── Page Loading Overlay (smooth delayed show/hide) ──
// Only shows the loading overlay if the operation takes > 300ms,
// so fast operations feel instant without any flicker.
const _pageLoading = {
    timer: null,
    visible: false,
    startTime: 0,
    DELAY: 300,        // ms before showing overlay
    MIN_VISIBLE: 400,  // ms minimum visible time to avoid flash
};

function showPageLoading(text) {
    _pageLoading.startTime = Date.now();
    // Clear any pending hide
    if (_pageLoading.timer) { clearTimeout(_pageLoading.timer); _pageLoading.timer = null; }
    // Delay showing: only show if still loading after DELAY ms
    _pageLoading.timer = setTimeout(() => {
        const el = document.getElementById('page-loading-overlay');
        if (!el) return;
        if (text) {
            const txt = el.querySelector('.page-loading-text');
            if (txt) txt.textContent = text;
        }
        el.classList.add('loading-visible');
        _pageLoading.visible = true;
        _pageLoading.timer = null;
    }, _pageLoading.DELAY);
}

function hidePageLoading() {
    const elapsed = Date.now() - _pageLoading.startTime;
    // If overlay was never shown (fast operation), just cancel the timer
    if (_pageLoading.timer) {
        clearTimeout(_pageLoading.timer);
        _pageLoading.timer = null;
    }
    if (!_pageLoading.visible) return; // never became visible → nothing to hide
    // If it just became visible, keep it for MIN_VISIBLE to avoid flash
    const visibleSince = elapsed - _pageLoading.DELAY;
    const remaining = Math.max(0, _pageLoading.MIN_VISIBLE - visibleSince);
    setTimeout(() => {
        const el = document.getElementById('page-loading-overlay');
        if (el) el.classList.remove('loading-visible');
        _pageLoading.visible = false;
    }, remaining);
}

const i18n = {
    'zh-CN': {
        // 通用
        loading: '加载中...',
        error: '错误',
        success: '成功',
        cancel: '取消',
        confirm: '确认',
        close: '关闭',

        // 登录页
        login_title: 'Teamclaw',
        login_subtitle: '请登录以开始对话',
        username: '用户名',
        password: '密码',
        login_btn: '登录',
        local_login_btn: '本机免密登录',
        login_verifying: '验证中...',
        login_error_invalid: '用户名只能包含字母、数字、下划线、短横线或中文',
        login_error_failed: '登录失败',
        login_error_network: '网络错误',
        login_footer: '身份验证后方可使用，对话和文件按用户隔离',

        // 头部
        encrypted: '● 已加密',
        history: '🤖Agents',
        new_chat: '+新',
        new_chat_mobile: '+',
        logout: '退出',
        current_session: '当前对话号',
        more_actions: '更多操作',

        // 移动端菜单
        menu_history: '🤖 Agents',
        menu_new: '➕ 新对话',
        menu_oasis: '🏛️ TeamsWork',
        menu_openclaw_cfg: '🦞 OpenClaw 配置',
        menu_logout: '🚪 退出',
        // 汉堡菜单 (no emoji, icon is separate)
        hmenu_agents: 'Agents',
        hmenu_settings: '设置',
        hmenu_openclaw: 'OpenClaw 配置',
        hmenu_new: '新对话',
        hmenu_oasis: 'TeamsWork',
        hmenu_logout: '退出',
        hmenu_lang: '语言',
        hmenu_public: '公开',
        public_starting: '启动中...',
        public_stopping: '停止中...',

        // 聊天区域
        welcome_message: '你好！我是 TeamBot 智能助手。我已经准备好为你服务，请输入你的指令。',
        new_session_message: '🆕 已开启新对话。我是 TeamBot 智能助手，请输入你的指令。',
        input_placeholder: '输入指令...（可粘贴图片/上传文件/录音）',
        send_btn: '发送',
        cancel_btn: '终止',
        busy_btn: '系统占用中',
        new_system_msg: '有新的系统消息',
        click_refresh: '点击刷新',
        no_response: '（无响应）',
        thinking_stopped: '⚠️ 已终止思考',
        login_expired: '⚠️ 登录已过期，请重新登录',
        agent_error: '❌ 错误',

        // 工具面板
        available_tools: '🧰 可用工具',
        tool_calling: '（调用工具中...）',
        tool_return: '🔧 工具返回',

        // 文件上传
        max_images: '最多上传5张图片',
        max_files: '最多上传3个文件',
        max_audios: '最多上传2个音频',
        audio_too_large: '音频过大，上限 25MB',
        video_too_large: '视频过大，上限 50MB',
        pdf_too_large: 'PDF过大，上限 10MB',
        file_too_large: '文件过大，上限 512KB',
        unsupported_type: '不支持的文件类型',
        supported_types: '支持: txt, md, csv, json, py, js, pdf, mp3, wav, avi, mp4 等',

        // 录音
        recording_title: '录音',
        recording_stop: '点击停止录音',
        mic_permission_denied: '无法访问麦克风，请检查浏览器权限设置。',
        recording_too_long: '录音过长，上限 25MB',

        // 历史会话
        history_title: '🤖 Agents',
        history_loading: '加载中...',
        history_empty: '暂无历史对话',
        history_error: '加载失败',
        history_loading_msg: '加载历史消息...',
        history_no_msg: '（此对话暂无消息记录）',
        new_session_confirm: '开启新对话？当前对话的历史记录将保留，可通过切回对话号恢复。',
        messages_count: '条消息',
        session_id: '对话号',
        delete_session: '删除',
        delete_session_confirm: '确定删除此对话？删除后不可恢复。',
        delete_all_confirm: '确定删除所有对话记录？此操作不可恢复！',
        delete_success: '删除成功',
        delete_fail: '删除失败',
        delete_all: '🗑️ 清空全部',

        // TTS
        tts_read: '朗读',
        tts_stop: '停止',
        tts_loading: '加载中...',
        tts_request_failed: 'TTS 请求失败',
        code_omitted: '（代码省略）',
        image_placeholder: '(图片)',
        audio_placeholder: '(语音)',
        file_placeholder: '(文件)',

        // OASIS
        oasis_title: 'TeamsWork 讨论论坛',
        oasis_subtitle: '多专家并行讨论系统',
        oasis_topics: '📋 讨论话题',
        oasis_topics_count: '个话题',
        oasis_no_topics: '暂无讨论话题',
        oasis_start_hint: '在聊天中让 Agent 发起 TeamsWork 讨论',
        oasis_back: '← 返回',
        oasis_conclusion: '讨论结论',
        oasis_waiting: '等待专家发言...',
        oasis_status_pending: '等待中',
        oasis_status_discussing: '讨论中',
        oasis_status_concluded: '已完成',
        oasis_status_error: '出错',
        oasis_status_cancelled: '已终止',
        oasis_round: '轮',
        oasis_posts: '帖',
        oasis_expert_creative: '创意专家',
        oasis_expert_critical: 'PUA专家',
        oasis_expert_data: '数据分析师',
        oasis_expert_synthesis: '综合顾问',
        oasis_cancel: '终止讨论',
        oasis_cancel_confirm: '确定要强制终止此讨论？',
        oasis_cancel_success: '讨论已终止',
        oasis_delete: '删除记录',
        oasis_delete_confirm: '确定要永久删除此讨论记录？删除后不可恢复。',
        oasis_delete_success: '记录已删除',
        oasis_action_fail: '操作失败',

        // 页面切换
        tab_chat: '💬 对话',
        tab_group: '👥 团队',
        tab_orchestrate: '🤝 工作流',
        tab_groupchat: '📨 消息中心',
        tip_open_msgcenter: '打开消息中心',

        // 群聊
        group_title: '👥 团队列表',
        group_new: '+ 新建',
        group_no_groups: '暂无团队',
        group_select_hint: '选择一个团队进行管理',
        group_create_hint: '创建或导入一个团队进行管理',
        group_members_btn: '👤 成员',
        group_mute: '🔇 急停',
        group_unmute: '🔊 恢复',
        group_members: '成员管理',
        group_current_members: '当前成员',
        group_add_agents: '添加 Agent Session',
        group_input_placeholder: '发送消息...',
        group_create_title: '新建团队',
        group_name_placeholder: '团队名称',
        group_no_sessions: '没有可用的 Agent Session',
        group_create_btn: '创建',
        group_delete_confirm: '确定删除此团队？',
        group_owner: '群主',
        group_agent: 'Agent',
        group_msg_count: '条消息',
        group_member_count: '人',

        // 离线提示
        offline_banner: '⚠️ 网络已断开，请检查连接',

        // 编排面板
        orch_expert_pool: '🧑‍💼 人设池',
        orch_expert_pool_text: '人设池',
        orch_preset_experts: '📚 预设人设',
        orch_custom_experts: '🛠️ 自定义人设',
        orch_internal_agents: '🤖 Internal Agent',
        orch_add_internal_agent_title: '新建 Internal Agent',
        orch_ia_name: 'Agent 名称',
        orch_ia_tag: '标签 (Tag)',
        orch_ia_tag_placeholder: '可拖入专家设置，或手动输入',
        orch_ia_created: 'Internal Agent 已创建',
        orch_ia_tag_set: 'Tag 已设置为',
orch_openclaw_sessions: '🦞 OpenClaw',
        orch_add_openclaw_title: '新建 OpenClaw Agent',
        orch_openclaw_agent_name: 'Agent 名称',
        orch_openclaw_ws_path: '路径',
        orch_openclaw_ws_loading: '加载默认路径...',
        orch_openclaw_ws_fallback: '输入 workspace 路径',
        orch_openclaw_ws_required: 'Workspace 路径不能为空',
        orch_openclaw_ws_reset: '重置为默认路径',
        orch_openclaw_workspace_hint: '💡 自动从默认 Agent 目录推导；可自定义',
        orch_openclaw_create_btn: '创建 Agent',
        orch_openclaw_creating: '创建中...',
        orch_openclaw_created: 'Agent "{name}" 创建成功！',
        orch_openclaw_exists: 'Agent "{name}" 已存在，请换一个名称',
        orch_openclaw_name_required: '请输入 Agent 名称',
        orch_openclaw_name_invalid: '名称只允许字母、数字、下划线、连字符',
        orch_oc_delete: '删除 Agent',
        orch_oc_delete_confirm: '确定删除 OpenClaw Agent "{name}"？此操作会删除真实 Agent。',
        orch_oc_delete_success: '已删除 OpenClaw Agent "{name}"',
        orch_oc_delete_failed: '删除 OpenClaw Agent "{name}" 失败',
        orch_oc_delete_main_blocked: 'main Agent 不能被删除',
        orch_oc_edit_files: '编辑核心文件',
        orch_oc_config: '配置',
        orch_oc_select_file: '← 点击文件查看/编辑',
        orch_oc_import_expert: '导入专家人设',
        orch_oc_import_expert_to_identity: '导入专家人设到 IDENTITY.md',
        orch_oc_create_import_expert: '可选：导入专家人设作为 Agent 身份',
        orch_oc_create_pick_expert: '选择专家',
        orch_oc_import_expert_tip: '从预设/自定义人设导入人设到此文件',
        orch_oc_import_expert_title: '导入专家人设',
        orch_oc_import_expert_desc: '选择一个专家，将其人设（persona）导入到当前文件中。',
        orch_oc_import_replace: '替换内容',
        orch_oc_import_append: '追加到末尾',
        orch_oc_import_search_ph: '搜索专家名称/标签...',
        orch_oc_import_no_result: '没有匹配的专家',
        orch_oc_import_public: '公共专家',
        orch_oc_import_agency: 'Agency 专家',
        orch_oc_import_custom: '自定义人设',
        orch_oc_import_done: '已导入 {name} 的人设',
        orch_oc_file_missing: '缺失',
        orch_oc_new_file: '新文件',
        orch_oc_save: '保存',
        orch_oc_saved: '已保存',
        orch_oc_unsaved: '未保存',
        orch_oc_cfg_loaded: '配置已加载',
        orch_oc_cfg_tools: 'Tools 权限',
        orch_oc_cfg_profile: '权限模式',
        orch_oc_cfg_no_profile: '（未设置）',
        orch_oc_cfg_tool_toggles: '单独工具开关（⚪默认 ✅允许 🚫禁止，点击切换）',
        orch_oc_cfg_skills: 'Skills 技能',
        orch_oc_cfg_skills_all: '全部可用（不限制）',
        orch_oc_cfg_saved: '"{name}" 配置已保存',
        orch_oc_quick_btn: '🦞 Setting OpenClaw Agent',
        orch_oc_quick_title: 'Setting OpenClaw Agent',
        orch_oc_quick_no_agents: 'OpenClaw 不可用',
        orch_oc_quick_empty: '暂无 Agent，点击下方按钮新建',
        orch_oc_quick_select: '选择要配置的 Agent：',
        orch_oc_quick_add: '新建 OpenClaw Agent',
        orch_oc_tab_files: '核心文件',
        orch_oc_tab_config: 'Skills & Tools',
        orch_oc_tab_channels: 'Channels 绑定',
        orch_oc_ch_empty: '暂无可用 Channel',
        orch_oc_ch_guide_title: '如何添加 Channel：',
        orch_oc_ch_guide_docs: '完整文档：',
        orch_oc_ch_desc: '点击 Channel 账号切换绑定状态（🔗已绑定 ⚪未绑定）',
        orch_manual_inject: '手动注入',
        orch_start_node: '开始节点',
        orch_end_node: '结束节点',
        orch_script_node: '脚本节点',
        orch_human_node: '人类节点',
        orch_cond_node: '选择器',
        orch_control_nodes: '控制节点',
        orch_start_author: 'begin',
        orch_end_author: 'bend',
        orch_start_default_content: '讨论开始',
        orch_end_default_content: '讨论结束',
        orch_cond_already_selector: '已经是选择器节点',
        orch_shortcuts_title: '快捷操作：',
        orch_shortcuts_body: '拖入专家到画布 · 连接端口=工作流 · Ctrl+G=分组 · 双击快速添加',
        // Orchestration toolbar buttons
        orch_btn_arrange: '🔄 排列',
        orch_btn_save: '💾 保存工作流',
        orch_btn_load: '📂 加载工作流',
        orch_btn_ai: '🤖 AI优化工作流',
        orch_btn_export: '📋 复制工作流到粘贴板',
        orch_btn_download: '⬇️ 导出工作流',
        orch_btn_upload: '⬆️ 导入工作流',
        orch_btn_focus: '🎯 专注',
        orch_btn_status: '🔄 状态',
        orch_btn_clear: '🗑️ 清空工作流',
        orch_tip_arrange: '自动排列',
        orch_tip_save: '保存工作流',
        orch_tip_load: '加载工作流',
        orch_tip_ai: 'AI优化工作流',
        orch_tip_export: '复制工作流到粘贴板',
        orch_tip_download: '导出工作流',
        orch_tip_upload: '导入工作流',
        orch_tip_status: '刷新 session 状态',
        orch_tip_clear: '清空工作流',
        // Canvas hints
        orch_hint_drag: '拖入专家开始编排',
        // Nav controls
        orch_tip_up: '上移',
        orch_tip_down: '下移',
        orch_tip_left: '左移',
        orch_tip_right: '右移',
        orch_tip_reset: '重置视图',
        orch_tip_zoomout: '缩小',
        orch_tip_zoomin: '放大',
        // Right panel
        orch_settings: '⚙️ 设置',
        orch_repeat: '每轮重复计划',
        orch_rounds: '轮次:',
        orch_stateful: '有状态模式',
        orch_node_stateful: '⚡ 有状态模式',
        orch_node_stateful_hint: '开启后该专家拥有记忆和工具能力（适合复杂任务）',
        orch_threshold: '聚类阈值:',
        orch_ai_gen: '🤖 AI 生成',
        orch_ai_hint: '点击「🤖 AI编排」自动生成 YAML',
        orch_prompt_label: '📨 发送的 Prompt',
        orch_prompt_copy: '复制',
        orch_prompt_hint: '点击 AI编排 后显示',
        orch_agent_yaml_label: '🤖 Agent YAML',
        orch_agent_yaml_copy: '复制',
        orch_agent_yaml_hint: '等待 Agent 生成',
        orch_rule_yaml: '📄 规则 YAML',
        orch_rule_yaml_hint: '拖入专家后自动生成...',
        orch_status_bar: '节点: {nodes} | 连线: {edges} | 分组: {groups}',
        orch_status_bar_init: '节点: 0 | 连线: 0 | 分组: 0',
        orch_manual_inject: '手动注入',
        orch_start_node: '开始节点',
        orch_end_node: '结束节点',
        orch_script_node: '脚本节点',
        orch_human_node: '人类节点',
        orch_cond_node: '选择器',
        orch_control_nodes: '控制节点',
        orch_start_author: 'begin',
        orch_end_author: 'bend',
        orch_start_default_content: '讨论开始',
        orch_end_default_content: '讨论结束',
        orch_cond_already_selector: '已经是选择器节点',
        orch_node_remove: '移除',
        orch_default_author: '主持人',
        orch_yaml_valid: '✅ 有效 YAML — {steps} 步骤 [{types}]',
        orch_yaml_saved_suffix: ' | 💾 已保存: {file}',
        orch_yaml_warn: '⚠️ YAML 校验问题: {error}',
        orch_comm_fail: '# 通信失败: {msg}',
        // Context menu
        orch_ctx_duplicate: '📋 复用此专家 (同序号)',
        orch_ctx_new_instance: '➕ 新建实例 (新序号)',
        orch_ctx_group_parallel: '🔀 创建并行分组',
        orch_ctx_group_all: '👥 创建全员分组',
        orch_ctx_delete: '🗑️ 删除选中',
        orch_ctx_refresh_yaml: '🔄 刷新 YAML',
        orch_ctx_clear: '🗑️ 清空画布',
        // Conditional edge
        orch_ctx_set_cond: '⚡ 设为条件边',
        orch_ctx_edit_cond: '✏️ 编辑条件边',
        orch_ctx_remove_cond: '🔗 恢复为普通边',
        orch_ctx_set_selector: '🎯 设为选择节点 (LLM路由)',
        orch_ctx_unset_selector: '🔗 取消选择节点',
        orch_modal_cond_edge: '⚡ 编辑条件边',
        orch_cond_label_type: '条件类型',
        orch_cond_label_keyword: '关键词',
        orch_cond_label_number: '数值',
        orch_cond_label_negate: '取反（NOT）',
        orch_cond_opt_contains: '最后发言 包含关键词',
        orch_cond_opt_not_contains: '最后发言 不包含关键词',
        orch_cond_opt_count_gte: '发言总数 ≥ N',
        orch_cond_opt_count_lt: '发言总数 < N',
        orch_cond_opt_always: '始终为真（无条件）',
        orch_cond_label_then: 'Then 目标（条件为真）',
        orch_cond_label_else: 'Else 目标（条件为假/循环回边）',
        orch_cond_none: '（无）',
        orch_cond_val_required: '请填写关键词或数值',
        // Group labels
        orch_group_parallel: '🔀 并行',
        orch_group_all: '👥 全员',
        orch_group_dissolve: '解散',
        // Modals
        orch_modal_edit_manual: '📝 编辑手动注入内容',
        orch_modal_author_ph: '作者',
        orch_modal_content_ph: '注入内容...',
        orch_modal_cancel: '取消',
        orch_modal_save: '保存',
        orch_modal_select_session: '🎯 选择目标 Agent Session',
        orch_modal_select_desc: '选择一个已有的对话 Session，或新建一个，生成完成后可跳转继续对话。',
        orch_modal_loading: '⏳ 加载中...',
        orch_modal_new_session: '新建对话',
        orch_modal_confirm_gen: '确认并生成',
        orch_modal_select_layout: '📂 选择布局',
        orch_modal_delete: '🗑️ 删除',
        orch_modal_load: '加载',
        // Toast messages
        orch_toast_arranged: '已自动排列',
        orch_toast_saved: '已保存: {name}',
        orch_toast_save_fail: '保存失败',
        orch_toast_no_layouts: '没有已保存的布局',
        orch_toast_deleted: '已删除: {name}',
        orch_toast_del_fail: '删除失败',
        orch_toast_loaded: '已加载: {name}',
        orch_toast_load_fail: '加载失败',
        orch_toast_yaml_copied: 'YAML 已复制!',
        orch_toast_gen_yaml: '请先生成 YAML',
        orch_toast_prompt_copied: 'Prompt 已复制',
        orch_toast_agent_yaml_copied: 'Agent YAML 已复制',
        orch_toast_select_2: '请先选中至少2个节点',
        orch_toast_add_first: '请先添加专家节点',
        orch_toast_agent_unavail: 'Agent 不可用',
        orch_toast_yaml_generated: 'YAML 已生成并保存! ✅',
        orch_toast_agent_valid: 'Agent 生成了有效的 YAML! ✅',
        orch_toast_session_updated: 'Session 状态已更新',
        orch_toast_session_fail: '获取状态失败',
        orch_toast_no_session: '没有选中的 Session',
        orch_toast_jumped: '已跳转到对话 #{id}',
        orch_toast_custom_added: '自定义人设已添加: {name}',
        orch_toast_fill_info: '请填写完整信息',
        orch_toast_net_error: '网络错误',
        orch_toast_expert_deleted: '已删除: {name}',
        orch_toast_expert_del_fail: '删除失败',
        orch_toast_added_mobile: '已添加到画布',
        // Team management
        orch_btn_create_team: '➕ 创建',
        orch_btn_delete_team: '🗑️ 删除',
        orch_btn_download_snapshot: '⬇️ 快照',
        orch_btn_upload_snapshot: '⬆️ 上传',
        orch_tip_create_team: '创建新team',
        orch_tip_delete_team: '删除当前team',
        orch_tip_download_snapshot: '下载team快照',
        orch_tip_upload_snapshot: '上传team快照',
        orch_toast_team_name_required: '请输入team名称',
        orch_toast_team_created: 'Team已创建',
        orch_toast_team_create_failed: '创建team失败',
        orch_toast_team_deleted: 'Team已删除 ({count}个agent已移除)',
        orch_toast_team_delete_failed: '删除team失败',
        orch_toast_snapshot_downloaded: '快照已下载',
        orch_toast_snapshot_download_failed: '下载快照失败',
        orch_toast_snapshot_uploaded: '快照已上传，agent已恢复',
        orch_toast_snapshot_upload_failed: '上传快照失败',
        orch_toast_invalid_zip: '请选择.zip文件',
        orch_toast_network_error: '网络错误',
        orch_confirm_delete_team: '删除team "{name}"及其所有agent？',
        // Export preview modal
        export_preview_title: '📦 导出团队快照',
        export_preview_loading: '正在加载预览...',
        export_preview_desc: '请选择要导出的内容：',
        export_preview_tip: '💡 提示：取消勾选某分类后，该分类下的内容将不会被导出',
        export_agents: '内部 Agents',
        export_personas: '自定义人设',
        export_skills: 'Skills',
        export_managed_skills: '托管 Skills',
        export_cron: '定时任务',
        export_workflows: 'Workflows',
        export_download: '📥 导出',
        export_downloading: '导出中...',
        export_none_selected: '请至少选择一项内容导出',
        export_preview_empty: '暂无可导出的内容',
        // Confirm dialogs
        orch_confirm_del_expert: '删除自定义人设 "{name}"？',
        orch_confirm_del_layout: '确定删除布局 "{name}"？',
        orch_prompt_layout_name: '布局名称:',
        // Agent status
        orch_status_communicating: '🔄 正在与 Agent 通信 (Session: #{id})...',
        orch_status_generating: '⏳ 生成中...',
        orch_status_waiting: '⏳ 等待 Agent 返回...',
        orch_status_auth_fail: '认证失败',
        orch_status_agent_unavail: 'Agent 不可用',
        orch_status_conn_error: '❌ 连接错误',
        orch_goto_chat: '💬 跳转到对话 {session} 继续聊天',
        orch_no_custom: '暂无自定义人设',
        orch_no_session: '暂无 Session',
        orch_load_fail: '❌ 加载失败',
        orch_load_session_fail: '❌ 加载 Session 列表失败',
        orch_msg_count: '{count}条消息',
        orch_add_expert_title: '🛠️ 添加自定义人设',
        orch_add_expert_btn: '添加自定义人设',
        orch_label_name: '名称',
        orch_label_tag: 'Tag (英文)',
        orch_label_temp: 'Temperature',
        orch_label_persona: 'Persona (角色描述)',
        orch_ph_name: '如：金融分析师',
        orch_ph_tag: '如：finance',
        orch_ph_persona: '描述这位专家的角色、专长和行为风格...',

        // Add Workflow
        wf_btn_title: '添加工作流',
        wf_btn_label: '+ 工作流',
        wf_popup_title: '📋 选择工作流',
        wf_no_workflows: '暂无已保存的工作流',
        wf_team_no_layouts: '该团队暂无已保存工作流',
        wf_cancel: '取消',
        wf_confirm: '添加',
        wf_context_prefix: '[工作流: {name}] ',

        // Persona
        persona_btn_title: '引入专家人设',
        persona_btn_label: '+ 人设',
        persona_popup_title: '🎭 选择专家人设',
        persona_no_experts: '暂无可用专家',
        persona_cancel: '取消',
        persona_confirm: '使用',
        persona_active: '当前人设',
        persona_public: '📋 公共专家',
        persona_agency: '🌐 Agency 专家',
        persona_custom: '🔧 自定义人设',

        // 其他
        persona_search_placeholder: '🔍 搜索专家名称 / 标签...',
        persona_no_match: '没有匹配的专家',
        splash_subtitle: 'TeamBot AI Agent',
        secure_footer: 'Secured by Nginx Reverse Proxy & SSH Tunnel',
        refresh: '刷新',
        collapse: '收起',

        // 设置
        settings: '⚙️',
        settings_title: '⚙️ 系统设置',
        settings_save: '保存',
        settings_saved: '✅ 设置已保存',
        settings_save_fail: '❌ 保存失败',
        settings_load_fail: '❌ 加载设置失败',
        settings_restart_hint: '修改配置后请先「保存」，再点击「重启服务」使配置生效',
        settings_restart_btn: '🔄 重启服务',
        settings_restarting: '⏳ 正在重启...',
        settings_restart_ok: '✅ 重启信号已发送，页面将在 15 秒后自动刷新',
        settings_restart_fail: '❌ 重启失败',
        settings_restart_confirm: '确定要重启所有服务吗？未保存的配置修改将丢失。',
        menu_settings: '⚙️ 设置',
        settings_group_llm: 'LLM 模型配置',
        settings_group_tts: '音频配置',
        settings_group_openclaw: 'OpenClaw 集成',
        settings_group_oasis: 'OASIS 论坛',
        settings_group_ports: '端口配置',
        settings_group_network: '公网地址',
        settings_group_bots: '机器人集成',
        settings_group_comm: '通信模式',
        settings_group_exec: '命令执行',
        settings_group_security: '安全密钥',
        settings_group_other: '其他',
        settings_help_audio_group: '留空时会自动跟随当前 LLM provider。检测到 OpenAI 时默认使用 gpt-4o-mini-tts / alloy / whisper-1；检测到 Gemini 时默认使用 gemini-2.5-flash-preview-tts / charon。',
        settings_help_tts_model: '留空时自动跟随当前 LLM provider。OpenAI 默认是 gpt-4o-mini-tts，Gemini 默认是 gemini-2.5-flash-preview-tts。',
        settings_help_tts_voice: '留空时自动跟随当前 LLM provider。OpenAI 默认声音是 alloy，Gemini 默认声音是 charon。',
        settings_help_stt_model: '留空时自动跟随当前 LLM provider。OpenAI 默认是 whisper-1；Gemini 目前没有内置 STT 默认值，可按需手动填写。',
        settings_antigravity_preset: '🚀 Antigravity 免费模型预设',
        settings_antigravity_hint: '一键填入 Antigravity-Manager 反代配置，通过 Google One Pro 会员免费使用模型。确保 Antigravity-Manager 已在本机运行。',
        settings_antigravity_apply: '应用 Antigravity 预设',
        settings_antigravity_applied: '✅ 已应用 Antigravity 预设，请选择模型后保存',
        settings_group_tunnel: '🌐 公网隧道',
        tunnel_start: '启动隧道',
        tunnel_stop: '停止隧道',
        tunnel_starting: '启动中...',
        tunnel_stopping: '停止中...',
        tunnel_running: '✅ 隧道运行中',
        tunnel_stopped: '❌ 隧道未运行',
        tunnel_url_hint: '点击复制公网地址',

        // OpenClaw 对话切换
        oc_tab_internal: '🤖 TeamBot',
        oc_tab_openclaw: '🦞 OpenClaw',
        oc_select_agent: '-- 选择 Agent --',
        oc_no_agents: '没有可用的 OpenClaw Agent',
        oc_chatting_with: '正在与 {name} 对话',
        oc_load_failed: '加载 OpenClaw Agent 失败',
        oc_not_configured: 'OpenClaw 未配置',
        oc_select_agent_hint: '请先选择一个 OpenClaw Agent',
    },
    'en': {
        // General
        loading: 'Loading...',
        error: 'Error',
        success: 'Success',
        cancel: 'Cancel',
        confirm: 'Confirm',
        close: 'Close',

        // Login
        login_title: 'Teamclaw',
        login_subtitle: 'Please login to start',
        username: 'Username',
        password: 'Password',
        login_btn: 'Login',
        local_login_btn: 'Local No-Password Login',
        login_verifying: 'Verifying...',
        login_error_invalid: 'Username can only contain letters, numbers, underscore, hyphen or Chinese',
        login_error_failed: 'Login failed',
        login_error_network: 'Network error',
        login_footer: 'Authentication required. Conversations and files are isolated by user',

        // Header
        encrypted: '● Encrypted',
        history: '🤖 Agents',
        new_chat: '+New',
        new_chat_mobile: '+',
        logout: 'Logout',
        current_session: 'Current session',
        more_actions: 'More actions',

        // Mobile menu
        menu_history: '🤖 Agents',
        menu_new: '➕ New Chat',
        menu_oasis: '🏛️ TeamsWork',
        menu_openclaw_cfg: '🦞 OpenClaw Config',
        menu_logout: '🚪 Logout',
        // Hamburger menu (no emoji, icon is separate)
        hmenu_agents: 'Agents',
        hmenu_settings: 'Settings',
        hmenu_openclaw: 'OpenClaw Config',
        hmenu_new: 'New Chat',
        hmenu_oasis: 'TeamsWork',
        hmenu_logout: 'Logout',
        hmenu_lang: 'Language',
        hmenu_public: 'Public',
        public_starting: 'Starting...',
        public_stopping: 'Stopping...',

        // Chat area
        welcome_message: 'Hello! I am TeamBot AI Assistant. Ready to serve you. Please enter your instructions.',
        new_session_message: '🆕 New conversation started. I am TeamBot AI Assistant. Please enter your instructions.',
        input_placeholder: 'Enter command... (paste images/upload files/record audio)',
        send_btn: 'Send',
        cancel_btn: 'Stop',
        busy_btn: 'System Busy',
        new_system_msg: 'New system message',
        click_refresh: 'Click to refresh',
        no_response: '(No response)',
        thinking_stopped: '⚠️ Thinking stopped',
        login_expired: '⚠️ Session expired, please login again',
        agent_error: '❌ Error',

        // Tool panel
        available_tools: '🧰 Available Tools',
        tool_calling: '(Calling tool...)',
        tool_return: '🔧 Tool Return',

        // File upload
        max_images: 'Maximum 5 images',
        max_files: 'Maximum 3 files',
        max_audios: 'Maximum 2 audio files',
        audio_too_large: 'Audio too large, limit 25MB',
        video_too_large: 'Video too large, limit 50MB',
        pdf_too_large: 'PDF too large, limit 10MB',
        file_too_large: 'File too large, limit 512KB',
        unsupported_type: 'Unsupported file type',
        supported_types: 'Supported: txt, md, csv, json, py, js, pdf, mp3, wav, avi, mp4, etc.',

        // Recording
        recording_title: 'Record',
        recording_stop: 'Click to stop recording',
        mic_permission_denied: 'Cannot access microphone. Please check browser permissions.',
        recording_too_long: 'Recording too long, limit 25MB',

        // History sessions
        history_title: '🤖 Agents',
        history_loading: 'Loading...',
        history_empty: 'No history',
        history_error: 'Failed to load',
        history_loading_msg: 'Loading messages...',
        history_no_msg: '(No messages in this conversation)',
        new_session_confirm: 'Start new conversation? Current history will be preserved.',
        messages_count: 'messages',
        session_id: 'Session',
        delete_session: 'Delete',
        delete_session_confirm: 'Delete this conversation? This cannot be undone.',
        delete_all_confirm: 'Delete ALL conversations? This cannot be undone!',
        delete_success: 'Deleted',
        delete_fail: 'Delete failed',
        delete_all: '🗑️ Clear All',

        // TTS
        tts_read: 'Read',
        tts_stop: 'Stop',
        tts_loading: 'Loading...',
        tts_request_failed: 'TTS request failed',
        code_omitted: '(code omitted)',
        image_placeholder: '(image)',
        audio_placeholder: '(audio)',
        file_placeholder: '(file)',

        // OASIS
        oasis_title: 'TeamsWork Discussion Forum',
        oasis_subtitle: 'Multi-Expert Parallel Discussion System',
        oasis_topics: '📋 Discussion Topics',
        oasis_topics_count: 'topics',
        oasis_no_topics: 'No discussion topics',
        oasis_start_hint: 'Ask Agent to start a TeamsWork discussion in chat',
        oasis_back: '← Back',
        oasis_conclusion: 'Conclusion',
        oasis_waiting: 'Waiting for experts...',
        oasis_status_pending: 'Pending',
        oasis_status_discussing: 'Discussing',
        oasis_status_concluded: 'Completed',
        oasis_status_error: 'Error',
        oasis_status_cancelled: 'Cancelled',
        oasis_round: 'rounds',
        oasis_posts: 'posts',
        oasis_expert_creative: 'Creative Expert',
        oasis_expert_critical: 'PUA Expert',
        oasis_expert_data: 'Data Analyst',
        oasis_expert_synthesis: 'Synthesis Advisor',
        oasis_cancel: 'Stop Discussion',
        oasis_cancel_confirm: 'Force stop this discussion?',
        oasis_cancel_success: 'Discussion stopped',
        oasis_delete: 'Delete',
        oasis_delete_confirm: 'Permanently delete this discussion? This cannot be undone.',
        oasis_delete_success: 'Record deleted',
        oasis_action_fail: 'Action failed',

        // Page switch
        tab_chat: '💬 Chat',
        tab_group: '👥 Team',
        tab_orchestrate: '🤝 Workflow',
        tab_groupchat: '📨 Messages',
        tip_open_msgcenter: 'Open Message Center',

        // Group chat
        group_title: '👥 Team List',
        group_new: '+ New',
        group_no_groups: 'No teams',
        group_select_hint: 'Select a team to manage',
        group_create_hint: 'Create or import a team to manage',
        group_members_btn: '👤 Members',
        group_mute: '🔇 Stop',
        group_unmute: '🔊 Resume',
        group_members: 'Member Management',
        group_current_members: 'Current Members',
        group_add_agents: 'Add Agent Session',
        group_input_placeholder: 'Send a message...',
        group_create_title: 'Create Team',
        group_name_placeholder: 'Team name',
        group_no_sessions: 'No available Agent Sessions',
        group_create_btn: 'Create',
        group_delete_confirm: 'Delete this team?',
        group_owner: 'Owner',
        group_agent: 'Agent',
        group_msg_count: 'messages',
        group_member_count: 'members',

        // Offline
        offline_banner: '⚠️ Network disconnected, please check connection',

        // Orchestration panel
        orch_expert_pool: '🧑‍💼 Expert Pool',
        orch_expert_pool_text: 'Expert Pool',
        orch_preset_experts: '📚 Preset Experts',
        orch_custom_experts: '🛠️ Custom Experts',
        orch_internal_agents: '🤖 Internal Agents',
        orch_add_internal_agent_title: 'New Internal Agent',
        orch_ia_name: 'Agent Name',
        orch_ia_tag: 'Tag',
        orch_ia_tag_placeholder: 'Drag an expert to set, or type manually',
        orch_ia_created: 'Internal Agent created',
        orch_ia_tag_set: 'Tag set to',
orch_openclaw_sessions: '🦞 OpenClaw',
        orch_add_openclaw_title: 'New OpenClaw Agent',
        orch_openclaw_agent_name: 'Agent Name',
        orch_openclaw_ws_path: 'Path',
        orch_openclaw_ws_loading: 'Loading default path...',
        orch_openclaw_ws_fallback: 'Enter workspace path',
        orch_openclaw_ws_required: 'Workspace path is required',
        orch_openclaw_ws_reset: 'Reset to default path',
        orch_openclaw_workspace_hint: '💡 Auto-derived from default agent directory; you can customize it',
        orch_openclaw_create_btn: 'Create Agent',
        orch_openclaw_creating: 'Creating...',
        orch_openclaw_created: 'Agent "{name}" created!',
        orch_openclaw_exists: 'Agent "{name}" already exists, please choose another name',
        orch_openclaw_name_required: 'Agent name is required',
        orch_openclaw_name_invalid: 'Name must be alphanumeric (a-z, 0-9, -, _)',
        orch_oc_delete: 'Delete Agent',
        orch_oc_delete_confirm: 'Delete OpenClaw agent "{name}"? This removes the real agent.',
        orch_oc_delete_success: 'Deleted OpenClaw agent "{name}"',
        orch_oc_delete_failed: 'Failed to delete OpenClaw agent "{name}"',
        orch_oc_delete_main_blocked: 'The main agent cannot be deleted',
        orch_oc_edit_files: 'Edit Core Files',
        orch_oc_config: 'Config',
        orch_oc_select_file: '← Click a file to view/edit',
        orch_oc_import_expert: 'Import Expert',
        orch_oc_import_expert_to_identity: 'Import Expert to IDENTITY.md',
        orch_oc_create_import_expert: 'Optional: Import expert persona as Agent identity',
        orch_oc_create_pick_expert: 'Pick Expert',
        orch_oc_import_expert_tip: 'Import persona from preset/custom experts into this file',
        orch_oc_import_expert_title: 'Import Expert Persona',
        orch_oc_import_expert_desc: 'Select an expert to import their persona into the current file.',
        orch_oc_import_replace: 'Replace content',
        orch_oc_import_append: 'Append to end',
        orch_oc_import_search_ph: 'Search expert name/tag...',
        orch_oc_import_no_result: 'No matching experts',
        orch_oc_import_public: 'Public Experts',
        orch_oc_import_agency: 'Agency Experts',
        orch_oc_import_custom: 'Custom Experts',
        orch_oc_import_done: 'Imported persona of {name}',
        orch_oc_file_missing: 'Missing',
        orch_oc_new_file: 'New file',
        orch_oc_save: 'Save',
        orch_oc_saved: 'Saved',
        orch_oc_unsaved: 'Unsaved',
        orch_oc_cfg_loaded: 'Config loaded',
        orch_oc_cfg_tools: 'Tool Permissions',
        orch_oc_cfg_profile: 'Permission Profile',
        orch_oc_cfg_no_profile: '(Not set)',
        orch_oc_cfg_tool_toggles: 'Individual tool toggles (⚪default ✅allow 🚫deny, click to cycle)',
        orch_oc_cfg_skills: 'Skills',
        orch_oc_cfg_skills_all: 'All available (unrestricted)',
        orch_oc_cfg_saved: '"{name}" config saved',
        orch_oc_quick_btn: '🦞 Setting OpenClaw Agent',
        orch_oc_quick_title: 'Setting OpenClaw Agent',
        orch_oc_quick_no_agents: 'OpenClaw not available',
        orch_oc_quick_empty: 'No agents yet. Click below to create one',
        orch_oc_quick_select: 'Select an agent to configure:',
        orch_oc_quick_add: 'New OpenClaw Agent',
        orch_oc_tab_files: 'Core Files',
        orch_oc_tab_config: 'Skills & Tools',
        orch_oc_tab_channels: 'Channels',
        orch_oc_ch_empty: 'No channels available',
        orch_oc_ch_guide_title: 'How to add a channel:',
        orch_oc_ch_guide_docs: 'Full docs:',
        orch_oc_ch_desc: 'Click a channel account to toggle binding (🔗bound ⚪unbound)',
        orch_manual_inject: 'Manual Inject',
        orch_start_node: 'Start Node',
        orch_end_node: 'End Node',
        orch_script_node: 'Script Node',
        orch_human_node: 'Human Node',
        orch_cond_node: 'Selector',
        orch_control_nodes: 'Control',
        orch_start_author: 'begin',
        orch_end_author: 'bend',
        orch_start_default_content: 'Discussion started',
        orch_end_default_content: 'Discussion ended',
        orch_cond_already_selector: 'is already a selector',
        orch_shortcuts_title: 'Shortcuts: ',
        orch_shortcuts_body: 'Drag expert to canvas · Connect ports=workflow · Ctrl+G=group · Double-click to add',
        // Orchestration toolbar buttons
        orch_btn_arrange: '🔄 Arrange',
        orch_btn_save: '💾 Save Workflow',
        orch_btn_load: '📂 Load Workflow',
        orch_btn_ai: '🤖 AI Optimize Workflow',
        orch_btn_export: '📋 Copy Workflow to Clipboard',
        orch_btn_focus: '🎯 Focus',
        orch_btn_status: '🔄 Status',
        orch_btn_clear: '🗑️ Clear Workflow',
        orch_tip_arrange: 'Auto arrange',
        orch_tip_save: 'Save workflow',
        orch_tip_load: 'Load workflow',
        orch_tip_ai: 'AI optimize workflow',
        orch_tip_export: 'Copy workflow to clipboard',
        orch_tip_status: 'Refresh session status',
        orch_tip_clear: 'Clear workflow',
        // Canvas hints
        orch_hint_drag: 'Drag experts to start orchestrating',
        // Nav controls
        orch_tip_up: 'Pan up',
        orch_tip_down: 'Pan down',
        orch_tip_left: 'Pan left',
        orch_tip_right: 'Pan right',
        orch_tip_reset: 'Reset view',
        orch_tip_zoomout: 'Zoom out',
        orch_tip_zoomin: 'Zoom in',
        // Right panel
        orch_settings: '⚙️ Settings',
        orch_repeat: 'Repeat plan each round',
        orch_rounds: 'Rounds:',
        orch_stateful: 'Stateful mode',
        orch_node_stateful: '⚡ Stateful mode',
        orch_node_stateful_hint: 'Expert has memory & tools when enabled (for complex tasks)',
        orch_threshold: 'Cluster threshold:',
        orch_ai_gen: '🤖 AI Generate',
        orch_ai_hint: 'Click "🤖 AI Orch" to auto-generate YAML',
        orch_prompt_label: '📨 Prompt Sent',
        orch_prompt_copy: 'Copy',
        orch_prompt_hint: 'Shown after AI Orch',
        orch_agent_yaml_label: '🤖 Agent YAML',
        orch_agent_yaml_copy: 'Copy',
        orch_agent_yaml_hint: 'Waiting for Agent',
        orch_rule_yaml: '📄 Rule YAML',
        orch_rule_yaml_hint: 'Auto-generated after adding experts...',
        orch_status_bar: 'Nodes: {nodes} | Edges: {edges} | Groups: {groups}',
        orch_status_bar_init: 'Nodes: 0 | Edges: 0 | Groups: 0',
        orch_manual_inject: 'Manual Inject',
        orch_start_node: 'Start Node',
        orch_end_node: 'End Node',
        orch_script_node: 'Script Node',
        orch_human_node: 'Human Node',
        orch_cond_node: 'Selector',
        orch_control_nodes: 'Control',
        orch_start_author: 'begin',
        orch_end_author: 'bend',
        orch_start_default_content: 'Discussion started',
        orch_end_default_content: 'Discussion ended',
        orch_cond_already_selector: 'is already a selector',
        orch_node_remove: 'Remove',
        orch_default_author: 'Moderator',
        orch_yaml_valid: '✅ Valid YAML — {steps} steps [{types}]',
        orch_yaml_saved_suffix: ' | 💾 Saved: {file}',
        orch_yaml_warn: '⚠️ YAML validation issue: {error}',
        orch_comm_fail: '# Communication failed: {msg}',
        // Context menu
        orch_ctx_duplicate: '📋 Duplicate (same instance)',
        orch_ctx_new_instance: '➕ New Instance',
        orch_ctx_group_parallel: '🔀 Group as Parallel',
        orch_ctx_group_all: '👥 Group as All Experts',
        orch_ctx_delete: '🗑️ Delete Selected',
        orch_ctx_refresh_yaml: '🔄 Refresh YAML',
        orch_ctx_clear: '🗑️ Clear Canvas',
        // Conditional edge
        orch_ctx_set_cond: '⚡ Set as Conditional Edge',
        orch_ctx_edit_cond: '✏️ Edit Conditional Edge',
        orch_ctx_remove_cond: '🔗 Revert to Fixed Edge',
        orch_ctx_set_selector: '🎯 Set as Selector Node (LLM Router)',
        orch_ctx_unset_selector: '🔗 Unset Selector Node',
        orch_modal_cond_edge: '⚡ Edit Conditional Edge',
        orch_cond_label_type: 'Condition Type',
        orch_cond_label_keyword: 'Keyword',
        orch_cond_label_number: 'Number',
        orch_cond_label_negate: 'Negate (NOT)',
        orch_cond_opt_contains: 'Last post contains keyword',
        orch_cond_opt_not_contains: 'Last post NOT contains keyword',
        orch_cond_opt_count_gte: 'Post count ≥ N',
        orch_cond_opt_count_lt: 'Post count < N',
        orch_cond_opt_always: 'Always true (unconditional)',
        orch_cond_label_then: 'Then Target (condition true)',
        orch_cond_label_else: 'Else Target (condition false / loop back)',
        orch_cond_none: '(none)',
        orch_cond_val_required: 'Please enter keyword or number',
        // Group labels
        orch_group_parallel: '🔀 Parallel',
        orch_group_all: '👥 All Experts',
        orch_group_dissolve: 'Dissolve',
        // Modals
        orch_modal_edit_manual: '📝 Edit Manual Injection',
        orch_modal_author_ph: 'Author',
        orch_modal_content_ph: 'Injection content...',
        orch_modal_cancel: 'Cancel',
        orch_modal_save: 'Save',
        orch_modal_select_session: '🎯 Select Target Agent Session',
        orch_modal_select_desc: 'Select an existing conversation session or create a new one. You can jump to it after generation.',
        orch_modal_loading: '⏳ Loading...',
        orch_modal_new_session: 'New Conversation',
        orch_modal_confirm_gen: 'Confirm & Generate',
        orch_modal_select_layout: '📂 Select Layout',
        orch_modal_delete: '🗑️ Delete',
        orch_modal_load: 'Load',
        // Toast messages
        orch_toast_arranged: 'Auto-arranged',
        orch_toast_saved: 'Saved: {name}',
        orch_toast_save_fail: 'Save failed',
        orch_toast_no_layouts: 'No saved layouts found',
        orch_toast_deleted: 'Deleted: {name}',
        orch_toast_del_fail: 'Delete failed',
        orch_toast_loaded: 'Loaded: {name}',
        orch_toast_load_fail: 'Load failed',
        orch_toast_yaml_copied: 'YAML copied!',
        orch_toast_gen_yaml: 'Generate YAML first',
        orch_toast_prompt_copied: 'Prompt copied',
        orch_toast_agent_yaml_copied: 'Agent YAML copied',
        orch_toast_select_2: 'Select at least 2 nodes',
        orch_toast_add_first: 'Add expert nodes first',
        orch_toast_agent_unavail: 'Agent unavailable',
        orch_toast_yaml_generated: 'YAML generated and saved! ✅',
        orch_toast_agent_valid: 'Agent generated valid YAML! ✅',
        orch_toast_session_updated: 'Session status updated',
        orch_toast_session_fail: 'Failed to get status',
        orch_toast_no_session: 'No session selected',
        orch_toast_jumped: 'Jumped to chat #{id}',
        orch_toast_custom_added: 'Custom expert added: {name}',
        orch_toast_fill_info: 'Please fill in all fields',
        orch_toast_net_error: 'Network error',
        orch_toast_expert_deleted: 'Deleted: {name}',
        orch_toast_expert_del_fail: 'Delete failed',
        orch_toast_added_mobile: 'added to canvas',
        // YAML file operations
        orch_btn_download: '⬇️ Export Workflow',
        orch_btn_upload: '⬆️ Import Workflow',
        orch_tip_download: 'Export workflow',
        orch_tip_upload: 'Import workflow',
        orch_toast_yaml_downloaded: 'YAML file downloaded',
        orch_toast_yaml_uploaded: 'YAML imported: {name}',
        orch_toast_yaml_upload_fail: 'YAML import failed',
        orch_toast_yaml_parse_fail: 'Invalid YAML file',
        orch_toast_drop_yaml: 'Drop YAML file here to import',
        orch_drop_hint: 'Release to import YAML file',
        orch_toast_not_yaml: 'Only .yaml / .yml files supported',
        // Team management
        orch_btn_create_team: '➕ Create',
        orch_btn_delete_team: '🗑️ Delete',
        orch_btn_download_snapshot: '⬇️ Snapshot',
        orch_btn_upload_snapshot: '⬆️ Upload',
        orch_tip_create_team: 'Create new team',
        orch_tip_delete_team: 'Delete current team',
        orch_tip_download_snapshot: 'Download team snapshot',
        orch_tip_upload_snapshot: 'Upload team snapshot',
        orch_toast_team_name_required: 'Please enter team name',
        orch_toast_team_created: 'Team created',
        orch_toast_team_create_failed: 'Failed to create team',
        orch_toast_team_deleted: 'Team deleted ({count} agents removed)',
        orch_toast_team_delete_failed: 'Failed to delete team',
        orch_toast_snapshot_downloaded: 'Snapshot downloaded',
        orch_toast_snapshot_download_failed: 'Failed to download snapshot',
        orch_toast_snapshot_uploaded: 'Snapshot uploaded and agents restored',
        orch_toast_snapshot_upload_failed: 'Failed to upload snapshot',
        orch_toast_invalid_zip: 'Please select a .zip file',
        orch_toast_network_error: 'Network error',
        orch_confirm_delete_team: 'Delete team "{name}" and all its agents?',
        // Export preview modal
        export_preview_title: '📦 Export Team Snapshot',
        export_preview_loading: 'Loading preview...',
        export_preview_desc: 'Please select items to export:',
        export_preview_tip: '💡 Tip: Uncheck a category to exclude it from export',
        export_agents: 'Internal Agents',
        export_personas: 'Custom Personas',
        export_skills: 'Skills',
        export_managed_skills: 'Managed Skills',
        export_cron: 'Cron Jobs',
        export_workflows: 'Workflows',
        export_download: '📥 Export',
        export_downloading: 'Exporting...',
        export_none_selected: 'Please select at least one item to export',
        export_preview_empty: 'No items available for export',
        // Confirm dialogs
        orch_confirm_del_expert: 'Delete custom expert "{name}"?',
        orch_confirm_del_layout: 'Delete layout "{name}"?',
        orch_prompt_layout_name: 'Layout name:',
        // Agent status
        orch_status_communicating: '🔄 Communicating with Agent (Session: #{id})...',
        orch_status_generating: '⏳ Generating...',
        orch_status_waiting: '⏳ Waiting for Agent response...',
        orch_status_auth_fail: 'Authentication failed',
        orch_status_agent_unavail: 'Agent unavailable',
        orch_status_conn_error: '❌ Connection error',
        orch_goto_chat: '💬 Jump to chat {session} to continue',
        orch_no_custom: 'No custom experts yet',
        orch_no_session: 'No sessions yet',
        orch_load_fail: '❌ Load failed',
        orch_load_session_fail: '❌ Failed to load session list',
        orch_msg_count: '{count} messages',
        orch_add_expert_title: '🛠️ Add Custom Expert',
        orch_add_expert_btn: 'Add custom expert',
        orch_label_name: 'Name',
        orch_label_tag: 'Tag (English)',
        orch_label_temp: 'Temperature',
        orch_label_persona: 'Persona (Role Description)',
        orch_ph_name: 'e.g. Financial Analyst',
        orch_ph_tag: 'e.g. finance',
        orch_ph_persona: 'Describe this expert\'s role, expertise and behavior style...',

        // Add Workflow
        wf_btn_title: 'Add Workflow',
        wf_btn_label: '+ Workflow',
        wf_popup_title: '📋 Select Workflow',
        wf_no_workflows: 'No saved workflows',
        wf_team_no_layouts: 'No saved workflows for this team',
        wf_cancel: 'Cancel',
        wf_confirm: 'Add',
        wf_context_prefix: '[Workflow: {name}] ',

        // Persona
        persona_btn_title: 'Use Expert Persona',
        persona_btn_label: '+ Persona',
        persona_popup_title: '🎭 Select Expert Persona',
        persona_no_experts: 'No experts available',
        persona_cancel: 'Cancel',
        persona_confirm: 'Use',
        persona_active: 'Active Persona',
        persona_public: '📋 Public Experts',
        persona_agency: '🌐 Agency Experts',
        persona_custom: '🔧 Custom Experts',

        // Others
        persona_search_placeholder: '🔍 Search expert name / tag...',
        persona_no_match: 'No matching experts',
        splash_subtitle: 'TeamBot AI Agent',
        secure_footer: 'Secured by Nginx Reverse Proxy & SSH Tunnel',
        refresh: 'Refresh',
        collapse: 'Collapse',

        // Settings
        settings: '⚙️',
        settings_title: '⚙️ System Settings',
        settings_save: 'Save',
        settings_saved: '✅ Settings saved',
        settings_save_fail: '❌ Save failed',
        settings_load_fail: '❌ Failed to load settings',
        settings_restart_hint: 'After editing, click "Save" first, then "Restart" to apply changes',
        settings_restart_btn: '🔄 Restart',
        settings_restarting: '⏳ Restarting...',
        settings_restart_ok: '✅ Restart signal sent, page will auto-refresh in 15 seconds',
        settings_restart_fail: '❌ Restart failed',
        settings_restart_confirm: 'Restart all services? Unsaved changes will be lost.',
        menu_settings: '⚙️ Settings',
        settings_group_llm: 'LLM Model',
        settings_group_tts: 'Audio',
        settings_group_openclaw: 'OpenClaw Integration',
        settings_group_oasis: 'OASIS Forum',
        settings_group_ports: 'Ports',
        settings_group_network: 'Public URLs',
        settings_group_bots: 'Bot Integration',
        settings_group_comm: 'Communication Mode',
        settings_group_exec: 'Command Execution',
        settings_group_security: 'Security',
        settings_group_other: 'Other',
        settings_help_audio_group: 'Leave these blank to follow the current LLM provider automatically. OpenAI defaults to gpt-4o-mini-tts / alloy / whisper-1; Gemini defaults to gemini-2.5-flash-preview-tts / charon.',
        settings_help_tts_model: 'Leave blank to follow the current LLM provider automatically. OpenAI defaults to gpt-4o-mini-tts, Gemini defaults to gemini-2.5-flash-preview-tts.',
        settings_help_tts_voice: 'Leave blank to follow the current LLM provider automatically. OpenAI uses alloy by default, Gemini uses charon.',
        settings_help_stt_model: 'Leave blank to follow the current LLM provider automatically. OpenAI defaults to whisper-1; Gemini does not currently have a built-in STT default.',
        settings_antigravity_preset: '🚀 Antigravity Free Models Preset',
        settings_antigravity_hint: 'Auto-fill Antigravity-Manager config. Uses Google One Pro membership for free model access. Make sure Antigravity-Manager is running locally.',
        settings_antigravity_apply: 'Apply Antigravity Preset',
        settings_antigravity_applied: '✅ Antigravity preset applied. Select a model and save.',
        settings_group_tunnel: '🌐 Public Tunnel',
        tunnel_start: 'Start Tunnel',
        tunnel_stop: 'Stop Tunnel',
        tunnel_starting: 'Starting...',
        tunnel_stopping: 'Stopping...',
        tunnel_running: '✅ Tunnel Running',
        tunnel_stopped: '❌ Tunnel Not Running',
        tunnel_url_hint: 'Click to copy public URL',

        // OpenClaw Chat Switcher
        oc_tab_internal: '🤖 TeamBot',
        oc_tab_openclaw: '🦞 OpenClaw',
        oc_select_agent: '-- Select Agent --',
        oc_no_agents: 'No OpenClaw agents available',
        oc_chatting_with: 'Chatting with {name}',
        oc_load_failed: 'Failed to load OpenClaw agents',
        oc_not_configured: 'OpenClaw not configured',
        oc_select_agent_hint: 'Please select an OpenClaw Agent first',
    }
};

// 当前语言
let currentLang = localStorage.getItem('lang') || 'zh-CN';
// 确保语言值有效
if (!i18n[currentLang]) { currentLang = 'zh-CN'; localStorage.setItem('lang', 'zh-CN'); }

// 获取翻译文本
function t(key, params) {
    let text = (i18n[currentLang] && i18n[currentLang][key]) || i18n['zh-CN'][key] || key;
    if (params) {
        Object.keys(params).forEach(k => {
            text = text.replace(new RegExp('\{' + k + '\}', 'g'), params[k]);
        });
    }
    return text;
}

// 切换语言
function toggleLanguage() {
    currentLang = currentLang === 'zh-CN' ? 'en' : 'zh-CN';
    localStorage.setItem('lang', currentLang);
    document.documentElement.lang = currentLang;
    applyTranslations();
}

// 应用翻译到页面
function applyTranslations() {
    // 更新语言按钮显示
    const langBtn = document.getElementById('lang-toggle-btn');
    if (langBtn) {
        langBtn.textContent = currentLang === 'zh-CN' ? 'EN' : '中文';
    }

    // 更新 data-i18n 属性的元素
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) {
            el.placeholder = t(key);
        } else if (el.tagName === 'TEXTAREA' && el.hasAttribute('placeholder')) {
            el.placeholder = t(key);
        } else {
            el.textContent = t(key);
        }
    });

    // 更新 data-i18n-placeholder 属性
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
    });

    // 更新 data-i18n-title 属性
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        el.title = t(el.getAttribute('data-i18n-title'));
    });

    // 更新 title
    document.title = 'Teamclaw | AI Agent';

    // 刷新编排面板的专家列表（专家名称和分类标签跟随语言切换）
    if (typeof orchRenderExpertSidebar === 'function') {
        orchRenderExpertSidebar();
    }
    // 刷新画布上已有的节点名称（跟随语言切换）
    if (typeof orch !== 'undefined' && orch.nodes && typeof orchRenderNode === 'function' && typeof orchRenderEdges === 'function') {
        orch.nodes.forEach(node => {
            const el = document.getElementById('onode-' + node.id);
            if (el) el.remove();
            orchRenderNode(node);
        });
        orchRenderEdges();
    }
    if (typeof renderPersonaPreview === 'function') {
        renderPersonaPreview();
    }
}

marked.setOptions({
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-'
});

let currentUserId = null;
let currentSessionId = null;
let currentAbortController = null;
let cancelTargetSessionId = null;  // 终止按钮绑定的会话ID
let pendingImages = []; // [{base64: "data:image/...", name: "file.jpg"}, ...]
let pendingFiles = [];  // [{name: "data.csv", content: "...(text content)"}, ...]
let pendingAudios = []; // [{base64: "data:audio/...", name: "recording.wav", format: "wav"}, ...]
let isRecording = false;

// OpenAI API 配置（前端不再存储 authToken，认证由服务端 session 完成）
const TEXT_EXTENSIONS = new Set(['.txt','.md','.csv','.json','.xml','.yaml','.yml','.log','.py','.js','.ts','.html','.css','.java','.c','.cpp','.h','.go','.rs','.sh','.bat','.ini','.toml','.cfg','.conf','.sql','.r','.rb']);
const AUDIO_EXTENSIONS = new Set(['.mp3','.wav','.ogg','.m4a','.webm','.flac','.aac']);
const VIDEO_EXTENSIONS = new Set(['.avi','.mp4','.mkv','.mov']);
const MAX_FILE_SIZE = 512 * 1024; // 512KB per text file
const MAX_PDF_SIZE = 10 * 1024 * 1024; // 10MB per PDF
const MAX_AUDIO_SIZE = 25 * 1024 * 1024; // 25MB per audio
const MAX_VIDEO_SIZE = 50 * 1024 * 1024; // 50MB per video
const MAX_IMAGE_SIZE = 10 * 1024 * 1024; // 压缩目标：10MB
const MAX_IMAGE_DIMENSION = 2048; // 最大边长

function compressImage(file) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            let { width, height } = img;
            if (width > MAX_IMAGE_DIMENSION || height > MAX_IMAGE_DIMENSION) {
                const scale = MAX_IMAGE_DIMENSION / Math.max(width, height);
                width = Math.round(width * scale);
                height = Math.round(height * scale);
            }
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);
            let quality = 0.85;
            let result = canvas.toDataURL('image/jpeg', quality);
            while (result.length > MAX_IMAGE_SIZE * 1.37 && quality > 0.3) {
                quality -= 0.1;
                result = canvas.toDataURL('image/jpeg', quality);
            }
            resolve(result);
        };
        img.src = URL.createObjectURL(file);
    });
}

// ===== File Upload Logic (images + text files + PDF + audio) =====
function handleFileSelect(event) {
    const files = event.target.files;
    if (!files.length) return;
    for (const file of files) {
        if (file.type.startsWith('image/')) {
            if (pendingImages.length >= 5) { alert(t('max_images')); break; }
            if (file.size <= MAX_IMAGE_SIZE) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    pendingImages.push({ base64: e.target.result, name: file.name });
                    renderImagePreviews();
                };
                reader.readAsDataURL(file);
            } else {
                compressImage(file).then((compressed) => {
                    pendingImages.push({ base64: compressed, name: file.name });
                    renderImagePreviews();
                });
            }
        } else if (file.type.startsWith('audio/') || AUDIO_EXTENSIONS.has('.' + file.name.split('.').pop().toLowerCase())) {
            if (file.size > MAX_AUDIO_SIZE) { alert(`${file.name}: ${t('audio_too_large')} (${(file.size/1024/1024).toFixed(1)}MB)`); continue; }
            if (pendingAudios.length >= 2) { alert(t('max_audios')); break; }
            const ext = file.name.split('.').pop().toLowerCase();
            const fmt = ({'mp3':'mp3','wav':'wav','ogg':'ogg','m4a':'m4a','webm':'webm','flac':'flac','aac':'aac'})[ext] || 'mp3';
            const reader = new FileReader();
            reader.onload = (e) => {
                pendingAudios.push({ base64: e.target.result, name: file.name, format: fmt });
                renderAudioPreviews();
            };
            reader.readAsDataURL(file);
        } else if (file.type.startsWith('video/') || VIDEO_EXTENSIONS.has('.' + file.name.split('.').pop().toLowerCase())) {
            // 视频文件：以 dataURL 形式存入 pendingFiles，type='media'
            if (file.size > MAX_VIDEO_SIZE) { alert(`${file.name}: ${t('video_too_large')} (${(file.size/1024/1024).toFixed(1)}MB)`); continue; }
            if (pendingFiles.length >= 3) { alert(t('max_files')); break; }
            const reader = new FileReader();
            reader.onload = (e) => {
                pendingFiles.push({ name: file.name, content: e.target.result, type: 'media' });
                renderFilePreviews();
            };
            reader.readAsDataURL(file);
        } else if (file.name.toLowerCase().endsWith('.pdf') || file.type === 'application/pdf') {
            if (file.size > MAX_PDF_SIZE) { alert(`${file.name}: ${t('pdf_too_large')} (${(file.size/1024/1024).toFixed(1)}MB)`); continue; }
            if (pendingFiles.length >= 3) { alert(t('max_files')); break; }
            const reader = new FileReader();
            reader.onload = (e) => {
                pendingFiles.push({ name: file.name, content: e.target.result, type: 'pdf' });
                renderFilePreviews();
            };
            reader.readAsDataURL(file);
        } else {
            const ext = '.' + file.name.split('.').pop().toLowerCase();
            if (!TEXT_EXTENSIONS.has(ext)) { alert(`${t('unsupported_type')}: ${ext}\n${t('supported_types')}`); continue; }
            if (file.size > MAX_FILE_SIZE) { alert(`${file.name}: ${t('file_too_large')} (${(file.size/1024).toFixed(0)}KB)`); continue; }
            if (pendingFiles.length >= 3) { alert(t('max_files')); break; }
            const reader = new FileReader();
            reader.onload = (e) => {
                pendingFiles.push({ name: file.name, content: e.target.result, type: 'text' });
                renderFilePreviews();
            };
            reader.readAsText(file);
        }
    }
    event.target.value = '';
}

// ===== Audio Recording =====
async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

// --- WAV 编码辅助函数 ---
function encodeWAV(samples, sampleRate) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);
    function writeString(offset, string) {
        for (let i = 0; i < string.length; i++) view.setUint8(offset + i, string.charCodeAt(i));
    }
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true); // PCM
    view.setUint16(22, 1, true); // mono
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, samples.length * 2, true);
    for (let i = 0; i < samples.length; i++) {
        const s = Math.max(-1, Math.min(1, samples[i]));
        view.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    return new Blob([buffer], { type: 'audio/wav' });
}

let audioContext = null;
let audioSourceNode = null;
let audioProcessorNode = null;
let recordedSamples = [];

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const AudioCtx = window.AudioContext || /** @type {any} */ (window).webkitAudioContext;
        audioContext = new AudioCtx({ sampleRate: 16000 });
        audioSourceNode = audioContext.createMediaStreamSource(stream);
        audioProcessorNode = audioContext.createScriptProcessor(4096, 1, 1);
        recordedSamples = [];
        audioProcessorNode.onaudioprocess = (e) => {
            const data = e.inputBuffer.getChannelData(0);
            recordedSamples.push(new Float32Array(data));
        };
        audioSourceNode.connect(audioProcessorNode);
        audioProcessorNode.connect(audioContext.destination);
        isRecording = true;
        document.getElementById('record-btn').classList.add('recording');
        document.getElementById('record-btn').title = t('recording_stop');
    } catch (err) {
        alert(t('mic_permission_denied') + '\n' + err.message);
    }
}

function stopRecording() {
    if (!audioContext) return;
    const stream = audioSourceNode.mediaStream;
    audioProcessorNode.disconnect();
    audioSourceNode.disconnect();
    stream.getTracks().forEach(t => t.stop());
    // 合并所有采样
    let totalLen = 0;
    for (const chunk of recordedSamples) totalLen += chunk.length;
    const merged = new Float32Array(totalLen);
    let offset = 0;
    for (const chunk of recordedSamples) { merged.set(chunk, offset); offset += chunk.length; }
    const sampleRate = audioContext.sampleRate;
    audioContext.close();
    audioContext = null;
    audioSourceNode = null;
    audioProcessorNode = null;
    recordedSamples = [];
    isRecording = false;
    document.getElementById('record-btn').classList.remove('recording');
    document.getElementById('record-btn').title = t('recording_title');
    const blob = encodeWAV(merged, sampleRate);
    if (blob.size > MAX_AUDIO_SIZE) { alert(t('recording_too_long')); return; }
    if (pendingAudios.length >= 2) { alert(t('max_audios')); return; }
    const reader = new FileReader();
    reader.onload = (e) => {
        const ts = new Date().toLocaleTimeString(currentLang === 'zh-CN' ? 'zh-CN' : 'en-US', {hour:'2-digit',minute:'2-digit',second:'2-digit'});
        const recName = currentLang === 'zh-CN' ? `录音_${ts}.wav` : `recording_${ts}.wav`;
        pendingAudios.push({ base64: e.target.result, name: recName, format: 'wav' });
        renderAudioPreviews();
    };
    reader.readAsDataURL(blob);
}

function removeAudio(index) {
    pendingAudios.splice(index, 1);
    renderAudioPreviews();
}

function renderAudioPreviews() {
    const area = document.getElementById('audio-preview-area');
    if (pendingAudios.length === 0) {
        area.style.display = 'none';
        area.innerHTML = '';
        return;
    }
    area.style.display = 'flex';
    area.innerHTML = pendingAudios.map((a, i) => `
        <div class="audio-preview-item">
            <span class="file-icon">🎤</span>
            <span class="file-name" title="${escapeHtml(a.name)}">${escapeHtml(a.name)}</span>
            <button class="remove-btn" onclick="removeAudio(${i})">&times;</button>
        </div>
    `).join('');
}

function handlePasteImage(event) {
    const items = event.clipboardData?.items;
    if (!items) return;
    for (const item of items) {
        if (!item.type.startsWith('image/')) continue;
        event.preventDefault();
        if (pendingImages.length >= 5) { alert(t('max_images')); break; }
        const file = item.getAsFile();
        const reader = new FileReader();
        reader.onload = (e) => {
            pendingImages.push({ base64: e.target.result, name: 'pasted_image.png' });
            renderImagePreviews();
        };
        reader.readAsDataURL(file);
    }
}

function removeImage(index) {
    pendingImages.splice(index, 1);
    renderImagePreviews();
}

function removeFile(index) {
    pendingFiles.splice(index, 1);
    renderFilePreviews();
}

function renderImagePreviews() {
    const area = document.getElementById('image-preview-area');
    if (pendingImages.length === 0) {
        area.style.display = 'none';
        area.innerHTML = '';
        return;
    }
    area.style.display = 'flex';
    area.innerHTML = pendingImages.map((img, i) => `
        <div class="image-preview-item">
            <img src="${img.base64}" alt="${img.name}">
            <button class="remove-btn" onclick="removeImage(${i})">&times;</button>
        </div>
    `).join('');
}

function renderFilePreviews() {
    const area = document.getElementById('file-preview-area');
    if (pendingFiles.length === 0) {
        area.style.display = 'none';
        area.innerHTML = '';
        return;
    }
    area.style.display = 'flex';
    area.innerHTML = pendingFiles.map((f, i) => `
        <div class="file-preview-item">
            <span class="file-icon">${f.type === 'media' ? '🎬' : '📄'}</span>
            <span class="file-name" title="${escapeHtml(f.name)}">${escapeHtml(f.name)}</span>
            <button class="remove-btn" onclick="removeFile(${i})">&times;</button>
        </div>
    `).join('');
}

// ===== Session (conversation) ID management =====
function generateSessionId() {
    return Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
}

function initSession() {
    let saved = sessionStorage.getItem('sessionId');
    if (!saved) {
        saved = generateSessionId();
        sessionStorage.setItem('sessionId', saved);
    }
    currentSessionId = saved;
    updateSessionDisplay();
}

function updateSessionDisplay() {
    const el = document.getElementById('session-display');
    if (el && currentSessionId) {
        el.textContent = '#' + currentSessionId.slice(-6);
        el.title = t('session_id') + ': ' + currentSessionId;
    }
}

// ===== Agent Meta Modal Logic =====
let _agentMetaCallback = null;  // resolve fn for the modal promise
let _agentMetaMode = 'create';  // 'create' or 'edit'
let _agentMetaSessionId = null;

async function openAgentMetaModal(mode, sessionId, existingMeta) {
    _agentMetaMode = mode;
    _agentMetaSessionId = sessionId;
    const modal = document.getElementById('agent-meta-modal');
    document.getElementById('agent-meta-modal-title').textContent =
        mode === 'edit' ? '✏️ Edit Agent Settings' : '🤖 New Agent Settings';
    document.getElementById('agent-meta-name').value = (existingMeta && existingMeta.name) || '';

    // ── Populate tools checkbox list ──
    const toolsContainer = document.getElementById('agent-meta-tools-container');
    // Determine which tools are currently enabled for this agent
    const existingTools = (existingMeta && existingMeta.tools) || null;
    let enabledToolNames = null; // null = all
    if (existingTools && typeof existingTools === 'object' && !Array.isArray(existingTools)) {
        enabledToolNames = new Set(Object.keys(existingTools).filter(k => existingTools[k] === true));
    } else if (typeof existingTools === 'string' && existingTools === 'none') {
        enabledToolNames = new Set();
    }
    // allTools comes from loadTools() global
    if (allTools.length > 0) {
        toolsContainer.innerHTML = `
            <div style="width:100%;display:flex;gap:6px;margin-bottom:4px;">
                <button type="button" onclick="_agentMetaToolsSelectAll(true)" style="font-size:10px;padding:2px 8px;border:1px solid #d1d5db;border-radius:4px;background:#f0fdf4;color:#16a34a;cursor:pointer;">全选</button>
                <button type="button" onclick="_agentMetaToolsSelectAll(false)" style="font-size:10px;padding:2px 8px;border:1px solid #d1d5db;border-radius:4px;background:#fef2f2;color:#dc2626;cursor:pointer;">全不选</button>
            </div>` +
            allTools.map(t => {
                const checked = (enabledToolNames === null || enabledToolNames.has(t.name)) ? 'checked' : '';
                return `<label style="display:inline-flex;align-items:center;gap:3px;font-size:11px;padding:3px 6px;border:1px solid #e5e7eb;border-radius:5px;cursor:pointer;background:#f9fafb;white-space:nowrap;" title="${escapeHtml(t.description || '')}">
                    <input type="checkbox" class="agent-meta-tool-cb" value="${escapeHtml(t.name)}" ${checked} style="margin:0;">
                    ${escapeHtml(t.name)}
                </label>`;
            }).join('');
    } else {
        toolsContainer.innerHTML = '<span style="color:#9ca3af;font-size:12px;">无可用工具（请先登录加载工具列表）</span>';
    }

    // Populate tag select options from experts list
    const tagSelect = document.getElementById('agent-meta-tag');
    const currentTag = (existingMeta && existingMeta.tag) || '';
    try {
        const r = await fetch('/proxy_visual/experts');
        const experts = await r.json();
        const tags = [...new Set(experts.map(e => e.tag).filter(Boolean))];
        tagSelect.innerHTML = '<option value="">(None)</option>' +
            tags.map(t => `<option value="${t}">${t}</option>`).join('');
    } catch (e) {
        console.warn('Failed to load expert tags', e);
    }
    tagSelect.value = currentTag;
    modal.style.display = 'flex';
    document.getElementById('agent-meta-name').focus();
    return new Promise(resolve => { _agentMetaCallback = resolve; });
}

function _agentMetaToolsSelectAll(selectAll) {
    document.querySelectorAll('.agent-meta-tool-cb').forEach(cb => { cb.checked = selectAll; });
}

function closeAgentMetaModal() {
    document.getElementById('agent-meta-modal').style.display = 'none';
    if (_agentMetaCallback) { _agentMetaCallback(null); _agentMetaCallback = null; }
}

function _collectAgentMeta() {
    const name = document.getElementById('agent-meta-name').value.trim() || null;
    const tag = document.getElementById('agent-meta-tag').value.trim() || null;

    // Collect tools from checkboxes
    const checkboxes = document.querySelectorAll('.agent-meta-tool-cb');
    let tools = null;
    if (checkboxes.length > 0) {
        const checkedNames = [];
        checkboxes.forEach(cb => { if (cb.checked) checkedNames.push(cb.value); });
        if (checkedNames.length === allTools.length) {
            // All selected → don't set tools (= no restriction)
            tools = null;
        } else {
            const obj = {};
            checkedNames.forEach(t => obj[t] = true);
            tools = obj;
        }
    }

    const meta = {};
    if (name !== null) meta.name = name;
    if (tools !== null) meta.tools = tools;
    if (tag !== null) meta.tag = tag;
    return meta;
}

async function submitAgentMeta() {
    const meta = _collectAgentMeta();
    if (_agentMetaMode === 'edit' && _agentMetaSessionId) {
        // Update existing agent via PUT
        try {
            const url = _currentAgentTeam 
                ? `/internal_agents/${encodeURIComponent(_agentMetaSessionId)}?team=${encodeURIComponent(_currentAgentTeam)}`
                : `/internal_agents/${encodeURIComponent(_agentMetaSessionId)}`;
            await fetch(url, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ meta })
            });
        } catch (e) { console.warn('Failed to update agent meta', e); }
    }
    document.getElementById('agent-meta-modal').style.display = 'none';
    if (_agentMetaCallback) { _agentMetaCallback(meta); _agentMetaCallback = null; }
}

// ===== Team Selection for Agent Sidebar =====
let _currentAgentTeam = '';  // Current selected team in agent sidebar

async function loadAgentTeams() {
    try {
        const resp = await fetch('/teams');
        const data = await resp.json();
        const select = document.getElementById('agent-team-select');
        if (!select) return;
        select.innerHTML = '<option value="">(公共)</option>';
        if (data.teams && data.teams.length > 0) {
            for (const team of data.teams) {
                const opt = document.createElement('option');
                opt.value = team;
                opt.textContent = team;
                select.appendChild(opt);
            }
        }
        // Restore previous selection
        select.value = _currentAgentTeam;
    } catch (e) {
        console.warn('Failed to load teams:', e);
    }
}

function onAgentTeamChange() {
    const select = document.getElementById('agent-team-select');
    _currentAgentTeam = select.value;
    loadSessionList();
}

// Helper: load internal agent meta as a map { session_id: meta } + all known sessions set
async function _loadAgentMetaMap(team = '') {
    try {
        const url = team ? `/internal_agents?team=${encodeURIComponent(team)}` : '/internal_agents';
        const resp = await fetch(url);
        const data = await resp.json();
        const map = {};
        if (data.agents) {
            for (const a of data.agents) map[a.session] = a.meta || {};
        }
        const allKnown = new Set(data.all_known_sessions || []);
        return { map, allKnown };
    } catch (e) { return { map: {}, allKnown: new Set() }; }
}

// Resolve display title: prefer agent meta name, fallback to original title
function _resolveTitle(originalTitle, sessionId, agentMap) {
    const meta = agentMap[sessionId];
    if (meta && meta.name) return meta.name;
    return originalTitle;
}

async function editAgentMeta(sessionId) {
    // Load current meta from backend
    let existingMeta = {};
    try {
        const agentResult = await _loadAgentMetaMap(_currentAgentTeam);
        existingMeta = agentResult.map[sessionId] || {};
    } catch (e) { /* ignore */ }
    // If tools is object, convert back to comma string for display
    if (existingMeta.tools && typeof existingMeta.tools === 'object') {
        existingMeta.tools = Object.keys(existingMeta.tools).join(',');
    }
    await openAgentMetaModal('edit', sessionId, existingMeta);
}

function handleNewSession() {
    // Open the agent meta modal; after user submits, create session + write JSON
    const newSid = generateSessionId();
    openAgentMetaModal('create', newSid, {}).then(async (meta) => {
        if (meta === null) return;  // User cancelled
        currentSessionId = newSid;
        sessionStorage.setItem('sessionId', currentSessionId);
        updateSessionDisplay();
        // Clear chat box for new conversation
        const chatBox = document.getElementById('chat-box');
        chatBox.innerHTML = `
            <div class="flex justify-start">
                <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700">
                    ${t('new_session_message')}
                </div>
            </div>`;
        // Write internal agent JSON
        try {
            const url = _currentAgentTeam ? `/internal_agents?team=${encodeURIComponent(_currentAgentTeam)}` : '/internal_agents';
            await fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ session: newSid, meta: meta })
            });
        } catch (e) { console.warn('Failed to save internal agent', e); }
    });
}

// ===== 历史会话侧边栏 =====
let sessionSidebarOpen = false;
let _historyPollingTimer = null;

function startHistoryPolling() {
    stopHistoryPolling();
    _historyPollingTimer = setInterval(() => {
        if (sessionSidebarOpen) {
            refreshHistoryList();
        } else {
            // sidebar 未打开也刷新状态（发光效果），以便打开时立即可见
            refreshSessionStatus();
        }
    }, 3000);
}
function stopHistoryPolling() {
    if (_historyPollingTimer) { clearInterval(_historyPollingTimer); _historyPollingTimer = null; }
}

function toggleSessionSidebar() {
    if (sessionSidebarOpen) { closeSessionSidebar(); } else { openSessionSidebar(); }
}

async function openSessionSidebar() {
    const sidebar = document.getElementById('session-sidebar');
    sidebar.style.display = 'flex';
    sessionSidebarOpen = true;
    // 移动端加遮罩
    if (window.innerWidth <= 768) {
        let overlay = document.getElementById('session-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'session-overlay';
            overlay.className = 'session-overlay';
            overlay.onclick = closeSessionSidebar;
            sidebar.parentElement.appendChild(overlay);
        }
        overlay.style.display = 'block';
    }
    // Load team list
    await loadAgentTeams();
    // 已有列表内容则增量刷新，否则全量加载
    const listEl = document.getElementById('session-list');
    if (listEl.querySelector('.session-item')) {
        refreshHistoryList();
    } else {
        await loadSessionList();
    }
}

function closeSessionSidebar() {
    document.getElementById('session-sidebar').style.display = 'none';
    const overlay = document.getElementById('session-overlay');
    if (overlay) overlay.style.display = 'none';
    sessionSidebarOpen = false;
}

// Session filter mode: 'named' = show sessions with agent name, 'unnamed' = show sessions without
let sessionFilterMode = 'named';
// Cached agent meta map (session_id → {name, tag, ...}), refreshed on each loadSessionList/refreshHistoryList
let _cachedAgentMap = {};
// All known session IDs across all JSON files (public + all teams), for unnamed detection
let _allKnownSessions = new Set();

function isNamedSession(sessionId) {
    const meta = _cachedAgentMap[sessionId];
    return !!(meta && meta.name);
}

function shouldShowSession(sessionId) {
    if (sessionFilterMode === 'named') {
        return isNamedSession(sessionId);
    } else {
        // Unnamed = not in ANY json across all sources
        return !_allKnownSessions.has(sessionId);
    }
}

function toggleNamedSessionsVisible() {
    sessionFilterMode = sessionFilterMode === 'named' ? 'unnamed' : 'named';
    const btn = document.getElementById('toggle-oasis-sessions-btn');
    if (btn) {
        btn.textContent = sessionFilterMode === 'named' ? '🏷️ 切换到无名会话' : '🏷️ 切换到已命名 Agents';
    }
    // Apply filter to all session items
    document.querySelectorAll('.session-item[data-session-id]').forEach(el => {
        el.style.display = shouldShowSession(el.dataset.sessionId) ? '' : 'none';
    });
}

async function loadSessionList() {
    const listEl = document.getElementById('session-list');
    if (!listEl.querySelector('.session-item')) {
        listEl.innerHTML = `<div class="text-xs text-gray-400 text-center py-4">${t('loading')}</div>`;
    }
    try {
        // Load sessions and agent meta in parallel
        const [resp, agentResult] = await Promise.all([fetch('/proxy_sessions'), _loadAgentMetaMap(_currentAgentTeam)]);
        _cachedAgentMap = agentResult.map;
        _allKnownSessions = agentResult.allKnown;
        const agentMap = agentResult.map;
        const data = await resp.json();
        // Merge: add sessions from agent JSON that are not in proxy_sessions
        const allSessions = (data.sessions || []).slice();
        const seenIds = new Set(allSessions.map(s => s.session_id));
        for (const [sid, meta] of Object.entries(agentMap)) {
            if (!seenIds.has(sid) && meta && meta.name) {
                allSessions.push({ session_id: sid, title: meta.name || 'Untitled', message_count: 0 });
                seenIds.add(sid);
            }
        }
        if (allSessions.length === 0) {
            listEl.innerHTML = `<div class="text-xs text-gray-400 text-center py-4">${t('history_empty')}</div>`;
            return;
        }
        listEl.innerHTML = '';
        allSessions.sort((a, b) => b.session_id.localeCompare(a.session_id));
        for (const s of allSessions) {
            const isActive = s.session_id === currentSessionId;
            const displayTitle = _resolveTitle(s.title, s.session_id, agentMap);
            const div = document.createElement('div');
            div.className = 'session-item' + (isActive ? ' active' : '');
            div.dataset.sessionId = s.session_id;
            div.innerHTML = `
                <div class="session-title">${escapeHtml(displayTitle)}</div>
                <div class="session-meta">#${s.session_id.slice(-6)} · ${s.message_count}${t('messages_count')}</div>
                <button class="session-edit" onclick="event.stopPropagation(); editAgentMeta('${s.session_id}')">✏️</button>
                <button class="session-delete" onclick="event.stopPropagation(); deleteSession('${s.session_id}')">${t('delete_session')}</button>
            `;
            div.onclick = () => switchToSession(s.session_id);
            if (!shouldShowSession(s.session_id)) {
                div.style.display = 'none';
            }
            listEl.appendChild(div);
        }
        refreshSessionStatus();
    } catch (e) {
        listEl.innerHTML = `<div class="text-xs text-red-400 text-center py-4">${t('history_error')}</div>`;
    }
}

// 增量刷新：不重建DOM，只更新标题/计数 + 状态发光
async function refreshHistoryList() {
    try {
        const [sessResp, statusResp, agentResult] = await Promise.all([
            fetch('/proxy_sessions'),
            fetch('/proxy_sessions_status'),
            _loadAgentMetaMap(_currentAgentTeam)
        ]);
        const sessData = await sessResp.json();
        const statusData = statusResp.ok ? await statusResp.json() : {};
        _cachedAgentMap = agentResult.map;
        _allKnownSessions = agentResult.allKnown;
        const agentMap = agentResult.map;
        const sessions = sessData.sessions || [];
        // Merge: add named sessions from agent JSON that are not in proxy_sessions
        const seenIds = new Set(sessions.map(s => s.session_id));
        for (const [sid, meta] of Object.entries(agentMap)) {
            if (!seenIds.has(sid) && meta && meta.name) {
                sessions.push({ session_id: sid, title: meta.name || 'Untitled', message_count: 0 });
                seenIds.add(sid);
            }
        }
        const listEl = document.getElementById('session-list');
        if (sessions.length === 0) {
            listEl.innerHTML = `<div class="text-xs text-gray-400 text-center py-4">${t('history_empty')}</div>`;
            return;
        }
        // 构建 session map
        const sessMap = {};
        for (const s of sessions) sessMap[s.session_id] = s;
        const statusMap = {};
        if (statusData.sessions) {
            for (const s of statusData.sessions) statusMap[s.session_id] = s;
        }
        // 现有 DOM 的 session id 集合
        const existingEls = listEl.querySelectorAll('.session-item[data-session-id]');
        const existingIds = new Set();
        existingEls.forEach(el => existingIds.add(el.dataset.sessionId));
        const newIds = new Set(sessions.map(s => s.session_id));
        // 删除不存在的
        existingEls.forEach(el => {
            if (!newIds.has(el.dataset.sessionId)) el.remove();
        });
        // 更新现有的 + 添加新的
        sessions.sort((a, b) => b.session_id.localeCompare(a.session_id));
        let prevEl = null;
        for (const s of sessions) {
            let div = listEl.querySelector(`.session-item[data-session-id="${s.session_id}"]`);
            if (div) {
                // 更新标题和计数
                const titleEl = div.querySelector('.session-title');
                const newTitle = escapeHtml(_resolveTitle(s.title, s.session_id, agentMap));
                if (titleEl && titleEl.innerHTML !== newTitle) titleEl.innerHTML = newTitle;
                const metaEl = div.querySelector('.session-meta');
                if (metaEl) {
                    const badge = metaEl.querySelector('.session-busy-badge');
                    const newMeta = `#${s.session_id.slice(-6)} · ${s.message_count}${t('messages_count')}`;
                    // 只更新文本部分，保留badge
                    const textNode = metaEl.firstChild;
                    if (textNode && textNode.nodeType === 3) {
                        if (textNode.textContent.trim() !== newMeta.trim()) textNode.textContent = newMeta;
                    } else {
                        // 重建meta但保留badge
                        const savedBadge = badge;
                        metaEl.textContent = newMeta;
                        if (savedBadge) metaEl.appendChild(savedBadge);
                    }
                }
                // active 状态
                div.classList.toggle('active', s.session_id === currentSessionId);
                // session 可见性
                div.style.display = shouldShowSession(s.session_id) ? '' : 'none';
            } else {
                // 新增的 session
                div = document.createElement('div');
                div.className = 'session-item' + (s.session_id === currentSessionId ? ' active' : '');
                div.dataset.sessionId = s.session_id;
                const displayTitle = _resolveTitle(s.title, s.session_id, agentMap);
                div.innerHTML = `
                    <div class="session-title">${escapeHtml(displayTitle)}</div>
                    <div class="session-meta">#${s.session_id.slice(-6)} · ${s.message_count}${t('messages_count')}</div>
                    <button class="session-edit" onclick="event.stopPropagation(); editAgentMeta('${s.session_id}')">✏️</button>
                    <button class="session-delete" onclick="event.stopPropagation(); deleteSession('${s.session_id}')">${t('delete_session')}</button>
                `;
                div.onclick = () => switchToSession(s.session_id);
                if (!shouldShowSession(s.session_id)) {
                    div.style.display = 'none';
                }
                if (prevEl && prevEl.nextSibling) {
                    listEl.insertBefore(div, prevEl.nextSibling);
                } else if (!prevEl) {
                    listEl.prepend(div);
                } else {
                    listEl.appendChild(div);
                }
            }
            // 更新发光状态（不移除再添加class，避免动画重启）
            const info = statusMap[s.session_id];
            const wantUser = info && info.busy && info.source !== 'system';
            const wantSystem = info && info.busy && info.source === 'system';
            const hasUser = div.classList.contains('busy-user');
            const hasSystem = div.classList.contains('busy-system');
            if (wantUser && !hasUser) { div.classList.remove('busy-system'); div.classList.add('busy-user'); }
            else if (wantSystem && !hasSystem) { div.classList.remove('busy-user'); div.classList.add('busy-system'); }
            else if (!wantUser && !wantSystem) { div.classList.remove('busy-user', 'busy-system'); }
            // badge
            const existingBadge = div.querySelector('.session-busy-badge');
            if (info && info.busy) {
                const badgeCls = info.source === 'system' ? 'system' : 'user';
                const badgeText = info.source === 'system' ? '⚙️' : '💬';
                if (existingBadge) {
                    if (!existingBadge.classList.contains(badgeCls)) {
                        existingBadge.className = 'session-busy-badge ' + badgeCls;
                        existingBadge.textContent = badgeText;
                    }
                } else {
                    const badge = document.createElement('span');
                    badge.className = 'session-busy-badge ' + badgeCls;
                    badge.textContent = badgeText;
                    div.querySelector('.session-meta')?.appendChild(badge);
                }
            } else if (existingBadge) {
                existingBadge.remove();
            }
            prevEl = div;
        }
    } catch (e) { /* silent */ }
}

async function refreshSessionStatus() {
    try {
        const resp = await fetch('/proxy_sessions_status');
        if (!resp.ok) return;
        const data = await resp.json();
        if (!data.sessions) return;
        const statusMap = {};
        for (const s of data.sessions) statusMap[s.session_id] = s;
        document.querySelectorAll('.session-item[data-session-id]').forEach(el => {
            const sid = el.dataset.sessionId;
            const info = statusMap[sid];
            el.classList.remove('busy-user', 'busy-system');
            el.querySelector('.session-busy-badge')?.remove();
            if (info && info.busy) {
                const cls = info.source === 'system' ? 'busy-system' : 'busy-user';
                el.classList.add(cls);
                const badge = document.createElement('span');
                badge.className = 'session-busy-badge ' + (info.source === 'system' ? 'system' : 'user');
                badge.textContent = info.source === 'system' ? '⚙️' : '💬';
                el.querySelector('.session-meta')?.appendChild(badge);
            }
        });
    } catch (e) { /* silent */ }
}

async function deleteSession(sessionId) {
    if (!confirm(t('delete_session_confirm'))) return;
    try {
        const resp = await fetch('/proxy_delete_session', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ session_id: sessionId })
        });
        const data = await resp.json();
        if (resp.ok && data.status === 'success') {
            // Also delete internal agent JSON record
            try {
                const url = _currentAgentTeam 
                    ? `/internal_agents/${encodeURIComponent(sessionId)}?team=${encodeURIComponent(_currentAgentTeam)}` 
                    : `/internal_agents/${encodeURIComponent(sessionId)}`;
                await fetch(url, { method: 'DELETE' });
            } catch (e) { /* ignore if not found */ }
            // 如果删除的是当前会话，自动开一个新的
            if (sessionId === currentSessionId) {
                currentSessionId = generateSessionId();
                sessionStorage.setItem('sessionId', currentSessionId);
                updateSessionDisplay();
                document.getElementById('chat-box').innerHTML = `
                    <div class="flex justify-start">
                        <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700">
                            ${t('new_session_message')}
                        </div>
                    </div>`;
            }
            await loadSessionList();
        } else {
            alert(t('delete_fail') + ': ' + (data.detail || data.error || ''));
        }
    } catch (e) {
        alert(t('delete_fail') + ': ' + e.message);
    }
}

async function deleteAllSessions() {
    // Collect visible session ids based on current filter mode
    const visibleIds = [];
    document.querySelectorAll('.session-item[data-session-id]').forEach(el => {
        if (el.style.display !== 'none') {
            visibleIds.push(el.dataset.sessionId);
        }
    });
    if (visibleIds.length === 0) return;
    const modeLabel = sessionFilterMode === 'named' ? '已命名' : '无名';
    if (!confirm(`确认删除当前显示的 ${visibleIds.length} 个${modeLabel}会话？`)) return;
    try {
        let failCount = 0;
        await Promise.all(visibleIds.map(async sid => {
            try {
                const resp = await fetch('/proxy_delete_session', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ session_id: sid })
                });
                const data = await resp.json();
                if (!resp.ok || data.status !== 'success') failCount++;
            } catch { failCount++; }
        }));
        // If current session was among deleted, reset it
        if (visibleIds.includes(currentSessionId)) {
            currentSessionId = generateSessionId();
            sessionStorage.setItem('sessionId', currentSessionId);
            updateSessionDisplay();
            document.getElementById('chat-box').innerHTML = `
                <div class="flex justify-start">
                    <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700">
                        ${t('new_session_message')}
                    </div>
                </div>`;
        }
        await loadSessionList();
        if (failCount > 0) alert(`${failCount} 个会话删除失败`);
    } catch (e) {
        alert(t('delete_fail') + ': ' + e.message);
    }
}

async function switchToSession(sessionId, force = false) {
    if (!force && sessionId === currentSessionId) { closeSessionSidebar(); return; }
    showPageLoading();
    hideNewMsgBanner();
    // 切换前先重置按钮到 idle 状态（避免旧 session 的 streaming/busy 状态残留）
    setStreamingUI(false);
    setSystemBusyUI(false);
    currentSessionId = sessionId;
    cancelTargetSessionId = null;  // 重置终止目标
    personaInjectedSession = null;  // Reset persona injection flag for new session
    sessionStorage.setItem('sessionId', sessionId);
    updateSessionDisplay();
    closeSessionSidebar();

    // 加载该会话的历史消息
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = `<div class="text-xs text-gray-400 text-center py-4">${t('history_loading_msg')}</div>`;

    try {
        const resp = await fetch('/proxy_session_history', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ session_id: sessionId })
        });
        const data = await resp.json();
        chatBox.innerHTML = '';

        if (!data.messages || data.messages.length === 0) {
            chatBox.innerHTML = `
                <div class="flex justify-start">
                    <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700">
                        ${t('history_no_msg')}
                    </div>
                </div>`;
            hidePageLoading();
            return;
        }

        for (const msg of data.messages) {
            if (msg.role === 'user') {
                // 支持多模态历史消息（content 可能是 string 或 array）
                let textContent = '';
                let imagesHtml = '';
                if (typeof msg.content === 'string') {
                    textContent = msg.content;
                } else if (Array.isArray(msg.content)) {
                    for (const part of msg.content) {
                        if (part.type === 'text') textContent = part.text || '';
                        else if (part.type === 'image_url') {
                            imagesHtml += `<img src="${part.image_url.url}" class="chat-inline-image">`;
                        }
                    }
                }
                chatBox.innerHTML += `
                    <div class="flex justify-end">
                        <div class="message-user bg-blue-600 text-white p-4 max-w-[85%] shadow-sm">
                            ${imagesHtml}${imagesHtml ? '<div style="margin-top:6px">' : ''}${escapeHtml(textContent || '('+t('image_placeholder')+')')}${imagesHtml ? '</div>' : ''}
                        </div>
                    </div>`;
            } else if (msg.role === 'tool') {
                chatBox.innerHTML += `
                    <div class="flex justify-start">
                        <div class="bg-gray-100 border border-dashed border-gray-300 p-3 max-w-[85%] shadow-sm text-xs text-gray-500 rounded-lg">
                            <div class="font-semibold text-gray-600 mb-1">🔧 ${t('tool_return')}: ${escapeHtml(msg.tool_name || '')}</div>
                            <pre class="whitespace-pre-wrap break-words">${escapeHtml(msg.content.length > 500 ? msg.content.slice(0, 500) + '...' : msg.content)}</pre>
                        </div>
                    </div>`;
            } else {
                let toolCallsHtml = '';
                if (msg.tool_calls && msg.tool_calls.length > 0) {
                    const callsList = msg.tool_calls.map(tc =>
                        `<span class="inline-block bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded mr-1 mb-1">🔧 ${escapeHtml(tc.name)}</span>`
                    ).join('');
                    toolCallsHtml = `<div class="mb-2">${callsList}</div>`;
                }
                chatBox.innerHTML += `
                    <div class="flex justify-start">
                        <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700 markdown-body" data-tts-ready="1">
                            ${toolCallsHtml}${msg.content ? marked.parse(msg.content) : '<span class="text-gray-400 text-xs">('+t('tool_calling')+')</span>'}
                        </div>
                    </div>`;
            }
        }
        // 为历史 AI 消息添加朗读按钮
        chatBox.querySelectorAll('[data-tts-ready="1"]').forEach(div => {
            div.removeAttribute('data-tts-ready');
            const ttsBtn = createTtsButton(() => extractTtsTextFromElement(div));
            div.appendChild(ttsBtn);
        });
        // 高亮代码块
        chatBox.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (e) {
        chatBox.innerHTML = `
            <div class="text-xs text-red-400 text-center py-4">${t('history_error')}: ${e.message}</div>`;
    }

    // 切换 session 后立即检查一次 busy 状态
    try {
        const sr = await fetch('/proxy_session_status', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ session_id: sessionId })
        });
        const sd = await sr.json();
        if (sd.busy) {
            setSystemBusyUI(true);
        } else {
            setSystemBusyUI(false);
        }
    } catch(e) {} finally {
        hidePageLoading();
    }
}

// ===== 本机免密登录 =====
async function handleLocalLogin() {
    const nameInput = document.getElementById('username-input');
    const errorDiv = document.getElementById('login-error');
    const localLoginBtn = document.getElementById('local-login-btn');
    const name = nameInput.value.trim();

    errorDiv.classList.add('hidden');

    if (!name) {
        errorDiv.textContent = '请输入用户名';
        errorDiv.classList.remove('hidden');
        nameInput.focus();
        return;
    }

    if (!/^[a-zA-Z0-9_\-\u4e00-\u9fa5]+$/.test(name)) {
        errorDiv.textContent = t('login_error_invalid');
        errorDiv.classList.remove('hidden');
        return;
    }

    localLoginBtn.disabled = true;
    localLoginBtn.textContent = t('login_verifying');
    showPageLoading();

    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 15000);
        const resp = await fetch("/proxy_login", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: name, password: "" }),
            signal: controller.signal
        });
        clearTimeout(timeout);
        let data;
        try { data = await resp.json(); } catch (_) { data = { error: 'Invalid server response' }; }
        if (!resp.ok) {
            errorDiv.textContent = data.detail || data.error || t('login_error_failed');
            errorDiv.classList.remove('hidden');
            return;
        }

        currentUserId = name;
        initSession();

        // Check if we should redirect to another page (e.g. group_chat)
        if (checkRedirectAfterLogin()) return;

        document.getElementById('uid-display').textContent = 'UID: ' + name;
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('chat-screen').style.display = 'flex';
        document.getElementById('user-input').focus();
        loadTools();
        refreshOasisTopics();
        startHistoryPolling();
        switchPage('group');
        // Show setup wizard if LLM not configured
        _checkAndShowSetupWizard();
    } catch (e) {
        if (e.name === 'AbortError') {
            errorDiv.textContent = '连接超时，请确认后端服务已启动后重试';
        } else {
            errorDiv.textContent = t('login_error_network') + ': ' + e.message;
        }
        errorDiv.classList.remove('hidden');
    } finally {
        localLoginBtn.disabled = false;
        localLoginBtn.textContent = t('local_login_btn') || '本机免密登录';
        hidePageLoading();
    }
}

// ===== 登录逻辑 =====
async function handleLogin() {
    const nameInput = document.getElementById('username-input');
    const pwInput = document.getElementById('password-input');
    const errorDiv = document.getElementById('login-error');
    const loginBtn = document.getElementById('login-btn');
    const name = nameInput.value.trim();
    const password = pwInput.value;

    errorDiv.classList.add('hidden');

    if (!name) { nameInput.focus(); return; }
    if (!password) { pwInput.focus(); return; }

    if (!/^[a-zA-Z0-9_\-\u4e00-\u9fa5]+$/.test(name)) {
        errorDiv.textContent = t('login_error_invalid');
        errorDiv.classList.remove('hidden');
        return;
    }

    loginBtn.disabled = true;
    loginBtn.textContent = t('login_verifying');
    showPageLoading();

    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 15000);
        const resp = await fetch("/proxy_login", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: name, password: password }),
            signal: controller.signal
        });
        clearTimeout(timeout);
        let data;
        try { data = await resp.json(); } catch (_) { data = { error: 'Invalid server response' }; }
        if (!resp.ok) {
            errorDiv.textContent = data.detail || data.error || t('login_error_failed');
            errorDiv.classList.remove('hidden');
            return;
        }

        currentUserId = name;
        // Auth is managed by server-side session + cookie, no sessionStorage needed
        initSession();

        // Check if we should redirect to another page (e.g. group_chat)
        if (checkRedirectAfterLogin()) return;

        document.getElementById('uid-display').textContent = 'UID: ' + name;
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('chat-screen').style.display = 'flex';
        document.getElementById('user-input').focus();
        loadTools();
        refreshOasisTopics(); // Load OASIS topics after login
        startHistoryPolling();
        // Default to team page after login
        switchPage('group');
        // Show setup wizard if LLM not configured
        _checkAndShowSetupWizard();
    } catch (e) {
        if (e.name === 'AbortError') {
            errorDiv.textContent = '连接超时，请确认后端服务已启动后重试';
        } else {
            errorDiv.textContent = t('login_error_network') + ': ' + e.message;
        }
        errorDiv.classList.remove('hidden');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = t('login_btn');
        hidePageLoading();
    }
}

// ===================== Settings Modal =====================
// 预定义分组：已知 key 归入对应分组，其余自动归入"其他"
const SETTINGS_GROUPS_ORDERED = [
    { id: 'llm', label: 'settings_group_llm', keys: ['LLM_API_KEY', 'LLM_BASE_URL', 'LLM_MODEL', 'LLM_PROVIDER', 'LLM_VISION_SUPPORT'] },
    { id: 'tts', label: 'settings_group_tts', keys: ['TTS_MODEL', 'TTS_VOICE', 'STT_MODEL'] },
    { id: 'oasis', label: 'settings_group_oasis', keys: ['OASIS_BASE_URL'] },
    { id: 'ports', label: 'settings_group_ports', keys: ['PORT_AGENT', 'PORT_SCHEDULER', 'PORT_OASIS', 'PORT_FRONTEND', 'PORT_BARK'] },
    { id: 'network', label: 'settings_group_network', keys: ['PUBLIC_DOMAIN', 'BARK_PUBLIC_URL'] },
    { id: 'bots', label: 'settings_group_bots', keys: ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_ALLOWED_USERS', 'QQ_APP_ID', 'QQ_BOT_SECRET', 'QQ_BOT_USERNAME'] },
    { id: 'comm', label: 'settings_group_comm', keys: ['OPENAI_STANDARD_MODE'] },
    { id: 'exec', label: 'settings_group_exec', keys: ['ALLOWED_COMMANDS', 'EXEC_TIMEOUT', 'MAX_OUTPUT_LENGTH'] },
    { id: 'security', label: 'settings_group_security', keys: ['INTERNAL_TOKEN'] },
];

const SETTINGS_GROUP_HELP_KEYS = {
    tts: 'settings_help_audio_group',
};

const SETTINGS_FIELD_HELP_KEYS = {
    TTS_MODEL: 'settings_help_tts_model',
    TTS_VOICE: 'settings_help_tts_voice',
    STT_MODEL: 'settings_help_stt_model',
};

let _settingsCache = {};

async function openSettings() {
    const modal = document.getElementById('settings-modal');
    const body = document.getElementById('settings-body');
    modal.style.display = 'flex';
    body.innerHTML = `<div class="settings-loading">${t('loading')}</div>`;
    try {
        const r = await fetch('/proxy_settings_full');
        const data = await r.json();
        if (data.error || !data.settings) throw new Error(data.error || 'unknown');
        _settingsCache = data.settings;
        renderSettings(data.settings);
    } catch (e) {
        body.innerHTML = `<div class="settings-error">${t('settings_load_fail')}: ${e.message}</div>`;
    }
}

function renderSettings(settings) {
    const body = document.getElementById('settings-body');
    let html = `<div class="settings-hint">${t('settings_restart_hint')}</div>`;

    // Tunnel control section
    html += `<div class="settings-group">`;
    html += `<div class="settings-group-title" onclick="this.parentElement.classList.toggle('collapsed')">${t('settings_group_tunnel')} <span class="settings-chevron">▼</span></div>`;
    html += `<div class="settings-group-body">`;
    html += `<div class="settings-field" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">`;
    html += `<span id="tunnel-status-text" style="font-size:13px;color:#888;">⏳ ${t('loading')}...</span>`;
    html += `<button id="tunnel-toggle-btn" onclick="toggleTunnel()" style="padding:4px 14px;border-radius:6px;border:1px solid #444;background:#222;color:#ddd;cursor:pointer;font-size:12px;" disabled>${t('tunnel_start')}</button>`;
    html += `</div>`;
    html += `<div id="tunnel-url-row" style="display:none;margin-top:6px;">`;
    html += `<input id="tunnel-url-input" class="settings-input" type="text" readonly style="font-size:12px;color:#6cf;cursor:pointer;" onclick="this.select();document.execCommand('copy')" />`;
    html += `</div>`;
    html += `</div></div>`;

    // Collect all keys from settings
    const allKeys = Object.keys(settings);
    const usedKeys = new Set();

    // Render predefined groups
    for (const group of SETTINGS_GROUPS_ORDERED) {
        const groupKeys = group.keys.filter(k => {
            usedKeys.add(k); return true;
        });
        if (group.id === 'llm') {
            html += _renderLlmGroup(settings);
        } else {
            html += _renderGroup({
                title: t(group.label),
                help: SETTINGS_GROUP_HELP_KEYS[group.id] ? t(SETTINGS_GROUP_HELP_KEYS[group.id]) : '',
            }, groupKeys, settings);
        }
    }

    // Collect remaining keys not in any group → "其他"
    const otherKeys = allKeys.filter(k => !usedKeys.has(k));
    if (otherKeys.length > 0) {
        html += _renderGroup({ title: t('settings_group_other') }, otherKeys, settings);
    }

    body.innerHTML = html;
    _refreshTunnelStatus();
    _initSettingsLlmGroup(settings);
}

/** 渲染 LLM 配置组（Provider 下拉 + API Key + Base URL + Model 检测下拉） */
function _renderLlmGroup(settings) {
    const curProvider = settings['LLM_PROVIDER'] || '';
    const curKey = settings['LLM_API_KEY'] || '';
    const curUrl = settings['LLM_BASE_URL'] || '';
    const curModel = settings['LLM_MODEL'] || '';
    const curVision = settings['LLM_VISION_SUPPORT'] || '';

    let html = `<div class="settings-group">`;
    html += `<div class="settings-group-title" onclick="this.parentElement.classList.toggle('collapsed')">${t('settings_group_llm')} <span class="settings-chevron">▼</span></div>`;
    html += `<div class="settings-group-body">`;

    // Provider dropdown
    html += `<div class="settings-field">`;
    html += `<label class="settings-label">LLM_PROVIDER</label>`;
    html += `<select class="settings-input" data-key="LLM_PROVIDER" id="settings-llm-provider" onchange="settingsLlmProviderChanged()">`;
    const providers = [
        { val: '', label: '-- 自动推断 --' },
        { val: 'deepseek', label: 'DeepSeek' },
        { val: 'openai', label: 'OpenAI' },
        { val: 'google', label: 'Gemini (Google)' },
        { val: 'anthropic', label: 'Claude (Anthropic)' },
        { val: 'antigravity', label: 'Antigravity (免费·Google One Pro)' },
        { val: 'minimax', label: 'MiniMax' },
        { val: 'ollama', label: 'Ollama (本地)' },
    ];
    for (const p of providers) {
        html += `<option value="${p.val}"${curProvider === p.val ? ' selected' : ''}>${p.label}</option>`;
    }
    // If current provider isn't in the list, add it
    if (curProvider && !providers.some(p => p.val === curProvider)) {
        html += `<option value="${escapeHtml(curProvider)}" selected>${escapeHtml(curProvider)}</option>`;
    }
    html += `</select>`;
    html += `</div>`;

    // API Key
    html += `<div class="settings-field">`;
    html += `<label class="settings-label">LLM_API_KEY</label>`;
    html += `<input class="settings-input" data-key="LLM_API_KEY" id="settings-llm-key" type="password" value="${escapeHtml(curKey)}" placeholder="API Key" autocomplete="off" />`;
    html += `</div>`;

    // Base URL
    html += `<div class="settings-field">`;
    html += `<label class="settings-label">LLM_BASE_URL</label>`;
    html += `<input class="settings-input" data-key="LLM_BASE_URL" id="settings-llm-url" type="text" value="${escapeHtml(curUrl)}" placeholder="https://api.deepseek.com" autocomplete="off" />`;
    html += `</div>`;

    // Model — dropdown + detect button
    html += `<div class="settings-field">`;
    html += `<label class="settings-label">LLM_MODEL</label>`;
    html += `<div style="display:flex;gap:8px;align-items:center;">`;
    html += `<select class="settings-input" data-key="LLM_MODEL" id="settings-llm-model" style="flex:1;">`;
    if (curModel) {
        html += `<option value="${escapeHtml(curModel)}" selected>${escapeHtml(curModel)}</option>`;
    }
    html += `<option value="">（点击"检测模型"获取列表）</option>`;
    html += `</select>`;
    html += `<button id="settings-detect-models-btn" onclick="settingsDetectModels()" style="padding:7px 14px;border-radius:7px;border:none;background:linear-gradient(135deg,#2563eb,#3b82f6);color:#fff;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;">🔍 检测模型</button>`;
    html += `</div>`;
    html += `<div id="settings-detect-status" style="margin-top:4px;font-size:11px;color:#6b7280;"></div>`;
    html += `</div>`;

    // Vision support
    html += `<div class="settings-field">`;
    html += `<label class="settings-label" title="LLM_VISION_SUPPORT">LLM_VISION_SUPPORT</label>`;
    html += `<input class="settings-input" data-key="LLM_VISION_SUPPORT" type="text" value="${escapeHtml(curVision)}" placeholder="留空自动推断" autocomplete="off" />`;
    html += `</div>`;

    html += `</div></div>`;
    return html;
}

/** Provider 切换时自动填充 Base URL */
function settingsLlmProviderChanged() {
    const provider = document.getElementById('settings-llm-provider').value;
    const defaults = _WIZARD_PROVIDER_DEFAULTS[provider];
    if (!defaults) return;

    const urlInput = document.getElementById('settings-llm-url');
    const keyInput = document.getElementById('settings-llm-key');

    // Only auto-fill if field looks like a default/empty
    const curUrl = urlInput.value.trim();
    const isDefaultUrl = !curUrl || Object.values(_WIZARD_PROVIDER_DEFAULTS).some(d => d.base_url === curUrl);
    if (isDefaultUrl && defaults.base_url) {
        urlInput.value = defaults.base_url;
    }

    if (defaults.auto_key) {
        keyInput.value = defaults.auto_key;
        keyInput.type = 'text';
    } else if (keyInput.value === 'sk-antigravity' || keyInput.value === 'ollama') {
        keyInput.value = '';
        keyInput.type = 'password';
    }

    // Reset model dropdown
    const modelSel = document.getElementById('settings-llm-model');
    const curModel = modelSel.value;
    modelSel.innerHTML = '';
    if (curModel) {
        const opt = document.createElement('option');
        opt.value = curModel; opt.textContent = curModel; opt.selected = true;
        modelSel.appendChild(opt);
    }
    const placeholder = document.createElement('option');
    placeholder.value = ''; placeholder.textContent = '（点击"检测模型"获取列表）';
    modelSel.appendChild(placeholder);
    document.getElementById('settings-detect-status').textContent = '';
}

/** 检测模型按钮（复用 wizard 的 discover_models API） */
async function settingsDetectModels() {
    const apiKey = document.getElementById('settings-llm-key').value.trim();
    const baseUrl = document.getElementById('settings-llm-url').value.trim();
    const statusEl = document.getElementById('settings-detect-status');
    const modelSel = document.getElementById('settings-llm-model');
    const detectBtn = document.getElementById('settings-detect-models-btn');
    const provider = document.getElementById('settings-llm-provider').value;

    if (!apiKey) { statusEl.textContent = '⚠️ 请先输入 API Key'; return; }
    if (!baseUrl) { statusEl.textContent = '⚠️ 请先输入 Base URL'; return; }

    const curModel = modelSel.value;
    detectBtn.disabled = true;
    detectBtn.textContent = '⏳ 检测中...';
    statusEl.textContent = '正在连接 API...';

    try {
        const resp = await fetch('/api/discover_models', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey, base_url: baseUrl }),
        });
        const data = await resp.json();

        if (!resp.ok || data.error) {
            statusEl.textContent = '❌ ' + (data.error || '检测失败') + (data.detail ? ': ' + data.detail : '');
            return;
        }

        const models = data.models || [];
        if (models.length === 0) {
            statusEl.textContent = '⚠️ API 返回了空的模型列表';
            return;
        }

        modelSel.innerHTML = '';
        for (const mid of models) {
            const opt = document.createElement('option');
            opt.value = mid; opt.textContent = mid;
            modelSel.appendChild(opt);
        }
        statusEl.textContent = `✅ 检测到 ${models.length} 个可用模型`;

        // Auto-select: prefer current model, then smart defaults
        if (curModel && models.includes(curModel)) {
            modelSel.value = curModel;
        } else {
            const preferredModels = {
                deepseek: ['deepseek-chat', 'deepseek-coder'],
                openai: ['gpt-4o', 'gpt-4.1', 'gpt-4-turbo'],
                google: ['gemini-2.5-pro', 'gemini-2.5-flash'],
                anthropic: ['claude-sonnet-4-20250514', 'claude-3-5-sonnet-20241022'],
                antigravity: ['gemini-2.5-pro', 'claude-sonnet-4-20250514', 'gpt-4o'],
                minimax: ['MiniMax-M2.7', 'MiniMax-M2.7-highspeed'],
            };
            const preferred = preferredModels[provider] || [];
            for (const pm of preferred) {
                if (models.includes(pm)) { modelSel.value = pm; break; }
            }
        }
    } catch (e) {
        statusEl.textContent = '❌ 网络错误: ' + e.message;
    } finally {
        detectBtn.disabled = false;
        detectBtn.textContent = '🔍 检测模型';
    }
}

/** Settings LLM 组初始化：根据当前 provider 设定 key 输入类型等 */
function _initSettingsLlmGroup(settings) {
    const provider = settings['LLM_PROVIDER'] || '';
    const keyInput = document.getElementById('settings-llm-key');
    if (keyInput && (provider === 'antigravity' || provider === 'ollama')) {
        keyInput.type = 'text';
    }
}

function _renderGroup(groupMeta, keys, settings) {
    const title = typeof groupMeta === 'string' ? groupMeta : groupMeta.title;
    const groupHelp = typeof groupMeta === 'string' ? '' : (groupMeta.help || '');
    let html = `<div class="settings-group">`;
    html += `<div class="settings-group-title" onclick="this.parentElement.classList.toggle('collapsed')">${title} <span class="settings-chevron">▼</span></div>`;
    html += `<div class="settings-group-body">`;
    if (groupHelp) {
        html += `<div style="margin-bottom:10px;font-size:12px;line-height:1.5;color:#9ca3af;">${escapeHtml(groupHelp)}</div>`;
    }
    for (const key of keys) {
        const val = settings[key] || '';
        const isPassword = /KEY|TOKEN|SECRET|PASSWORD/i.test(key);
        const helpKey = SETTINGS_FIELD_HELP_KEYS[key];
        const helpText = helpKey ? t(helpKey) : '';
        html += `<div class="settings-field">`;
        html += `<label class="settings-label" title="${key}">${key}</label>`;
        html += `<input class="settings-input" data-key="${key}" type="${isPassword ? 'password' : 'text'}" value="${escapeHtml(val)}" placeholder="${key}" autocomplete="off" />`;
        if (helpText) {
            html += `<div style="margin-top:5px;font-size:11px;line-height:1.5;color:#9ca3af;">${escapeHtml(helpText)}</div>`;
        }
        html += `</div>`;
    }
    html += `</div></div>`;
    return html;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML.replace(/"/g, '&quot;');
}

function closeSettings() {
    document.getElementById('settings-modal').style.display = 'none';
}

async function saveSettings() {
    const inputs = document.querySelectorAll('#settings-body .settings-input[data-key]');
    const updates = {};
    inputs.forEach(inp => {
        const key = inp.dataset.key;
        if (!key) return;
        const val = (inp.tagName === 'SELECT' ? inp.value : inp.value.trim());
        const orig = _settingsCache[key] || '';
        if (val !== orig) {
            updates[key] = val;
        }
    });
    if (Object.keys(updates).length === 0) {
        closeSettings();
        return;
    }
    try {
        const r = await fetch('/proxy_settings_full', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ settings: updates }),
        });
        const data = await r.json();
        if (data.status === 'success') {
            let msg = t('settings_saved');
            if (data.updated?.length) {
                msg += '\n' + data.updated.join(', ');
            }
            appendMessage(msg, false);
            // 更新缓存
            for (const k of (data.updated || [])) {
                const inp = document.querySelector(`#settings-body .settings-input[data-key="${k}"]`);
                if (inp) _settingsCache[k] = (inp.tagName === 'SELECT' ? inp.value : inp.value.trim());
            }
        } else {
            alert(t('settings_save_fail'));
        }
    } catch (e) {
        alert(t('settings_save_fail') + ': ' + e.message);
    }
}

async function restartServices() {
    if (!confirm(t('settings_restart_confirm'))) return;
    const btn = document.getElementById('restart-btn');
    if (btn) {
        btn.disabled = true;
        btn.textContent = t('settings_restarting');
    }
    try {
        const r = await fetch('/proxy_restart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });
        const data = await r.json();
        if (data.status === 'success') {
            appendMessage(t('settings_restart_ok'), false);
            closeSettings();
            setTimeout(() => location.reload(), 15000);
        } else {
            alert(t('settings_restart_fail') + ': ' + (data.detail || data.error || ''));
            if (btn) { btn.disabled = false; btn.textContent = t('settings_restart_btn'); }
        }
    } catch (e) {
        // 网络断开说明服务已在重启中，属于正常现象
        appendMessage(t('settings_restart_ok'), false);
        closeSettings();
        setTimeout(() => location.reload(), 15000);
    }
}

// ===== Public Toggle (header shortcut for tunnel) =====
async function _syncPublicToggle() {
    const toggle = document.getElementById('public-toggle');
    const label = document.getElementById('public-toggle-label');
    const urlRow = document.getElementById('public-url-row');
    const urlInput = document.getElementById('public-url-input');
    if (!toggle) return;
    try {
        const r = await fetch('/proxy_tunnel/status');
        const data = await r.json();
        toggle.checked = !!data.running;
        toggle.disabled = false;
        label.textContent = '🌐';
        if (data.running && data.public_domain && urlRow && urlInput) {
            urlRow.style.display = '';
            urlInput.value = data.public_domain;
            urlInput.title = t('tunnel_url_hint');
        } else if (urlRow) {
            urlRow.style.display = 'none';
        }
    } catch (e) {
        toggle.disabled = true;
    }
}

async function handlePublicToggle(checked) {
    const toggle = document.getElementById('public-toggle');
    const urlRow = document.getElementById('public-url-row');
    toggle.disabled = true;
    if (urlRow) urlRow.style.display = 'none';
    try {
        const endpoint = checked ? '/proxy_tunnel/start' : '/proxy_tunnel/stop';
        await fetch(endpoint, { method: 'POST' });
        // Poll for status update
        const maxPolls = checked ? 30 : 10;
        const interval = checked ? 2000 : 1000;
        for (let i = 0; i < maxPolls; i++) {
            await new Promise(r => setTimeout(r, interval));
            const sr = await fetch('/proxy_tunnel/status');
            const sd = await sr.json();
            if (checked && sd.running) break;
            if (!checked && !sd.running) break;
        }
    } catch (e) { /* ignore */ }
    await _syncPublicToggle();
    // Also refresh the tunnel section inside settings body if present
    if (typeof _refreshTunnelStatus === 'function') _refreshTunnelStatus();
}

// ===== Tunnel Control =====
let _tunnelRunning = false;

async function _refreshTunnelStatus() {
    try {
        const r = await fetch('/proxy_tunnel/status');
        const data = await r.json();
        _tunnelRunning = data.running;
        const statusEl = document.getElementById('tunnel-status-text');
        const btn = document.getElementById('tunnel-toggle-btn');
        const urlRow = document.getElementById('tunnel-url-row');
        const urlInput = document.getElementById('tunnel-url-input');
        if (!statusEl) return;

        if (data.running) {
            statusEl.textContent = t('tunnel_running');
            statusEl.style.color = '#6cf';
            btn.textContent = t('tunnel_stop');
            btn.style.background = '#622';
            btn.style.borderColor = '#a44';
            btn.disabled = false;
            if (data.public_domain) {
                urlRow.style.display = 'block';
                urlInput.value = data.public_domain;
                urlInput.title = t('tunnel_url_hint');
            } else {
                urlRow.style.display = 'none';
            }
        } else {
            statusEl.textContent = t('tunnel_stopped');
            statusEl.style.color = '#888';
            btn.textContent = t('tunnel_start');
            btn.style.background = '#222';
            btn.style.borderColor = '#444';
            btn.disabled = false;
            urlRow.style.display = 'none';
        }
    } catch (e) {
        const statusEl = document.getElementById('tunnel-status-text');
        if (statusEl) {
            statusEl.textContent = '⚠️ ' + e.message;
            statusEl.style.color = '#f88';
        }
    }
}

async function toggleTunnel() {
    const btn = document.getElementById('tunnel-toggle-btn');
    btn.disabled = true;

    if (_tunnelRunning) {
        btn.textContent = t('tunnel_stopping');
        try {
            await fetch('/proxy_tunnel/stop', { method: 'POST' });
        } catch (e) { /* ignore */ }
        // Poll until stopped
        for (let i = 0; i < 10; i++) {
            await new Promise(r => setTimeout(r, 1000));
            await _refreshTunnelStatus();
            if (!_tunnelRunning) break;
        }
    } else {
        btn.textContent = t('tunnel_starting');
        try {
            await fetch('/proxy_tunnel/start', { method: 'POST' });
        } catch (e) { /* ignore */ }
        // Poll until running with URL
        for (let i = 0; i < 30; i++) {
            await new Promise(r => setTimeout(r, 2000));
            await _refreshTunnelStatus();
            if (_tunnelRunning) break;
        }
    }
    btn.disabled = false;
}

// Reset UI to login screen without clearing backend session
function showLoginScreen() {
    currentUserId = null;
    currentSessionId = null;
    stopHistoryPolling();
    sessionStorage.removeItem('sessionId');
    document.getElementById('chat-screen').style.display = 'none';
    document.getElementById('login-screen').style.display = 'flex';
    document.getElementById('username-input').value = '';
    document.getElementById('password-input').value = '';
    document.getElementById('login-error').classList.add('hidden');
    document.getElementById('username-input').focus();
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = `
        <div class="flex justify-start">
            <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700">
                ${t('welcome_message')}
            </div>
        </div>`;
    // Stop OASIS polling
    stopOasisPolling();
}

// User-initiated logout: clear backend session + reset UI
function handleLogout() {
    fetch("/proxy_logout", { method: 'POST' });
    showLoginScreen();
}

// ===== Tool Panel 逻辑 =====
let toolPanelOpen = false;
let allTools = [];
let enabledToolSet = new Set();

function toggleToolPanel() {
    const panel = document.getElementById('tool-panel');
    const icon = document.getElementById('tool-toggle-icon');
    toolPanelOpen = !toolPanelOpen;
    if (toolPanelOpen) {
        panel.classList.remove('collapsed');
        panel.classList.add('expanded');
        icon.classList.add('open');
    } else {
        panel.classList.remove('expanded');
        panel.classList.add('collapsed');
        icon.classList.remove('open');
    }
}

function updateToolCount() {
    const toolCount = document.getElementById('tool-count');
    toolCount.textContent = '(' + enabledToolSet.size + '/' + allTools.length + ')';
}

function toggleTool(name, tagEl) {
    if (enabledToolSet.has(name)) {
        enabledToolSet.delete(name);
        tagEl.classList.remove('enabled');
        tagEl.classList.add('disabled');
    } else {
        enabledToolSet.add(name);
        tagEl.classList.remove('disabled');
        tagEl.classList.add('enabled');
    }
    updateToolCount();
}

function getEnabledTools() {
    if (enabledToolSet.size === allTools.length) return null;
    return Array.from(enabledToolSet);
}

async function loadTools() {
    try {
        const resp = await fetch('/proxy_tools');
        if (!resp.ok) return;
        const data = await resp.json();
        const tools = data.tools || [];
        const toolList = document.getElementById('tool-list');
        const wrapper = document.getElementById('tool-panel-wrapper');

        if (tools.length === 0) {
            wrapper.style.display = 'none';
            return;
        }

        allTools = tools;
        enabledToolSet = new Set(tools.map(t => t.name));
        toolList.innerHTML = '';
        tools.forEach(t => {
            const tag = document.createElement('span');
            tag.className = 'tool-tag enabled';
            tag.title = t.description || '';
            tag.textContent = t.name;
            tag.onclick = () => toggleTool(t.name, tag);
            toolList.appendChild(tag);
        });
        updateToolCount();
        wrapper.style.display = 'block';
    } catch (e) {
        console.warn('Failed to load tools:', e);
    }
}

// ── Redirect helper: after login, check if we should redirect to another page ──
function checkRedirectAfterLogin() {
    const urlParams = new URLSearchParams(window.location.search);
    const redirect = urlParams.get('redirect');
    if (redirect === 'group_chat') {
        window.location.href = '/mobile/group_chat';
        return true;
    }
    return false;
}

// Session check
(async function checkSession() {
    // 初始化语言
    document.documentElement.lang = currentLang;
    applyTranslations();

    // 首先检查 URL 中是否有登录 Token (magic link)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const userFromUrl = urlParams.get('user');
    
    if (token && userFromUrl) {
        // 尝试自动登录 - 使用 proxy_login_with_token API
        try {
            const resp = await fetch('/proxy_login_with_token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userFromUrl, token: token })
            });
            const data = await resp.json();
            if (resp.ok && data.ok) {
                // Token 登录成功
                currentUserId = userFromUrl;
                initSession();
                document.getElementById('uid-display').textContent = 'UID: ' + userFromUrl;
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('chat-screen').style.display = 'flex';
                // Check if we should redirect to another page after login
                if (checkRedirectAfterLogin()) return;
                loadTools();
                refreshOasisTopics();
                startHistoryPolling();
                _syncPublicToggle();
                switchPage('group');
                _checkAndShowSetupWizard();
                // 移除 URL 中的 token 参数（安全原因）
                if (window.history.replaceState) {
                    window.history.replaceState({}, document.title, window.location.pathname);
                }
                return;
            } else {
                console.warn('Token login failed:', data.error || 'Unknown error');
            }
        } catch (e) {
            console.warn('Token auto-login failed:', e);
        }
        // Token 登录失败，清除参数继续检查其他登录方式
        if (window.history.replaceState) {
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }

    // Always check backend session (cookie-based), no sessionStorage gate
    try {
        const resp = await fetch('/proxy_check_session');
        if (resp.ok) {
            const data = await resp.json();
            if (data.valid && data.user_id) {
                currentUserId = data.user_id;
                initSession();
                // Check if we should redirect to another page after login
                if (checkRedirectAfterLogin()) return;
                document.getElementById('uid-display').textContent = 'UID: ' + data.user_id;
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('chat-screen').style.display = 'flex';
                loadTools();
                refreshOasisTopics();
                startHistoryPolling();
                _syncPublicToggle();
                // Default to team page after auto-login
                switchPage('group');
                _checkAndShowSetupWizard();
                return;
            }
        }
    } catch (e) {
        // Network error (e.g. server restarting), fall through to login page
    }
})();

// Login input handlers
document.getElementById('username-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); document.getElementById('password-input').focus(); }
});
document.getElementById('password-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); handleLogin(); }
});

// ===================== First-Run Setup Wizard =====================

const _WIZARD_PROVIDER_DEFAULTS = {
    deepseek:    { base_url: 'https://api.deepseek.com',           key_hint: 'sk-...' },
    openai:      { base_url: 'https://api.openai.com',             key_hint: 'sk-...' },
    google:      { base_url: 'https://generativelanguage.googleapis.com/v1beta', key_hint: 'AIza...' },
    anthropic:   { base_url: 'https://api.anthropic.com',          key_hint: 'sk-ant-...' },
    antigravity: { base_url: 'http://127.0.0.1:8045',              key_hint: 'sk-antigravity', auto_key: 'sk-antigravity' },
    minimax:     { base_url: 'https://api.minimaxi.com',           key_hint: 'sk-api-...' },
    ollama:      { base_url: 'http://127.0.0.1:11434',             key_hint: 'ollama', auto_key: 'ollama' },
    custom:      { base_url: '',                                    key_hint: 'your-api-key' },
};

function _checkAndShowSetupWizard() {
    // Check if LLM is configured — if not, show the wizard
    const status = window._setupStatus;
    if (status && !status.llm_configured) {
        _showSetupWizard(status);
    } else if (!status) {
        // Fallback: fetch setup status now
        fetch('/api/setup_status').then(r => r.json()).then(d => {
            window._setupStatus = d;
            if (!d.llm_configured) _showSetupWizard(d);
        }).catch(() => {});
    }
}

/**
 * Public function called by the LLM warning banner.
 * Always opens the Setup Wizard (banner is only visible when LLM is not configured).
 * Fetches fresh setup status to update button availability.
 */
function openSetupWizard() {
    fetch('/api/setup_status').then(r => r.json()).then(d => {
        window._setupStatus = d;
        _showSetupWizard(d);
    }).catch(() => {
        // Even on error, show the wizard with whatever status we have
        _showSetupWizard(window._setupStatus || {});
    });
}

function _showSetupWizard(status) {
    const modal = document.getElementById('setup-wizard-modal');
    if (!modal) return;
    modal.style.display = 'flex';

    // Show auto-detect buttons — always visible, grayed out when unavailable
    const openclawBtn = document.getElementById('wizard-import-openclaw-btn');
    const antigravityBtn = document.getElementById('wizard-use-antigravity-btn');
    const openclawSub = document.getElementById('wizard-openclaw-subtitle');
    const antigravitySub = document.getElementById('wizard-antigravity-subtitle');

    if (openclawBtn) {
        const available = status && status.openclaw_installed;
        openclawBtn.disabled = !available;
        openclawBtn.style.opacity = available ? '1' : '0.45';
        openclawBtn.style.cursor = available ? 'pointer' : 'not-allowed';
        if (openclawSub) openclawSub.textContent = available
            ? '自动读取已配置的 API Key、模型和 Provider'
            : '⚠️ 未检测到 OpenClaw（未安装）';
    }
    if (antigravityBtn) {
        const available = status && status.antigravity_running;
        antigravityBtn.disabled = !available;
        antigravityBtn.style.opacity = available ? '1' : '0.45';
        antigravityBtn.style.cursor = available ? 'pointer' : 'not-allowed';
        if (antigravitySub) antigravitySub.textContent = available
            ? '通过 Google One Pro 会员免费访问 Claude / Gemini / GPT'
            : '⚠️ Antigravity 未运行（未启动或无法连接）';
    }

    // Pre-fill if already partially configured (e.g. user already set some values before)
    if (status && status.current_base_url) {
        const urlInput = document.getElementById('wizard-base-url');
        if (urlInput && !urlInput.value) urlInput.value = status.current_base_url;
    }
    if (status && status.current_provider) {
        const providerSel = document.getElementById('wizard-provider');
        if (providerSel && !providerSel.value) {
            for (const opt of providerSel.options) {
                if (opt.value === status.current_provider) {
                    providerSel.value = status.current_provider;
                    break;
                }
            }
        }
    }
}

async function wizardImportOpenClaw() {
    const btn = document.getElementById('wizard-import-openclaw-btn');
    const statusEl = document.getElementById('wizard-auto-detect-status');
    const errorEl = document.getElementById('wizard-error');

    btn.disabled = true;
    btn.style.opacity = '0.6';
    statusEl.textContent = '正在从 OpenClaw 读取配置...';
    errorEl.style.display = 'none';

    try {
        const resp = await fetch('/api/import_openclaw_config');
        const data = await resp.json();

        if (!resp.ok || data.error) {
            statusEl.textContent = '⚠️ ' + (data.error || '导入失败');
            return;
        }

        // Fill in wizard fields
        const providerSel = document.getElementById('wizard-provider');
        const keyInput = document.getElementById('wizard-api-key');
        const urlInput = document.getElementById('wizard-base-url');

        // Map OpenClaw provider to wizard provider value
        if (data.provider && providerSel) {
            const providerMap = { openai: 'openai', deepseek: 'deepseek', google: 'google', anthropic: 'anthropic', antigravity: 'antigravity', minimax: 'minimax', ollama: 'ollama' };
            providerSel.value = providerMap[data.provider] || '';
        }
        if (data.api_key && keyInput) {
            keyInput.value = data.api_key;
            keyInput.type = 'text';
        }
        if (data.base_url && urlInput) urlInput.value = data.base_url;

        statusEl.textContent = '✅ 已从 OpenClaw 导入配置' + (data.model ? `（模型: ${data.model}）` : '') + '，点击"检测模型"确认';

        // Auto-trigger model detection
        setTimeout(() => wizardDetectModels(), 300);

    } catch (e) {
        statusEl.textContent = '⚠️ 网络错误: ' + e.message;
    } finally {
        btn.disabled = false;
        btn.style.opacity = '1';
    }
}

async function wizardUseAntigravity() {
    const btn = document.getElementById('wizard-use-antigravity-btn');
    const statusEl = document.getElementById('wizard-auto-detect-status');

    btn.disabled = true;
    btn.style.opacity = '0.6';
    statusEl.textContent = '正在配置 Antigravity...';

    // Set provider to antigravity, which auto-fills key and URL
    const providerSel = document.getElementById('wizard-provider');
    if (providerSel) {
        providerSel.value = 'antigravity';
        wizardProviderChanged();
    }

    statusEl.textContent = '✅ 已选择 Antigravity，正在检测可用模型...';

    // Auto-trigger model detection
    setTimeout(() => {
        wizardDetectModels();
        btn.disabled = false;
        btn.style.opacity = '1';
    }, 300);
}

function wizardProviderChanged() {
    const provider = document.getElementById('wizard-provider').value;
    const defaults = _WIZARD_PROVIDER_DEFAULTS[provider];
    if (!defaults) return;

    const urlInput = document.getElementById('wizard-base-url');
    const keyInput = document.getElementById('wizard-api-key');

    if (defaults.base_url) urlInput.value = defaults.base_url;
    keyInput.placeholder = defaults.key_hint || 'API Key';

    if (defaults.auto_key) {
        keyInput.value = defaults.auto_key;
        keyInput.type = 'text';
    } else {
        if (keyInput.value === 'sk-antigravity' || keyInput.value === 'ollama') keyInput.value = '';
        keyInput.type = 'password';
    }

    // Reset model dropdown
    const modelSel = document.getElementById('wizard-model');
    modelSel.innerHTML = '<option value="">先点击"检测模型"</option>';
    modelSel.disabled = true;
    document.getElementById('wizard-detect-status').textContent = '';
    document.getElementById('wizard-error').style.display = 'none';
}

async function wizardDetectModels() {
    const apiKey = document.getElementById('wizard-api-key').value.trim();
    const baseUrl = document.getElementById('wizard-base-url').value.trim();
    const statusEl = document.getElementById('wizard-detect-status');
    const errorEl = document.getElementById('wizard-error');
    const modelSel = document.getElementById('wizard-model');
    const detectBtn = document.getElementById('wizard-detect-btn');

    errorEl.style.display = 'none';

    if (!apiKey) {
        errorEl.textContent = '请先输入 API Key';
        errorEl.style.display = 'block';
        return;
    }
    if (!baseUrl) {
        errorEl.textContent = '请先输入 Base URL';
        errorEl.style.display = 'block';
        return;
    }

    detectBtn.disabled = true;
    detectBtn.textContent = '⏳ 检测中...';
    statusEl.textContent = '正在连接 API 并获取模型列表...';

    try {
        const resp = await fetch('/api/discover_models', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey, base_url: baseUrl }),
        });
        const data = await resp.json();

        if (!resp.ok || data.error) {
            errorEl.textContent = data.error || '检测失败';
            if (data.detail) errorEl.textContent += ': ' + data.detail;
            errorEl.style.display = 'block';
            statusEl.textContent = '';
            return;
        }

        const models = data.models || [];
        if (models.length === 0) {
            statusEl.textContent = '⚠️ API 返回了空的模型列表';
            return;
        }

        modelSel.innerHTML = '';
        for (const mid of models) {
            const opt = document.createElement('option');
            opt.value = mid;
            opt.textContent = mid;
            modelSel.appendChild(opt);
        }
        modelSel.disabled = false;
        statusEl.textContent = `✅ 检测到 ${models.length} 个可用模型`;

        // Auto-select smart defaults
        const provider = document.getElementById('wizard-provider').value;
        const preferredModels = {
            deepseek: ['deepseek-chat', 'deepseek-coder'],
            openai: ['gpt-4o', 'gpt-4.1', 'gpt-4-turbo'],
            google: ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-pro'],
            anthropic: ['claude-sonnet-4-20250514', 'claude-3-5-sonnet-20241022'],
            antigravity: ['gemini-2.5-pro', 'claude-sonnet-4-20250514', 'gpt-4o'],
            minimax: ['MiniMax-M2.7', 'MiniMax-M2.7-highspeed'],
        };
        const preferred = preferredModels[provider] || [];
        for (const pm of preferred) {
            if (models.includes(pm)) {
                modelSel.value = pm;
                break;
            }
        }
    } catch (e) {
        errorEl.textContent = '网络错误: ' + e.message;
        errorEl.style.display = 'block';
    } finally {
        detectBtn.disabled = false;
        detectBtn.textContent = '🔍 检测模型';
    }
}

async function wizardSave() {
    const provider = document.getElementById('wizard-provider').value;
    const apiKey = document.getElementById('wizard-api-key').value.trim();
    const baseUrl = document.getElementById('wizard-base-url').value.trim();
    const model = document.getElementById('wizard-model').value;
    const errorEl = document.getElementById('wizard-error');
    const saveBtn = document.getElementById('wizard-save-btn');

    errorEl.style.display = 'none';

    if (!apiKey) {
        errorEl.textContent = '请输入 API Key';
        errorEl.style.display = 'block';
        return;
    }
    if (!baseUrl) {
        errorEl.textContent = '请输入 Base URL';
        errorEl.style.display = 'block';
        return;
    }
    if (!model) {
        errorEl.textContent = '请选择一个模型（先点击"检测模型"）';
        errorEl.style.display = 'block';
        return;
    }

    saveBtn.disabled = true;
    saveBtn.textContent = '⏳ 保存中...';

    try {
        const settings = {
            LLM_API_KEY: apiKey,
            LLM_BASE_URL: baseUrl,
            LLM_MODEL: model,
        };
        if (provider && provider !== 'custom') {
            settings.LLM_PROVIDER = provider;
        }

        const resp = await fetch('/proxy_settings_full', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ settings }),
        });
        const data = await resp.json();

        if (data.status === 'success') {
            // Hide wizard
            document.getElementById('setup-wizard-modal').style.display = 'none';
            // Hide warning banner
            document.getElementById('llm-warning-banner').style.display = 'none';
            // Show success message
            appendMessage('✅ LLM 配置已保存！正在重启服务...', false);
            // Restart services
            fetch('/proxy_restart', { method: 'POST', headers: { 'Content-Type': 'application/json' } }).catch(() => {});
            // Update cached status
            if (window._setupStatus) window._setupStatus.llm_configured = true;
        } else {
            errorEl.textContent = '保存失败: ' + (data.error || '未知错误');
            errorEl.style.display = 'block';
        }
    } catch (e) {
        errorEl.textContent = '网络错误: ' + e.message;
        errorEl.style.display = 'block';
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = '保存并开始';
    }
}

function wizardSkip() {
    document.getElementById('setup-wizard-modal').style.display = 'none';
}

function copyMagicPrompt(el) {
    const code = el.querySelector('code');
    if (code) {
        navigator.clipboard.writeText(code.textContent).then(() => {
            const origBg = el.style.background;
            el.style.background = '#dcfce7';
            setTimeout(() => { el.style.background = origBg || '#fff'; }, 800);
        }).catch(() => {});
    }
}

// ===== 聊天逻辑 =====
const chatBox = document.getElementById('chat-box');
const inputField = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const cancelBtn = document.getElementById('cancel-btn');
const busyBtn = document.getElementById('busy-btn');
const refreshChatBtn = document.getElementById('refresh-chat-btn');
let _hasUnreadSystemMsg = 0;  // 0=无未读, 1=有未读

function showNewMsgBanner() {
    if (_hasUnreadSystemMsg) return;
    _hasUnreadSystemMsg = 1;
    refreshChatBtn.classList.add('has-new');
}

function hideNewMsgBanner() {
    _hasUnreadSystemMsg = 0;
    refreshChatBtn.classList.remove('has-new');
}

function handleNewMsgRefresh() {
    hideNewMsgBanner();
    switchToSession(currentSessionId, true);
}

// 按钮三态：idle(发送) / streaming(终止) / busy(系统占用中)
function setStreamingUI(streaming) {
    if (streaming) {
        sendBtn.style.display = 'none';
        cancelBtn.style.display = 'inline-block';
        busyBtn.style.display = 'none';
        inputField.disabled = true;
        cancelTargetSessionId = currentSessionId;
    } else {
        sendBtn.style.display = 'inline-block';
        cancelBtn.style.display = 'none';
        busyBtn.style.display = 'none';
        sendBtn.disabled = false;
        inputField.disabled = false;
        cancelTargetSessionId = null;
    }
}

function setSystemBusyUI(busy) {
    if (busy) {
        sendBtn.style.display = 'none';
        cancelBtn.style.display = 'inline-block';
        busyBtn.style.display = 'none';
        inputField.disabled = true;
        cancelTargetSessionId = currentSessionId;
    } else {
        sendBtn.style.display = 'inline-block';
        cancelBtn.style.display = 'none';
        busyBtn.style.display = 'none';
        sendBtn.disabled = false;
        inputField.disabled = false;
        cancelTargetSessionId = null;
    }
}

async function handleCancel() {
    const targetSession = cancelTargetSessionId || currentSessionId;
    if (currentAbortController) {
        currentAbortController.abort();
        currentAbortController = null;
    }
    try {
        await fetch("/proxy_cancel", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ session_id: targetSession })
        });
    } catch(e) { /* ignore */ }
    // 恢复 UI（无论是用户流式还是系统调用被终止）
    setStreamingUI(false);
    setSystemBusyUI(false);
}

// ===== TTS 朗读功能 =====
let currentTtsAudio = null;
let currentTtsBtn = null;

function stripMarkdownForTTS(md) {
    // 移除代码块（含内容）
    let text = md.replace(/```[\s\S]*?```/g, '('+t('code_omitted')+')');
    // 移除行内代码
    text = text.replace(/`[^`]+`/g, '');
    // 移除图片
    text = text.replace(/!\[.*?\]\(.*?\)/g, '');
    // 移除链接，保留文字
    text = text.replace(/\[([^\]]+)\]\(.*?\)/g, '$1');
    // 移除标题标记
    text = text.replace(/^#{1,6}\s+/gm, '');
    // 移除粗体/斜体标记
    text = text.replace(/\*{1,3}([^*]+)\*{1,3}/g, '$1');
    // 移除工具调用提示行
    text = text.replace(/.*🔧.*调用工具.*\n?/g, '');
    text = text.replace(/.*✅.*工具执行完成.*\n?/g, '');
    // 清理多余空行
    text = text.replace(/\n{3,}/g, '\n\n').trim();
    return text;
}

function extractTtsTextFromElement(element) {
    if (!element) return '';
    const clone = element.cloneNode(true);
    clone.querySelectorAll('.tts-btn').forEach(btn => btn.remove());
    return (clone.innerText || clone.textContent || '').trim();
}

function stopTtsPlayback() {
    if (currentTtsAudio) {
        currentTtsAudio.pause();
        currentTtsAudio.src = '';
        currentTtsAudio = null;
    }
    if (currentTtsBtn) {
        currentTtsBtn.classList.remove('playing', 'loading');
        currentTtsBtn.querySelector('.tts-label').textContent = t('tts_read');
        currentTtsBtn = null;
    }
}

async function handleTTS(btn, text) {
    // 如果点击的是正在播放的按钮，则停止
    if (btn === currentTtsBtn && currentTtsAudio) {
        stopTtsPlayback();
        return;
    }
    // 停止上一个播放
    stopTtsPlayback();

    const cleanText = stripMarkdownForTTS(text);
    if (!cleanText) return;

    currentTtsBtn = btn;
    btn.classList.add('loading');
    btn.querySelector('.tts-label').textContent = t('tts_loading');

    try {
        const resp = await fetch('/proxy_tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: cleanText })
        });
        if (!resp.ok) throw new Error(t('tts_request_failed'));

        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        currentTtsAudio = audio;

        btn.classList.remove('loading');
        btn.classList.add('playing');
        btn.querySelector('.tts-label').textContent = t('tts_stop');

        audio.onended = () => {
            URL.revokeObjectURL(url);
            stopTtsPlayback();
        };
        audio.onerror = () => {
            URL.revokeObjectURL(url);
            stopTtsPlayback();
        };
        audio.play();
    } catch (e) {
        console.error('TTS error:', e);
        stopTtsPlayback();
    }
}

function createTtsButton(textRef) {
    const btn = document.createElement('div');
    btn.className = 'tts-btn';
    btn.innerHTML = `
        <span class="tts-spinner"></span>
        <svg class="tts-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
        </svg>
        <span class="tts-label">${t('tts_read')}</span>`;
    btn.onclick = () => handleTTS(btn, textRef());
    return btn;
}

function appendMessage(content, isUser = false, images = [], fileNames = [], audioNames = [], workflowNames = []) {
    const wrapper = document.createElement('div');
    wrapper.className = `flex ${isUser ? 'justify-end' : 'justify-start'} animate-in fade-in duration-300`;
    const div = document.createElement('div');
    div.className = `p-4 max-w-[85%] shadow-sm ${isUser ? 'bg-blue-600 text-white message-user' : 'bg-white border text-gray-800 message-agent'}`;
    if (isUser) {
        let extraHtml = '';
        if (images && images.length > 0) {
            extraHtml += images.map(src => `<img src="${src}" class="chat-inline-image">`).join('');
        }
        if (fileNames && fileNames.length > 0) {
            extraHtml += fileNames.map(n => `<div class="chat-file-tag">📄 ${escapeHtml(n)}</div>`).join('');
        }
        if (audioNames && audioNames.length > 0) {
            extraHtml += audioNames.map(n => `<div class="chat-audio-tag">🎤 ${escapeHtml(n)}</div>`).join('');
        }
        if (workflowNames && workflowNames.length > 0) {
            extraHtml += workflowNames.map(n => `<div class="chat-workflow-tag">📋 ${escapeHtml(n)}</div>`).join('');
        }
        if (extraHtml) {
            div.innerHTML = extraHtml + (content ? '<div style="margin-top:6px">' + escapeHtml(content) + '</div>' : '');
        } else {
            div.innerText = content;
        }
    } else {
        div.className += " markdown-body";
        div.innerHTML = marked.parse(content);
        div.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
        // AI 消息添加朗读按钮（content 非空时）
        if (content) {
            const ttsBtn = createTtsButton(() => extractTtsTextFromElement(div));
            div.appendChild(ttsBtn);
        }
    }
    wrapper.appendChild(div);
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
}

function showTyping() {
    const wrapper = document.createElement('div');
    wrapper.id = 'typing-indicator';
    wrapper.className = 'flex justify-start';
    wrapper.innerHTML = `
        <div class="message-agent bg-white border p-4 flex space-x-2 items-center shadow-sm">
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        </div>`;
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function handleSend() {
    const text = inputField.value.trim();
    if (!text && pendingImages.length === 0 && pendingFiles.length === 0 && pendingAudios.length === 0 && pendingWorkflows.length === 0) return;
    if (sendBtn.disabled) return;

    // Guard: if in OpenClaw mode but no agent selected, prompt user
    if (_ocChatMode === 'openclaw' && !_ocSelectedAgent) {
        alert(t('oc_select_agent_hint'));
        return;
    }

    // Stop recording if active
    if (isRecording) stopRecording();

    // Capture images, files, audios, workflows before clearing
    const imagesToSend = pendingImages.map(img => img.base64);
    const imagePreviewSrcs = [...imagesToSend];
    const filesToSend = pendingFiles.map(f => ({ name: f.name, content: f.content, type: f.type }));
    const fileNames = pendingFiles.map(f => f.name);
    const audiosToSend = pendingAudios.map(a => ({ base64: a.base64, name: a.name, format: a.format }));
    const audioNames = pendingAudios.map(a => a.name);
    const workflowsToSend = pendingWorkflows.map(w => ({ name: w.name, team: w.team, displayName: w.displayName, yaml: w.yaml }));
    const workflowNames = pendingWorkflows.map(w => w.displayName);

    const label = text || (imagePreviewSrcs.length ? '('+t('image_placeholder')+')' : audioNames.length ? '('+t('audio_placeholder')+')' : workflowNames.length ? '(workflow)' : '('+t('file_placeholder')+')');
    appendMessage(label, true, imagePreviewSrcs, fileNames, audioNames, workflowNames);
    inputField.value = '';
    inputField.style.height = 'auto';
    pendingImages = [];
    pendingFiles = [];
    pendingAudios = [];
    pendingWorkflows = [];
    renderImagePreviews();
    renderFilePreviews();
    renderAudioPreviews();
    renderWorkflowPreviews();
    sendBtn.disabled = true;
    showTyping();

    currentAbortController = new AbortController();
    setStreamingUI(true);

    let agentDiv = null;
    let fullText = '';

    try {
        // --- 构造 workflow 前缀（隐藏在消息中发送给后端） ---
        let workflowPrefix = '';
        for (const wf of workflowsToSend) {
            workflowPrefix += `【oasis workflow, use it now】\n` +
                `Team Name: ${wf.team || '(non-team)'}\n` +
                `YAML Name: ${wf.name}\n` +
                (wf.yaml ? `---\n${wf.yaml}\n---\n` : '');
        }
        const fullText_to_send = workflowPrefix + text;

        // --- 构造 OpenAI 格式的 content parts ---
        const contentParts = [];
        if (fullText_to_send) {
            contentParts.push({ type: 'text', text: fullText_to_send });
        }
        // 图片 → image_url
        for (const img of imagesToSend) {
            contentParts.push({ type: 'image_url', image_url: { url: img } });
        }
        // 音频 → input_audio
        for (const audio of audiosToSend) {
            contentParts.push({
                type: 'input_audio',
                input_audio: { data: audio.base64, format: audio.format || 'webm' }
            });
        }
        // 文件 → file
        for (const f of filesToSend) {
            const fileData = f.content.startsWith('data:') ? f.content : 'data:application/octet-stream;base64,' + f.content;
            contentParts.push({
                type: 'file',
                file: { filename: f.name, file_data: fileData }
            });
        }

        // 如果只有纯文本，content 用字符串；否则用 parts 数组
        let msgContent;
        if (contentParts.length === 1 && contentParts[0].type === 'text') {
            msgContent = contentParts[0].text;
        } else if (contentParts.length > 0) {
            msgContent = contentParts;
        } else {
            msgContent = '(空消息)';
        }

        // --- 构造 OpenAI /v1/chat/completions 请求 ---
        const messages = [];
        // Inject expert persona as system message only on the first message in this session
        if (selectedPersona && selectedPersona.persona && personaInjectedSession !== currentSessionId) {
            messages.push({ role: 'system', content: `[Expert Persona: ${selectedPersona.name}]\n${selectedPersona.persona}` });
            personaInjectedSession = currentSessionId;
        }
        messages.push({ role: 'user', content: msgContent });

        // ── OpenClaw chat mode: route to /proxy_openclaw_chat with agent:<name> model ──
        const isOpenClawChat = (_ocChatMode === 'openclaw' && _ocSelectedAgent);
        const openaiPayload = isOpenClawChat ? {
            model: 'agent:' + _ocSelectedAgent.name,
            messages: messages,
            stream: true,
        } : {
            model: 'teambot',
            messages: messages,
            stream: true,
            session_id: currentSessionId,
            enabled_tools: getEnabledTools(),
        };
        const chatEndpoint = isOpenClawChat ? '/proxy_openclaw_chat' : '/v1/chat/completions';

        const response = await fetch(chatEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(openaiPayload),
            signal: currentAbortController.signal
        });

        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) typingIndicator.remove();

        if (response.status === 401) {
            appendMessage(t('login_expired'), false);
            showLoginScreen();
            return;
        }
        if (!response.ok) throw new Error("Agent error");

        agentDiv = appendMessage('', false);

        // --- 解析 OpenAI SSE 流式响应（支持分段渲染） ---
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let allSegmentTexts = [];  // 记录所有段落的文本

        // 辅助函数：封存当前文本气泡，添加朗读按钮
        function sealCurrentBubble() {
            if (fullText && agentDiv) {
                agentDiv.innerHTML = marked.parse(fullText);
                agentDiv.querySelectorAll('pre code').forEach(b => hljs.highlightElement(b));
                const ttsBtn = createTtsButton(() => extractTtsTextFromElement(agentDiv));
                agentDiv.appendChild(ttsBtn);
                allSegmentTexts.push(fullText);
            }
        }

        // 辅助函数：创建新的 AI 文本气泡
        function startNewBubble() {
            fullText = '';
            agentDiv = appendMessage('', false);
        }

        // 辅助函数：创建工具调用指示区
        function createToolIndicator(toolName, type) {
            if (type === 'end') {
                // 查找最后一个同名且仍在运行的 indicator 并更新
                const allRunning = chatBox.querySelectorAll(`.stream-tool-indicator[data-tool-name="${CSS.escape(toolName)}"] .stream-tool-running`);
                const last = allRunning.length ? allRunning[allRunning.length - 1] : null;
                if (last) {
                    last.textContent = '✅';
                    last.classList.remove('stream-tool-running');
                    last.classList.add('stream-tool-done');
                }
                return;
            }
            const w = document.createElement('div');
            w.className = 'flex justify-start animate-in fade-in duration-200';
            const d = document.createElement('div');
            d.className = 'stream-tool-indicator';
            d.dataset.toolName = toolName;
            d.innerHTML = `<span class="stream-tool-icon">🔧</span> <span class="stream-tool-name">${escapeHtml(toolName)}</span> <span class="stream-tool-status stream-tool-running">…</span>`;
            w.appendChild(d);
            chatBox.appendChild(w);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                const data = line.slice(6).trim();
                if (data === '[DONE]') continue;

                try {
                    const chunk = JSON.parse(data);
                    const delta = chunk.choices && chunk.choices[0] && chunk.choices[0].delta;
                    if (!delta) continue;

                    // --- 处理结构化 meta 事件 ---
                    if (delta.meta) {
                        const m = delta.meta;
                        if (m.type === 'tools_start') {
                            // LLM 回复结束，即将调工具 → 封存当前气泡
                            sealCurrentBubble();
                        } else if (m.type === 'tool_start') {
                            createToolIndicator(m.name, 'start');
                        } else if (m.type === 'tool_end') {
                            createToolIndicator(m.name, 'end');
                        } else if (m.type === 'tools_end') {
                            // 所有工具执行完毕（可选：加分隔符）
                        } else if (m.type === 'ai_start') {
                            // 新一轮 LLM 开始 → 创建新文本气泡
                            startNewBubble();
                        }
                        continue;
                    }

                    // --- 处理文本内容 ---
                    if (delta.content) {
                        fullText += delta.content;
                        agentDiv.innerHTML = marked.parse(fullText);
                        agentDiv.querySelectorAll('pre code').forEach((block) => {
                            if (!block.dataset.highlighted) {
                                hljs.highlightElement(block);
                                block.dataset.highlighted = 'true';
                            }
                        });
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }
                } catch(e) {
                    // 跳过无法解析的 chunk
                }
            }
        }

        // 流式结束：封存最后一个气泡
        if (fullText) {
            agentDiv.innerHTML = marked.parse(fullText);
            agentDiv.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
            const ttsBtn = createTtsButton(() => extractTtsTextFromElement(agentDiv));
            agentDiv.appendChild(ttsBtn);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        if (!fullText && allSegmentTexts.length === 0) {
            agentDiv.innerHTML = `<span class="text-gray-400">${t('no_response')}</span>`;
        }

        // After agent response, refresh OASIS topics (in case a new discussion was started)
        setTimeout(() => refreshOasisTopics(), 1000);

    } catch (error) {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) typingIndicator.remove();
        if (error.name === 'AbortError') {
            if (agentDiv) {
                fullText += '\n\n' + t('thinking_stopped');
                agentDiv.innerHTML = marked.parse(fullText);
            } else {
                appendMessage(t('thinking_stopped'), false);
            }
        } else {
            appendMessage(t('agent_error') + ': ' + error.message, false);
        }
    } finally {
        currentAbortController = null;
        setStreamingUI(false);
        hideNewMsgBanner();
    }
}

inputField.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});
inputField.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
});
inputField.addEventListener('paste', handlePasteImage);

// ================================================================
// ===== Add Workflow 功能 =====
// ================================================================
let pendingWorkflows = [];  // [{name: 'xxx'}, ...]

function renderWorkflowPreviews() {
    const area = document.getElementById('workflow-preview-area');
    if (!pendingWorkflows.length) { area.style.display = 'none'; return; }
    area.style.display = 'flex';
    area.innerHTML = pendingWorkflows.map((wf, i) =>
        `<span class="workflow-tag">📋 Workflow: ${escapeHtml(wf.displayName)}<span class="wf-remove" onclick="removeWorkflow(${i})">&times;</span></span>`
    ).join('');
}

function removeWorkflow(idx) {
    pendingWorkflows.splice(idx, 1);
    renderWorkflowPreviews();
}

async function showWorkflowPopup() {
    try {
        // Load team list and global workflows in parallel
        const [teamsResp, globalResp] = await Promise.all([
            fetch('/teams'),
            fetch('/proxy_visual/load-layouts'),
        ]);
        const teamsData = await teamsResp.json();
        const globalLayouts = await globalResp.json();
        const teams = teamsData.teams || [];

        // Load team workflows in parallel
        const teamResults = await Promise.all(teams.map(async (teamName) => {
            try {
                const r = await fetch('/proxy_visual/load-layouts?team=' + encodeURIComponent(teamName));
                const layouts = await r.json();
                return { team: teamName, layouts: layouts || [] };
            } catch { return { team: teamName, layouts: [] }; }
        }));

        // Build grouped data: [{group, team, layouts}]
        const groups = [];
        if (globalLayouts.length) groups.push({ group: '(公共)', team: '', layouts: globalLayouts });
        teamResults.forEach((tr) => {
            groups.push({ group: tr.team, team: tr.team, layouts: tr.layouts });
        });

        if (!groups.length) { alert(t('wf_no_workflows')); return; }

        const overlay = document.createElement('div');
        overlay.className = 'orch-modal-overlay';
        overlay.id = 'wf-popup-overlay';
        overlay.innerHTML = `
            <div class="orch-modal" style="min-width:360px;max-width:460px;">
                <h3>${t('wf_popup_title')}</h3>
                <div id="wf-select-list" style="max-height:360px;overflow-y:auto;"></div>
                <div class="orch-modal-btns">
                    <button id="wf-cancel-btn" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">${t('wf_cancel')}</button>
                    <button id="wf-confirm-btn" disabled style="padding:6px 14px;border-radius:6px;border:none;background:#7c3aed;color:white;cursor:pointer;font-size:12px;opacity:0.5;">${t('wf_confirm')}</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        let selectedName = null;
        let selectedTeam = '';
        overlay.querySelector('#wf-cancel-btn').addEventListener('click', () => overlay.remove());
        overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

        const listEl = overlay.querySelector('#wf-select-list');
        for (const grp of groups) {
            // Group header
            const header = document.createElement('div');
            header.style.cssText = 'padding:6px 8px;font-size:12px;font-weight:600;color:#6b7280;border-bottom:1px solid #e5e7eb;margin-top:6px;display:flex;align-items:center;gap:4px;';
            header.innerHTML = `<span style="font-size:14px;">${grp.team ? '👥' : '🌐'}</span>${escapeHtml(grp.group)}`;
            listEl.appendChild(header);

            if (!grp.layouts.length) {
                const emptyRow = document.createElement('div');
                emptyRow.className = 'orch-session-item';
                emptyRow.style.cssText = 'padding:8px 12px 8px 24px;border-radius:8px;cursor:default;opacity:0.65;margin-bottom:2px;display:flex;align-items:center;gap:8px;font-size:12px;color:#6b7280;';
                emptyRow.innerHTML = `<span style="font-size:14px;">📭</span><span style="flex:1;">${escapeHtml(t('wf_team_no_layouts'))}</span>`;
                listEl.appendChild(emptyRow);
                continue;
            }
            for (const name of grp.layouts) {
                const item = document.createElement('div');
                item.className = 'orch-session-item';
                item.style.cssText = 'padding:8px 12px 8px 24px;border-radius:8px;cursor:pointer;border:1px solid transparent;margin-bottom:2px;display:flex;align-items:center;gap:8px;transition:all 0.15s;';
                item.innerHTML = `<span style="font-size:14px;">📋</span><span style="flex:1;font-size:13px;color:#374151;">${escapeHtml(name)}</span>`;
                const teamVal = grp.team;
                item.addEventListener('click', () => {
                    listEl.querySelectorAll('.orch-session-item').forEach(el => {
                        el.style.background = '';
                        el.style.borderColor = 'transparent';
                    });
                    item.style.background = '#f5f3ff';
                    item.style.borderColor = '#c4b5fd';
                    selectedName = name;
                    selectedTeam = teamVal;
                    const btn = overlay.querySelector('#wf-confirm-btn');
                    btn.disabled = false;
                    btn.style.opacity = '1';
                });
                item.addEventListener('dblclick', async () => {
                    selectedName = name;
                    selectedTeam = teamVal;
                    await addWorkflowToContext(selectedName, selectedTeam);
                    overlay.remove();
                });
                listEl.appendChild(item);
            }
        }

        overlay.querySelector('#wf-confirm-btn').addEventListener('click', async () => {
            if (selectedName) {
                await addWorkflowToContext(selectedName, selectedTeam);
                overlay.remove();
            }
        });
    } catch(e) {
        console.error('Failed to load workflows:', e);
    }
}

async function addWorkflowToContext(name, team) {
    team = team || '';
    const displayName = team ? `${team}/${name}` : name;
    // Avoid duplicate
    if (pendingWorkflows.some(w => w.displayName === displayName)) return;

    // Load raw YAML content for this workflow (team-scoped)
    let yamlText = '';
    try {
        const teamQ = team ? '?team=' + encodeURIComponent(team) : '';
        const r = await fetch(`/proxy_visual/load-yaml-raw/${encodeURIComponent(name)}${teamQ}`);
        const data = await r.json();
        yamlText = data.yaml || '';
    } catch(e) {
        console.warn('Failed to load workflow YAML:', e);
    }

    pendingWorkflows.push({ name: name, team: team, displayName: displayName, yaml: yamlText });
    renderWorkflowPreviews();
    inputField.focus();
}

// ================================================================
// ===== Persona (Expert Persona) 功能 =====
// ================================================================
var selectedPersona = null;  // { name, tag, persona, source }
var personaInjectedSession = null;  // session ID where persona was already injected (avoid repeated prompt)

// ── OpenClaw Chat Mode State ──
var _ocChatMode = 'internal';       // 'internal' | 'openclaw'
var _ocSelectedAgent = null;        // { name: string } — currently selected OpenClaw agent
var _ocAgentsCache = [];            // cached list of OpenClaw agents from /proxy_openclaw_sessions
var _ocAvailable = false;           // whether OpenClaw is available (detected at init)

function getLocalizedExpertName(expert) {
    if (!expert) return '';
    const isZh = (typeof currentLang !== 'undefined' && currentLang === 'zh-CN');
    return (isZh ? (expert.name_zh || expert.name) : (expert.name_en || expert.name)) || expert.tag || '';
}

function createPersonaSelection(expert) {
    if (!expert) return null;
    return {
        name: expert.name,
        name_zh: expert.name_zh,
        name_en: expert.name_en,
        tag: expert.tag,
        persona: expert.persona,
        source: expert.source,
    };
}

function renderPersonaPreview() {
    const area = document.getElementById('persona-preview-area');
    const btn = document.getElementById('persona-add-btn');
    if (!area) return;
    if (!selectedPersona) {
        area.style.display = 'none';
        if (btn) btn.classList.remove('active');
        return;
    }
    area.style.display = 'flex';
    if (btn) btn.classList.add('active');
    const preview = selectedPersona.persona.length > 60 ? selectedPersona.persona.slice(0, 60) + '…' : selectedPersona.persona;
    const displayName = getLocalizedExpertName(selectedPersona);
    area.innerHTML = `<span class="persona-tag" title="${escapeHtml(selectedPersona.persona)}">🎭 ${escapeHtml(displayName)}: ${escapeHtml(preview)}<span class="persona-remove" onclick="clearPersona()">&times;</span></span>`;
}

function clearPersona() {
    selectedPersona = null;
    personaInjectedSession = null;
    renderPersonaPreview();
}

async function showPersonaPopup() {
    try {
        const r = await fetch('/proxy_oasis/experts');
        const data = await r.json();
        const experts = data.experts || [];
        if (!experts.length) { alert(t('persona_no_experts')); return; }

        const overlay = document.createElement('div');
        overlay.className = 'orch-modal-overlay';
        overlay.id = 'persona-popup-overlay';
        overlay.innerHTML = `
            <div class="orch-modal" style="min-width:360px;max-width:480px;">
                <h3>${t('persona_popup_title')}</h3>
                <div id="persona-search-box" style="margin-bottom:8px;">
                    <input type="text" id="persona-search-input" placeholder="${escapeHtml(t('persona_search_placeholder'))}" style="width:100%;padding:6px 10px;border:1px solid #d1d5db;border-radius:8px;font-size:12px;outline:none;" />
                </div>
                <div id="persona-select-list" style="max-height:360px;overflow-y:auto;"></div>
                <div class="orch-modal-btns">
                    <button id="persona-cancel-btn" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">${t('persona_cancel')}</button>
                    <button id="persona-confirm-btn" disabled style="padding:6px 14px;border-radius:6px;border:none;background:#0891b2;color:white;cursor:pointer;font-size:12px;opacity:0.5;">${t('persona_confirm')}</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        let chosen = null;
        overlay.querySelector('#persona-cancel-btn').addEventListener('click', () => overlay.remove());
        overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

        const listEl = overlay.querySelector('#persona-select-list');

        function renderExpertList(filteredExperts) {
            listEl.innerHTML = '';
            const groups = [];
            const pub = filteredExperts.filter(e => e.source === 'public');
            const agn = filteredExperts.filter(e => e.source === 'agency');
            const cus = filteredExperts.filter(e => e.source === 'custom');
            if (pub.length) groups.push({ label: t('persona_public'), items: pub });
            if (agn.length) groups.push({ label: t('persona_agency'), items: agn });
            if (cus.length) groups.push({ label: t('persona_custom'), items: cus });

            for (const group of groups) {
                const header = document.createElement('div');
                header.className = 'persona-expert-group';
                header.textContent = `${group.label} (${group.items.length})`;
                listEl.appendChild(header);

                for (const expert of group.items) {
                    const item = document.createElement('div');
                    item.className = 'persona-expert-item';
                    if (chosen && chosen.tag === expert.tag) {
                        item.classList.add('selected');
                    }
                    const personaPreview = expert.persona.length > 80 ? expert.persona.slice(0, 80) + '…' : expert.persona;
                    const displayName = getLocalizedExpertName(expert);
                    const desc = expert.description ? `<div style="font-size:10px;color:#9ca3af;margin-top:1px;">${escapeHtml(expert.description)}</div>` : '';
                    item.innerHTML = `
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:16px;">🎭</span>
                            <div style="flex:1;min-width:0;">
                                <div style="font-size:13px;color:#374151;font-weight:600;">${escapeHtml(displayName)} <span style="font-size:10px;color:#9ca3af;font-weight:400;">${escapeHtml(expert.tag)}</span></div>
                                <div style="font-size:11px;color:#6b7280;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(personaPreview)}</div>
                                ${desc}
                            </div>
                        </div>
                    `;
                    item.addEventListener('click', () => {
                        listEl.querySelectorAll('.persona-expert-item').forEach(el => el.classList.remove('selected'));
                        item.classList.add('selected');
                        chosen = expert;
                        const btn = overlay.querySelector('#persona-confirm-btn');
                        btn.disabled = false;
                        btn.style.opacity = '1';
                    });
                    item.addEventListener('dblclick', () => {
                        chosen = expert;
                        selectedPersona = createPersonaSelection(chosen);
                        personaInjectedSession = null;  // Reset so persona is injected in next send
                        renderPersonaPreview();
                        overlay.remove();
                    });
                    listEl.appendChild(item);
                }
            }

            if (!filteredExperts.length) {
                listEl.innerHTML = `<div style="text-align:center;color:#9ca3af;padding:20px;font-size:12px;">${escapeHtml(t('persona_no_match'))}</div>`;
            }
        }

        renderExpertList(experts);

        // Search filter
        const searchInput = overlay.querySelector('#persona-search-input');
        searchInput.addEventListener('input', () => {
            const q = searchInput.value.trim().toLowerCase();
            if (!q) { renderExpertList(experts); return; }
            const filtered = experts.filter(e =>
                (e.name || '').toLowerCase().includes(q) ||
                (e.name_zh || '').toLowerCase().includes(q) ||
                (e.name_en || '').toLowerCase().includes(q) ||
                e.tag.toLowerCase().includes(q) ||
                (e.persona || '').toLowerCase().includes(q) ||
                (e.description || '').toLowerCase().includes(q) ||
                (e.category || '').toLowerCase().includes(q)
            );
            renderExpertList(filtered);
        });
        setTimeout(() => searchInput.focus(), 100);

        overlay.querySelector('#persona-confirm-btn').addEventListener('click', () => {
            if (chosen) {
                selectedPersona = createPersonaSelection(chosen);
                personaInjectedSession = null;  // Reset so persona is injected in next send
                renderPersonaPreview();
                overlay.remove();
            }
        });
    } catch(e) {
        console.error('Failed to load experts:', e);
    }
}

// ================================================================
// ===== OASIS 讨论面板逻辑 =====
// ================================================================

let currentPage = 'group'; // 'chat' or 'group' or 'orchestrate'
let oasisPanelOpen = false;
let oasisCurrentTopicId = null;
let oasisPollingTimer = null;
let oasisStreamReader = null;
let oasisTownModeEnabled = localStorage.getItem('oasisTownModeEnabled') === '1';
let oasisTownAudioEnabled = localStorage.getItem('oasisTownAudioEnabled') === '1';
let oasisTownMountedTopicId = null;
let oasisManualPostSubmitting = false;
let oasisHumanReplySubmitting = false;
let _oasisExpertsCache = null;
let _overviewDetailCache = null;

// BroadcastChannel for cross-tab OASIS data sharing
const oasisBroadcast = (typeof BroadcastChannel !== 'undefined')
    ? new BroadcastChannel('oasis-data-sync')
    : null;

// Listen for requests from other tabs (e.g. group_chat_mobile)
if (oasisBroadcast) {
    oasisBroadcast.onmessage = (e) => {
        if (e.data.type === 'request-refresh') {
            // Another tab is asking us to push fresh data
            refreshOasisTopics();
        }
    };
}

// Expert avatar mapping
const expertAvatars = {
    [t('oasis_expert_creative')]: { cls: 'expert-creative', icon: '💡' },
    [t('oasis_expert_critical')]: { cls: 'expert-critical', icon: '🔍' },
    '批判专家': { cls: 'expert-critical', icon: '🔍' },
    'Critical Expert': { cls: 'expert-critical', icon: '🔍' },
    'Critical Thinker': { cls: 'expert-critical', icon: '🔍' },
    [t('oasis_expert_data')]: { cls: 'expert-data', icon: '📊' },
    [t('oasis_expert_synthesis')]: { cls: 'expert-synthesis', icon: '🎯' },
};

function getExpertAvatar(name) {
    return expertAvatars[name] || { cls: 'expert-default', icon: '🤖' };
}

function getStatusBadge(status) {
    const map = {
        'pending': { cls: 'oasis-status-pending', text: t('oasis_status_pending') },
        'discussing': { cls: 'oasis-status-discussing', text: t('oasis_status_discussing') },
        'concluded': { cls: 'oasis-status-concluded', text: t('oasis_status_concluded') },
        'error': { cls: 'oasis-status-error', text: t('oasis_status_error') },
        'cancelled': { cls: 'oasis-status-error', text: t('oasis_status_cancelled') },
    };
    return map[status] || { cls: 'oasis-status-pending', text: status };
}

function getOasisTownTrackSrc() {
    const hour = new Date().getHours();
    if (hour < 12) return '/static/assets/audio/town-morning.mp3';
    if (hour < 18) return '/static/assets/audio/town-afternoon.mp3';
    return '/static/assets/audio/town-evening.mp3';
}

function updateOasisTownAudioButton() {
    const btn = document.getElementById('oasis-town-audio-btn');
    if (!btn) return;
    btn.textContent = oasisTownAudioEnabled ? '♪ ON' : '♪ OFF';
    btn.classList.toggle('is-on', oasisTownAudioEnabled);
    btn.classList.toggle('is-off', !oasisTownAudioEnabled);
}

function destroyOasisTownRuntime() {
    try {
        if (window.OasisTown && typeof window.OasisTown.destroy === 'function') {
            window.OasisTown.destroy();
        }
    } catch (err) {
        console.warn('[OASIS] Failed to destroy town runtime:', err);
    }
    oasisTownMountedTopicId = null;
    const canvas = document.getElementById('oasis-town-canvas');
    if (canvas) canvas.innerHTML = '';
}

function syncOasisTownRuntime(detail) {
    ensureOasisTownPlacement();
    const canvas = document.getElementById('oasis-town-canvas');
    if (!oasisTownModeEnabled || !detail || !canvas) {
        destroyOasisTownRuntime();
        return;
    }
    if (!window.OasisTown || typeof window.OasisTown.mount !== 'function') {
        console.warn('[OASIS] Town bundle is not ready');
        return;
    }
    if (oasisTownMountedTopicId !== detail.topic_id) {
        window.OasisTown.mount(canvas, detail);
        oasisTownMountedTopicId = detail.topic_id;
        return;
    }
    if (typeof window.OasisTown.update === 'function') {
        window.OasisTown.update(detail);
    }
}

function isOasisTownHostedInChat() {
    return oasisTownModeEnabled && currentPage === 'chat';
}

function ensureOasisPanelOpen() {
    if (!oasisPanelOpen) {
        toggleOasisPanel();
    }
}

function ensureOasisTownPlacement() {
    const stage = document.getElementById('oasis-town-stage');
    const composer = document.getElementById('oasis-town-composer');
    const chatHost = document.getElementById('oasis-chat-town-host');
    const detailHost = document.getElementById('oasis-detail-town-host');
    const panel = document.getElementById('oasis-panel');
    const chatPage = document.getElementById('page-chat');
    const hostInChat = isOasisTownHostedInChat();
    const target = hostInChat ? chatHost : detailHost;
    if (panel) panel.classList.toggle('oasis-town-chat-mode', hostInChat);
    if (chatPage) chatPage.classList.toggle('oasis-town-active', hostInChat);
    if (target && stage && stage.parentElement !== target) target.appendChild(stage);
    if (target && composer && composer.parentElement !== target) target.appendChild(composer);
}

function renderOasisTownIdleState() {
    const stageQuestionEl = document.getElementById('oasis-town-stage-question');
    if (stageQuestionEl) {
        stageQuestionEl.textContent = currentLang === 'zh-CN'
            ? '在这里输入一个新话题，直接把专家们叫到广场里。'
            : 'Type a new idea here to call the experts into the plaza.';
    }
    const metaEl = document.getElementById('oasis-town-stage-meta');
    if (metaEl) {
        metaEl.innerHTML = `
            <span class="oasis-stage-chip">${currentLang === 'zh-CN' ? '🟡 未选中运行中的讨论' : '🟡 No live discussion selected'}</span>
            <span class="oasis-stage-chip">${currentLang === 'zh-CN' ? '✍️ 发送即可开启新话题' : '✍️ Submit to start a topic'}</span>
        `;
    }
    const stripEl = document.getElementById('oasis-resident-strip');
    if (stripEl) {
        stripEl.innerHTML = `<div class="oasis-resident-empty">${
            currentLang === 'zh-CN'
                ? '广场现在空着。左侧输入会新开一个 OASIS 讨论，并把详细发言放到右侧。'
                : 'The plaza is idle. Submitting from the left starts a fresh OASIS thread on the right.'
        }</div>`;
    }
    destroyOasisTownRuntime();
    updateOasisChatTownHud(null);
}

function updateOasisChatTownHud(detail) {
    const copyEl = document.getElementById('oasis-chat-town-search-copy');
    const residentEl = document.getElementById('oasis-chat-town-stat-residents');
    const postsEl = document.getElementById('oasis-chat-town-stat-posts');
    const hideBtn = document.getElementById('oasis-chat-town-hide-btn');
    if (hideBtn) {
        const hidden = document.getElementById('oasis-chat-town-shell')?.classList.contains('hud-hidden');
        hideBtn.textContent = hidden ? 'SHOW UI' : 'HIDE UI';
    }
    if (!copyEl || !residentEl || !postsEl) return;

    const participants = detail ? collectOasisParticipants(detail) : [];
    const postCount = detail && detail.posts ? detail.posts.length : 0;
    const liveCount = detail && (detail.status === 'discussing' || detail.status === 'pending')
        ? participants.length
        : 0;

    residentEl.textContent = String(liveCount);
    postsEl.textContent = String(postCount);
    copyEl.textContent = detail && detail.question
        ? `${currentLang === 'zh-CN'
            ? (detail.status === 'concluded' ? '已归档话题' : '实时话题')
            : (detail.status === 'concluded' ? 'Archived thread' : 'Live thread')}: ${detail.question}`
        : (currentLang === 'zh-CN'
            ? 'Idle plaza. 从左侧输入一句话，直接开启新的 OASIS 讨论。'
            : 'Idle plaza. Start a fresh OASIS discussion from the town composer.');
}

function toggleOasisTownHudVisibility() {
    const shell = document.getElementById('oasis-chat-town-shell');
    if (!shell) return;
    shell.classList.toggle('hud-hidden');
    updateOasisChatTownHud(_overviewDetailCache && _overviewDetailCache.topic_id === oasisCurrentTopicId ? _overviewDetailCache : null);
}

function applyOasisTownMode() {
    const panel = document.getElementById('oasis-panel');
    const btn = document.getElementById('oasis-town-mode-btn');
    if (panel) panel.classList.toggle('oasis-town-mode', oasisTownModeEnabled);
    if (btn) {
        btn.textContent = oasisTownModeEnabled ? '🏘️ ON' : '🏘️ OFF';
        btn.classList.toggle('is-active', oasisTownModeEnabled);
    }
    if (!oasisTownModeEnabled) {
        destroyOasisTownRuntime();
    } else if (currentPage === 'chat') {
        ensureOasisPanelOpen();
    }
    ensureOasisTownPlacement();
    if (oasisTownModeEnabled && _overviewDetailCache && oasisCurrentTopicId) {
        syncOasisTownRuntime(_overviewDetailCache);
        updateOasisTownComposer(_overviewDetailCache);
        updateOasisChatTownHud(_overviewDetailCache);
    } else if (oasisTownModeEnabled) {
        renderOasisTownIdleState();
        updateOasisTownComposer(null);
        updateOasisChatTownHud(null);
    }
    syncOasisTownAudioState(!oasisTownModeEnabled || !oasisPanelOpen);
}

function toggleOasisTownMode() {
    oasisTownModeEnabled = !oasisTownModeEnabled;
    localStorage.setItem('oasisTownModeEnabled', oasisTownModeEnabled ? '1' : '0');
    applyOasisTownMode();
}

function syncOasisTownAudioState(forcePause = false) {
    const audio = document.getElementById('oasis-town-bgm');
    if (!audio) return;
    const src = getOasisTownTrackSrc();
    if (audio.getAttribute('src') !== src) {
        audio.setAttribute('src', src);
    }
    audio.volume = 0.22;
    updateOasisTownAudioButton();
    if (forcePause || !oasisTownModeEnabled || !oasisTownAudioEnabled) {
        audio.pause();
        return;
    }
    audio.play().catch((err) => {
        console.warn('[OASIS] Failed to play town audio:', err);
        audio.pause();
        oasisTownAudioEnabled = false;
        localStorage.setItem('oasisTownAudioEnabled', '0');
        updateOasisTownAudioButton();
    });
}

function toggleOasisTownAudio() {
    oasisTownAudioEnabled = !oasisTownAudioEnabled;
    localStorage.setItem('oasisTownAudioEnabled', oasisTownAudioEnabled ? '1' : '0');
    syncOasisTownAudioState(!oasisTownAudioEnabled);
}

function formatTime(ts) {
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString(currentLang === 'zh-CN' ? 'zh-CN' : 'en-US', { hour: '2-digit', minute: '2-digit' });
}

function toggleOasisPanel() {
    const panel = document.getElementById('oasis-panel');
    oasisPanelOpen = !oasisPanelOpen;
    if (oasisPanelOpen) {
        panel.classList.remove('collapsed-panel');
        panel.classList.remove('mobile-open');
        syncOasisTownAudioState();
        if (oasisTownModeEnabled && _overviewDetailCache && oasisCurrentTopicId) {
            syncOasisTownRuntime(_overviewDetailCache);
        }
        refreshOasisTopics();
    } else {
        panel.classList.add('collapsed-panel');
        panel.classList.remove('mobile-open');
        syncOasisTownAudioState(true);
        destroyOasisTownRuntime();
        stopOasisPolling();
    }
}

function toggleOasisMobile() {
    const panel = document.getElementById('oasis-panel');
    if (panel.classList.contains('mobile-open')) {
        panel.classList.remove('mobile-open');
        syncOasisTownAudioState(true);
        destroyOasisTownRuntime();
        stopOasisPolling();
    } else {
        panel.classList.remove('collapsed-panel');
        panel.classList.add('mobile-open');
        syncOasisTownAudioState();
        refreshOasisTopics();
    }
}

updateOasisTownAudioButton();
applyOasisTownMode();

// ── Hamburger menu (tab-bar left ☰ button) ──
function toggleHamburgerMenu() {
    const panel = document.getElementById('hamburger-panel');
    if (!panel) return;
    if (panel.style.display === 'none' || !panel.style.display) {
        // Sync UID display
        const uidSrc = document.getElementById('uid-display');
        const uidDst = document.getElementById('hamburger-uid');
        if (uidSrc && uidDst) uidDst.textContent = uidSrc.textContent || '—';
        panel.style.display = 'block';
        // Close on outside click
        setTimeout(() => document.addEventListener('click', _closeHamburgerOutside, { once: true }), 0);
    } else {
        panel.style.display = 'none';
    }
}
function closeHamburgerMenu() {
    const panel = document.getElementById('hamburger-panel');
    if (panel) panel.style.display = 'none';
}
function _closeHamburgerOutside(e) {
    const wrapper = document.querySelector('.hamburger-menu-wrapper');
    if (wrapper && !wrapper.contains(e.target)) closeHamburgerMenu();
}

function toggleMobileMenu() {
    const dd = document.getElementById('mobile-menu-dropdown');
    if (dd.style.display === 'none') {
        dd.style.display = 'block';
        // close when tapping outside
        setTimeout(() => document.addEventListener('click', closeMobileMenuOutside, { once: true }), 0);
    } else {
        dd.style.display = 'none';
    }
}
function closeMobileMenu() {
    document.getElementById('mobile-menu-dropdown').style.display = 'none';
}
function closeMobileMenuOutside(e) {
    const wrapper = document.querySelector('.mobile-menu-wrapper');
    if (!wrapper.contains(e.target)) closeMobileMenu();
}

function stopOasisPolling() {
    if (oasisPollingTimer) {
        clearInterval(oasisPollingTimer);
        oasisPollingTimer = null;
    }
    if (oasisStreamReader) {
        oasisStreamReader.cancel();
        oasisStreamReader = null;
    }
}

async function refreshOasisTopics() {
    try {
        const resp = await fetch('/proxy_oasis/topics');
        console.log('[OASIS] Topics response status:', resp.status);
        if (!resp.ok) {
            console.error('[OASIS] Failed to fetch topics:', resp.status);
            return;
        }
        const topics = await resp.json();
        console.log('[OASIS] Topics data:', topics);
        renderTopicList(topics);
        // Broadcast to other tabs (group_chat_mobile etc.)
        if (oasisBroadcast) {
            oasisBroadcast.postMessage({ type: 'topics', data: topics });
        }
    } catch (e) {
        console.error('[OASIS] Failed to load topics:', e);
    }
}

function renderTopicList(topics) {
    const container = document.getElementById('oasis-topic-list');
    const countEl = document.getElementById('oasis-topic-count');
    countEl.textContent = topics.length + ' ' + t('oasis_topics_count');

    if (topics.length === 0) {
        container.innerHTML = `
            <div class="oasis-topic-list-empty">
                <div class="oasis-empty-town">🏘️</div>
                <p>${t('oasis_no_topics')}</p>
                <p class="oasis-empty-subtitle">${t('oasis_start_hint')}</p>
            </div>`;
        return;
    }

    // Sort: discussing first, then by created_at desc
    topics.sort((a, b) => {
        if (a.status === 'discussing' && b.status !== 'discussing') return -1;
        if (b.status === 'discussing' && a.status !== 'discussing') return 1;
        return (b.created_at || 0) - (a.created_at || 0);
    });

    container.innerHTML = topics.map(topic => {
        const badge = getStatusBadge(topic.status);
        const isActive = topic.topic_id === oasisCurrentTopicId;
        const isRunning = topic.status === 'discussing' || topic.status === 'pending';
        return `
            <div class="oasis-topic-item ${isActive ? 'active' : ''}" onclick="openOasisTopic('${topic.topic_id}')">
                <div class="flex items-center justify-between mb-2">
                    <span class="oasis-status-badge ${badge.cls}">${badge.text}</span>
                    <div class="flex items-center space-x-1">
                        ${isRunning ? `<button onclick="event.stopPropagation(); cancelOasisTopic('${topic.topic_id}')" class="oasis-action-btn oasis-btn-cancel" title="${t('oasis_cancel')}">⏹</button>` : ''}
                        <button onclick="event.stopPropagation(); deleteOasisTopic('${topic.topic_id}')" class="oasis-action-btn oasis-btn-delete" title="${t('oasis_delete')}">🗑</button>
                        <span class="oasis-list-count">${topic.created_at ? formatTime(topic.created_at) : ''}</span>
                    </div>
                </div>
                <p class="text-sm font-semibold leading-relaxed text-[#32293a] line-clamp-3">${escapeHtml(topic.question)}</p>
                <div class="flex items-center flex-wrap gap-2 mt-3">
                    <span class="oasis-stage-chip">💬 ${topic.post_count || 0} ${t('oasis_posts')}</span>
                    <span class="oasis-stage-chip">🔄 ${topic.current_round}/${topic.max_rounds} ${t('oasis_round')}</span>
                </div>
            </div>`;
    }).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function openOasisTopic(topicId) {
    oasisCurrentTopicId = topicId;
    stopOasisPolling();
    showPageLoading();

    // Switch to detail view
    document.getElementById('oasis-topic-list-view').style.display = 'none';
    document.getElementById('oasis-detail-view').style.display = 'flex';

    // Load topic detail
    try {
        await loadTopicDetail(topicId);
    } finally {
        hidePageLoading();
    }
}

function showOasisTopicList() {
    stopOasisPolling();
    oasisCurrentTopicId = null;
    destroyOasisTownRuntime();
    document.getElementById('oasis-detail-view').style.display = 'none';
    document.getElementById('oasis-topic-list-view').style.display = 'flex';
    if (oasisTownModeEnabled) {
        renderOasisTownIdleState();
        updateOasisTownComposer(null);
    }
    refreshOasisTopics();
}

async function loadTopicDetail(topicId) {
    try {
        const resp = await fetch(`/proxy_oasis/topics/${topicId}`);
        console.log('[OASIS] Detail response status:', resp.status);
        if (!resp.ok) {
            console.error('[OASIS] Failed to fetch detail:', resp.status);
            return;
        }
        const detail = await resp.json();
        console.log('[OASIS] Detail data:', detail);
        console.log('[OASIS] Posts count:', (detail.posts || []).length);
        renderTopicDetail(detail);

        // If still discussing, start polling for updates
        if (detail.status === 'discussing' || detail.status === 'pending') {
            startDetailPolling(topicId);
        }
    } catch (e) {
        console.warn('Failed to load topic detail:', e);
    }
}

function collectOasisParticipants(detail) {
    const people = new Map();
    (detail.timeline || []).forEach(ev => {
        if (!ev.agent) return;
        const item = people.get(ev.agent) || { name: ev.agent, posts: 0, events: 0 };
        item.events += 1;
        people.set(ev.agent, item);
    });
    (detail.posts || []).forEach(post => {
        if (!post.author) return;
        const item = people.get(post.author) || { name: post.author, posts: 0, events: 0 };
        item.posts += 1;
        people.set(post.author, item);
    });
    return [...people.values()].sort((a, b) => {
        if (b.posts !== a.posts) return b.posts - a.posts;
        if (b.events !== a.events) return b.events - a.events;
        return a.name.localeCompare(b.name);
    });
}

async function loadOasisExperts(force = false) {
    if (_oasisExpertsCache && !force) return _oasisExpertsCache;
    const resp = await fetch('/proxy_oasis/experts');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    _oasisExpertsCache = data.experts || [];
    return _oasisExpertsCache;
}

function pickTownDefaultExpertTags(experts) {
    const preferred = ['creative', 'critical', 'data', 'synthesis'];
    const available = [...new Set((experts || []).map(e => e.tag).filter(Boolean))];
    const tags = [];
    if (selectedPersona && selectedPersona.tag && available.includes(selectedPersona.tag)) {
        tags.push(selectedPersona.tag);
    }
    preferred.forEach(tag => {
        if (available.includes(tag) && !tags.includes(tag)) tags.push(tag);
    });
    available.forEach(tag => {
        if (!tags.includes(tag)) tags.push(tag);
    });
    return tags.slice(0, Math.min(4, Math.max(available.length, 1)));
}

function buildTownQuickStartYaml(tags) {
    const lines = [
        'version: 1',
        'discussion: true',
        'repeat: true',
        'plan:',
        '  - parallel:',
    ];
    tags.forEach((tag, idx) => {
        lines.push(`      - "${tag}#temp#${idx + 1}"`);
    });
    return lines.join('\n');
}

function renderOasisTownStage(detail) {
    const stageQuestionEl = document.getElementById('oasis-town-stage-question');
    if (stageQuestionEl) {
        stageQuestionEl.textContent = detail.question || '';
    }

    const badge = getStatusBadge(detail.status);
    const metaEl = document.getElementById('oasis-town-stage-meta');
    if (metaEl) {
        metaEl.innerHTML = `
            <span class="oasis-stage-chip">${escapeHtml(badge.text)}</span>
            <span class="oasis-stage-chip">💬 ${(detail.posts || []).length} ${t('oasis_posts')}</span>
            <span class="oasis-stage-chip">🔄 ${detail.current_round}/${detail.max_rounds} ${t('oasis_round')}</span>
        `;
    }

    const stripEl = document.getElementById('oasis-resident-strip');
    if (!stripEl) return;
    const participants = collectOasisParticipants(detail);
    if (participants.length === 0) {
        stripEl.innerHTML = `<div class="oasis-resident-empty">${t('oasis_waiting')}</div>`;
        return;
    }

    stripEl.innerHTML = participants.slice(0, 8).map(person => {
        const avatar = getExpertAvatar(person.name);
        const roleText = person.posts > 0
            ? (currentLang === 'zh-CN' ? `${person.posts} 条发言` : `${person.posts} posts`)
            : (currentLang === 'zh-CN' ? '等待出场' : 'waiting');
        const eventText = currentLang === 'zh-CN'
            ? `${person.events} 次调度`
            : `${person.events} calls`;
        return `
            <div class="oasis-resident-card">
                <div class="oasis-resident-house">
                    <div class="oasis-expert-avatar ${avatar.cls}" title="${escapeHtml(person.name)}">${avatar.icon}</div>
                </div>
                <div class="oasis-resident-name">${escapeHtml(person.name)}</div>
                <div class="oasis-resident-role">${roleText}<br>${eventText}</div>
            </div>
        `;
    }).join('');
}

function updateOasisTownComposer(detail) {
    const input = document.getElementById('oasis-town-input');
    const note = document.getElementById('oasis-town-composer-note');
    const title = document.getElementById('oasis-town-composer-title');
    const submitBtn = document.getElementById('oasis-town-submit-btn');
    if (!input || !note || !title || !submitBtn) return;

    const topicId = detail && detail.topic_id ? detail.topic_id : '';
    const sameTopic = input.dataset.topicId === topicId;
    if (!sameTopic) {
        input.value = '';
    }
    input.dataset.topicId = topicId;

    const status = detail && detail.status ? detail.status : '';
    const isLive = topicId && topicId === oasisCurrentTopicId && status === 'discussing';
    const isBusy = oasisManualPostSubmitting;
    title.textContent = currentLang === 'zh-CN' ? '实时引导' : 'LIVE PROMPT';

    if (isLive) {
        note.textContent = currentLang === 'zh-CN'
            ? '输入一句新观点后回车或点按钮，正在进行的讨论会立刻收到这条发言。'
            : 'Press Enter or click the button to inject a new angle into the running discussion.';
        note.className = 'oasis-town-composer-note is-live';
        input.placeholder = currentLang === 'zh-CN'
            ? '例如：请从成本、风险和用户体验三个角度继续争论'
            : 'Example: keep debating from cost, risk, and user experience.';
    } else {
        note.textContent = currentLang === 'zh-CN'
            ? '当前没有选中运行中的 topic。直接发送会新开一个 OASIS 讨论，并在右侧打开详细发言流。'
            : 'No live topic is selected. Submit here to start a fresh OASIS discussion on the right.';
        note.className = 'oasis-town-composer-note is-live';
        input.placeholder = currentLang === 'zh-CN'
            ? '例如：围绕这个想法拉起一场新的专家讨论'
            : 'Example: start a new expert discussion around this idea.';
    }

    input.disabled = isBusy;
    submitBtn.disabled = isBusy;
    submitBtn.textContent = isBusy
        ? (currentLang === 'zh-CN' ? '发送中' : 'SENDING')
        : (isLive
            ? (currentLang === 'zh-CN' ? '推动发帖' : 'NUDGE')
            : (currentLang === 'zh-CN' ? '开启讨论' : 'START TOPIC'));
}

function renderTopicDetail(detail) {
    // Cache detail for overview visualization
    cacheOverviewDetail(detail);

    const badge = getStatusBadge(detail.status);
    document.getElementById('oasis-detail-status').className = 'oasis-status-badge ' + badge.cls;
    document.getElementById('oasis-detail-status').textContent = badge.text;
    const roundText = currentLang === 'zh-CN' ? `第 ${detail.current_round}/${detail.max_rounds} ${t('oasis_round')}` : `Round ${detail.current_round}/${detail.max_rounds}`;
    document.getElementById('oasis-detail-round').textContent = roundText;
    document.getElementById('oasis-detail-question').textContent = detail.question;
    renderPendingHumanPanel(detail);
    renderOasisTownStage(detail);
    updateOasisTownComposer(detail);
    updateOasisChatTownHud(detail);
    syncOasisTownRuntime(detail);

    // Render action buttons in detail header
    const actionsEl = document.getElementById('oasis-detail-actions');
    const isRunning = detail.status === 'discussing' || detail.status === 'pending';
    let btns = '';
    // Always show overview button when there is data
    const hasData = (detail.posts && detail.posts.length > 0) || (detail.timeline && detail.timeline.length > 0);
    if (hasData) {
        btns += `<button onclick="showDiscussionOverview()" class="oasis-detail-action-btn overview">📊 ${currentLang==='zh-CN'?'讨论概览':'Overview'}</button>`;
    }
    if (isRunning) {
        btns += `<button onclick="cancelOasisTopic('${detail.topic_id}')" class="oasis-detail-action-btn cancel">⏹ ${t('oasis_cancel')}</button>`;
    }
    btns += `<button onclick="deleteOasisTopic('${detail.topic_id}')" class="oasis-detail-action-btn delete">🗑 ${t('oasis_delete')}</button>`;
    actionsEl.innerHTML = btns;

    renderPosts(detail.posts || [], detail.timeline || [], detail.discussion !== false);

    // Show/hide conclusion
    const conclusionArea = document.getElementById('oasis-conclusion-area');
    if (detail.conclusion && detail.status === 'concluded') {
        document.getElementById('oasis-conclusion-text').innerHTML = marked.parse(detail.conclusion || '');
        conclusionArea.style.display = 'block';
        // Reset to expanded state
        const textEl = document.getElementById('oasis-conclusion-text');
        const toggleEl = document.getElementById('oasis-conclusion-toggle');
        textEl.style.display = '';
        if (toggleEl) toggleEl.textContent = '▼';
    } else {
        conclusionArea.style.display = 'none';
    }
}

function renderPendingHumanPanel(detail) {
    const panel = document.getElementById('oasis-human-node-panel');
    if (!panel) return;

    const pending = detail && detail.pending_human ? detail.pending_human : null;
    const isWaitingForHuman = !!pending && (detail.status === 'discussing' || detail.status === 'pending');
    if (!isWaitingForHuman) {
        panel.style.display = 'none';
        panel.innerHTML = '';
        return;
    }

    const disabled = oasisHumanReplySubmitting ? 'disabled' : '';
    panel.style.display = 'block';
    panel.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
            <div>
                <div style="font-size:12px;font-weight:700;color:#92400e;">${currentLang === 'zh-CN' ? '等待人类节点回复' : 'Waiting For Human Reply'}</div>
                <div style="font-size:10px;color:#a16207;margin-top:3px;">
                    node: ${escapeHtml(pending.node_id || '')} · round: ${escapeHtml(String(pending.round_num ?? ''))}
                </div>
            </div>
            <div style="font-size:10px;color:#92400e;">${escapeHtml(pending.author || '')}</div>
        </div>
        <div style="margin-top:6px;font-size:11px;color:#3f3f46;white-space:pre-wrap;">${escapeHtml(pending.prompt || '')}</div>
        <textarea id="oasis-human-reply-input" rows="2" ${disabled}
            placeholder="${currentLang === 'zh-CN' ? '直接输入你的普通回复，不需要 JSON 格式' : 'Type a plain text reply. No JSON needed.'}"
            style="width:100%;min-height:44px;margin-top:8px;padding:10px 12px;border:1px solid #e5e7eb;border-radius:12px;resize:vertical;background:white;"></textarea>
        <div style="display:flex;justify-content:flex-end;margin-top:8px;">
            <button id="oasis-human-reply-btn" ${disabled} onclick="submitOasisHumanReply()"
                style="padding:8px 14px;border:none;border-radius:999px;background:#f59e0b;color:white;font-size:12px;font-weight:700;cursor:pointer;">
                ${oasisHumanReplySubmitting
                    ? (currentLang === 'zh-CN' ? '提交中' : 'Sending')
                    : (currentLang === 'zh-CN' ? '提交人类回复' : 'Submit Human Reply')}
            </button>
        </div>
    `;
}

async function submitOasisHumanReply() {
    if (oasisHumanReplySubmitting || !_overviewDetailCache || !_overviewDetailCache.pending_human) return;
    const detail = _overviewDetailCache;
    const pending = detail.pending_human;
    const input = document.getElementById('oasis-human-reply-input');
    if (!input) return;
    const content = (input.value || '').trim();
    if (!content) {
        input.focus();
        return;
    }

    oasisHumanReplySubmitting = true;
    renderPendingHumanPanel(detail);
    try {
        const resp = await fetch(`/proxy_oasis/topics/${detail.topic_id}/human-reply`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                node_id: pending.node_id,
                round_num: pending.round_num,
                content,
            }),
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
            throw new Error(data.error || data.detail || data.message || `HTTP ${resp.status}`);
        }
        input.value = '';
        await loadTopicDetail(detail.topic_id);
        refreshOasisTopics();
    } catch (e) {
        alert((currentLang === 'zh-CN' ? '提交人类回复失败' : 'Failed to submit human reply') + ': ' + e.message);
    } finally {
        oasisHumanReplySubmitting = false;
        if (_overviewDetailCache) {
            renderPendingHumanPanel(_overviewDetailCache);
        }
    }
}

function toggleConclusionCollapse() {
    const textEl = document.getElementById('oasis-conclusion-text');
    const toggleEl = document.getElementById('oasis-conclusion-toggle');
    if (!textEl) return;
    const collapsed = textEl.style.display === 'none';
    textEl.style.display = collapsed ? '' : 'none';
    if (toggleEl) toggleEl.textContent = collapsed ? '▼' : '▶';
}

// ── Discussion Overview: DAG timeline visualization ──
function cacheOverviewDetail(detail) { _overviewDetailCache = detail; }

function showDiscussionOverview() {
    const detail = _overviewDetailCache;
    if (!detail) { alert('No discussion data'); return; }
    const timeline = detail.timeline || [];
    const posts = detail.posts || [];
    if (timeline.length === 0 && posts.length === 0) { alert(currentLang==='zh-CN'?'暂无讨论数据':'No discussion data'); return; }

    // Collect all agents (with agent rows) + system row
    const agentSet = new Set();
    timeline.forEach(ev => { if (ev.agent) agentSet.add(ev.agent); });
    posts.forEach(p => { if (p.author) agentSet.add(p.author); });
    const agents = [...agentSet];
    const hasSysEvents = timeline.some(ev => !ev.agent);
    const rowKeys = [...agents];
    if (hasSysEvents) rowKeys.push('__system__');

    // Merge all events sorted by time
    const allEvents = [];
    timeline.forEach(ev => allEvents.push({ t: ev.elapsed||0, type: 'timeline', data: ev }));
    posts.forEach(p => allEvents.push({ t: p.elapsed||0, type: 'post', data: p }));
    allEvents.sort((a,b) => a.t - b.t);

    const maxTime = allEvents.length ? Math.max(allEvents[allEvents.length-1].t, 1) : 1;
    const fmtT = (s) => { const r=Math.round(s); if(r<60) return r+'s'; return Math.floor(r/60)+'m'+(r%60?r%60+'s':''); };

    // Colors for each event type
    const evColors = {
        start:       { bg:'#ecfdf5', border:'#6ee7b7', text:'#047857' },
        agent_call:  { bg:'#fef3c7', border:'#fcd34d', text:'#92400e' },
        agent_done:  { bg:'#d1fae5', border:'#6ee7b7', text:'#065f46' },
        post:        { bg:'#dbeafe', border:'#93c5fd', text:'#1e40af' },
        conclude:    { bg:'#ede9fe', border:'#c4b5fd', text:'#5b21b6' },
        round:       { bg:'#fce7f3', border:'#f9a8d4', text:'#9d174d' },
        if_branch:   { bg:'#fff7ed', border:'#fdba74', text:'#c2410c' },
        manual_post: { bg:'#e0e7ff', border:'#a5b4fc', text:'#3730a3' },
    };
    // Bar colors for duration spans (call→done)
    const barColors = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444','#ec4899','#06b6d4','#84cc16'];
    const evIcons = {start:'🚀',round:'📢',agent_call:'⏳',agent_done:'✅',conclude:'🏁',manual_post:'📝',if_branch:'🔀',post:'💬'};

    // Layout constants
    const labelW = 130;    // left label column width
    const chartW = 700;    // timeline chart width (scrollable)
    const rowH = 42;       // row height
    const markerR = 7;     // event marker radius
    const headerH = 30;    // time axis header height

    // Compute tick marks (aim for ~8-12 ticks)
    const tickCount = Math.min(Math.max(Math.ceil(maxTime/5), 5), 20);
    const tickStep = maxTime / tickCount;
    const niceStep = tickStep < 5 ? 5 : tickStep < 10 ? 10 : tickStep < 15 ? 15 : tickStep < 30 ? 30 : tickStep < 60 ? 60 : Math.ceil(tickStep/60)*60;
    const ticks = [];
    for (let t = 0; t <= maxTime + niceStep*0.5; t += niceStep) ticks.push(t);

    const tToX = (t) => (t / maxTime) * chartW;

    // Build per-agent events and duration bars
    const agentEventsMap = {};
    const agentBars = {};
    rowKeys.forEach(k => { agentEventsMap[k] = []; agentBars[k] = []; });
    allEvents.forEach(ev => {
        let key;
        if (ev.type === 'post') key = ev.data.author;
        else if (ev.data.agent) key = ev.data.agent;
        else key = '__system__';
        if (!agentEventsMap[key]) return;
        agentEventsMap[key].push(ev);
    });

    // Build duration bars: pair agent_call with agent_done
    agents.forEach((agent, ai) => {
        const evs = agentEventsMap[agent];
        const callStack = [];
        evs.forEach(ev => {
            if (ev.type === 'timeline' && ev.data.event === 'agent_call') callStack.push(ev.t);
            else if (ev.type === 'timeline' && ev.data.event === 'agent_done' && callStack.length > 0) {
                const startT = callStack.shift();
                agentBars[agent].push({ start: startT, end: ev.t, color: barColors[ai % barColors.length] });
            }
        });
        // If there are unclosed calls, extend to current max
        callStack.forEach(st => {
            agentBars[agent].push({ start: st, end: maxTime, color: barColors[ai % barColors.length], open: true });
        });
    });

    // Build SVG for each row
    function buildRowSvg(key, _idx) {
        const evs = agentEventsMap[key] || [];
        const bars = agentBars[key] || [];
        const y = rowH / 2;
        let svg = '';

        // Background track line
        svg += `<line x1="0" y1="${y}" x2="${chartW}" y2="${y}" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="4,3"/>`;

        // Duration bars
        bars.forEach(bar => {
            const x1 = tToX(bar.start);
            const x2 = tToX(bar.end);
            const w = Math.max(x2 - x1, 3);
            svg += `<rect x="${x1}" y="${y-8}" width="${w}" height="16" rx="4" fill="${bar.color}" opacity="0.18" stroke="${bar.color}" stroke-width="1.5" ${bar.open?'stroke-dasharray="4,2"':''}/>`;
            svg += `<rect x="${x1}" y="${y-8}" width="${w}" height="16" rx="4" fill="${bar.color}" opacity="0.08"/>`;
            // Duration label inside bar if wide enough
            const dur = bar.end - bar.start;
            if (w > 36) {
                svg += `<text x="${x1+w/2}" y="${y+3.5}" text-anchor="middle" font-size="8" font-weight="600" fill="${bar.color}" opacity="0.7">${fmtT(dur)}</text>`;
            }
        });

        // Event markers (circles with icons)
        evs.forEach(ev => {
            const x = tToX(ev.t);
            const evType = ev.type === 'post' ? 'post' : (ev.data.event || 'start');
            const col = evColors[evType] || evColors.start;
            const icon = evIcons[evType] || '⏱';

            // Tooltip text
            let tip = fmtT(ev.t) + ' ';
            if (ev.type === 'post') {
                tip += (currentLang==='zh-CN'?'💬 发言':'💬 Post');
                const txt = (ev.data.content||'').substring(0,40);
                if (txt) tip += ': ' + txt;
            } else {
                tip += icon + ' ' + (ev.data.detail || ev.data.event || '');
            }

            // Drop shadow + circle
            svg += `<circle cx="${x}" cy="${y}" r="${markerR+1}" fill="white" opacity="0.9"/>`;
            svg += `<circle cx="${x}" cy="${y}" r="${markerR}" fill="${col.bg}" stroke="${col.border}" stroke-width="1.5" style="cursor:pointer;">`;
            svg += `<title>${escapeHtml(tip)}</title></circle>`;
            // Icon text (emoji fallback)
            svg += `<text x="${x}" y="${y+3.5}" text-anchor="middle" font-size="9" style="pointer-events:none;">${icon}</text>`;

            // Time label below marker (only for significant events or sparse areas)
            svg += `<text x="${x}" y="${y+markerR+10}" text-anchor="middle" font-size="7" fill="#94a3b8">${fmtT(ev.t)}</text>`;
        });

        return svg;
    }

    // Build the complete SVG chart
    const totalH = headerH + rowKeys.length * rowH + 4;
    let chartSvg = '';

    // Time axis header with ticks
    chartSvg += `<g transform="translate(0,0)">`;
    ticks.forEach(t => {
        const x = tToX(t);
        if (x > chartW) return;
        chartSvg += `<line x1="${x}" y1="${headerH-4}" x2="${x}" y2="${totalH}" stroke="#f1f5f9" stroke-width="1"/>`;
        chartSvg += `<text x="${x}" y="${headerH-8}" text-anchor="middle" font-size="9" fill="#94a3b8" font-weight="500">${fmtT(t)}</text>`;
    });
    // Axis baseline
    chartSvg += `<line x1="0" y1="${headerH}" x2="${chartW}" y2="${headerH}" stroke="#e2e8f0" stroke-width="1.5"/>`;
    chartSvg += `</g>`;

    // Rows
    rowKeys.forEach((key, i) => {
        const yOff = headerH + i * rowH;
        // Alternating row background
        if (i % 2 === 0) chartSvg += `<rect x="0" y="${yOff}" width="${chartW}" height="${rowH}" fill="#fafbfc"/>`;
        // Row separator
        chartSvg += `<line x1="0" y1="${yOff+rowH}" x2="${chartW}" y2="${yOff+rowH}" stroke="#f1f5f9" stroke-width="1"/>`;
        chartSvg += `<g transform="translate(0,${yOff})">${buildRowSvg(key, i)}</g>`;
    });

    // Build left labels HTML
    let labelsHtml = `<div style="height:${headerH}px;display:flex;align-items:flex-end;padding:0 8px 4px;font-size:9px;font-weight:600;color:#94a3b8;border-bottom:1.5px solid #e2e8f0;">Agent</div>`;
    rowKeys.forEach((key, i) => {
        const isSystem = key === '__system__';
        const name = isSystem ? (currentLang==='zh-CN'?'系统':'System') : key;
        const icon = isSystem ? '🎯' : getExpertAvatar(key).icon;
        const bg = i % 2 === 0 ? '#fafbfc' : 'white';
        labelsHtml += `<div style="height:${rowH}px;display:flex;align-items:center;padding:0 8px;gap:6px;background:${bg};border-bottom:1px solid #f1f5f9;white-space:nowrap;overflow:hidden;">
            <span style="font-size:13px;flex-shrink:0;">${icon}</span>
            <span style="font-size:11px;font-weight:600;color:#374151;overflow:hidden;text-overflow:ellipsis;" title="${escapeHtml(name)}">${escapeHtml(name)}</span>
        </div>`;
    });

    // Legend
    const legendItems = [
        {type:'start', label:currentLang==='zh-CN'?'开始':'Start'},
        {type:'agent_call', label:currentLang==='zh-CN'?'调用':'Call'},
        {type:'post', label:currentLang==='zh-CN'?'发言':'Post'},
        {type:'agent_done', label:currentLang==='zh-CN'?'完成':'Done'},
        {type:'round', label:currentLang==='zh-CN'?'轮次':'Round'},
        {type:'conclude', label:currentLang==='zh-CN'?'总结':'Conclude'},
        {type:'if_branch', label:currentLang==='zh-CN'?'分支':'Branch'},
    ];
    const legendHtml = legendItems.map(l => {
        const c = evColors[l.type]||evColors.start;
        return `<span style="display:inline-flex;align-items:center;gap:4px;font-size:10px;color:#6b7280;">
            <span style="width:14px;height:14px;border-radius:50%;background:${c.bg};border:1.5px solid ${c.border};display:inline-flex;align-items:center;justify-content:center;font-size:8px;">${evIcons[l.type]||'⏱'}</span>${l.label}</span>`;
    }).join('');
    const barLegend = `<span style="display:inline-flex;align-items:center;gap:4px;font-size:10px;color:#6b7280;margin-left:8px;">
        <span style="width:24px;height:10px;border-radius:3px;background:${barColors[0]};opacity:0.25;border:1.5px solid ${barColors[0]};display:inline-block;"></span>${currentLang==='zh-CN'?'执行时长':'Duration'}</span>`;

    // Summary stats
    const totalDuration = allEvents.length ? allEvents[allEvents.length-1].t : 0;
    const totalPosts = posts.length;
    const summaryText = currentLang==='zh-CN'
        ? `共 ${agents.length} 位专家 · ${totalPosts} 条发言 · ${detail.current_round||0} 轮讨论 · 总时长 ${fmtT(Math.round(totalDuration))}`
        : `${agents.length} experts · ${totalPosts} posts · ${detail.current_round||0} rounds · Duration ${fmtT(Math.round(totalDuration))}`;

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'oasis-overview-overlay';
    overlay.style.cssText = 'position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;';
    overlay.innerHTML = `
        <div style="background:white;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.2);width:94vw;max-width:960px;max-height:88vh;display:flex;flex-direction:column;overflow:hidden;">
            <div style="display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid #e5e7eb;flex-shrink:0;">
                <h3 style="font-size:15px;font-weight:700;color:#111827;">📊 ${currentLang==='zh-CN'?'团队讨论时间轴':'Discussion Timeline'}</h3>
                <button onclick="document.getElementById('oasis-overview-overlay').remove()" style="background:none;border:none;font-size:20px;color:#9ca3af;cursor:pointer;padding:4px 8px;border-radius:6px;line-height:1;">&times;</button>
            </div>
            <div style="padding:10px 20px 6px;flex-shrink:0;">
                <div style="font-size:12px;color:#6b7280;padding:8px 12px;background:#f8fafc;border-radius:8px;border:1px solid #e2e8f0;">
                    ${summaryText}
                </div>
            </div>
            <div style="flex:1;overflow:hidden;display:flex;padding:0 20px 10px;">
                <!-- Left labels (fixed) -->
                <div style="width:${labelW}px;flex-shrink:0;overflow:hidden;border-right:1.5px solid #e2e8f0;">
                    ${labelsHtml}
                </div>
                <!-- Right chart (horizontally scrollable) -->
                <div style="flex:1;overflow-x:auto;overflow-y:hidden;">
                    <svg width="${chartW+20}" height="${totalH}" viewBox="0 0 ${chartW+20} ${totalH}" style="display:block;min-width:${chartW+20}px;">
                        <g transform="translate(10,0)">${chartSvg}</g>
                    </svg>
                </div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;padding:8px 20px 14px;border-top:1px solid #e5e7eb;flex-shrink:0;align-items:center;">
                ${legendHtml}${barLegend}
            </div>
        </div>`;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
}

function fmtElapsed(sec) {
    if (sec === undefined || sec === null) return '';
    const s = Math.round(sec);
    if (s < 60) return 'T+' + s + 's';
    const m = Math.floor(s / 60);
    return 'T+' + m + 'm' + (s % 60) + 's';
}

function handleOasisTownComposerKeydown(event) {
    if (event.key !== 'Enter' || event.shiftKey) return;
    event.preventDefault();
    submitOasisTopicPost();
}

async function createOasisTopicFromTownPrompt(question) {
    const experts = await loadOasisExperts();
    const tags = pickTownDefaultExpertTags(experts);
    if (!tags.length) {
        throw new Error(currentLang === 'zh-CN' ? '没有可用的 OASIS 专家' : 'No OASIS experts available');
    }
    const resp = await fetch('/proxy_oasis/topics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            question,
            max_rounds: 5,
            discussion: true,
            schedule_yaml: buildTownQuickStartYaml(tags),
        }),
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
        throw new Error(data.error || data.detail || data.message || `HTTP ${resp.status}`);
    }
    return data;
}

async function submitOasisTopicPost() {
    if (oasisManualPostSubmitting) return;
    const detail = _overviewDetailCache && _overviewDetailCache.topic_id === oasisCurrentTopicId
        ? _overviewDetailCache
        : null;
    const isLive = !!(detail && detail.status === 'discussing' && detail.topic_id === oasisCurrentTopicId);

    const input = document.getElementById('oasis-town-input');
    if (!input) return;
    const content = (input.value || '').trim();
    if (!content) {
        input.focus();
        return;
    }

    oasisManualPostSubmitting = true;
    updateOasisTownComposer(detail);
    try {
        ensureOasisPanelOpen();
        if (isLive) {
            const resp = await fetch(`/proxy_oasis/topics/${oasisCurrentTopicId}/posts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content }),
            });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok) {
                throw new Error(data.error || data.detail || data.message || `HTTP ${resp.status}`);
            }
            input.value = '';
            await loadTopicDetail(oasisCurrentTopicId);
        } else {
            const created = await createOasisTopicFromTownPrompt(content);
            input.value = '';
            await refreshOasisTopics();
            if (created.topic_id) {
                await openOasisTopic(created.topic_id);
            }
        }
        refreshOasisTopics();
        input.focus();
    } catch (e) {
        alert((currentLang === 'zh-CN' ? 'Town 提交失败' : 'Town submit failed') + ': ' + e.message);
    } finally {
        oasisManualPostSubmitting = false;
        const latest = _overviewDetailCache && _overviewDetailCache.topic_id === oasisCurrentTopicId
            ? _overviewDetailCache
            : detail;
        updateOasisTownComposer(latest);
    }
}

function renderPosts(posts, timeline, _isDiscussion) {
    const box = document.getElementById('oasis-posts-box');
    if (!box) return;
    const sameTopic = box.dataset.topicId === (oasisCurrentTopicId || '');
    const shouldStickToBottom = !sameTopic || (box.scrollHeight - box.scrollTop - box.clientHeight < 96);
    box.dataset.topicId = oasisCurrentTopicId || '';
    box.classList.add('oasis-town-feed');

    if (posts.length === 0 && (!timeline || timeline.length === 0)) {
        box.innerHTML = `
            <div class="oasis-topic-list-empty" style="min-height: 260px;">
                <div class="oasis-empty-town">💭</div>
                <p>${t('oasis_waiting')}</p>
            </div>`;
        return;
    }

    // ── timeline 事件（绿色卡片）+ 帖子混排 ──
    const items = [];
    if (timeline) {
        for (const ev of timeline) {
            // 讨论模式下不显示 agent_done
            if (ev.event === 'agent_done') continue;
            items.push({type: 'event', elapsed: ev.elapsed, data: ev});
        }
    }
    for (const p of posts) {
        items.push({type: 'post', elapsed: p.elapsed || 0, data: p});
    }
    items.sort((a, b) => a.elapsed - b.elapsed);

    box.innerHTML = items.map(item => {
        if (item.type === 'event') {
            const ev = item.data;
            const evIcons = {start:'🚀', round:'📢', agent_call:'⏳', agent_done:'✅', conclude:'🏁', manual_post:'📝', if_branch:'🔀', script_start:'🧪', script_done:'📜', script_timeout:'⏰', human_wait:'🙋', human_reply:'💬', human_timeout:'⌛'};
            const icon = evIcons[ev.event] || '⏱';
            const label = ev.agent ? ev.agent + (ev.detail ? ' · ' + ev.detail : '') : (ev.detail || ev.event);
            return `
                <div class="oasis-post oasis-town-event">
                    <div class="oasis-town-event-icon">${icon}</div>
                    <div class="oasis-town-event-body">
                        <div class="oasis-town-event-title">${escapeHtml(label)}</div>
                        <span class="oasis-town-event-time">${fmtElapsed(ev.elapsed)}</span>
                    </div>
                </div>`;
        }
        // Post
        const p = item.data;
        const avatar = getExpertAvatar(p.author);
        const isReply = p.reply_to !== null && p.reply_to !== undefined;
        const totalVotes = p.upvotes + p.downvotes;
        const upPct = totalVotes > 0 ? (p.upvotes / totalVotes * 100) : 50;
        const alignRight = ((p.id || 0) + (p.author || '').length) % 2 === 0;

        return `
            <div class="oasis-post oasis-town-post ${alignRight ? 'oasis-town-post-right' : ''} ${isReply ? 'reply' : ''}">
                <div class="oasis-town-post-shell">
                    <div class="oasis-town-speaker">
                        <div class="oasis-expert-avatar ${avatar.cls}" title="${escapeHtml(p.author)}">${avatar.icon}</div>
                        <div class="oasis-town-speaker-meta">
                            <span class="oasis-town-speaker-name">${escapeHtml(p.author)}</span>
                            <span class="oasis-town-speaker-role">${isReply ? '↩ ' + (currentLang === 'zh-CN' ? '回复' : 'reply') + ' #' + p.reply_to : (currentLang === 'zh-CN' ? '广场发言' : 'square post')}</span>
                        </div>
                        <div class="oasis-town-post-time">${fmtElapsed(p.elapsed)}</div>
                    </div>
                    <div class="oasis-town-speech markdown-body">${marked.parse(p.content || '')}</div>
                    <div class="oasis-town-post-footer">
                        <div class="oasis-town-post-meta">
                            <span class="oasis-town-vote-summary">#${p.id}</span>
                            <span class="oasis-town-vote-summary">👍 ${p.upvotes}</span>
                            <span class="oasis-town-vote-summary">👎 ${p.downvotes}</span>
                        </div>
                        ${totalVotes > 0 ? `
                            <div class="flex-1 oasis-vote-bar flex">
                                <div class="oasis-vote-up" style="width: ${upPct}%"></div>
                                <div class="oasis-vote-down" style="width: ${100 - upPct}%"></div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>`;
    }).join('');

    if (shouldStickToBottom) {
        box.scrollTop = box.scrollHeight;
    }

    // Highlight code blocks in rendered markdown
    box.querySelectorAll('pre code').forEach(el => {
        try { hljs.highlightElement(el); } catch(e) {}
    });
}

function startDetailPolling(topicId) {
    stopOasisPolling();
    let lastPostCount = 0;
    let lastTimelineCount = 0;
    let errorCount = 0;
    oasisPollingTimer = setInterval(async () => {
        if (oasisCurrentTopicId !== topicId) {
            stopOasisPolling();
            return;
        }
        try {
            const resp = await fetch(`/proxy_oasis/topics/${topicId}`);
            if (!resp.ok) {
                errorCount++;
                console.warn(`OASIS polling error: HTTP ${resp.status}`);
                if (errorCount >= 5) {
                    console.error('OASIS polling failed 5 times, stopping');
                    stopOasisPolling();
                }
                return;
            }
            errorCount = 0;
            const detail = await resp.json();

            // Re-render if posts or timeline changed
            const currentPostCount = (detail.posts || []).length;
            const currentTimelineCount = (detail.timeline || []).length;
            if (currentPostCount !== lastPostCount || currentTimelineCount !== lastTimelineCount || detail.status !== 'discussing') {
                renderTopicDetail(detail);
                lastPostCount = currentPostCount;
                lastTimelineCount = currentTimelineCount;
            }

            // Stop polling when discussion ends
            if (detail.status === 'concluded' || detail.status === 'error') {
                stopOasisPolling();
                refreshOasisTopics();
            }
        } catch (e) {
            errorCount++;
            console.warn('OASIS polling error:', e);
        }
    }, 1500); // Poll every 1.5 seconds for faster updates
}

async function cancelOasisTopic(topicId) {
    if (!confirm(t('oasis_cancel_confirm'))) return;
    try {
        const resp = await fetch(`/proxy_oasis/topics/${topicId}/cancel`, { method: 'POST' });
        const data = await resp.json();
        if (resp.ok) {
            stopOasisPolling();
            if (oasisCurrentTopicId === topicId) {
                await loadTopicDetail(topicId);
            }
            refreshOasisTopics();
        } else {
            alert(t('oasis_action_fail') + ': ' + (data.error || data.detail || data.message || ''));
        }
    } catch (e) {
        alert(t('oasis_action_fail') + ': ' + e.message);
    }
}

async function deleteOasisTopic(topicId) {
    if (!confirm(t('oasis_delete_confirm'))) return;
    try {
        const resp = await fetch(`/proxy_oasis/topics/${topicId}/purge`, { method: 'POST' });
        const data = await resp.json();
        if (resp.ok) {
            stopOasisPolling();
            if (oasisCurrentTopicId === topicId) {
                showOasisTopicList();
            } else {
                refreshOasisTopics();
            }
        } else {
            alert(t('oasis_action_fail') + ': ' + (data.error || data.detail || data.message || ''));
        }
    } catch (e) {
        alert(t('oasis_action_fail') + ': ' + e.message);
    }
}

async function deleteAllOasisTopics() {
    const countEl = document.getElementById('oasis-topic-count');
    const count = parseInt(countEl.textContent) || 0;
    if (count === 0) {
        alert(t('oasis_no_topics') || '暂无讨论话题');
        return;
    }
    const confirmMsg = (currentLang === 'zh-CN')
        ? `确定要清空所有 ${count} 个讨论话题吗？此操作不可恢复！`
        : `Delete all ${count} topics? This cannot be undone!`;
    if (!confirm(confirmMsg)) return;

    try {
        const resp = await fetch('/proxy_oasis/topics', { method: 'DELETE' });
        const data = await resp.json();
        if (resp.ok) {
            stopOasisPolling();
            showOasisTopicList();
            alert((currentLang === 'zh-CN' ? '已删除 ' : 'Deleted ') + data.deleted_count + (currentLang === 'zh-CN' ? ' 个话题' : ' topics'));
        } else {
            alert(t('oasis_action_fail') + ': ' + (data.error || data.detail || data.message || ''));
        }
    } catch (e) {
        alert(t('oasis_action_fail') + ': ' + e.message);
    }
}

// Auto-refresh topic list periodically when panel is open
setInterval(() => {
    if (oasisPanelOpen && !oasisCurrentTopicId && currentUserId) {
        refreshOasisTopics();
    }
}, 10000); // Every 10 seconds

// === System trigger polling: 检测后台系统触发产生的新消息 ===
let _sessionStatusTimer = null;

function startSessionStatusPolling() {
    stopSessionStatusPolling();
    _sessionStatusTimer = setInterval(async () => {
        if (!currentUserId || !currentSessionId) return;
        // 用户正在流式对话中，跳过轮询
        if (cancelBtn.style.display !== 'none') return;
        try {
            const resp = await fetch('/proxy_session_status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ session_id: currentSessionId })
            });
            const data = await resp.json();

            // --- 系统占用状态 ---
            if (data.busy) {
                setSystemBusyUI(true);
            } else if (busyBtn.style.display !== 'none') {
                // busy → 不busy：恢复按钮，显示刷新横幅
                setSystemBusyUI(false);
                showNewMsgBanner();
            }
        } catch(e) {
            // 静默忽略
        }
    }, 5000); // 每 5 秒轮询一次
}

function stopSessionStatusPolling() {
    if (_sessionStatusTimer) {
        clearInterval(_sessionStatusTimer);
        _sessionStatusTimer = null;
    }
}

// 登录成功后启动轮询
const _origLogin = typeof handleLogin === 'function' ? null : null;
// 监听 chat-container 可见性来启动/停止轮询
const _chatObserver = new MutationObserver(() => {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer && chatContainer.style.display !== 'none') {
        startSessionStatusPolling();
    } else {
        stopSessionStatusPolling();
    }
});
_chatObserver.observe(document.body, { childList: true, subtree: true, attributes: true });

// ================================================================
// ===== Group Chat (群聊) 逻辑 =====
// ================================================================

// Agent 颜色方案：根据名字 hash 分配一致的颜色
const _agentColorPalette = [
    { bg: '#f0fdf4', border: '#bbf7d0', text: '#166534', sender: '#15803d', pre: '#1a2e1a', code: '#d1fae5' },
    { bg: '#eff6ff', border: '#bfdbfe', text: '#1e40af', sender: '#2563eb', pre: '#1e2a4a', code: '#dbeafe' },
    { bg: '#fdf4ff', border: '#e9d5ff', text: '#6b21a8', sender: '#7c3aed', pre: '#2d1a3e', code: '#ede9fe' },
    { bg: '#fff7ed', border: '#fed7aa', text: '#9a3412', sender: '#ea580c', pre: '#3b1a0a', code: '#ffedd5' },
    { bg: '#fef2f2', border: '#fecaca', text: '#991b1b', sender: '#dc2626', pre: '#3b1212', code: '#fee2e2' },
    { bg: '#f0fdfa', border: '#99f6e4', text: '#115e59', sender: '#0d9488', pre: '#0f2d2a', code: '#ccfbf1' },
    { bg: '#fefce8', border: '#fde68a', text: '#854d0e', sender: '#ca8a04', pre: '#2d2305', code: '#fef9c3' },
    { bg: '#fdf2f8', border: '#fbcfe8', text: '#9d174d', sender: '#db2777', pre: '#3b0d24', code: '#fce7f3' },
];
const _agentColorCache = {};
function getAgentColor(sender) {
    if (_agentColorCache[sender]) return _agentColorCache[sender];
    let hash = 0;
    for (let i = 0; i < sender.length; i++) {
        hash = ((hash << 5) - hash) + sender.charCodeAt(i);
        hash |= 0;
    }
    const color = _agentColorPalette[Math.abs(hash) % _agentColorPalette.length];
    _agentColorCache[sender] = color;
    return color;
}
function applyAgentColor(el, sender) {
    const c = getAgentColor(sender);
    const content = el.querySelector('.group-msg-content');
    const senderEl = el.querySelector('.group-msg-sender');
    if (content) {
        content.style.background = c.bg;
        content.style.borderColor = c.border;
        content.style.color = c.text;
    }
    if (senderEl) senderEl.style.color = c.sender;
    el.querySelectorAll('.group-msg-content pre').forEach(pre => { pre.style.background = c.pre; });
    el.querySelectorAll('.group-msg-content code').forEach(code => { code.style.color = c.code; });
}

let currentGroupId = null;
let groupPollingTimer = null;
let groupLastMsgId = 0;
let groupMuted = false;
const groupSenderTitles = {};  // sender -> display title mapping

function getGroupSenderTitle(sender) {
    let name = groupSenderTitles[sender] || sender;
    if (name.length > 7) name = name.slice(0, 7) + '…';
    return name;
}

// === @ Mention 功能 ===
let mentionSelectedIds = [];  // 被 @ 选中的 agent session_id 列表
let currentGroupMembers = []; // 当前群的 agent 成员缓存

function onGroupInputChange(_e) {
    const input = document.getElementById('group-input');
    const val = input.value;
    const cursorPos = input.selectionStart;
    // 检测光标前一个字符是否刚输入了 @
    if (cursorPos > 0 && val[cursorPos - 1] === '@') {
        showMentionPopup();
    }
}

function showMentionPopup() {
    const popup = document.getElementById('mention-popup');
    const listEl = document.getElementById('mention-list');
    // 从 groupSenderTitles 构建 agent 列表
    const agents = [];
    for (const [key, title] of Object.entries(groupSenderTitles)) {
        agents.push({ id: key, title: title });
    }
    if (agents.length === 0) {
        listEl.innerHTML = '<div style="padding:10px 14px;font-size:12px;color:#9ca3af;">群内暂无 Agent 成员</div>';
        popup.classList.add('show');
        return;
    }
    currentGroupMembers = agents;
    listEl.innerHTML = agents.map(a => {
        const sel = mentionSelectedIds.includes(a.id) ? ' selected' : '';
        const check = mentionSelectedIds.includes(a.id) ? '✓' : '';
        return `<div class="mention-item${sel}" data-id="${a.id}" onclick="toggleMentionItem(this, '${a.id}')">
            <div class="mention-check">${check}</div>
            <div class="mention-name" title="${a.title}">${a.title}</div>
        </div>`;
    }).join('');
    popup.classList.add('show');
}

function toggleMentionItem(el, agentId) {
    const idx = mentionSelectedIds.indexOf(agentId);
    if (idx >= 0) {
        mentionSelectedIds.splice(idx, 1);
        el.classList.remove('selected');
        el.querySelector('.mention-check').textContent = '';
    } else {
        mentionSelectedIds.push(agentId);
        el.classList.add('selected');
        el.querySelector('.mention-check').textContent = '✓';
    }
}

function confirmMention() {
    const popup = document.getElementById('mention-popup');
    popup.classList.remove('show');
    const input = document.getElementById('group-input');
    // 删掉输入框里刚输入的 @，替换为 @name 标签
    let val = input.value;
    // 找到最后一个 @ 的位置并替换
    const lastAt = val.lastIndexOf('@');
    if (lastAt >= 0) {
        const before = val.slice(0, lastAt);
        const after = val.slice(lastAt + 1);
        const tags = mentionSelectedIds.map(id => '@' + (groupSenderTitles[id] || id)).join(' ');
        input.value = before + tags + ' ' + after;
    }
    input.focus();
}

function hideMentionPopup() {
    document.getElementById('mention-popup').classList.remove('show');
}

// 点击输入区域外关闭弹层
document.addEventListener('click', function(e) {
    const popup = document.getElementById('mention-popup');
    const inputArea = document.querySelector('.group-input-area');
    if (popup && inputArea && !inputArea.contains(e.target)) {
        popup.classList.remove('show');
    }
});

async function switchPage(page) {
    currentPage = page;
    showPageLoading();
    // Update tabs
    document.getElementById('tab-chat').classList.toggle('active', page === 'chat');
    document.getElementById('tab-group').classList.toggle('active', page === 'group');
    document.getElementById('tab-orchestrate').classList.toggle('active', page === 'orchestrate');
    // Show/hide pages
    const chatPage = document.getElementById('page-chat');
    const groupPage = document.getElementById('page-group');
    const orchPage = document.getElementById('page-orchestrate');
    try {
        if (page === 'chat') {
            chatPage.classList.remove('hidden-page');
            chatPage.style.display = 'flex';
            groupPage.classList.remove('active');
            groupPage.classList.remove('mobile-chat-open');
            if (orchPage) orchPage.classList.remove('active');
            stopGroupPolling();
            stopGroupListPolling();
            // Lazy-init OpenClaw chat switcher on first visit to Chat tab
            if (!window._ocSwitcherInitialized && typeof ocInitSwitcher === 'function') {
                window._ocSwitcherInitialized = true;
                ocInitSwitcher();
            }
        } else if (page === 'group') {
            chatPage.classList.add('hidden-page');
            chatPage.style.display = 'none';
            groupPage.classList.add('active');
            if (orchPage) orchPage.classList.remove('active');
            await loadGroupList();
            startGroupListPolling();
            // 如果已有打开的群，恢复消息轮询
            if (currentGroupId) {
                startGroupPolling(currentGroupId);
            }
        } else if (page === 'orchestrate') {
            chatPage.classList.add('hidden-page');
            chatPage.style.display = 'none';
            groupPage.classList.remove('active');
            groupPage.classList.remove('mobile-chat-open');
            if (orchPage) orchPage.classList.add('active');
            stopGroupPolling();
            stopGroupListPolling();
            if (!window._orchInitialized) { orchInit(); window._orchInitialized = true; }
        }
    } finally {
        applyOasisTownMode();
        hidePageLoading();
    }
}

function stopGroupPolling() {
    if (groupPollingTimer) { clearInterval(groupPollingTimer); groupPollingTimer = null; }
}

let _groupListPollingTimer = null;
function startGroupListPolling() {
    stopGroupListPolling();
    _groupListPollingTimer = setInterval(() => {
        if (currentPage === 'group' && currentUserId) {
            loadGroupList();
        }
    }, 8000);
}
function stopGroupListPolling() {
    if (_groupListPollingTimer) { clearInterval(_groupListPollingTimer); _groupListPollingTimer = null; }
}

async function loadGroupList() {
    try {
        const resp = await fetch('/teams', { cache: 'no-store' });
        if (!resp.ok) return;
        const data = await resp.json();
        const teams = data.teams || [];
        renderGroupList(teams);
    } catch (e) {
        console.error('Failed to load teams:', e);
    }
}

function renderGroupList(teams) {
    const container = document.getElementById('group-list');
    const placeholder = document.getElementById('group-empty-placeholder');
    if (!teams || teams.length === 0) {
        container.innerHTML = `
            <div class="group-empty-state" style="padding:40px 0;">
                <div class="empty-icon">👥</div>
                <div class="empty-text">${t('group_no_groups')}</div>
            </div>`;
        // Update placeholder hint to "create or import"
        if (placeholder) {
            const hintEl = placeholder.querySelector('.empty-text');
            if (hintEl) {
                hintEl.textContent = t('group_create_hint');
                hintEl.setAttribute('data-i18n', 'group_create_hint');
            }
        }
        return;
    }
    // Has teams: restore placeholder hint to "select a team"
    if (placeholder) {
        const hintEl = placeholder.querySelector('.empty-text');
        if (hintEl) {
            hintEl.textContent = t('group_select_hint');
            hintEl.setAttribute('data-i18n', 'group_select_hint');
        }
    }
    container.innerHTML = teams.map(team => {
        const isActive = team === currentGroupId;
        return `
            <div class="group-item ${isActive ? 'active' : ''}" onclick="openGroup('${team}')">
                <div class="group-name">${escapeHtml(team)}</div>
                <div class="group-meta">点击进入群聊</div>
                <button class="group-delete-btn" onclick="event.stopPropagation(); deleteTeamByName('${team}')">🗑️</button>
            </div>`;
    }).join('');
}

async function openGroup(teamName) {
    showPageLoading();
    currentGroupId = teamName;
    groupLastMsgId = 0;
    groupRenderedMsgIds.clear();
    stopGroupPolling();

    // Mobile: switch to chat view
    document.getElementById('page-group').classList.add('mobile-chat-open');

    document.getElementById('group-empty-placeholder').style.display = 'none';
    const activeChat = document.getElementById('group-active-chat');
    activeChat.style.display = 'flex';

    // 设置团队名称和ID
    document.getElementById('group-active-name').textContent = teamName;
    document.getElementById('group-active-id').textContent = '#Team';

    // 清空消息框内容（保留成员表格）
    const box = document.getElementById('group-messages-box');
    box.innerHTML = '<div style="text-align:center;color:#9ca3af;padding:40px 0;font-size:13px;">暂无消息</div>' +
        '<div id="team-members-overlay" class="team-members-overlay" style="display:flex;">'+        '<div class="team-members-header">' +
        '<div style="display:flex;align-items:center;gap:8px;">' +
        '<button id="team-tab-members" onclick="switchTeamTab(\'members\')" style="padding:4px 12px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid #2563eb;background:#2563eb;color:white;">👥 成员</button>' +
        '<button id="team-tab-experts" onclick="switchTeamTab(\'experts\')" style="padding:4px 12px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid #d1d5db;background:#f9fafb;color:#374151;">🧑‍💼 人设池</button>' +
        '<button id="team-tab-workflows" onclick="switchTeamTab(\'workflows\')" style="padding:4px 12px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid #d1d5db;background:#f9fafb;color:#374151;">📂 工作流</button>' +
        '</div>' +
        '<div style="display:flex;gap:8px;align-items:center;">' +
        '<span id="team-tab-actions-members">' +
        '<button onclick="loadTeamMembers()" class="text-gray-400 hover:text-gray-600 hover:bg-gray-100 px-2 py-1 rounded transition-colors" title="刷新成员列表">🔄</button>' +
        '<button onclick="showAddTeamMemberModal()" class="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 px-3 py-1 rounded border border-blue-200" title="添加成员">➕ 添加成员</button>' +
        '</span>' +
        '<span id="team-tab-actions-experts" style="display:none;">' +
        '<button onclick="loadTeamExperts()" class="text-gray-400 hover:text-gray-600 hover:bg-gray-100 px-2 py-1 rounded transition-colors" title="刷新专家列表">🔄</button>' +
        '<button onclick="showAddTeamExpertModal()" class="text-xs bg-green-50 text-green-600 hover:bg-green-100 px-3 py-1 rounded border border-green-200" title="添加专家">➕ 创建专家</button>' +
        '</span>' +
        '<span id="team-tab-actions-workflows" style="display:none;">' +
        '<button onclick="loadTeamWorkflows()" class="text-gray-400 hover:text-gray-600 hover:bg-gray-100 px-2 py-1 rounded transition-colors" title="刷新工作流列表">🔄</button>' +
        '<button onclick="newTeamWorkflowOnCanvas()" class="text-xs bg-purple-50 text-purple-600 hover:bg-purple-100 px-3 py-1 rounded border border-purple-200" title="新建工作流（跳转画布）">➕ 创建工作流</button>' +
        '</span>' +
        '<button onclick="toggleTeamMembersView()" class="text-gray-400 hover:text-gray-600 text-sm">&times;</button>' +
        '</div>' +
        '</div>' +
        '<div id="team-panel-members" class="team-members-table-container">' +
        '<table class="team-members-table">' +
        '<thead>' +
        '<tr>' +
        '<th class="text-left">名称</th>' +
        '<th class="text-left">类型</th>' +
        '<th class="text-left">标签</th>' +
'<th class="text-left">Global Name</th>' +
        '<th class="text-right">操作</th>' +
        '</tr>' +
        '</thead>' +
        '<tbody id="team-members-table-body">' +
        '</tbody>' +
        '</table>' +
        '</div>' +
        '<div id="team-panel-experts" class="team-members-table-container" style="display:none;">' +
        '<table class="team-members-table">' +
        '<thead>' +
        '<tr>' +
        '<th class="text-left">名称</th>' +
        '<th class="text-left">标签 (Tag)</th>' +
        '<th class="text-left" style="max-width:300px;">人设 (Persona)</th>' +
        '<th class="text-center">温度</th>' +
        '<th class="text-right">操作</th>' +
        '</tr>' +
        '</thead>' +
        '<tbody id="team-experts-table-body">' +
        '</tbody>' +
        '</table>' +
        '</div>' +
        '<div id="team-panel-workflows" class="team-members-table-container" style="display:none;">' +
        '<table class="team-members-table">' +
        '<thead>' +
        '<tr>' +
        '<th class="text-left">工作流名称</th>' +
        '<th class="text-left">文件</th>' +
        '<th class="text-right">操作</th>' +
        '</tr>' +
        '</thead>' +
        '<tbody id="team-workflows-table-body">' +
        '</tbody>' +
        '</table>' +
        '</div>' +
        '</div>';

    // 清空成员列表
    document.getElementById('group-current-members').innerHTML = '<div class="text-xs text-gray-400 p-2">加载中...</div>';
    document.getElementById('group-available-sessions').innerHTML = '<div class="text-xs text-gray-400 p-2">加载中...</div>';

    // 默认加载并显示成员表
    await loadTeamMembers();

    // 更新团队列表选中状态
    await loadGroupList();
    hidePageLoading();
}

function groupBackToList() {
    document.getElementById('page-group').classList.remove('mobile-chat-open');
    // Close member panel if open
    if (groupMemberPanelOpen) toggleGroupMemberPanel();
}

function renderGroupMessages(messages) {
    const box = document.getElementById('group-messages-box');
    if (messages.length === 0) {
        box.innerHTML = '<div style="text-align:center;color:#9ca3af;padding:40px 0;font-size:13px;">暂无消息</div>';
        return;
    }
    box.innerHTML = messages.map(m => {
        const isSelf = m.sender === currentUserId || m.sender === currentUserId;
        const isAgent = !isSelf && m.sender_display;
        const msgClass = isSelf ? 'self' : (isAgent ? 'agent' : 'other');
        const displayName = isAgent ? (m.sender_display || getGroupSenderTitle(m.sender)) : m.sender;
        const timeStr = new Date(m.timestamp * 1000).toLocaleTimeString(currentLang === 'zh-CN' ? 'zh-CN' : 'en-US', {hour:'2-digit',minute:'2-digit'});
        return `
            <div class="group-msg ${msgClass}" ${isAgent ? 'data-agent-sender="'+escapeHtml(m.sender)+'"' : ''}>
                <div class="group-msg-sender">${escapeHtml(displayName)}</div>
                <div class="group-msg-content markdown-body">${marked.parse(m.content || '')}</div>
                <div class="group-msg-time">${timeStr}</div>
            </div>`;
    }).join('');
    box.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
    box.querySelectorAll('.group-msg.agent[data-agent-sender]').forEach(el => applyAgentColor(el, el.dataset.agentSender));
    box.scrollTop = box.scrollHeight;
}

// 已显示的消息 ID 集合，用于去重
const groupRenderedMsgIds = new Set();

function appendGroupMessages(messages) {
    const box = document.getElementById('group-messages-box');
    // Remove "no messages" placeholder if present
    const placeholder = box.querySelector('div[style*="text-align:center"]');
    if (placeholder && messages.length > 0) placeholder.remove();

    for (const m of messages) {
        // 去重：跳过已经渲染过的消息
        if (m.id && groupRenderedMsgIds.has(m.id)) {
            // 仍然更新 groupLastMsgId 以保持轮询指针正确
            if (m.id > groupLastMsgId) groupLastMsgId = m.id;
            continue;
        }
        if (m.id) groupRenderedMsgIds.add(m.id);

        const isSelf = m.sender === currentUserId;
        const isAgent = !isSelf && m.sender_display;
        const msgClass = isSelf ? 'self' : (isAgent ? 'agent' : 'other');
        const displayName = isAgent ? (m.sender_display || getGroupSenderTitle(m.sender)) : m.sender;
        const timeStr = new Date(m.timestamp * 1000).toLocaleTimeString(currentLang === 'zh-CN' ? 'zh-CN' : 'en-US', {hour:'2-digit',minute:'2-digit'});
        const div = document.createElement('div');
        div.className = `group-msg ${msgClass}`;
        div.innerHTML = `
            <div class="group-msg-sender">${escapeHtml(displayName)}</div>
            <div class="group-msg-content markdown-body">${marked.parse(m.content || '')}</div>
            <div class="group-msg-time">${timeStr}</div>`;
        div.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
        if (isAgent) applyAgentColor(div, m.sender);
        box.appendChild(div);
        if (m.id > groupLastMsgId) groupLastMsgId = m.id;
    }
    box.scrollTop = box.scrollHeight;
}

function startGroupPolling(groupId) {
    stopGroupPolling();
    groupPollingTimer = setInterval(async () => {
        if (currentGroupId !== groupId || currentPage !== 'group') {
            stopGroupPolling();
            return;
        }
        try {
            const resp = await fetch(`/proxy_groups/${groupId}/messages?after_id=${groupLastMsgId}`);
            if (!resp.ok) return;
            const data = await resp.json();
            if (data.messages && data.messages.length > 0) {
                appendGroupMessages(data.messages);
                // 有新消息时也刷新群列表（更新消息计数）
                loadGroupList();
            }
        } catch (e) {
            // silent
        }
    }, 5000);
}

async function sendGroupMessage() {
    const input = document.getElementById('group-input');
    const text = input.value.trim();
    if (!text || !currentGroupId) return;

    // 收集 mentions：从 mentionSelectedIds 中取出被 @ 的 agent
    const mentions = mentionSelectedIds.length > 0 ? [...mentionSelectedIds] : null;
    // 发送后清空 mention 选中状态
    mentionSelectedIds = [];
    hideMentionPopup();
    input.value = '';

    try {
        const body = { content: text };
        if (mentions) body.mentions = mentions;
        const resp = await fetch(`/proxy_groups/${currentGroupId}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        const result = await resp.json();
        const realId = result.id || (groupLastMsgId + 1);
        // Immediately show in UI with real server ID
        appendGroupMessages([{
            id: realId,
            sender: currentUserId,
            content: text,
            timestamp: Date.now() / 1000
        }]);
    } catch (e) {
        console.error('Failed to send group message:', e);
    }
}

function renderGroupMembers(members) {
    const container = document.getElementById('group-current-members');
    container.innerHTML = members.map(m => {
        const badge = m.is_agent
            ? `<span class="member-badge badge-agent">${t('group_agent')}</span>`
            : `<span class="member-badge badge-owner">${t('group_owner')}</span>`;
        let displayName = m.is_agent && m.title ? m.title : (m.user_id + (m.session_id !== 'default' ? '#' + m.session_id : ''));
        if (displayName.length > 7) displayName = displayName.slice(0, 7) + '…';
        return `
            <div class="member-item">
                <span class="member-name" title="${escapeHtml(m.user_id + '#' + m.session_id)}">${escapeHtml(displayName)}</span>
                ${badge}
            </div>`;
    }).join('');
}

let groupMemberPanelOpen = false;
function toggleGroupMemberPanel() {
    groupMemberPanelOpen = !groupMemberPanelOpen;
    document.getElementById('group-member-panel').style.display = groupMemberPanelOpen ? 'flex' : 'none';
    if (groupMemberPanelOpen && currentGroupId) {
        loadAvailableSessions();
    }
}

async function loadAvailableSessions() {
    const container = document.getElementById('group-available-sessions');
    container.innerHTML = '<div class="text-xs text-gray-400 p-2">' + t('loading') + '</div>';
    try {
        // Load sessions, group detail, and agent meta in parallel
        const [resp, agentMap] = await Promise.all([
            fetch(`/proxy_groups/${currentGroupId}/sessions`),
            _loadAgentMetaMap()
        ]);
        if (!resp.ok) return;
        const data = await resp.json();
        const sessions = data.sessions || [];

        // Get current members to mark them
        const detailResp = await fetch(`/proxy_groups/${currentGroupId}`);
        const detail = await detailResp.json();
        const memberSet = new Set((detail.members || []).map(m => m.user_id + '#' + m.session_id));

        if (sessions.length === 0) {
            container.innerHTML = '<div class="text-xs text-gray-400 p-2">' + t('group_no_sessions') + '</div>';
            return;
        }

        container.innerHTML = sessions.map(s => {
            const key = currentUserId + '#' + s.session_id;
            const checked = memberSet.has(key) ? 'checked' : '';
            const title = _resolveTitle(s.title || s.session_id, s.session_id, agentMap);
            return `
                <label class="session-checkbox">
                    <input type="checkbox" ${checked} onchange="toggleGroupAgent('${s.session_id}', this.checked)">
                    <span class="session-label" title="${escapeHtml(title)}">${escapeHtml(title)}</span>
                </label>`;
        }).join('');
    } catch (e) {
        container.innerHTML = '<div class="text-xs text-red-400 p-2">加载失败</div>';
    }
}

async function toggleGroupAgent(sessionId, add) {
    if (!currentGroupId) return;
    try {
        await fetch(`/proxy_groups/${currentGroupId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                members: [{
                    user_id: currentUserId,
                    session_id: sessionId,
                    action: add ? 'add' : 'remove'
                }]
            })
        });
        // Refresh member list
        const resp = await fetch(`/proxy_groups/${currentGroupId}`);
        const detail = await resp.json();
        renderGroupMembers(detail.members || []);
    } catch (e) {
        console.error('Failed to toggle group agent:', e);
    }
}

function showCreateTeamModal() {
    const modal = document.getElementById('create-team-modal');
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => {
            document.getElementById('team-name-input').focus();
        }, 100);
    }
}

function closeCreateTeamModal() {
    const modal = document.getElementById('create-team-modal');
    if (modal) modal.style.display = 'none';
}

async function submitCreateTeam() {
    const input = document.getElementById('team-name-input');
    const name = (input.value || '').trim();
    if (!name) {
        alert('请输入团队名称');
        return;
    }

    try {
        const resp = await fetch('/teams', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team: name })
        });
        if (!resp.ok) {
            const err = await resp.json();
            alert('创建失败: ' + (err.error || '未知错误'));
            return;
        }
        closeCreateTeamModal();
        await loadGroupList();
        openGroup(name);
    } catch (e) {
        alert('创建失败: ' + e.message);
    }
}

async function deleteTeamByName(teamName) {
    if (!confirm(`确定要删除团队 "${teamName}" 吗？`)) return;
    try {
        const resp = await fetch(`/teams/${encodeURIComponent(teamName)}`, {
            method: 'DELETE'
        });
        if (!resp.ok) {
            const err = await resp.json();
            alert('删除失败: ' + (err.error || '未知错误'));
            return;
        }
        if (currentGroupId === teamName) {
            currentGroupId = null;
            document.getElementById('group-active-chat').style.display = 'none';
            document.getElementById('group-empty-placeholder').style.display = 'flex';
            document.getElementById('page-group').classList.remove('mobile-chat-open');
            stopGroupPolling();
        }
        loadGroupList();
    } catch (e) {
        alert('删除失败: ' + e.message);
    }
}

function toggleTeamMembersView() {
    const overlay = document.getElementById('team-members-overlay');
    if (!overlay) return;
    
    if (overlay.style.display === 'none' || overlay.style.display === '') {
        overlay.style.display = 'flex';
        loadTeamMembers();
    } else {
        overlay.style.display = 'none';
    }
}

async function loadTeamMembers() {
    if (!currentGroupId) return;
    
    const tbody = document.getElementById('team-members-table-body');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-gray-400 py-8">加载中...</td></tr>';
    
    try {
        const resp = await fetch(`/teams/${encodeURIComponent(currentGroupId)}/members`, { cache: 'no-store' });
        if (!resp.ok) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-red-400 py-8">加载失败</td></tr>';
            return;
        }
        
        const data = await resp.json();
        const members = data.members || [];
        
        if (members.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-gray-400 py-8">暂无成员</td></tr>';
            return;
        }
        
        tbody.innerHTML = members.map(m => {
            let typeBadge;
            if (m.type === 'oasis') {
                typeBadge = '<span class="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded">Oasis</span>';
            } else if (m.tag === 'openclaw') {
                typeBadge = '<span class="text-xs bg-purple-50 text-purple-600 px-2 py-1 rounded">🦞 OpenClaw</span>';
            } else {
                typeBadge = '<span class="text-xs bg-green-50 text-green-600 px-2 py-1 rounded">Ext</span>';
            }
            const meta = m.meta || {};
            const apiUrl = meta.api_url || '';
            const apiKey = meta.api_key || '';
            const model = meta.model || '';
            const headers = meta.headers || {};
            const deleteTitle = (m.tag === 'openclaw' && !canDeleteOpenClawAgent(m.global_name || ''))
                ? '从团队移除（main 不会被真实删除）'
                : '删除成员';
            
            // For openclaw type, use the full orchestration config modal (files/tools/channels)
            const configBtn = m.tag === 'openclaw'
                ? `<button onclick="orchShowAgentConfigModal('${escapeHtml(m.global_name)}')" class="text-purple-500 hover:text-purple-700 text-xs px-2 py-1 rounded hover:bg-purple-50" title="OpenClaw 配置 (Files / Tools / Channels)">🦞⚙️</button>`
                : `<button onclick="showAgentConfigModal('${m.type}', '${escapeHtml(m.global_name)}', '${escapeHtml(m.name)}', '${escapeHtml(m.tag || '')}', '${escapeHtml(apiUrl)}', '${escapeHtml(apiKey)}', '${escapeHtml(model)}', '${escapeHtml(typeof headers === 'object' ? JSON.stringify(headers).replace(/"/g, '&quot;').replace(/'/g, "\\'") : headers)}')" class="text-blue-500 hover:text-blue-700 text-xs px-2 py-1 rounded hover:bg-blue-50" title="配置">⚙️</button>`;
            
            return `
                <tr>
                    <td class="font-medium text-gray-800">${escapeHtml(m.name)}</td>
                    <td>${typeBadge}</td>
                    <td>${escapeHtml(m.tag || '-')}</td>
                    <td class="font-mono text-xs text-gray-500">${escapeHtml(m.global_name || '-')}</td>
                    <td style="text-align:right;">
                        ${configBtn}
                        <button onclick="deleteTeamMember('${m.type}', '${escapeHtml(m.global_name)}', '${escapeHtml(m.name)}', '${escapeHtml(m.tag || '')}')" class="text-red-500 hover:text-red-700 text-xs px-2 py-1 rounded hover:bg-red-50" title="${deleteTitle}">🗑️</button>
                    </td>
                </tr>`;
        }).join('');
    } catch (e) {
        console.error('Failed to load team members:', e);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-red-400 py-8">加载失败: ' + e.message + '</td></tr>';
    }
}

// Store preview data for export
let _exportPreviewData = null;
let _exportSelectedSkills = new Set(); // Store selected skill IDs: "agent/skill" or "managed/skill"

/**
 * Toggle all skills based on the "select all" checkbox
 */
function toggleAllSkills(checked) {
    const checkboxes = document.querySelectorAll('.export-skill-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checked;
        const skillId = cb.getAttribute('data-skill-id');
        if (checked) {
            _exportSelectedSkills.add(skillId);
        } else {
            _exportSelectedSkills.delete(skillId);
        }
    });
}

/**
 * Toggle a single skill selection
 */
function toggleSkill(skillId, checked) {
    if (checked) {
        _exportSelectedSkills.add(skillId);
    } else {
        _exportSelectedSkills.delete(skillId);
    }
    // Update "select all" checkbox state
    updateSkillsSelectAllState();
}

/**
 * Update the "select all" checkbox state based on individual selections
 */
function updateSkillsSelectAllState() {
    const selectAllCheckbox = document.getElementById('export-skills-all');
    const checkboxes = document.querySelectorAll('.export-skill-checkbox');
    if (checkboxes.length === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
        return;
    }
    const checkedCount = document.querySelectorAll('.export-skill-checkbox:checked').length;
    if (checkedCount === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === checkboxes.length) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
    } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
    }
}

/**
 * Open export preview modal and load preview data
 * This function replaces the old direct download flow
 */
async function downloadTeam() {
    if (!currentGroupId) {
        alert('请先选择一个团队');
        return;
    }
    await openExportPreviewModal();
}

/**
 * Open the export preview modal (as dropdown from button)
 */
async function openExportPreviewModal() {
    const modal = document.getElementById('export-preview-modal');
    const dropdown = document.getElementById('export-preview-dropdown');
    const loadingEl = document.getElementById('export-preview-loading');
    const contentEl = document.getElementById('export-preview-content');
    const errorEl = document.getElementById('export-preview-error');
    const confirmBtn = document.getElementById('export-confirm-btn');
    
    // Position dropdown relative to export button
    const btn = document.getElementById('team-download-btn');
    if (btn && window.innerWidth > 480) {
        const rect = btn.getBoundingClientRect();
        // Position dropdown below the button, aligned to left
        dropdown.style.top = (rect.bottom + 8) + 'px';
        dropdown.style.left = rect.left + 'px';
        // Ensure it doesn't go off-screen
        const rightEdge = rect.left + 400; // min-width is 400px
        if (rightEdge > window.innerWidth) {
            dropdown.style.left = (rect.right - 400) + 'px';
        }
    }
    
    // Reset state
    loadingEl.style.display = 'block';
    contentEl.style.display = 'none';
    errorEl.style.display = 'none';
    errorEl.textContent = '';
    confirmBtn.disabled = true;
    _exportPreviewData = null;
    
    modal.style.display = 'block';
    
    // Load preview data
    try {
        const resp = await fetch('/teams/snapshot/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team: currentGroupId })
        });
        
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || '加载预览失败');
        }
        
        const data = await resp.json();
        _exportPreviewData = data;
        
        renderExportPreview(data);
        
        loadingEl.style.display = 'none';
        contentEl.style.display = 'block';
        confirmBtn.disabled = false;
    } catch (e) {
        loadingEl.style.display = 'none';
        errorEl.style.display = 'block';
        errorEl.textContent = '❌ ' + e.message;
    }
}

/**
 * Close the export preview modal
 */
function closeExportPreviewModal() {
    const modal = document.getElementById('export-preview-modal');
    const dropdown = document.getElementById('export-preview-dropdown');
    modal.style.display = 'none';
    // Clear position styles
    dropdown.style.top = '';
    dropdown.style.left = '';
    _exportPreviewData = null;
}

/**
 * Render preview data in the modal
 */
function renderExportPreview(data) {
    const sections = data.sections || {};
    
    // Agents
    const agents = sections.agents || { count: 0, items: [] };
    document.getElementById('export-agents-count').textContent = agents.count || 0;
    const agentsListEl = document.getElementById('export-agents-list');
    if (agents.items && agents.items.length > 0) {
        agentsListEl.innerHTML = agents.items.map(a => 
            `<div class="py-0.5">• ${escapeHtml(a.name)}${a.tag ? ` [${escapeHtml(a.tag)}]` : ''}</div>`
        ).join('');
    } else {
        agentsListEl.innerHTML = '<div class="text-gray-400 italic">' + t('export_preview_empty') + '</div>';
    }
    
    // Personas
    const personas = sections.personas || { count: 0, items: [] };
    document.getElementById('export-personas-count').textContent = personas.count || 0;
    const personasListEl = document.getElementById('export-personas-list');
    if (personas.items && personas.items.length > 0) {
        personasListEl.innerHTML = personas.items.map(p => 
            `<div class="py-0.5">• ${escapeHtml(p.name)}${p.tag !== p.name ? ` [${escapeHtml(p.tag)}]` : ''}</div>`
        ).join('');
    } else {
        personasListEl.innerHTML = '<div class="text-gray-400 italic">' + t('export_preview_empty') + '</div>';
    }
    
    // Skills - Render by agent with individual checkboxes
    const skills = sections.skills || { agents: [], details: [], managed: [] };
    let totalSkills = 0;
    const skillsListEl = document.getElementById('export-skills-list');
    let skillsHtml = '';
    
    // Calculate total and build HTML
    if (skills.details && skills.details.length > 0) {
        skills.details.forEach(d => {
            if (d.skills && d.skills.length > 0) {
                totalSkills += d.skills.length;
                const agentName = escapeHtml(d.agent);
                // Agent header
                skillsHtml += `<div class="mt-2 mb-1 font-medium text-gray-700 text-xs uppercase tracking-wide border-b border-gray-200 pb-1">${agentName}</div>`;
                // Skills for this agent
                d.skills.forEach(s => {
                    const skillId = `${d.agent}/${s}`;
                    const isChecked = _exportSelectedSkills.has(skillId);
                    skillsHtml += `
                        <div class="flex items-center gap-2 py-0.5 hover:bg-gray-100 rounded">
                            <input type="checkbox" id="skill-${escapeHtml(skillId.replace(/\//g, '-'))}" 
                                class="export-skill-checkbox" 
                                data-skill-id="${escapeHtml(skillId)}"
                                ${isChecked ? 'checked' : ''}
                                onchange="toggleSkill('${escapeHtml(skillId)}', this.checked)">
                            <label for="skill-${escapeHtml(skillId.replace(/\//g, '-'))}" class="text-gray-700 cursor-pointer select-none text-sm flex-1">
                                ${escapeHtml(s)}
                            </label>
                        </div>`;
                });
            }
        });
    }
    
    // Managed skills section
    if (skills.managed && skills.managed.length > 0) {
        totalSkills += skills.managed.length;
        skillsHtml += `<div class="mt-3 mb-1 font-medium text-gray-700 text-xs uppercase tracking-wide border-b border-gray-200 pb-1">${t('export_managed_skills')}</div>`;
        skills.managed.forEach(s => {
            const skillId = `managed/${s.name}`;
            const isChecked = _exportSelectedSkills.has(skillId);
            skillsHtml += `
                <div class="flex items-center gap-2 py-0.5 hover:bg-gray-100 rounded">
                    <input type="checkbox" id="skill-${escapeHtml(skillId.replace(/\//g, '-'))}" 
                        class="export-skill-checkbox" 
                        data-skill-id="${escapeHtml(skillId)}"
                        ${isChecked ? 'checked' : ''}
                        onchange="toggleSkill('${escapeHtml(skillId)}', this.checked)">
                    <label for="skill-${escapeHtml(skillId.replace(/\//g, '-'))}" class="text-gray-700 cursor-pointer select-none text-sm flex-1">
                        ${escapeHtml(s.name)}
                    </label>
                </div>`;
        });
    }
    
    if (!skillsHtml) {
        skillsHtml = '<div class="text-gray-400 italic p-2">' + t('export_preview_empty') + '</div>';
    }
    skillsListEl.innerHTML = skillsHtml;
    document.getElementById('export-skills-count').textContent = totalSkills;
    
    // Setup "select all" checkbox for skills
    const selectAllCheckbox = document.getElementById('export-skills-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.onchange = function() {
            toggleAllSkills(this.checked);
        };
        // Initial state
        updateSkillsSelectAllState();
    }
    
    // Cron
    const cron = sections.cron || {};
    let totalCron = 0;
    Object.values(cron).forEach(c => {
        if (c.count) totalCron += c.count;
    });
    document.getElementById('export-cron-count').textContent = totalCron;
    const cronListEl = document.getElementById('export-cron-list');
    let cronHtml = '';
    Object.entries(cron).forEach(([agent, info]) => {
        if (info.count > 0 && info.items) {
            cronHtml += `<div class="font-medium text-gray-700 mt-1">${escapeHtml(agent)}:</div>`;
            info.items.forEach(c => {
                cronHtml += `<div class="ml-3 py-0.5 text-xs">• ${escapeHtml(c.name)} <span class="text-gray-400">(${escapeHtml(c.schedule)})</span></div>`;
            });
        }
    });
    if (!cronHtml) {
        cronHtml = '<div class="text-gray-400 italic">' + t('export_preview_empty') + '</div>';
    }
    cronListEl.innerHTML = cronHtml;
    
    // Workflows
    const workflows = sections.workflows || { count: 0, items: [] };
    document.getElementById('export-workflows-count').textContent = workflows.count || 0;
    const workflowsListEl = document.getElementById('export-workflows-list');
    if (workflows.items && workflows.items.length > 0) {
        workflowsListEl.innerHTML = workflows.items.map(w => 
            `<div class="py-0.5 truncate" title="${escapeHtml(w)}">• ${escapeHtml(w)}</div>`
        ).join('');
    } else {
        workflowsListEl.innerHTML = '<div class="text-gray-400 italic">' + t('export_preview_empty') + '</div>';
    }
}

/**
 * Confirm export with selected options
 */
async function confirmExportTeam() {
    if (!currentGroupId || !_exportPreviewData) return;
    
    // Get selected sections
    const include = {
        agents: document.getElementById('export-agents').checked,
        personas: document.getElementById('export-personas').checked,
        skills: document.getElementById('export-skills-all').checked,
        cron: document.getElementById('export-cron').checked,
        workflows: document.getElementById('export-workflows').checked
    };
    
    // Handle granular skills selection - only if some skills are selected but not all
    const skills = _exportPreviewData.sections?.skills || { details: [], managed: [] };
    let allSkillsCount = 0;
    skills.details?.forEach(d => { if (d.skills) allSkillsCount += d.skills.length; });
    if (skills.managed) allSkillsCount += skills.managed.length;
    
    // If skills section is enabled but not all skills selected, use granular mode
    if (include.skills && _exportSelectedSkills.size > 0 && _exportSelectedSkills.size < allSkillsCount) {
        // Build granular skills selection map
        const granularSkills = {};
        _exportSelectedSkills.forEach(skillId => {
            const [agent, ...skillParts] = skillId.split('/');
            const skillName = skillParts.join('/'); // skill name might contain '/'
            if (!granularSkills[agent]) {
                granularSkills[agent] = [];
            }
            granularSkills[agent].push(skillName);
        });
        include.skills = granularSkills;
    }
    
    // Check if at least one is selected
    const hasSelection = Object.values(include).some(v => {
        if (typeof v === 'object') return Object.keys(v).length > 0;
        return v;
    });
    if (!hasSelection) {
        alert(t('export_none_selected'));
        return;
    }
    
    const confirmBtn = document.getElementById('export-confirm-btn');
    const originalText = confirmBtn.textContent;
    confirmBtn.disabled = true;
    confirmBtn.textContent = '⏳ ' + t('export_downloading');
    
    try {
        const resp = await fetch('/teams/snapshot/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team: currentGroupId, include })
        });
        if (!resp.ok) {
            const err = await resp.json();
            alert('导出失败: ' + (err.error || '未知错误'));
            return;
        }
        const blob = await resp.blob();
        const disposition = resp.headers.get('Content-Disposition') || '';
        let filename = `team_${currentGroupId}_snapshot.zip`;
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // Close modal after successful download
        closeExportPreviewModal();
        
        // Show success toast if available
        if (window.orchToast) {
            window.orchToast(t('orch_toast_snapshot_downloaded'));
        }
    } catch (e) {
        alert('导出失败: ' + e.message);
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = originalText;
    }
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function uploadTeam(input) {
    const file = input.files[0];
    if (!file) return;
    
    if (!confirm(`确定要上传并恢复团队快照吗？这将覆盖当前团队的内部Agent配置。`)) {
        input.value = '';
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('team', currentGroupId);

    try {
        const resp = await fetch('/teams/snapshot/upload', {
            method: 'POST',
            body: formData
        });
        if (!resp.ok) {
            const err = await resp.json();
            alert('上传失败: ' + (err.error || '未知错误'));
            return;
        }
        alert('上传成功！');
        loadGroupList();
        loadTeamMembers();
    } catch (e) {
        alert('上传失败: ' + e.message);
    }
    input.value = '';
}

// ── Import team dropdown & Hub import ──

function toggleImportDropdown() {
    const dd = document.getElementById('import-dropdown');
    if (dd.style.display === 'none' || !dd.style.display) {
        dd.style.display = 'block';
        // Close when clicking outside
        setTimeout(() => {
            document.addEventListener('click', _closeImportDropdownOutside, { once: true, capture: true });
        }, 0);
    } else {
        dd.style.display = 'none';
    }
}

function closeImportDropdown() {
    const dd = document.getElementById('import-dropdown');
    if (dd) dd.style.display = 'none';
}

function _closeImportDropdownOutside(e) {
    const dd = document.getElementById('import-dropdown');
    const btn = document.getElementById('team-upload-btn');
    if (dd && !dd.contains(e.target) && btn && !btn.contains(e.target)) {
        dd.style.display = 'none';
    }
}

function showHubImportModal() {
    const modal = document.getElementById('hub-import-modal');
    if (modal) modal.style.display = 'flex';
}

function closeHubImportModal() {
    const modal = document.getElementById('hub-import-modal');
    if (modal) modal.style.display = 'none';
    const input = document.getElementById('hub-curl-input');
    if (input) input.value = '';
}

// Parse curl command or URL to extract download link and team name
function _parseHubInput(raw) {
    raw = raw.trim();
    let url = '';
    let teamName = '';

    // Match URL in curl command: curl ... 'URL' or curl ... "URL" or curl ... URL
    const curlMatch = raw.match(/curl\s+.*?(?:-[A-Za-z]\s+)*['"]?(https?:\/\/[^\s'"]+)['"]?/);
    if (curlMatch) {
        url = curlMatch[1];
    } else if (raw.startsWith('http://') || raw.startsWith('https://')) {
        url = raw.split(/\s/)[0];
    }

    if (!url) return { url: '', teamName: '' };

    // Infer team name from URL: /api/workflows/<name>/download → <name>
    const wfMatch = url.match(/\/api\/workflows\/([^/]+)\/download/);
    if (wfMatch) teamName = wfMatch[1];

    // Also try from -o parameter: -o team_xxx.zip → xxx
    const outMatch = raw.match(/-o\s+['"]?team_([^.\s'"]+)/);
    if (outMatch && !teamName) teamName = outMatch[1];

    return { url, teamName };
}

async function importFromHub() {
    const raw = document.getElementById('hub-curl-input').value;
    if (!raw.trim()) {
        alert('请粘贴下载命令或 URL');
        return;
    }

    const { url, teamName } = _parseHubInput(raw);
    if (!url) {
        alert('无法解析出有效的下载链接，请检查格式');
        return;
    }

    let finalTeam = teamName;
    if (!finalTeam) {
        finalTeam = prompt('无法从命令中推断团队名，请输入团队名称：');
        if (!finalTeam || !finalTeam.trim()) return;
        finalTeam = finalTeam.trim();
    }

    if (!confirm(`将从 Hub 下载并导入团队 "${finalTeam}"，确定继续吗？`)) return;

    try {
        const resp = await fetch('/teams/snapshot/import_from_url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, team: finalTeam })
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            alert('导入失败: ' + (err.error || resp.statusText));
            return;
        }
        alert('✅ 导入成功！');
        closeHubImportModal();
        loadGroupList();
    } catch (e) {
        alert('导入失败: ' + e.message);
    }
}

// Track ongoing deletion to prevent double-clicks
let _deletingTeamMember = false;

function canDeleteOpenClawAgent(agentName) {
    return !!agentName && agentName.toLowerCase() !== 'main';
}

async function removeTeamExternalMember(teamName, globalName) {
    const resp = await fetch(`/teams/${encodeURIComponent(teamName)}/members/external`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ global_name: globalName })
    });
    const result = await resp.json().catch(() => ({}));
    if (!resp.ok) {
        throw new Error(result.error || '删除失败');
    }
    return result;
}

async function deleteTeamMember(type, globalName, name, tag) {
    if (!currentGroupId) return;
    if (_deletingTeamMember) return; // Prevent double-click

    const isOpenClaw = tag === 'openclaw';
    const canDeleteRealOpenClaw = isOpenClaw && canDeleteOpenClawAgent(globalName || '');
    const confirmMsg = isOpenClaw
        ? (canDeleteRealOpenClaw
            ? `确定要删除成员 "${name}"？\n这会同时删除真实的 OpenClaw Agent "${globalName}"。`
            : `确定要将成员 "${name}" 从团队移除？\nmain Agent 不会被真实删除，只会解除团队绑定。`)
        : `确定要删除成员 "${name}"？`;

    if (!confirm(confirmMsg)) {
        return;
    }
    
    _deletingTeamMember = true;
    
    // Show loading state on the delete button (use data-id to find the correct button)
    // Since we're re-rendering the list, just disable all delete buttons in the members table
    const tbody = document.getElementById('team-members-table-body');
    if (tbody) {
        const deleteBtns = tbody.querySelectorAll('button[onclick*="deleteTeamMember"]');
        deleteBtns.forEach(btn => {
            btn.disabled = true;
            btn.dataset.originalText = btn.textContent;
            btn.textContent = '⏳';
        });
    }
    
    try {
        if (type === 'oasis') {
            const url = `/internal_agents/${encodeURIComponent(globalName)}?team=${encodeURIComponent(currentGroupId)}`;
            const resp = await fetch(url, { method: 'DELETE' });
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.error || '删除失败');
            }
        } else if (isOpenClaw) {
            if (canDeleteRealOpenClaw) {
                const agentResp = await fetch('/proxy_openclaw_remove', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: globalName })
                });
                const agentResult = await agentResp.json().catch(() => ({}));
                if (!agentResp.ok || !agentResult.ok) {
                    throw new Error(agentResult.error || '删除 OpenClaw Agent 失败');
                }
            }
            await removeTeamExternalMember(currentGroupId, globalName);
        } else {
            // External agent: remove from external_agents.json
            await removeTeamExternalMember(currentGroupId, globalName);
        }
        
        // Use non-blocking toast instead of alert
        if (typeof orchToast === 'function') {
            if (isOpenClaw && canDeleteRealOpenClaw) {
                orchToast(`成员 "${name}" 和 OpenClaw Agent 已删除`);
            } else if (isOpenClaw) {
                orchToast(`成员 "${name}" 已从团队移除`);
            } else {
                orchToast(`成员 "${name}" 已删除`);
            }
        }
        
        // Reload the list - this will clear and re-render the table
        await loadTeamMembers();
        
        // Ensure members overlay stays visible after refresh
        const membersOverlay = document.getElementById('team-members-overlay');
        if (membersOverlay) membersOverlay.style.display = 'flex';
    } catch (e) {
        console.error('Failed to delete team member:', e);
        if (typeof orchToast === 'function') {
            orchToast('删除失败: ' + e.message);
        } else {
            alert('删除失败: ' + e.message);
        }
    } finally {
        _deletingTeamMember = false;
        // Restore button states
        const tbody = document.getElementById('team-members-table-body');
        if (tbody) {
            const deleteBtns = tbody.querySelectorAll('button[onclick*="deleteTeamMember"]');
            deleteBtns.forEach(btn => {
                btn.disabled = false;
                if (btn.dataset.originalText) {
                    btn.textContent = btn.dataset.originalText;
                }
            });
        }
    }
}

function showAddTeamMemberModal() {
    if (!currentGroupId) {
        alert('请先选择一个团队');
        return;
    }
    
    const overlay = document.createElement('div');
    overlay.className = 'orch-modal-overlay';
    overlay.id = 'add-team-member-overlay';
    overlay.innerHTML = `
        <div class="orch-modal" style="min-width:380px;max-width:460px;">
            <h3>➕ 添加成员</h3>
            
            <div style="display:flex;gap:6px;margin-bottom:12px;">
                <button id="tab-oasis" onclick="switchAddMemberTab('oasis')" style="flex:1;padding:7px;border:1px solid #d1d5db;border-radius:6px;background:#2563eb;color:white;font-size:11px;cursor:pointer;">Oasis</button>
                <button id="tab-openclaw" onclick="switchAddMemberTab('openclaw')" style="flex:1;padding:7px;border:1px solid #d1d5db;border-radius:6px;background:#f9fafb;color:#374151;font-size:11px;cursor:pointer;">🦞 OpenClaw</button>
                <button id="tab-external" onclick="switchAddMemberTab('external')" style="flex:1;padding:7px;border:1px solid #d1d5db;border-radius:6px;background:#f9fafb;color:#374151;font-size:11px;cursor:pointer;">External</button>
            </div>
            
            <!-- Oasis Agent Form -->
            <div id="form-oasis">
                <div style="display:flex;flex-direction:column;gap:8px;">
                    <label style="font-size:11px;font-weight:600;color:#374151;">名称
                        <input id="add-oasis-name" type="text" placeholder="输入Agent名称" style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;">
                    </label>
                    <label style="font-size:11px;font-weight:600;color:#374151;">标签 (Tag)
                        <select id="add-oasis-tag" style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;background:white;">
                            <option value="">(无标签)</option>
                        </select>
                    </label>
                    <label style="font-size:11px;font-weight:600;color:#374151;">工具 (Tools)
                        <div style="display:flex;gap:4px;margin:4px 0;">
                            <button type="button" onclick="document.querySelectorAll('.add-oasis-tool-cb').forEach(c=>c.checked=true)" style="font-size:10px;padding:2px 8px;border:1px solid #d1d5db;border-radius:4px;background:#f0fdf4;color:#16a34a;cursor:pointer;">全选</button>
                            <button type="button" onclick="document.querySelectorAll('.add-oasis-tool-cb').forEach(c=>c.checked=false)" style="font-size:10px;padding:2px 8px;border:1px solid #d1d5db;border-radius:4px;background:#fef2f2;color:#dc2626;cursor:pointer;">全不选</button>
                        </div>
                        <div id="add-oasis-tools-container" style="max-height:120px;overflow-y:auto;border:1px solid #d1d5db;border-radius:6px;padding:6px;display:flex;flex-wrap:wrap;gap:4px;margin-top:2px;">
                            <span style="color:#9ca3af;font-size:11px;">加载中...</span>
                        </div>
                    </label>
                    <div id="add-oasis-drop-zone" style="border:2px dashed #d1d5db;border-radius:8px;padding:12px;text-align:center;font-size:11px;color:#9ca3af;cursor:default;transition:all .15s;">
                        📦 拖入专家设置标签
                    </div>
                </div>
                <div class="orch-modal-btns" style="margin-top:12px;">
                    <button onclick="document.getElementById('add-team-member-overlay').remove()" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">取消</button>
                    <button onclick="showImportOasisModal()" style="padding:6px 14px;border-radius:6px;border:1px solid #2563eb;background:#eff6ff;color:#2563eb;cursor:pointer;font-size:12px;">📥 导入已有</button>
                    <button onclick="addOasisMember(event)" style="padding:6px 14px;border-radius:6px;border:none;background:#2563eb;color:white;cursor:pointer;font-size:12px;">新建</button>
                </div>
            </div>
            
            <!-- External Agent Form -->
            <div id="form-external" style="display:none;">
                <div style="display:flex;flex-direction:column;gap:8px;">
                    <label style="font-size:11px;font-weight:600;color:#374151;">名称
                        <input id="add-ext-name" type="text" placeholder="输入Agent名称" style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;">
                    </label>
                    <label style="font-size:11px;font-weight:600;color:#374151;">Global Name
                        <input id="add-ext-global-name" type="text" placeholder="输入Global Name" style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;">
                    </label>
                    <label style="font-size:11px;font-weight:600;color:#374151;">标签 (Tag)
                        <div style="display:flex;gap:4px;margin-top:2px;">
                            <select id="add-ext-tag-select" onchange="document.getElementById('add-ext-tag-custom').value=this.value" style="flex:1;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;background:white;">
                                <option value="">(无标签)</option>
                                <option value="codex">codex</option>
                                <option value="claude-code">claude-code</option>
                                <option value="gemini-cli">gemini-cli</option>
                                <option value="aider">aider</option>
                                <option value="custom">自定义...</option>
                            </select>
                            <input id="add-ext-tag-custom" type="text" placeholder="或输入自定义tag" style="flex:1;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;">
                        </div>
                    </label>
                    <label style="font-size:11px;color:#9ca3af;margin-bottom:2px;margin-top:8px;display:block;">API URL *</label>
                    <input id="add-ext-url" type="text" placeholder="https://api.example.com/v1" style="font-family:monospace;font-size:12px;width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;">
                    <label style="font-size:11px;color:#9ca3af;margin-bottom:2px;margin-top:8px;display:block;">API Key</label>
                    <input id="add-ext-key" type="text" placeholder="sk-xxx (optional)" style="font-family:monospace;font-size:12px;width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;">
                    <label style="font-size:11px;color:#9ca3af;margin-bottom:2px;margin-top:8px;display:block;">Model</label>
                    <input id="add-ext-model" type="text" placeholder="gpt-4 / deepseek-chat (optional)" style="font-family:monospace;font-size:12px;width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;">
                    <label style="font-size:11px;color:#9ca3af;margin-bottom:2px;margin-top:8px;display:block;">Headers (JSON)</label>
                    <textarea id="add-ext-headers" placeholder='{"X-Custom": "value"}' style="font-family:monospace;font-size:11px;min-height:60px;width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;resize:vertical;"></textarea>
                </div>
                <div class="orch-modal-btns" style="margin-top:12px;">
                    <button onclick="document.getElementById('add-team-member-overlay').remove()" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">取消</button>
                    <button onclick="addExternalMember(event)" style="padding:6px 14px;border-radius:6px;border:none;background:#10b981;color:white;cursor:pointer;font-size:12px;">添加</button>
                </div>
            </div>

            <!-- OpenClaw Agent Form -->
            <div id="form-openclaw" style="display:none;">
                <div style="display:flex;flex-direction:column;gap:8px;">
                    <label style="font-size:11px;font-weight:600;color:#374151;">
                        Team内名称
                        <input id="add-oc-name" type="text" placeholder="work, research, coding"
                               style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;"
                               pattern="[a-zA-Z0-9_-]+" title="仅支持字母、数字、下划线、短横线">
                        <div style="font-size:10px;color:#6b7280;margin-top:3px;">
                            🔗 Global Name 将自动生成为 <b>${escapeHtml(currentGroupId)}_&lt;名称&gt;</b>
                        </div>
                    </label>
                    <label style="font-size:11px;font-weight:600;color:#374151;">
                        工作空间路径
                        <div style="display:flex;gap:4px;align-items:center;margin-top:2px;">
                            <input id="add-oc-workspace" type="text" placeholder="加载中..."
                                   style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:11px;font-family:monospace;color:#374151;">
                            <button id="add-oc-ws-reset" type="button" title="重置"
                                    style="padding:4px 6px;border:1px solid #d1d5db;border-radius:4px;background:#f9fafb;cursor:pointer;font-size:11px;white-space:nowrap;">↺</button>
                        </div>
                    </label>
                    <div style="font-size:10px;color:#6b7280;background:#f9fafb;border-radius:6px;padding:8px;">
                        📂 工作空间是OpenClaw Agent存储文件和配置的地方，建议使用绝对路径
                    </div>
                    <div style="border:1px dashed #c4b5fd;border-radius:8px;padding:10px;background:#faf5ff;">
                        <div style="display:flex;align-items:center;justify-content:space-between;">
                            <span style="font-size:11px;font-weight:600;color:#7c3aed;">📥 导入专家人设 (可选)</span>
                            <button id="add-oc-pick-expert" type="button" style="padding:3px 10px;border-radius:4px;border:1px solid #8b5cf6;background:#f5f3ff;color:#7c3aed;cursor:pointer;font-size:10px;font-weight:500;">选择专家</button>
                        </div>
                        <div id="add-oc-expert-preview" style="display:none;margin-top:8px;padding:6px 8px;background:white;border-radius:6px;border:1px solid #e5e7eb;font-size:11px;color:#374151;"></div>
                    </div>
                </div>
                <div class="orch-modal-btns" style="margin-top:12px;">
                    <button onclick="document.getElementById('add-team-member-overlay').remove()" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">取消</button>
                    <button onclick="showImportOpenClawModal()" style="padding:6px 14px;border-radius:6px;border:1px solid #7c3aed;background:#faf5ff;color:#7c3aed;cursor:pointer;font-size:12px;">📥 导入已有</button>
                    <button onclick="addOpenClawMember()" style="padding:6px 14px;border-radius:6px;border:none;background:#7c3aed;color:white;cursor:pointer;font-size:12px;">🦞 新建</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Load expert tags for Oasis Agent select options
    (async () => {
        try {
            const r = await fetch('/proxy_visual/experts');
            const experts = await r.json();
            const tags = [...new Set(experts.map(e => e.tag).filter(Boolean))];
            const options = '<option value="">(无标签)</option>' +
                tags.map(t => `<option value="${t}">${t}</option>`).join('');
            
            const oasisTagSelect = document.getElementById('add-oasis-tag');
            if (oasisTagSelect) oasisTagSelect.innerHTML = options;
        } catch (e) {
            console.warn('Failed to load expert tags', e);
        }

        // Populate tools checkboxes for Oasis Agent
        const toolsContainer = document.getElementById('add-oasis-tools-container');
        if (toolsContainer && allTools.length > 0) {
            toolsContainer.innerHTML = allTools.map(t =>
                `<label style="display:inline-flex;align-items:center;gap:3px;font-size:10px;padding:2px 5px;border:1px solid #e5e7eb;border-radius:4px;cursor:pointer;background:#f9fafb;white-space:nowrap;" title="${escapeHtml(t.description || '')}">
                    <input type="checkbox" class="add-oasis-tool-cb" value="${escapeHtml(t.name)}" checked style="margin:0;">
                    ${escapeHtml(t.name)}
                </label>`
            ).join('');
        } else if (toolsContainer) {
            toolsContainer.innerHTML = '<span style="color:#9ca3af;font-size:11px;">无可用工具</span>';
        }
    })();
    
    // Setup drop zone for Oasis Agent
    const dropZone = document.getElementById('add-oasis-drop-zone');
    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            dropZone.style.borderColor = '#2563eb';
            dropZone.style.background = '#eff6ff';
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = '#d1d5db';
            dropZone.style.background = '';
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#d1d5db';
            dropZone.style.background = '';
            try {
                const data = JSON.parse(e.dataTransfer.getData('application/json'));
                if (data.tag && data.tag !== 'manual' && data.tag !== 'conditional') {
                    const tagSelect = document.getElementById('add-oasis-tag');
                    tagSelect.value = data.tag;
                    dropZone.innerHTML = '✅ Tag: <b>' + escapeHtml(data.tag) + '</b> (' + escapeHtml(data.name || '') + ')';
                    dropZone.style.borderColor = '#2563eb';
                    dropZone.style.color = '#374151';
                }
            } catch(err) {}
        });
    }

    // ── OpenClaw Agent Form Setup ──
    const ocNameInp = document.getElementById('add-oc-name');
    const ocWsInp = document.getElementById('add-oc-workspace');
    let ocParentDir = '';
    let ocWsManualEdit = false;

    // Fetch default workspace parent dir
    fetch('/proxy_openclaw_default_workspace').then(r => r.json()).then(res => {
        if (res.ok && res.parent_dir) {
            ocParentDir = res.parent_dir;
            // If name already typed, populate workspace
            const wn = _ocWsAgentName();
            if (wn && !ocWsManualEdit) {
                ocWsInp.value = ocParentDir + '/workspace-' + wn;
            }
            ocWsInp.placeholder = ocParentDir + '/workspace-...';
        } else {
            ocWsInp.placeholder = '请输入工作空间路径';
        }
    }).catch(() => { ocWsInp.placeholder = '请输入工作空间路径'; });

    // Derive workspace-friendly agent name (includes team prefix)
    function _ocWsAgentName() {
        const n = ocNameInp.value.trim();
        if (!n) return '';
        return currentGroupId ? (currentGroupId + '_' + n) : n;
    }

    // Name changes → auto-update workspace (unless user has manually edited it)
    ocNameInp.addEventListener('input', () => {
        ocNameInp.style.borderColor = '#d1d5db';
        ocNameInp.style.background = '';
        if (!ocWsManualEdit) {
            const wn = _ocWsAgentName();
            if (wn) {
                ocWsInp.value = (ocParentDir || '') + '/workspace-' + wn;
            } else {
                ocWsInp.value = '';
            }
        }
    });

    // Track manual workspace edits
    ocWsInp.addEventListener('input', () => { ocWsManualEdit = true; });

    // Reset button: revert workspace to auto-derived value
    overlay.querySelector('#add-oc-ws-reset').addEventListener('click', () => {
        ocWsManualEdit = false;
        const wn = _ocWsAgentName();
        ocWsInp.value = wn ? ((ocParentDir || '') + '/workspace-' + wn) : '';
        ocWsInp.style.borderColor = '#d1d5db';
    });

    // Expert import picker
    const ocExpertPreview = overlay.querySelector('#add-oc-expert-preview');
    overlay.querySelector('#add-oc-pick-expert').addEventListener('click', () => {
        showExpertPickerForTeam((expert) => {
            const content = '# ' + (expert.name || expert.tag) + '\n\n' + (expert.persona || '');
            // Store selected expert content on the button for later access
            overlay.querySelector('#add-oc-pick-expert')._selectedExpertContent = content;
            
            ocExpertPreview.style.display = 'block';
            ocExpertPreview.innerHTML = '<div style="display:flex;align-items:center;gap:6px;"><span style="font-size:16px;">' + (expert.emoji || '⭐') + '</span><span style="font-weight:600;">' + escapeHtml(expert.name) + '</span><button id="add-oc-clear-expert" type="button" style="margin-left:auto;padding:1px 6px;border:1px solid #d1d5db;border-radius:4px;background:#f9fafb;cursor:pointer;font-size:10px;color:#6b7280;">✕</button></div>'
                + '<div style="font-size:10px;color:#6b7280;margin-top:4px;max-height:60px;overflow:hidden;white-space:pre-wrap;word-break:break-all;">' + escapeHtml((expert.persona || '').slice(0, 120) + ((expert.persona || '').length > 120 ? '…' : '')) + '</div>';
            ocExpertPreview.querySelector('#add-oc-clear-expert').addEventListener('click', (ev) => {
                ev.stopPropagation();
                overlay.querySelector('#add-oc-pick-expert')._selectedExpertContent = null;
                ocExpertPreview.style.display = 'none';
                ocExpertPreview.innerHTML = '';
            });
        });
    });
    
    // Click outside to close
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.remove();
        }
    });
}

function switchAddMemberTab(tab) {
    document.getElementById('form-oasis').style.display = tab === 'oasis' ? 'block' : 'none';
    document.getElementById('form-external').style.display = tab === 'external' ? 'block' : 'none';
    document.getElementById('form-openclaw').style.display = tab === 'openclaw' ? 'block' : 'none';
    
    document.getElementById('tab-oasis').style.background = tab === 'oasis' ? '#2563eb' : '#f9fafb';
    document.getElementById('tab-oasis').style.color = tab === 'oasis' ? 'white' : '#374151';
    document.getElementById('tab-openclaw').style.background = tab === 'openclaw' ? '#7c3aed' : '#f9fafb';
    document.getElementById('tab-openclaw').style.color = tab === 'openclaw' ? 'white' : '#374151';
    document.getElementById('tab-external').style.background = tab === 'external' ? '#10b981' : '#f9fafb';
    document.getElementById('tab-external').style.color = tab === 'external' ? 'white' : '#374151';
}

async function addOasisMember(event) {
    const btn = event ? event.target : null;
    if (btn && btn.disabled) return;
    
    const name = document.getElementById('add-oasis-name').value.trim();
    const tag = document.getElementById('add-oasis-tag').value.trim();
    
    if (!name) {
        if (typeof orchToast === 'function') {
            orchToast('请输入Agent名称');
        } else {
            alert('请输入Agent名称');
        }
        return;
    }

    // Collect tools from checkboxes
    const toolCbs = document.querySelectorAll('.add-oasis-tool-cb');
    let tools = null;
    if (toolCbs.length > 0) {
        const checked = [];
        toolCbs.forEach(cb => { if (cb.checked) checked.push(cb.value); });
        if (checked.length < allTools.length) {
            // Not all selected → build whitelist object
            const obj = {};
            checked.forEach(t => obj[t] = true);
            tools = obj;
        }
        // If all selected → tools stays null (no restriction)
    }
    
    // Generate automatic session ID (UUID format)
    const session = 'oc_' + Date.now().toString(36) + Math.random().toString(36).substring(2, 11);
    
    // Disable button and show loading
    if (btn) {
        btn.disabled = true;
        btn.dataset.originalText = btn.textContent;
        btn.textContent = '⏳ 创建中...';
    }
    
    try {
        const url = `/internal_agents?team=${encodeURIComponent(currentGroupId)}`;
        const meta = { name: name, tag: tag || '' };
        if (tools !== null) meta.tools = tools;
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session: session,
                meta: meta
            })
        });
        
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || '添加失败');
        }
        
        if (typeof orchToast === 'function') {
            orchToast('成员添加成功');
        }
        document.getElementById('add-team-member-overlay').remove();
        await loadTeamMembers();
        // Ensure members overlay stays visible after refresh
        const membersOverlay = document.getElementById('team-members-overlay');
        if (membersOverlay) membersOverlay.style.display = 'flex';
    } catch (e) {
        console.error('Failed to add team member:', e);
        if (typeof orchToast === 'function') {
            orchToast('添加失败: ' + e.message);
        } else {
            alert('添加失败: ' + e.message);
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            if (btn.dataset.originalText) {
                btn.textContent = btn.dataset.originalText;
            }
        }
    }
}

async function addExternalMember(event) {
    const btn = event ? event.target : null;
    if (btn && btn.disabled) return;
    
    const name = document.getElementById('add-ext-name').value.trim();
    const globalName = document.getElementById('add-ext-global-name').value.trim();
    const apiUrl = document.getElementById('add-ext-url').value.trim();
    const apiKey = document.getElementById('add-ext-key').value.trim();
    const model = document.getElementById('add-ext-model').value.trim();
    const headersStr = document.getElementById('add-ext-headers').value.trim();

    // Collect tag: custom input takes priority, then select
    const tagCustom = document.getElementById('add-ext-tag-custom').value.trim();
    const tagSelect = document.getElementById('add-ext-tag-select').value;
    const tag = tagCustom || (tagSelect !== 'custom' ? tagSelect : '');
    
    if (!name || !globalName) {
        if (typeof orchToast === 'function') {
            orchToast('请输入名称和Global Name');
        } else {
            alert('请输入名称和Global Name');
        }
        return;
    }
    
    if (!apiUrl) {
        if (typeof orchToast === 'function') {
            orchToast('API URL 不能为空');
        } else {
            alert('API URL 不能为空');
        }
        return;
    }
    
    let headers = {};
    if (headersStr) {
        try {
            headers = JSON.parse(headersStr);
        } catch (e) {
            if (typeof orchToast === 'function') {
                orchToast('Headers JSON 解析错误: ' + e.message);
            } else {
                alert('Headers JSON 解析错误: ' + e.message);
            }
            return;
        }
    }
    
    // Disable button and show loading
    if (btn) {
        btn.disabled = true;
        btn.dataset.originalText = btn.textContent;
        btn.textContent = '⏳ 添加中...';
    }
    
    try {
        const url = `/teams/${encodeURIComponent(currentGroupId)}/members/external`;
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                tag: tag,
                global_name: globalName,
                api_url: apiUrl,
                api_key: apiKey,
                model: model,
                headers: headers
            })
        });
        
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || '添加失败');
        }
        
        if (typeof orchToast === 'function') {
            orchToast('成员添加成功');
        }
        document.getElementById('add-team-member-overlay').remove();
        await loadTeamMembers();
        // Ensure members overlay stays visible after refresh
        const membersOverlay = document.getElementById('team-members-overlay');
        if (membersOverlay) membersOverlay.style.display = 'flex';
    } catch (e) {
        console.error('Failed to add external team member:', e);
        if (typeof orchToast === 'function') {
            orchToast('添加失败: ' + e.message);
        } else {
            alert('添加失败: ' + e.message);
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            if (btn.dataset.originalText) {
                btn.textContent = btn.dataset.originalText;
            }
        }
    }
}

async function deleteGroup(groupId) {    if (!confirm(t('group_delete_confirm'))) return;
    try {
        await fetch(`/proxy_groups/${groupId}`, {
            method: 'DELETE'
        });
        if (currentGroupId === groupId) {
            currentGroupId = null;
            document.getElementById('group-active-chat').style.display = 'none';
            document.getElementById('group-empty-placeholder').style.display = 'flex';
            document.getElementById('page-group').classList.remove('mobile-chat-open');
            stopGroupPolling();
        }
        loadGroupList();
    } catch (e) {
        alert('删除失败: ' + e.message);
    }
}

function updateMuteButton() {
    const btn = document.getElementById('group-mute-btn');
    if (!btn) return;
    if (groupMuted) {
        btn.textContent = t('group_unmute');
        btn.style.background = '#f0fdf4';
        btn.style.color = '#16a34a';
        btn.style.borderColor = '#bbf7d0';
    } else {
        btn.textContent = t('group_mute');
        btn.style.background = '#fef2f2';
        btn.style.color = '#dc2626';
        btn.style.borderColor = '#fecaca';
    }
}

async function loadGroupMuteStatus(groupId) {
    try {
        const resp = await fetch(`/proxy_groups/${groupId}/mute_status`);
        if (resp.ok) {
            const data = await resp.json();
            groupMuted = data.muted;
            updateMuteButton();
        }
    } catch (e) { console.error('Failed to load mute status:', e); }
}

async function toggleGroupMute() {
    if (!currentGroupId) return;
    const action = groupMuted ? 'unmute' : 'mute';
    try {
        const resp = await fetch(`/proxy_groups/${currentGroupId}/${action}`, {
            method: 'POST'
        });
        if (resp.ok) {
            groupMuted = !groupMuted;
            updateMuteButton();
        }
    } catch (e) { console.error('Failed to toggle mute:', e); }
}

// ===== Orchestration Mobile Toggle Functions =====
function orchToggleMobileSidebar() {
    const sidebar = document.querySelector('.orch-sidebar');
    const backdrop = document.getElementById('orch-mobile-backdrop');
    const rightPanel = document.querySelector('.orch-right-panel');
    if (rightPanel) rightPanel.classList.remove('mobile-open');
    sidebar.classList.toggle('mobile-open');
    backdrop.classList.toggle('active', sidebar.classList.contains('mobile-open'));
}

function orchToggleMobilePanel() {
    const panel = document.querySelector('.orch-right-panel');
    const backdrop = document.getElementById('orch-mobile-backdrop');
    const sidebar = document.querySelector('.orch-sidebar');
    if (sidebar) sidebar.classList.remove('mobile-open');
    panel.classList.toggle('mobile-open');
    backdrop.classList.toggle('active', panel.classList.contains('mobile-open'));
}

function orchCloseMobilePanels() {
    const sidebar = document.querySelector('.orch-sidebar');
    const panel = document.querySelector('.orch-right-panel');
    const backdrop = document.getElementById('orch-mobile-backdrop');
    if (sidebar) sidebar.classList.remove('mobile-open');
    if (panel) panel.classList.remove('mobile-open');
    if (backdrop) backdrop.classList.remove('active');
}

function toggleOrchExpertList() {
    // No-op: collapse feature removed
}

function toggleOrchFocusMode() {
    const sidebar = document.querySelector('.orch-sidebar');
    const panel = document.querySelector('.orch-right-panel');
    const btn = document.getElementById('orch-focus-btn');
    const isFocused = sidebar.classList.contains('focus-hidden');
    sidebar.classList.toggle('focus-hidden', !isFocused);
    panel.classList.toggle('focus-hidden', !isFocused);
    if (btn) btn.classList.toggle('focus-active', !isFocused);
}

// Agent 配置模态框
let currentConfigAgent = null;

async function showAgentConfigModal(type, globalName, name, tag, api_url, api_key, model, headers) {
    currentConfigAgent = { type, globalName, name, tag, api_url, api_key, model, headers };
    
    // Create modal dynamically like orchestration page
    const overlay = document.createElement('div');
    overlay.className = 'orch-modal-overlay';
    overlay.id = 'agent-config-overlay';
    
    const typeLabel = type === 'oasis' ? 'Oasis Agent' : 'External Agent';
    
    // External Agent form fields (like orchestration page)
    const externalForm = type === 'external' ? `
        <label style="font-size:11px;color:#9ca3af;margin-bottom:2px;margin-top:8px;display:block;">API URL *</label>
        <input id="config-ext-url" type="text" value="${escapeHtml(api_url || '')}" placeholder="https://api.example.com/v1" style="font-family:monospace;font-size:12px;width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;">
        <label style="font-size:11px;color:#9ca3af;margin-bottom:2px;margin-top:8px;display:block;">API Key</label>
        <input id="config-ext-key" type="text" value="${escapeHtml(api_key || '')}" placeholder="sk-xxx (optional)" style="font-family:monospace;font-size:12px;width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;">
        <label style="font-size:11px;color:#9ca3af;margin-bottom:2px;margin-top:8px;display:block;">Model</label>
        <input id="config-ext-model" type="text" value="${escapeHtml(model || '')}" placeholder="gpt-4 / deepseek-chat (optional)" style="font-family:monospace;font-size:12px;width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;">
        <label style="font-size:11px;color:#9ca3af;margin-bottom:2px;margin-top:8px;display:block;">Headers (JSON)</label>
        <textarea id="config-ext-headers" placeholder='{"X-Custom": "value"}' style="font-family:monospace;font-size:11px;min-height:60px;width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;resize:vertical;">${escapeHtml(typeof headers === 'object' ? JSON.stringify(headers, null, 2) : headers || '')}</textarea>
    ` : '';
    
    // Oasis Agent tag section
    const tagSection = type === 'oasis' ? `
        <label style="font-size:11px;font-weight:600;color:#374151;">标签 (Tag)</label>
        <select id="config-agent-tag" style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;background:white;">
            <option value="">(无标签)</option>
        </select>
        <div id="config-tag-drop-zone" style="border:2px dashed #d1d5db;border-radius:8px;padding:12px;text-align:center;font-size:11px;color:#9ca3af;cursor:default;transition:all .15s;margin-top:8px;">
            📦 拖入专家设置标签
        </div>
    ` : '';
    
    overlay.innerHTML = `
        <div class="orch-modal" style="min-width:380px;max-width:460px;">
            <h3>⚙️ ${type === 'external' ? '🌐 ' : ''}配置成员 — ${typeLabel}</h3>
            <div style="display:flex;flex-direction:column;gap:8px;margin:10px 0;">
                <label style="font-size:11px;font-weight:600;color:#374151;">类型</label>
                <div id="config-agent-type" style="padding:6px 8px;background:#f3f4f6;border-radius:6px;font-size:12px;color:#374151;">${typeLabel}</div>
                
                <label style="font-size:11px;font-weight:600;color:#374151;">名称</label>
                <input id="config-agent-name" type="text" placeholder="输入成员名称" style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;">
                
                ${tagSection}
                ${externalForm}
                
                <label style="font-size:11px;font-weight:600;color:#374151;">Global Name</label>
                <input id="config-agent-global-name" type="text" value="${globalName}" disabled style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;background:#f3f4f6;cursor:not-allowed;color:#9ca3af;">
            </div>
            <div class="orch-modal-btns">
                <button id="config-cancel" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">取消</button>
                <button id="config-save" style="padding:6px 14px;border-radius:6px;border:none;background:${type === 'external' ? '#10b981' : '#2563eb'};color:white;cursor:pointer;font-size:12px;">保存</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Set initial values
    document.getElementById('config-agent-name').value = name;
    
    // Setup event handlers
    overlay.querySelector('#config-cancel').addEventListener('click', () => {
        overlay.remove();
        currentConfigAgent = null;
    });
    
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.remove();
            currentConfigAgent = null;
        }
    });
    
    overlay.querySelector('#config-save').addEventListener('click', async () => {
        const newName = document.getElementById('config-agent-name').value.trim();
        
        if (!newName) {
            alert('名称不能为空');
            return;
        }
        
        const meta = { name: newName };
        
        // Oasis Agent: save tag
        if (type === 'oasis') {
            const newTag = document.getElementById('config-agent-tag').value.trim();
            meta.tag = newTag;
        } else {
            // External Agent: save api_url, api_key, model, headers
            const extUrl = document.getElementById('config-ext-url').value.trim();
            if (!extUrl) {
                alert('API URL 不能为空');
                return;
            }
            meta.api_url = extUrl;
            meta.api_key = document.getElementById('config-ext-key').value.trim();
            meta.model = document.getElementById('config-ext-model').value.trim();
            
            const hdrsStr = document.getElementById('config-ext-headers').value.trim();
            if (hdrsStr) {
                try {
                    meta.headers = JSON.parse(hdrsStr);
                } catch (e) {
                    alert('Headers JSON 解析错误: ' + e.message);
                    return;
                }
            } else {
                meta.headers = {};
            }
        }
        
        try {
            const url = `/internal_agents/${encodeURIComponent(globalName)}?team=${encodeURIComponent(currentGroupId)}`;
            const resp = await fetch(url, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ meta })
            });
            
            if (!resp.ok) {
                const err = await resp.json();
                alert('保存失败: ' + (err.error || '未知错误'));
                return;
            }
            
            alert('保存成功！');
            overlay.remove();
            currentConfigAgent = null;
            loadTeamMembers();
        } catch (e) {
            alert('保存失败: ' + e.message);
        }
    });
    
    // Load expert tags for Oasis Agent
    if (type === 'oasis') {
        try {
            const r = await fetch('/proxy_visual/experts');
            const experts = await r.json();
            const tags = [...new Set(experts.map(e => e.tag).filter(Boolean))];
            const tagSelect = document.getElementById('config-agent-tag');
            tagSelect.innerHTML = '<option value="">(无标签)</option>' +
                tags.map(t => `<option value="${t}">${t}</option>`).join('');
            tagSelect.value = tag || '';
        } catch (e) {
            console.warn('Failed to load expert tags', e);
        }
        
        // Setup drop zone for expert tags
        const dropZone = document.getElementById('config-tag-drop-zone');
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            dropZone.style.borderColor = '#2563eb';
            dropZone.style.background = '#eff6ff';
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = '#d1d5db';
            dropZone.style.background = '';
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#d1d5db';
            dropZone.style.background = '';
            try {
                const data = JSON.parse(e.dataTransfer.getData('application/json'));
                if (data.tag && data.tag !== 'manual' && data.tag !== 'conditional') {
                    const tagSelect = document.getElementById('config-agent-tag');
                    tagSelect.value = data.tag;
                dropZone.innerHTML = '✅ Tag: <b>' + escapeHtml(data.tag) + '</b> (' + escapeHtml(data.name || '') + ')';
                    dropZone.style.borderColor = '#2563eb';
                    dropZone.style.color = '#374151';
                }
            } catch(err) {}
        });
    }
}

// ── Expert Picker for Team Page ──
async function showExpertPickerForTeam(onSelect) {
    const overlay = document.createElement('div');
    overlay.className = 'orch-modal-overlay';
    overlay.id = 'team-expert-picker-overlay';
    overlay.style.zIndex = '10001';
    overlay.innerHTML = `
        <div class="orch-modal" style="min-width:360px;max-width:520px;width:85vw;max-height:75vh;display:flex;flex-direction:column;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <h3 style="margin:0;font-size:14px;">📥 选择专家</h3>
                <button id="team-ep-close" style="background:none;border:none;font-size:18px;cursor:pointer;padding:2px 6px;color:#6b7280;">✕</button>
            </div>
            <input id="team-ep-search" type="text" placeholder="搜索专家..." style="padding:4px 8px;border:1px solid #d1d5db;border-radius:4px;font-size:11px;margin-bottom:8px;">
            <div id="team-ep-list" style="flex:1;overflow-y:auto;min-height:0;display:flex;flex-direction:column;gap:4px;">
                <div style="text-align:center;color:#9ca3af;padding:20px;font-size:11px;">⏳ 加载中...</div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    overlay.querySelector('#team-ep-close').addEventListener('click', () => overlay.remove());
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

    const listEl = overlay.querySelector('#team-ep-list');
    const searchInput = overlay.querySelector('#team-ep-search');
    let allExperts = [];

    try {
        const r = await fetch('/proxy_visual/experts');
        allExperts = await r.json();
    } catch(e) {
        listEl.innerHTML = '<div style="color:#ef4444;padding:20px;text-align:center;font-size:11px;">❌ 网络错误</div>';
        return;
    }

    function renderList(filter) {
        listEl.innerHTML = '';
        const keyword = (filter || '').toLowerCase();
        const filtered = keyword ? allExperts.filter(ex =>
            (ex.name||'').toLowerCase().includes(keyword) ||
            (ex.tag||'').toLowerCase().includes(keyword) ||
            (ex.persona||'').toLowerCase().includes(keyword) ||
            (ex.category||'').toLowerCase().includes(keyword)
        ) : allExperts;

        if (filtered.length === 0) {
            listEl.innerHTML = '<div style="text-align:center;color:#9ca3af;padding:20px;font-size:11px;">无结果</div>';
            return;
        }

        const groups = { public: [], agency: [], custom: [] };
        filtered.forEach(ex => {
            const src = ex.source || 'public';
            if (groups[src]) groups[src].push(ex); else groups.public.push(ex);
        });
        const groupLabels = {
            public: { icon: '🌟', label: '公共专家' },
            agency: { icon: '🏢', label: '机构专家' },
            custom: { icon: '🛠️', label: '自定义' },
        };

        for (const [src, items] of Object.entries(groups)) {
            if (items.length === 0) continue;
            const info = groupLabels[src] || { icon: '📂', label: src };
            const header = document.createElement('div');
            header.style.cssText = 'font-size:10px;font-weight:600;color:#6b7280;padding:4px 0;margin-top:4px;';
            header.textContent = info.icon + ' ' + info.label + ' (' + items.length + ')';
            listEl.appendChild(header);

            for (const ex of items) {
                const row = document.createElement('div');
                row.style.cssText = 'display:flex;align-items:flex-start;gap:8px;padding:8px 10px;border:1px solid #e5e7eb;border-radius:8px;cursor:pointer;transition:all .15s;background:#fff;';
                row.addEventListener('mouseenter', () => { row.style.background = '#f5f3ff'; row.style.borderColor = '#c4b5fd'; });
                row.addEventListener('mouseleave', () => { row.style.background = '#fff'; row.style.borderColor = '#e5e7eb'; });
                const personaPreview = (ex.persona || '').length > 80 ? (ex.persona.slice(0, 80) + '…') : (ex.persona || '-');
                row.innerHTML = `
                    <span style="font-size:18px;flex-shrink:0;">${ex.emoji || '⭐'}</span>
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:12px;font-weight:600;color:#1f2937;">${escapeHtml(ex.name)}</div>
                        <div style="font-size:10px;color:#6b7280;margin-top:1px;">${escapeHtml(ex.tag)}${ex.category ? ' · ' + escapeHtml(ex.category) : ''}</div>
                        <div style="font-size:10px;color:#9ca3af;margin-top:3px;line-height:1.4;white-space:pre-wrap;word-break:break-all;">${escapeHtml(personaPreview)}</div>
                    </div>
                    <span style="font-size:14px;color:#7c3aed;flex-shrink:0;margin-top:2px;">→</span>
                `;
                row.addEventListener('click', () => {
                    if (typeof onSelect === 'function') onSelect(ex);
                    overlay.remove();
                });
                listEl.appendChild(row);
            }
        }
    }

    renderList('');
    searchInput.addEventListener('input', () => renderList(searchInput.value));
    setTimeout(() => searchInput.focus(), 100);
}

// ── Team Tab Switching (Members / Experts / Workflows) ──
function switchTeamTab(tab) {
    const btnMembers = document.getElementById('team-tab-members');
    const btnExperts = document.getElementById('team-tab-experts');
    const btnWorkflows = document.getElementById('team-tab-workflows');
    const panelMembers = document.getElementById('team-panel-members');
    const panelExperts = document.getElementById('team-panel-experts');
    const panelWorkflows = document.getElementById('team-panel-workflows');
    const actionsMembers = document.getElementById('team-tab-actions-members');
    const actionsExperts = document.getElementById('team-tab-actions-experts');
    const actionsWorkflows = document.getElementById('team-tab-actions-workflows');
    if (!btnMembers || !btnExperts) return;

    // Reset all tabs to inactive
    const inactiveStyle = {background: '#f9fafb', color: '#374151', borderColor: '#d1d5db'};
    [btnMembers, btnExperts, btnWorkflows].forEach(btn => {
        if (btn) { btn.style.background = inactiveStyle.background; btn.style.color = inactiveStyle.color; btn.style.borderColor = inactiveStyle.borderColor; }
    });
    if (panelMembers) panelMembers.style.display = 'none';
    if (panelExperts) panelExperts.style.display = 'none';
    if (panelWorkflows) panelWorkflows.style.display = 'none';
    if (actionsMembers) actionsMembers.style.display = 'none';
    if (actionsExperts) actionsExperts.style.display = 'none';
    if (actionsWorkflows) actionsWorkflows.style.display = 'none';

    if (tab === 'experts') {
        btnExperts.style.background = '#7c3aed'; btnExperts.style.color = 'white'; btnExperts.style.borderColor = '#7c3aed';
        if (panelExperts) panelExperts.style.display = '';
        if (actionsExperts) actionsExperts.style.display = '';
        loadTeamExperts();
    } else if (tab === 'workflows') {
        if (btnWorkflows) { btnWorkflows.style.background = '#059669'; btnWorkflows.style.color = 'white'; btnWorkflows.style.borderColor = '#059669'; }
        if (panelWorkflows) panelWorkflows.style.display = '';
        if (actionsWorkflows) actionsWorkflows.style.display = '';
        loadTeamWorkflows();
    } else {
        btnMembers.style.background = '#2563eb'; btnMembers.style.color = 'white'; btnMembers.style.borderColor = '#2563eb';
        if (panelMembers) panelMembers.style.display = '';
        if (actionsMembers) actionsMembers.style.display = '';
        loadTeamMembers();
    }
}

// ── Load Team Experts ──
async function loadTeamExperts() {
    if (!currentGroupId) return;
    const tbody = document.getElementById('team-experts-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-gray-400 py-8">加载中...</td></tr>';

    try {
        const resp = await fetch(`/teams/${encodeURIComponent(currentGroupId)}/experts`, { cache: 'no-store' });
        if (!resp.ok) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-red-400 py-8">加载失败</td></tr>';
            return;
        }
        const data = await resp.json();
        const experts = data.experts || [];
        if (experts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-gray-400 py-8">暂无专家，点击 ➕ 添加</td></tr>';
            return;
        }
        tbody.innerHTML = experts.map(e => {
            const personaPreview = (e.persona || '').length > 80 ? (e.persona.slice(0, 80) + '…') : (e.persona || '-');
            return `
                <tr>
                    <td class="font-medium text-gray-800">${escapeHtml(e.name)}</td>
                    <td class="font-mono text-xs text-gray-500">${escapeHtml(e.tag)}</td>
                    <td style="max-width:300px;white-space:pre-wrap;word-break:break-all;font-size:11px;color:#6b7280;">${escapeHtml(personaPreview)}</td>
                    <td class="text-center text-xs text-gray-500">${e.temperature ?? 0.7}</td>
                    <td style="text-align:right;white-space:nowrap;">
                        <button onclick="editTeamExpert('${escapeHtml(e.tag)}')" class="text-blue-500 hover:text-blue-700 text-xs px-2 py-1 rounded hover:bg-blue-50" title="编辑">✏️</button>
                        <button onclick="deleteTeamExpert('${escapeHtml(e.tag)}', '${escapeHtml(e.name)}')" class="text-red-500 hover:text-red-700 text-xs px-2 py-1 rounded hover:bg-red-50" title="删除">🗑️</button>
                    </td>
                </tr>`;
        }).join('');
    } catch (err) {
        console.error('Failed to load team experts:', err);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-red-400 py-8">加载失败: ' + err.message + '</td></tr>';
    }
}

// ── Load Team Workflows ──
async function loadTeamWorkflows() {
    if (!currentGroupId) return;
    const tbody = document.getElementById('team-workflows-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="3" class="text-center text-gray-400 py-8">加载中...</td></tr>';

    try {
        const resp = await fetch(`/proxy_visual/load-layouts?team=${encodeURIComponent(currentGroupId)}`, { cache: 'no-store' });
        if (!resp.ok) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-red-400 py-8">加载失败</td></tr>';
            return;
        }
        const workflows = await resp.json();
        if (!workflows || workflows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-gray-400 py-8">暂无工作流（在编排页面保存后会出现在这里）</td></tr>';
            return;
        }
        tbody.innerHTML = workflows.map(name => {
            const safeName = escapeHtml(name);
            return `
                <tr>
                    <td class="font-medium text-gray-800">📂 ${safeName}</td>
                    <td class="font-mono text-xs text-gray-500">${safeName}.yaml</td>
                    <td style="text-align:right;white-space:nowrap;">
<button onclick="viewTeamWorkflowYaml('${safeName}')" class="text-blue-500 hover:text-blue-700 text-xs px-2 py-1 rounded hover:bg-blue-50" title="在画布中查看">👁️ 查看</button>
                        <button onclick="deleteTeamWorkflow('${safeName}')" class="text-red-500 hover:text-red-700 text-xs px-2 py-1 rounded hover:bg-red-50" title="删除">🗑️</button>
                    </td>
                </tr>`;
        }).join('');
    } catch (err) {
        console.error('Failed to load team workflows:', err);
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-red-400 py-8">加载失败: ' + err.message + '</td></tr>';
    }
}

// ── View Team Workflow on Canvas ──
async function viewTeamWorkflowYaml(name) {
    if (!currentGroupId) return;
    try {
        // Switch to orchestrate page
        switchPage('orchestrate');
        // Ensure orchestration is initialized
        if (!window._orchInitialized) { orchInit(); window._orchInitialized = true; }
        // Load team list and set team context
        await orchLoadTeamList();
        orch.teamName = currentGroupId;
        orch.teamEnabled = true;
        orchShowTeamButtons(true);
        const sel = document.getElementById('orch-team-select');
        if (sel) sel.value = currentGroupId;
        // Refresh sidebar agents/experts for the team
        orchLoadExperts();
        orchLoadSessionAgents();
        orchLoadOpenClawSessions();
        // Load the workflow onto the canvas
        await orchDoLoadLayout(name);
    } catch (err) {
        alert('加载失败: ' + err.message);
    }
}

// ── Delete Team Workflow ──
async function deleteTeamWorkflow(name) {
    if (!currentGroupId) return;
    if (!confirm(`确定删除工作流 "${name}" 吗？此操作不可撤销。`)) return;
    try {
        const resp = await fetch(`/proxy_visual/delete-layout/${encodeURIComponent(name)}?team=${encodeURIComponent(currentGroupId)}`, { method: 'DELETE' });
        if (resp.ok) {
            loadTeamWorkflows();
        } else {
            alert('删除失败');
        }
    } catch (err) {
        alert('删除失败: ' + err.message);
    }
}

// ── New Team Workflow on Canvas ──
function newTeamWorkflowOnCanvas() {
    if (!currentGroupId) { alert('请先选择一个团队'); return; }
    // Switch to orchestrate page
    switchPage('orchestrate');
    // Ensure orchestration is initialized
    if (!window._orchInitialized) { orchInit(); window._orchInitialized = true; }
    // Load team list and set team context
    orchLoadTeamList().then(() => {
        orch.teamName = currentGroupId;
        orch.teamEnabled = true;
        orchShowTeamButtons(true);
        const sel = document.getElementById('orch-team-select');
        if (sel) sel.value = currentGroupId;
        // Refresh sidebar agents/experts for the team
        orchLoadExperts();
        orchLoadSessionAgents();
        orchLoadOpenClawSessions();
        // Clear canvas for a fresh new workflow
        orchClearCanvas();
    });
}

// ── Show Add/Edit Team Expert Modal ──
function showAddTeamExpertModal(editData) {
    if (!currentGroupId) { alert('请先选择一个团队'); return; }
    const isEdit = !!editData;
    const title = isEdit ? '✏️ 编辑团队专家' : '➕ 添加团队专家';
    const btnLabel = isEdit ? '保存' : '添加';
    const btnColor = isEdit ? '#2563eb' : '#7c3aed';

    const overlay = document.createElement('div');
    overlay.className = 'orch-modal-overlay';
    overlay.id = 'team-expert-modal-overlay';
    overlay.innerHTML = `
        <div class="orch-modal" style="min-width:400px;max-width:520px;width:85vw;">
            <h3 style="margin:0 0 12px;font-size:14px;">${title}</h3>
            <div style="display:flex;flex-direction:column;gap:8px;">
                <label style="font-size:11px;font-weight:600;color:#374151;">名称
                    <input id="te-name" type="text" placeholder="专家名称" value="${escapeHtml((editData && editData.name) || '')}" style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;">
                </label>
                <label style="font-size:11px;font-weight:600;color:#374151;">标签 (Tag)
                    <input id="te-tag" type="text" placeholder="唯一标识符，如 creative, analyst" value="${escapeHtml((editData && editData.tag) || '')}" ${isEdit ? 'disabled style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;background:#f3f4f6;color:#6b7280;"' : 'style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;"'}>
                </label>
                <label style="font-size:11px;font-weight:600;color:#374151;">人设 (Persona)
                    <textarea id="te-persona" placeholder="描述这个专家的角色、性格和专长..." style="width:100%;min-height:120px;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;resize:vertical;font-family:inherit;line-height:1.5;">${escapeHtml((editData && editData.persona) || '')}</textarea>
                </label>
                <label style="font-size:11px;font-weight:600;color:#374151;">温度 (Temperature)
                    <input id="te-temperature" type="number" min="0" max="2" step="0.1" value="${(editData && editData.temperature) ?? 0.7}" style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;">
                </label>
                ${!isEdit ? '<div style="border:1px dashed #c4b5fd;border-radius:8px;padding:10px;background:#faf5ff;"><div style="display:flex;align-items:center;justify-content:space-between;"><span style="font-size:11px;font-weight:600;color:#7c3aed;">📥 从全局专家库导入 (可选)</span><button id="te-import-btn" type="button" style="padding:3px 10px;border-radius:4px;border:1px solid #8b5cf6;background:#f5f3ff;color:#7c3aed;cursor:pointer;font-size:10px;font-weight:500;">选择专家</button></div><div id="te-import-preview" style="display:none;margin-top:8px;padding:6px 8px;background:white;border-radius:6px;border:1px solid #e5e7eb;font-size:11px;color:#374151;"></div></div>' : ''}
            </div>
            <div class="orch-modal-btns" style="margin-top:12px;">
                <button onclick="document.getElementById('team-expert-modal-overlay').remove()" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">取消</button>
                <button id="te-submit-btn" style="padding:6px 14px;border-radius:6px;border:none;background:${btnColor};color:white;cursor:pointer;font-size:12px;">${btnLabel}</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

    // Import from global expert pool (only for add mode)
    if (!isEdit) {
        const importBtn = overlay.querySelector('#te-import-btn');
        if (importBtn) {
            importBtn.addEventListener('click', () => {
                showExpertPickerForTeam((expert) => {
                    document.getElementById('te-name').value = expert.name || '';
                    document.getElementById('te-tag').value = expert.tag || '';
                    document.getElementById('te-persona').value = expert.persona || '';
                    document.getElementById('te-temperature').value = expert.temperature ?? 0.7;
                    const preview = overlay.querySelector('#te-import-preview');
                    if (preview) {
                        preview.style.display = 'block';
                        preview.innerHTML = '✅ 已导入: <b>' + escapeHtml(expert.name) + '</b> (' + escapeHtml(expert.tag) + ')';
                    }
                });
            });
        }
    }

    // Submit handler
    overlay.querySelector('#te-submit-btn').addEventListener('click', async () => {
        const name = document.getElementById('te-name').value.trim();
        const tag = document.getElementById('te-tag').value.trim();
        const persona = document.getElementById('te-persona').value.trim();
        const temperature = parseFloat(document.getElementById('te-temperature').value) || 0.7;

        if (!name || !tag || !persona) {
            alert('名称、标签和人设都不能为空');
            return;
        }

        try {
            const url = isEdit
                ? `/teams/${encodeURIComponent(currentGroupId)}/experts/${encodeURIComponent(tag)}`
                : `/teams/${encodeURIComponent(currentGroupId)}/experts`;
            const method = isEdit ? 'PUT' : 'POST';
            const resp = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, tag, persona, temperature })
            });
            const result = await resp.json();
            if (!resp.ok) {
                alert(result.error || '操作失败');
                return;
            }
            overlay.remove();
            loadTeamExperts();
        } catch (err) {
            alert('网络错误: ' + err.message);
        }
    });
}

// ── Edit Team Expert ──
async function editTeamExpert(tag) {
    if (!currentGroupId) return;
    try {
        const resp = await fetch(`/teams/${encodeURIComponent(currentGroupId)}/experts`);
        if (!resp.ok) { alert('加载失败'); return; }
        const data = await resp.json();
        const expert = (data.experts || []).find(e => e.tag === tag);
        if (!expert) { alert('未找到专家 tag=' + tag); return; }
        showAddTeamExpertModal(expert);
    } catch (err) {
        alert('网络错误: ' + err.message);
    }
}

// ── Delete Team Expert ──
async function deleteTeamExpert(tag, name) {
    if (!confirm(`删除团队专家 "${name}" (${tag})？`)) return;
    try {
        const resp = await fetch(`/teams/${encodeURIComponent(currentGroupId)}/experts/${encodeURIComponent(tag)}`, {
            method: 'DELETE'
        });
        const result = await resp.json();
        if (!resp.ok) {
            alert(result.error || '删除失败');
            return;
        }
        loadTeamExperts();
    } catch (err) {
        alert('网络错误: ' + err.message);
    }
}

// ── Add OpenClaw Member Function ──
async function addOpenClawMember() {
    const overlay = document.getElementById('add-team-member-overlay');
    if (!overlay) return;

    const ocNameInp = document.getElementById('add-oc-name');
    const ocWsInp = document.getElementById('add-oc-workspace');
    
    const shortName = ocNameInp.value.trim();
    const workspace = ocWsInp.value.trim();
    
    if (!shortName) {
        if (typeof orchToast === 'function') {
            orchToast('请输入Agent名称');
        } else {
            alert('请输入Agent名称');
        }
        return;
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(shortName)) {
        if (typeof orchToast === 'function') {
            orchToast('名称只能包含字母、数字、下划线、短横线');
        } else {
            alert('名称只能包含字母、数字、下划线、短横线');
        }
        return;
    }
    if (!workspace) {
        if (typeof orchToast === 'function') {
            orchToast('请输入工作空间路径');
        } else {
            alert('请输入工作空间路径');
        }
        return;
    }

    // Auto-generate global name: team + "_" + shortName
    const globalName = currentGroupId + '_' + shortName;

    const btn = overlay.querySelector('#form-openclaw button[onclick="addOpenClawMember()"]');
    btn.disabled = true;
    btn.textContent = '⏳ 创建中...';

    // Get selected expert content
    const pickBtn = overlay.querySelector('#add-oc-pick-expert');
    const selectedExpertContent = pickBtn ? pickBtn._selectedExpertContent : null;

    try {
        // 1. Create the agent on OASIS server (use globalName as the OASIS agent name)
        const r = await fetch('/proxy_openclaw_add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: globalName, workspace }),
        });
        const res = await r.json();
        
        if (r.ok && res.ok) {
            // 2. If expert was selected, write IDENTITY.md
            if (selectedExpertContent) {
                try {
                    await fetch('/proxy_openclaw_workspace_file', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            workspace,
                            filename: 'IDENTITY.md',
                            content: selectedExpertContent
                        }),
                    });
                } catch(e) { console.warn('Failed to write IDENTITY.md:', e); }
            }

            // 3. Save to external_agents.json (name=shortName, tag=openclaw, global_name=globalName)
            try {
                await fetch(`/teams/${encodeURIComponent(currentGroupId)}/members/external`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: shortName,
                        tag: 'openclaw',
                        global_name: globalName
                    })
                });
            } catch(e) { console.warn('Failed to save to external_agents.json:', e); }
            
            if (typeof orchToast === 'function') {
                orchToast('🦞 OpenClaw Agent创建成功！');
            }
            overlay.remove();
            await loadTeamMembers();
            // Ensure members overlay stays visible after refresh
            const membersOverlay = document.getElementById('team-members-overlay');
            if (membersOverlay) membersOverlay.style.display = 'flex';

            // Auto-open the full config modal (files/tools/channels) for the new agent
            setTimeout(() => orchShowAgentConfigModal(globalName), 500);
        } else {
            if (r.status === 409) {
                if (typeof orchToast === 'function') {
                    orchToast('⚠️ Agent名称已存在，请使用其他名称');
                } else {
                    alert('⚠️ Agent名称已存在，请使用其他名称');
                }
                ocNameInp.style.borderColor = '#ef4444';
                ocNameInp.style.background = '#fef2f2';
                ocNameInp.focus();
                ocNameInp.select();
            } else {
                const errMsg = res.error || '创建失败';
                if (typeof orchToast === 'function') {
                    orchToast('❌ ' + errMsg);
                } else {
                    alert('❌ ' + errMsg);
                }
            }
            btn.disabled = false;
            btn.textContent = '🦞 新建';
        }
    } catch(e) {
        if (typeof orchToast === 'function') {
            orchToast('❌ 网络错误');
        } else {
            alert('❌ 网络错误');
        }
        btn.disabled = false;
        btn.textContent = '🦞 新建';
    }
}


// ─── Import existing Internal Agent into team ───
let _importSelectedOasis = null;

function showImportOasisModal() {
    // Close the add-member modal
    const addOverlay = document.getElementById('add-team-member-overlay');
    if (addOverlay) addOverlay.remove();

    const overlay = document.createElement('div');
    overlay.className = 'orch-modal-overlay';
    overlay.id = 'import-oasis-overlay';
    overlay.innerHTML = `
        <div class="orch-modal" style="min-width:380px;max-width:500px;">
            <h3>📥 导入 Internal Agent</h3>
            <div style="font-size:11px;color:#6b7280;margin-bottom:8px;">从公共 Internal Agents 列表中选择，导入到当前团队：</div>
            <div id="import-oasis-list" style="max-height:300px;overflow-y:auto;border:1px solid #e5e7eb;border-radius:8px;padding:4px;">
                <div style="padding:12px;text-align:center;font-size:11px;color:#9ca3af;">⏳ 加载中...</div>
            </div>
            <div class="orch-modal-btns" style="margin-top:12px;">
                <button onclick="document.getElementById('import-oasis-overlay').remove()" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">取消</button>
                <button id="import-oasis-join-btn" onclick="_doImportOasis()" disabled style="padding:6px 14px;border-radius:6px;border:none;background:#2563eb;color:white;cursor:pointer;font-size:12px;opacity:0.5;">加入团队</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

    _importSelectedOasis = null;
    _loadImportOasisList();
}

async function _loadImportOasisList() {
    const listEl = document.getElementById('import-oasis-list');
    if (!listEl) return;
    try {
        const resp = await fetch('/internal_agents');
        const data = await resp.json();
        const agents = data.agents || [];

        if (agents.length === 0) {
            listEl.innerHTML = '<div style="padding:12px;text-align:center;font-size:11px;color:#9ca3af;">没有可导入的 Internal Agent</div>';
            return;
        }

        listEl.innerHTML = agents.map(a => {
            const meta = a.meta || {};
            const name = meta.name || '(unnamed)';
            const tag = meta.tag || '';
            const sid = a.session || '';
            return `<div class="import-item" data-session="${escapeHtml(sid)}" data-name="${escapeHtml(name)}" data-tag="${escapeHtml(tag)}"
                         onclick="_selectImportOasis(this)"
                         style="padding:8px 10px;border-radius:6px;cursor:pointer;display:flex;align-items:center;gap:8px;transition:background .15s;border:2px solid transparent;">
                <div style="width:32px;height:32px;border-radius:50%;background:#eff6ff;display:flex;align-items:center;justify-content:center;font-size:14px;">🤖</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-size:12px;font-weight:600;color:#374151;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(name)}</div>
                    <div style="font-size:10px;color:#9ca3af;font-family:monospace;">${escapeHtml(sid.slice(-12))}${tag ? ' \u00b7 ' + escapeHtml(tag) : ''}</div>
                </div>
            </div>`;
        }).join('');
    } catch(e) {
        listEl.innerHTML = '<div style="padding:12px;text-align:center;font-size:11px;color:#ef4444;">加载失败: ' + e.message + '</div>';
    }
}

function _selectImportOasis(el) {
    el.parentElement.querySelectorAll('.import-item').forEach(item => {
        item.style.borderColor = 'transparent';
        item.style.background = '';
    });
    el.style.borderColor = '#2563eb';
    el.style.background = '#eff6ff';
    _importSelectedOasis = { session: el.dataset.session, name: el.dataset.name, tag: el.dataset.tag };
    const btn = document.getElementById('import-oasis-join-btn');
    if (btn) { btn.disabled = false; btn.style.opacity = '1'; }
}

async function _doImportOasis() {
    if (!_importSelectedOasis) { alert('请先选择一个 Agent'); return; }
    const { session, name, tag } = _importSelectedOasis;
    try {
        const url = `/internal_agents?team=${encodeURIComponent(currentGroupId)}`;
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session, meta: { name, tag: tag || '' } })
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || '导入失败');
        }
        alert('✅ Internal Agent 已导入团队');
        document.getElementById('import-oasis-overlay').remove();
        loadTeamMembers();
        // Ensure members overlay stays visible after refresh
        const membersOverlay = document.getElementById('team-members-overlay');
        if (membersOverlay) membersOverlay.style.display = 'flex';
    } catch (e) {
        console.error('Failed to import oasis agent:', e);
        alert('导入失败: ' + e.message);
    }
}

// ─── Import existing OpenClaw Agent into team ───
let _importSelectedOC = null;

function showImportOpenClawModal() {
    // Close the add-member modal
    const addOverlay = document.getElementById('add-team-member-overlay');
    if (addOverlay) addOverlay.remove();

    const overlay = document.createElement('div');
    overlay.className = 'orch-modal-overlay';
    overlay.id = 'import-oc-overlay';
    overlay.innerHTML = `
        <div class="orch-modal" style="min-width:380px;max-width:500px;">
            <h3>📥 导入 OpenClaw Agent</h3>
            <div style="font-size:11px;color:#6b7280;margin-bottom:8px;">从全局 OpenClaw Agents 列表中选择，导入到当前团队：</div>
            <div id="import-oc-list" style="max-height:260px;overflow-y:auto;border:1px solid #e5e7eb;border-radius:8px;padding:4px;">
                <div style="padding:12px;text-align:center;font-size:11px;color:#9ca3af;">⏳ 加载中...</div>
            </div>
            <label style="font-size:11px;font-weight:600;color:#374151;margin-top:8px;display:block;">
                Team内名称 (可选，留空则使用原名)
                <input id="import-oc-team-name" type="text" placeholder="留空使用原名"
                       style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;"
                       pattern="[a-zA-Z0-9_-]+" title="仅支持字母、数字、下划线、短横线">
            </label>
            <div class="orch-modal-btns" style="margin-top:12px;">
                <button onclick="document.getElementById('import-oc-overlay').remove()" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">取消</button>
                <button id="import-oc-join-btn" onclick="_doImportOpenClaw()" disabled style="padding:6px 14px;border-radius:6px;border:none;background:#7c3aed;color:white;cursor:pointer;font-size:12px;opacity:0.5;">🦞 加入团队</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

    _importSelectedOC = null;
    _loadImportOCList();
}

async function _loadImportOCList() {
    const listEl = document.getElementById('import-oc-list');
    if (!listEl) return;
    try {
        const resp = await fetch('/proxy_openclaw_sessions');
        const data = await resp.json();

        if (!data.available) {
            listEl.innerHTML = '<div style="padding:12px;text-align:center;font-size:11px;color:#9ca3af;">🚫 OpenClaw 未配置</div>';
            return;
        }

        const agents = data.agents || [];

        if (agents.length === 0) {
            listEl.innerHTML = '<div style="padding:12px;text-align:center;font-size:11px;color:#9ca3af;">没有可导入的 OpenClaw Agent</div>';
            return;
        }

        listEl.innerHTML = agents.map(a => {
            const name = a.name || '';
            const model = a.model || '';
            const workspace = a.workspace || '';
            return `<div class="import-item" data-name="${escapeHtml(name)}" data-workspace="${escapeHtml(workspace)}"
                         onclick="_selectImportOC(this)"
                         style="padding:8px 10px;border-radius:6px;cursor:pointer;display:flex;align-items:center;gap:8px;transition:background .15s;border:2px solid transparent;">
                <div style="width:32px;height:32px;border-radius:50%;background:#faf5ff;display:flex;align-items:center;justify-content:center;font-size:14px;">🦞</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-size:12px;font-weight:600;color:#374151;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(name)}</div>
                    <div style="font-size:10px;color:#9ca3af;font-family:monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(model)}${workspace ? ' \u00b7 ' + escapeHtml(workspace) : ''}</div>
                </div>
            </div>`;
        }).join('');
    } catch(e) {
        listEl.innerHTML = '<div style="padding:12px;text-align:center;font-size:11px;color:#ef4444;">加载失败: ' + e.message + '</div>';
    }
}

function _selectImportOC(el) {
    el.parentElement.querySelectorAll('.import-item').forEach(item => {
        item.style.borderColor = 'transparent';
        item.style.background = '';
    });
    el.style.borderColor = '#7c3aed';
    el.style.background = '#faf5ff';
    _importSelectedOC = { name: el.dataset.name, workspace: el.dataset.workspace };
    const btn = document.getElementById('import-oc-join-btn');
    if (btn) { btn.disabled = false; btn.style.opacity = '1'; }
}

async function _doImportOpenClaw() {
    if (!_importSelectedOC) { alert('请先选择一个 OpenClaw Agent'); return; }

    const ocGlobalName = _importSelectedOC.name;
    const teamNameInput = document.getElementById('import-oc-team-name');
    const shortName = (teamNameInput && teamNameInput.value.trim()) || ocGlobalName;

    try {
        // Save to external_agents.json (tag=openclaw, global_name=original openclaw agent name)
        const resp = await fetch(`/teams/${encodeURIComponent(currentGroupId)}/members/external`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: shortName, tag: 'openclaw', global_name: ocGlobalName })
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || '导入失败');
        }
        alert('🦞 OpenClaw Agent 已导入团队');
        document.getElementById('import-oc-overlay').remove();
        loadTeamMembers();
        // Ensure members overlay stays visible after refresh
        const membersOverlay = document.getElementById('team-members-overlay');
        if (membersOverlay) membersOverlay.style.display = 'flex';
    } catch (e) {
        console.error('Failed to import openclaw agent:', e);
        alert('导入失败: ' + e.message);
    }
}

// ================================================================
// ===== OpenClaw Chat Switcher Logic =====
// ================================================================

/**
 * Load available OpenClaw agents from /proxy_openclaw_sessions
 * and populate the <select> dropdown.
 */
async function ocLoadAgents() {
    const select = document.getElementById('oc-agent-select');
    if (!select) return;

    // Show loading state
    select.innerHTML = '<option value="">⏳ ' + t('loading') + '</option>';
    select.disabled = true;

    try {
        const resp = await fetch('/proxy_openclaw_sessions');
        const data = await resp.json();

        if (!data.available) {
            select.innerHTML = '<option value="">🚫 ' + t('oc_not_configured') + '</option>';
            _ocAvailable = false;
            return;
        }
        _ocAvailable = true;
        _ocAgentsCache = data.agents || [];

        select.innerHTML = '<option value="">' + t('oc_select_agent') + '</option>';
        for (const agent of _ocAgentsCache) {
            const opt = document.createElement('option');
            opt.value = agent.name;
            opt.textContent = '🦞 ' + agent.name;
            select.appendChild(opt);
        }

        // Restore previous selection if still available
        if (_ocSelectedAgent) {
            const found = _ocAgentsCache.find(a => a.name === _ocSelectedAgent.name);
            if (found) {
                select.value = found.name;
            } else {
                _ocSelectedAgent = null;
            }
        }
    } catch (e) {
        console.error('ocLoadAgents failed:', e);
        select.innerHTML = '<option value="">❌ ' + t('oc_load_failed') + '</option>';
    } finally {
        select.disabled = false;
    }
}

/**
 * Switch between 'internal' (TeamBot) and 'openclaw' chat modes.
 */
function ocSwitchTo(mode) {
    _ocChatMode = mode;

    const tabInternal = document.getElementById('oc-tab-internal');
    const tabOpenclaw = document.getElementById('oc-tab-openclaw');
    const agentSelector = document.getElementById('oc-agent-selector');

    if (tabInternal) tabInternal.classList.toggle('active', mode === 'internal');
    if (tabOpenclaw) tabOpenclaw.classList.toggle('active', mode === 'openclaw');

    if (mode === 'openclaw') {
        if (agentSelector) agentSelector.style.display = 'flex';
        // Load agents if cache is empty
        if (_ocAgentsCache.length === 0) {
            ocLoadAgents();
        }
    } else {
        if (agentSelector) agentSelector.style.display = 'none';
        _ocSelectedAgent = null;
    }

    // Update chat box hint
    ocUpdateChatHint();
}

/**
 * Handle agent selection change from the dropdown.
 */
function ocOnAgentChange() {
    const select = document.getElementById('oc-agent-select');
    if (!select) return;

    const agentName = select.value;
    if (agentName) {
        _ocSelectedAgent = { name: agentName };
    } else {
        _ocSelectedAgent = null;
    }

    ocUpdateChatHint();
}

/**
 * Update the welcome/hint message in chat box based on current OpenClaw state.
 */
function ocUpdateChatHint() {
    const chatBox = document.getElementById('chat-box');
    if (!chatBox) return;

    // Only show hint when switching modes (don't clear ongoing conversations)
    if (_ocChatMode === 'openclaw' && _ocSelectedAgent) {
        // If chat box only has the welcome message, update it
        const firstMsg = chatBox.querySelector('.message-agent');
        if (firstMsg && chatBox.children.length <= 1) {
            firstMsg.innerHTML = t('oc_chatting_with', { name: _ocSelectedAgent.name }) +
                '<br><span style="font-size:0.85em;color:#6b7280;">OpenClaw Agent — ' + escapeHtml(_ocSelectedAgent.name) + '</span>';
        }
    }
}

/**
 * Initialize the OpenClaw Chat Switcher on page load.
 * Detects if OpenClaw is available; if yes, shows the switcher bar.
 */
async function ocInitSwitcher() {
    const switcher = document.getElementById('openclaw-chat-switcher');
    if (!switcher) return;

    try {
        const resp = await fetch('/proxy_openclaw_sessions');
        const data = await resp.json();

        if (data.available && data.agents && data.agents.length > 0) {
            _ocAvailable = true;
            _ocAgentsCache = data.agents;
            switcher.style.display = '';
            // Pre-populate agent dropdown
            const select = document.getElementById('oc-agent-select');
            if (select) {
                select.innerHTML = '<option value="">' + t('oc_select_agent') + '</option>';
                for (const agent of _ocAgentsCache) {
                    const opt = document.createElement('option');
                    opt.value = agent.name;
                    opt.textContent = '🦞 ' + agent.name;
                    select.appendChild(opt);
                }
            }
        } else {
            _ocAvailable = false;
            switcher.style.display = 'none';
        }
    } catch (e) {
        // OpenClaw not available, hide switcher
        _ocAvailable = false;
        switcher.style.display = 'none';
        console.log('OpenClaw not available for chat switcher:', e.message);
    }
}

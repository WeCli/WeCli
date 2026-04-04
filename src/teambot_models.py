"""
Pydantic request models for TeamBot runtime APIs.
"""

from pydantic import BaseModel, Field


class TeamBotSubagentRefRequest(BaseModel):
    user_id: str
    password: str = ""
    agent_ref: str


class TeamBotSubagentHistoryRequest(TeamBotSubagentRefRequest):
    limit: int = 12


class TeamBotToolPolicyUpdateRequest(BaseModel):
    user_id: str
    password: str = ""
    policy: dict


class TeamBotSessionRuntimeRequest(BaseModel):
    user_id: str
    password: str = ""
    session_id: str


class TeamBotPlanUpdateRequest(TeamBotSessionRuntimeRequest):
    title: str
    status: str = "active"
    items: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class TeamBotWorkflowPresetApplyRequest(TeamBotSessionRuntimeRequest):
    preset_id: str
    metadata: dict = Field(default_factory=dict)


class TeamBotTodoUpdateRequest(TeamBotSessionRuntimeRequest):
    items: list[dict] = Field(default_factory=list)


class TeamBotSessionModeUpdateRequest(TeamBotSessionRuntimeRequest):
    mode: str = "execute"
    reason: str = ""


class TeamBotSessionInboxDeliverRequest(TeamBotSessionRuntimeRequest):
    target_ref: str = ""
    limit: int = 20
    force: bool = False


class TeamBotSessionInboxListRequest(TeamBotSessionRuntimeRequest):
    target_ref: str = ""
    status: str = "queued"
    limit: int = 20


class TeamBotSessionInboxSendRequest(TeamBotSessionRuntimeRequest):
    target_ref: str = ""
    body: str = ""


class TeamBotRunInterruptRequest(TeamBotSessionRuntimeRequest):
    run_id: str = ""
    agent_ref: str = ""


class TeamBotBridgeAttachRequest(TeamBotSessionRuntimeRequest):
    role: str = "viewer"
    label: str = ""


class TeamBotBridgeDetachRequest(BaseModel):
    user_id: str
    password: str = ""
    bridge_id: str


class TeamBotVoiceStateUpdateRequest(TeamBotSessionRuntimeRequest):
    enabled: bool = False
    auto_read_aloud: bool = False
    last_transcript: str = ""
    tts_model: str = ""
    tts_voice: str = ""
    stt_model: str = ""


class TeamBotBuddyActionRequest(BaseModel):
    user_id: str
    password: str = ""
    session_id: str = ""
    action: str = "pet"


class TeamBotKairosUpdateRequest(TeamBotSessionRuntimeRequest):
    enabled: bool = False
    reason: str = ""


class TeamBotDreamRequest(TeamBotSessionRuntimeRequest):
    reason: str = ""


class TeamBotVerificationCreateRequest(TeamBotSessionRuntimeRequest):
    title: str
    status: str = "passed"
    details: str = ""


class TeamBotApprovalResolutionRequest(BaseModel):
    user_id: str
    password: str = ""
    approval_id: str
    action: str = "approve"
    reason: str = ""
    remember: bool = False
    session_id: str = ""

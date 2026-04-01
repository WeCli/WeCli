import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "selfskill" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import configure_openclaw as co  # noqa: E402


class ConfigureOpenClawSyncTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

        root = Path(self.tempdir.name)
        self.env_path = root / "config" / ".env"
        self.env_path.parent.mkdir(parents=True, exist_ok=True)

        self.openclaw_home = root / ".openclaw"
        self.openclaw_home.mkdir(parents=True, exist_ok=True)
        self.config_path = self.openclaw_home / "openclaw.json"

        self.original_env_path = co.ENV_PATH
        self.original_openclaw_home = co.OPENCLAW_HOME
        self.original_config_path = co.OPENCLAW_CONFIG_PATH

        co.ENV_PATH = str(self.env_path)
        co.OPENCLAW_HOME = str(self.openclaw_home)
        co.OPENCLAW_CONFIG_PATH = str(self.config_path)

        self.addCleanup(self._restore_paths)

        self.runtime_patcher = mock.patch.object(co, "detect_gateway_runtime", return_value="stopped")
        self.runtime_patcher.start()
        self.addCleanup(self.runtime_patcher.stop)

    def _restore_paths(self):
        co.ENV_PATH = self.original_env_path
        co.OPENCLAW_HOME = self.original_openclaw_home
        co.OPENCLAW_CONFIG_PATH = self.original_config_path

    def _write_openclaw_config(self, data):
        self.config_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _read_openclaw_config(self):
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def test_detect_llm_config_prefers_effective_openai_env_key(self):
        self._write_openclaw_config(
            {
                "env": {"OPENAI_API_KEY": "env-openai-key"},
                "models": {
                    "providers": {
                        "openai": {
                            "baseUrl": "https://api.openai.com/v1",
                            "apiKey": "provider-openai-key",
                            "api": "openai-completions",
                            "models": [{"id": "gpt-5.4", "name": "gpt-5.4"}],
                        }
                    }
                },
                "agents": {"defaults": {"model": {"primary": "openai/gpt-5.4"}}},
            }
        )

        detected = co.detect_llm_config_from_openclaw()

        self.assertEqual(detected["LLM_API_KEY"], "env-openai-key")
        self.assertEqual(detected["LLM_BASE_URL"], "https://api.openai.com")
        self.assertEqual(detected["LLM_MODEL"], "gpt-5.4")
        self.assertEqual(detected["LLM_PROVIDER"], "openai")

    def test_export_openai_config_updates_provider_and_env_key(self):
        self._write_openclaw_config(
            {
                "env": {"OPENAI_API_KEY": "old-env-key"},
                "models": {
                    "providers": {
                        "openai": {
                            "baseUrl": "https://api.openai.com/v1",
                            "apiKey": "old-provider-key",
                            "api": "openai-completions",
                            "models": [],
                        }
                    }
                },
                "agents": {"defaults": {"model": {"primary": "openai/old-model"}, "models": {}}},
            }
        )

        result = co.export_llm_config_to_openclaw(
            api_key="new-openai-key",
            base_url="https://api.openai.com",
            model="gpt-5.4",
            provider="openai",
        )
        saved = self._read_openclaw_config()

        self.assertTrue(result["ok"])
        self.assertEqual(saved["env"]["OPENAI_API_KEY"], "new-openai-key")
        self.assertEqual(saved["models"]["providers"]["openai"]["apiKey"], "new-openai-key")
        self.assertEqual(saved["models"]["providers"]["openai"]["baseUrl"], "https://api.openai.com/v1")
        self.assertEqual(saved["agents"]["defaults"]["model"]["primary"], "openai/gpt-5.4")

        models = saved["models"]["providers"]["openai"]["models"]
        self.assertIn("gpt-5.4", [entry["id"] for entry in models])

    def test_export_ollama_config_allows_empty_api_key(self):
        self._write_openclaw_config(
            {
                "models": {
                    "providers": {
                        "ollama": {
                            "baseUrl": "http://127.0.0.1:11434/v1",
                            "apiKey": "old-placeholder",
                            "api": "openai-completions",
                            "models": [],
                        }
                    }
                },
                "agents": {"defaults": {"model": {"primary": "openai/old-model"}, "models": {}}},
            }
        )

        result = co.export_llm_config_to_openclaw(
            api_key="",
            base_url="http://127.0.0.1:11434",
            model="llama3.2:latest",
            provider="ollama",
        )
        saved = self._read_openclaw_config()

        self.assertTrue(result["ok"])
        self.assertEqual(result["provider"], "ollama")
        self.assertEqual(saved["models"]["providers"]["ollama"]["baseUrl"], "http://127.0.0.1:11434/v1")
        self.assertEqual(saved["models"]["providers"]["ollama"]["apiKey"], "ollama")
        self.assertEqual(saved["agents"]["defaults"]["model"]["primary"], "ollama/llama3.2:latest")
        models = saved["models"]["providers"]["ollama"]["models"]
        self.assertIn("llama3.2:latest", [entry["id"] for entry in models])

    @mock.patch.object(co, "export_llm_config_to_openclaw")
    @mock.patch.object(
        co,
        "read_teamclaw_llm_config",
        return_value={
            "LLM_API_KEY": "",
            "LLM_BASE_URL": "http://127.0.0.1:11434",
            "LLM_MODEL": "llama3.2:latest",
            "LLM_PROVIDER": "ollama",
        },
    )
    def test_sync_teamclaw_llm_to_openclaw_allows_keyless_ollama(
        self,
        _mock_read_teamclaw_llm_config,
        mock_export,
    ):
        mock_export.return_value = {"ok": True, "provider": "ollama"}

        result = co.sync_teamclaw_llm_to_openclaw()

        self.assertEqual(result["provider"], "ollama")
        mock_export.assert_called_once_with(
            api_key="",
            base_url="http://127.0.0.1:11434",
            model="llama3.2:latest",
            provider="ollama",
        )

    @mock.patch.object(co, "repair_sessions_health", return_value={"checked": True, "missing": 0, "repaired": False})
    @mock.patch.object(co, "detect_sessions_file", return_value="/tmp/openclaw/sessions.json")
    @mock.patch.object(co, "detect_gateway_token", return_value="gateway-token-1234")
    @mock.patch.object(co, "detect_gateway_port", return_value=19001)
    @mock.patch.object(co, "detect_gateway_auth_mode", return_value="token")
    @mock.patch.object(co, "enable_chat_completions_endpoint", return_value=(True, True))
    @mock.patch.object(co, "set_env_with_validation")
    @mock.patch.object(co, "read_env", return_value=([], {}))
    @mock.patch.object(co, "wait_for_gateway_runtime", return_value="running")
    @mock.patch.object(co, "run_cmd", return_value=(0, "started", ""))
    @mock.patch.object(co, "detect_gateway_runtime", return_value="stopped")
    @mock.patch.object(co, "detect_openclaw_bin", return_value="/usr/local/bin/openclaw")
    def test_sync_openclaw_runtime_for_teamclaw_startup_refreshes_runtime_env_only(
        self,
        _mock_detect_bin,
        _mock_runtime,
        _mock_run_cmd,
        _mock_wait_runtime,
        _mock_read_env,
        mock_set_env,
        _mock_enable_chat,
        _mock_auth_mode,
        _mock_port,
        _mock_token,
        _mock_sessions,
        _mock_repair,
    ):
        result = co.sync_openclaw_runtime_for_teamclaw_startup()

        self.assertTrue(result["installed"])
        self.assertTrue(result["gateway_started"])
        self.assertEqual(result["runtime_after"], "running")
        self.assertEqual(result["api_url"], "http://127.0.0.1:19001/v1/chat/completions")
        self.assertTrue(result["token_present"])
        self.assertEqual(result["sessions_file"], "/tmp/openclaw/sessions.json")
        self.assertCountEqual(
            result["env_updates"],
            ["OPENCLAW_API_URL", "OPENCLAW_GATEWAY_TOKEN", "OPENCLAW_SESSIONS_FILE"],
        )
        self.assertEqual(
            mock_set_env.call_args_list,
            [
                mock.call("OPENCLAW_API_URL", "http://127.0.0.1:19001/v1/chat/completions"),
                mock.call("OPENCLAW_GATEWAY_TOKEN", "gateway-token-1234"),
                mock.call("OPENCLAW_SESSIONS_FILE", "/tmp/openclaw/sessions.json"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
